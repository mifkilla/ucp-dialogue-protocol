"""Small, dependency-free reference for UCP continuity, Python 3.11+.

This is a single-writer local event store, not an authorization service. Caller
identities, current agreements and external evidence must be authenticated by
the integrating application. The hash chain detects inconsistent edits, not
lies or a complete rewrite. No method executes tools or contacts participants.
Journal ordering cannot establish when an external action happened. Executors
must recheck authority immediately before an effect. Adapters must represent
outgoing communication with action="contact"; arbitrary names have no inferred
semantics. A resource identifies a particular effect/idempotency target.
Reviewer lists identify alternative designated reviewers, not unanimous
multi-party approval. Callers supply these lists and identities without
authentication here. The integrating authority must collect all approvals
required for a shared agreement amendment before recording its acceptance.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def detached(value: Any) -> Any:
    return json.loads(canonical(value))


class ContinuityError(ValueError):
    """An operation would violate the reference contract."""


@dataclass(frozen=True)
class CurrentAgreement:
    project: str
    participant: str
    revision: str
    permissions: frozenset[tuple[str, str]] = frozenset()
    authority_known: bool = True
    no_contact: bool = False

    def permits(self, action: str, resource: str) -> bool:
        return bool(self.authority_known and self.revision and
                    (action, resource) in self.permissions and
                    not (self.no_contact and action == "contact"))

    def snapshot(self) -> dict:
        value = asdict(self)
        value["permissions"] = sorted([list(p) for p in self.permissions])
        return value


class Continuity:
    """Append-only records; optional JSONL persistence for one writer/process.

    Expected-head checks protect logical updates in this instance. They are not
    a cross-process lock. Read values are detached from internal state.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else None
        self._events: list[dict] = []
        if self.path is not None and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                body = {k: v for k, v in event.items() if k != "hash"}
                expected_previous = self._events[-1]["hash"] if self._events else None
                if (event.get("seq") != len(self._events) + 1 or
                        event.get("previous") != expected_previous or
                        event.get("hash") != digest(body)):
                    raise ContinuityError("Invalid event chain")
                self._events.append(event)

    def events(self) -> list[dict]:
        return detached(self._events)

    def _append(self, kind: str, **data: Any) -> dict:
        event = detached({"seq": len(self._events) + 1, "kind": kind,
                          "previous": self._events[-1]["hash"] if self._events else None,
                          "data": data})
        event["hash"] = digest(event)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(canonical(event) + "\n")
                stream.flush()
        self._events.append(event)
        return detached(event)

    def _event(self, seq: int, kind: str | None = None) -> dict:
        if not isinstance(seq, int) or not 1 <= seq <= len(self._events):
            raise ContinuityError("Unknown event")
        event = self._events[seq - 1]
        if kind is not None and event["kind"] != kind:
            raise ContinuityError("Unexpected event kind")
        return event

    @staticmethod
    def _required(**values: str) -> None:
        if any(not isinstance(v, str) or not v.strip() for v in values.values()):
            raise ContinuityError("Nonempty text required: " + ", ".join(values))

    def remember(self, *, project: str, participant: str, key: str, category: str,
                 content: Any, source: str, expected_head: int | None = None) -> int:
        self._required(project=project, participant=participant, key=key, source=source)
        if category not in {"agreement", "work", "experience"}:
            raise ContinuityError("Unknown memory category")
        previous = [e for e in self._events if e["kind"] == "record" and
                    all(e["data"][k] == v for k, v in
                        {"project": project, "participant": participant,
                         "key": key, "category": category}.items())]
        head = previous[-1]["seq"] if previous else None
        if expected_head != head:
            raise ContinuityError("Stale record head; inspect both versions")
        return self._append("record", project=project, participant=participant,
                            key=key, category=category, content=content,
                            source=source, supersedes=head)["seq"]

    def challenge_record(self, record_id: int, *, reason: str, source: str) -> int:
        self._event(record_id, "record")
        self._required(reason=reason, source=source)
        return self._append("record_challenge", record_id=record_id,
                            reason=reason, source=source)["seq"]

    def _outcome(self, plan_id: int) -> dict | None:
        found = [e for e in self._events if e["kind"] == "outcome" and
                 e["data"]["plan_id"] == plan_id]
        return found[0] if found else None

    def _invalid(self, plan_id: int) -> bool:
        return any(e["kind"] == "outcome_invalidation" and
                   e["data"]["plan_id"] == plan_id for e in self._events)

    def _effect(self, plan_id: int) -> str:
        reconciliations = [e for e in self._events if e["kind"] == "reconciliation" and
                           e["data"]["plan_id"] == plan_id]
        invalidations = [e["seq"] for e in self._events if
                         e["kind"] == "outcome_invalidation" and
                         e["data"]["plan_id"] == plan_id]
        threshold = max(invalidations, default=0)
        fresh = [e for e in reconciliations if e["seq"] > threshold]
        if fresh:
            return fresh[-1]["data"]["effect_status"]
        outcome = self._outcome(plan_id)
        return (outcome["data"]["effect_status"]
                if outcome is not None and not self._invalid(plan_id) else "unknown")

    def cold_boot(self, *, project: str, participant: str,
                  current: CurrentAgreement | None, keys: set[str] | None = None,
                  limit: int = 8) -> dict:
        if limit < 1:
            raise ContinuityError("Positive retrieval limit required")
        if current is not None and (current.project, current.participant) != (project, participant):
            raise ContinuityError("Current agreement has the wrong scope")
        heads: dict[tuple[str, str], dict] = {}
        for event in self._events:
            data = event["data"]
            if (event["kind"] == "record" and data["project"] == project and
                    data["participant"] == participant and
                    (keys is None or data["key"] in keys)):
                heads[(data["category"], data["key"])] = event
        records = {category: [] for category in ("agreement", "work", "experience")}
        for event in sorted(heads.values(), key=lambda e: e["seq"], reverse=True):
            item = detached(event)
            item["challenges"] = [detached(e) for e in self._events if
                                  e["kind"] == "record_challenge" and
                                  e["data"]["record_id"] == event["seq"]]
            records[event["data"]["category"]].append(item)
        unknown = [detached(e) for e in self._events if e["kind"] == "plan" and
                   e["data"]["project"] == project and e["data"]["participant"] == participant
                   and self._effect(e["seq"]) == "unknown"]
        # Unknown effects are never discarded to satisfy a retrieval size limit.
        return {
            "agreement": {"current": current.snapshot() if current else None,
                          "authority_status": "known" if current and current.authority_known else "unknown",
                          "history": records["agreement"][:limit],
                          "contact_allowed": bool(current and current.permits("contact", participant))},
            "work": {"records": records["work"][:limit], "unknown_effects": unknown},
            "experience": {"records": records["experience"][:limit],
                           "rules": [self.rule_snapshot(e["seq"]) for e in self._events
                                     if e["kind"] == "rule_candidate" and
                                     e["data"]["project"] == project and
                                     e["data"]["participant"] == participant]},
            "boundary": "Historical records are data, not current authorization. Reconcile unknown effects before retrying.",
        }

    def plan(self, *, project: str, participant: str, case_id: str, action: str,
             resource: str, expected_effect: str, verification: str,
             current: CurrentAgreement, validation_rule: int | None = None,
             applied_rule: int | None = None, interface: str | None = None) -> int:
        self._required(project=project, participant=participant, case_id=case_id,
                       action=action, resource=resource, expected_effect=expected_effect,
                       verification=verification)
        if (current.project, current.participant) != (project, participant) or not current.permits(action, resource):
            raise ContinuityError("Current authority does not cover this plan")
        for event in self._events:
            if event["kind"] != "plan":
                continue
            data = event["data"]
            if all(data[k] == v for k, v in {"project": project, "participant": participant,
                                           "action": action, "resource": resource}.items()):
                # resource is an effect/idempotency target, not just a broad service name.
                effect = self._effect(event["seq"])
                if effect in {"unknown", "confirmed"}:
                    raise ContinuityError("Reconcile unknown effect or avoid an already confirmed duplicate")
        if validation_rule is not None and applied_rule is not None:
            raise ContinuityError("Separate validation from use of an accepted rule")
        snapshot = None
        selected_rule = validation_rule if validation_rule is not None else applied_rule
        if selected_rule is not None:
            snapshot = self.rule_snapshot(selected_rule)
            candidate = snapshot["candidate"]
            if (candidate["project"], candidate["participant"], candidate["interface"]) != (project, participant, interface):
                raise ContinuityError("Rule scope or interface mismatch")
            if applied_rule is not None and snapshot["state"] != "accepted":
                raise ContinuityError("Only accepted rules can be selected as standing rules")
        if validation_rule is not None:
            candidate = snapshot["candidate"]
            if case_id == candidate["source_case"]:
                raise ContinuityError("Validation requires a new case")
            if verification != candidate["validation_plan"]:
                raise ContinuityError("Validation must use the declared check")
            if snapshot["state"] in {"retired", "rejected"} or self._invalid(candidate["basis_plan"]):
                raise ContinuityError("Rule cannot be validated on its current basis")
        return self._append("plan", project=project, participant=participant, case_id=case_id,
                            action=action, resource=resource, expected_effect=expected_effect,
                            verification=verification, agreement=current.snapshot(),
                            validation_rule=validation_rule, applied_rule=applied_rule,
                            interface=interface,
                            rule_digest=snapshot["digest"] if snapshot else None)["seq"]

    def outcome(self, plan_id: int, *, status: str, effect_status: str, evidence: str) -> int:
        plan = self._event(plan_id, "plan")
        self._required(evidence=evidence)
        if self._outcome(plan_id) is not None:
            raise ContinuityError("Outcome exists; append an invalidation instead")
        if status not in {"success", "failure", "partial", "unverified"} or effect_status not in {"confirmed", "not_occurred", "unknown"}:
            raise ContinuityError("Unknown outcome status")
        if status == "success" and effect_status != "confirmed":
            raise ContinuityError("Unknown or absent effects cannot establish success")
        if status == "unverified" and effect_status != "unknown":
            raise ContinuityError("Unverified outcome requires an unknown effect")
        event = self._append("outcome", plan_id=plan_id, status=status,
                             effect_status=effect_status, evidence=evidence)
        if plan["data"].get("applied_rule") is not None and status in {"failure", "partial"}:
            self.challenge_rule(plan["data"]["applied_rule"],
                                reason="Failed selected-rule application; causality is not established",
                                source=f"outcome:{event['seq']}")
        return event["seq"]

    def invalidate_outcome(self, plan_id: int, *, reason: str, evidence: str) -> int:
        if self._outcome(plan_id) is None:
            raise ContinuityError("No outcome to invalidate")
        self._required(reason=reason, evidence=evidence)
        event = self._append("outcome_invalidation", plan_id=plan_id,
                             reason=reason, evidence=evidence)
        applied_rule = self._event(plan_id, "plan")["data"].get("applied_rule")
        if applied_rule is not None:
            self.challenge_rule(applied_rule, reason="Selected application outcome invalidated",
                                source=f"outcome_invalidation:{event['seq']}")
        return event["seq"]

    def reconcile(self, plan_id: int, *, effect_status: str, evidence: str) -> int:
        self._event(plan_id, "plan")
        self._required(evidence=evidence)
        if effect_status not in {"confirmed", "not_occurred", "unknown"}:
            raise ContinuityError("Unknown reconciliation status")
        return self._append("reconciliation", plan_id=plan_id,
                            effect_status=effect_status, evidence=evidence)["seq"]

    def close(self, plan_id: int, *, diagnosis_closed: bool, repair_status: str,
              effect_status: str, evidence: str) -> int:
        self._event(plan_id, "plan")
        self._required(evidence=evidence)
        if type(diagnosis_closed) is not bool or repair_status not in {"not_attempted", "attempted", "verified", "blocked"}:
            raise ContinuityError("Invalid closure status")
        if effect_status != self._effect(plan_id):
            raise ContinuityError("Closure contradicts recorded effect evidence")
        if repair_status == "verified" and effect_status != "confirmed":
            raise ContinuityError("An unknown effect is not a verified repair")
        return self._append("closure", plan_id=plan_id, diagnosis_closed=diagnosis_closed,
                            repair_status=repair_status, effect_status=effect_status,
                            evidence=evidence)["seq"]

    def propose_rule(self, *, basis_plan: int, interface: str, statement: str,
                     counterexample: str, validation_plan: str,
                     reviewers: list[str]) -> int:
        basis = self._event(basis_plan, "plan")["data"]
        self._required(interface=interface, statement=statement, counterexample=counterexample,
                       validation_plan=validation_plan)
        if not reviewers or any(not isinstance(r, str) or not r.strip() for r in reviewers):
            raise ContinuityError("Authorized reviewer IDs required")
        if self._outcome(basis_plan) is None or self._invalid(basis_plan):
            raise ContinuityError("A rule requires a recorded, non-invalidated source outcome")
        return self._append("rule_candidate", project=basis["project"], participant=basis["participant"],
                            source_case=basis["case_id"], basis_plan=basis_plan,
                            interface=interface, statement=statement, counterexample=counterexample,
                            validation_plan=validation_plan, reviewers=sorted(set(reviewers)))["seq"]

    def rule_snapshot(self, rule_id: int) -> dict:
        candidate_event = self._event(rule_id, "rule_candidate")
        candidate = detached(candidate_event["data"])
        changes = [detached(e) for e in self._events if
                   e["kind"] in {"rule_validation", "rule_review", "rule_challenge"} and
                   e["data"]["rule_id"] == rule_id]
        plans = {candidate["basis_plan"]} | {e["data"]["plan_id"] for e in changes if e["kind"] == "rule_validation"}
        invalidations = [detached(e) for e in self._events if
                         e["kind"] == "outcome_invalidation" and e["data"]["plan_id"] in plans]
        validation_plans = {e["data"]["plan_id"] for e in changes if e["kind"] == "rule_validation"}
        reconciliations = [detached(e) for e in self._events if
                           e["kind"] == "reconciliation" and
                           e["data"]["plan_id"] in validation_plans]
        state = "candidate"
        latest_challenge = 0
        for event in sorted(changes + invalidations + reconciliations, key=lambda e: e["seq"]):
            if state in {"retired", "rejected"}:
                continue
            if (event["kind"] in {"rule_challenge", "outcome_invalidation"} or
                    (event["kind"] == "reconciliation" and
                     event["data"]["effect_status"] != "confirmed")):
                state = "needs_review"
                latest_challenge = event["seq"]
            elif event["kind"] == "rule_validation":
                if event["data"]["plan_id"] > latest_challenge:
                    state = "validated"
            elif event["kind"] == "rule_review":
                state = event["data"]["decision"]
        snapshot = {"rule_id": rule_id, "candidate": candidate, "changes": changes,
                    "invalidations": invalidations, "reconciliations": reconciliations, "state": state,
                    "latest_challenge": latest_challenge}
        snapshot["digest"] = digest(snapshot)
        return snapshot

    def validate_rule(self, rule_id: int, plan_id: int) -> int:
        snapshot = self.rule_snapshot(rule_id)
        plan = self._event(plan_id, "plan")
        outcome = self._outcome(plan_id)
        if snapshot["state"] in {"retired", "rejected"} or self._invalid(snapshot["candidate"]["basis_plan"]):
            raise ContinuityError("Rule requires a new basis or has ended")
        if plan["data"]["validation_rule"] != rule_id or plan["data"]["rule_digest"] != snapshot["digest"]:
            raise ContinuityError("Validation was not planned against this snapshot")
        if (outcome is None or outcome["data"]["status"] != "success" or
                self._invalid(plan_id) or self._effect(plan_id) != "confirmed"):
            raise ContinuityError("Validation needs a successful verified outcome")
        if any(e["kind"] == "reconciliation" and e["data"]["plan_id"] == plan_id and
               e["data"]["effect_status"] != "confirmed" for e in self._events):
            raise ContinuityError("Disputed validation evidence requires a newly planned case")
        if plan_id <= snapshot["latest_challenge"]:
            raise ContinuityError("Validation must be planned after counterevidence")
        if any(e["kind"] == "rule_validation" and
               e["data"]["case_id"] == plan["data"]["case_id"] for e in snapshot["changes"]):
            raise ContinuityError("Repeated case is not new validation")
        return self._append("rule_validation", rule_id=rule_id, plan_id=plan_id,
                            case_id=plan["data"]["case_id"], outcome_id=outcome["seq"])["seq"]

    def review_rule(self, rule_id: int, *, reviewer: str, snapshot_digest: str, decision: str) -> int:
        snapshot = self.rule_snapshot(rule_id)
        if reviewer not in snapshot["candidate"]["reviewers"]:
            raise ContinuityError("Reviewer has no assigned authority")
        if snapshot_digest != snapshot["digest"]:
            raise ContinuityError("Stale or unshown rule snapshot")
        if decision not in {"accepted", "rejected", "retired"}:
            raise ContinuityError("Unknown review decision")
        if snapshot["state"] in {"retired", "rejected"}:
            raise ContinuityError("Ended rule requires a new candidate")
        if decision == "accepted" and snapshot["state"] != "validated":
            raise ContinuityError("Acceptance requires current validation")
        return self._append("rule_review", rule_id=rule_id, reviewer=reviewer,
                            snapshot_digest=snapshot_digest, decision=decision)["seq"]

    def challenge_rule(self, rule_id: int, *, reason: str, source: str) -> int:
        self._event(rule_id, "rule_candidate")
        self._required(reason=reason, source=source)
        return self._append("rule_challenge", rule_id=rule_id, reason=reason, source=source)["seq"]

    def applicable_rules(self, *, project: str, participant: str, interface: str) -> list[dict]:
        return [snapshot for event in self._events if event["kind"] == "rule_candidate"
                and all(event["data"][k] == v for k, v in
                        {"project": project, "participant": participant, "interface": interface}.items())
                for snapshot in [self.rule_snapshot(event["seq"]) ]
                if snapshot["state"] == "accepted"]


def demo() -> dict:
    """Run a synthetic repair-to-new-session example, without external effects."""
    import tempfile

    with tempfile.TemporaryDirectory() as root:
        path = Path(root) / "events.jsonl"
        store = Continuity(path)

        def permission(target):
            return CurrentAgreement("demo", "partner", "current-v1", frozenset({("cancel", target)}))

        def plan(target, case, **kwargs):
            return store.plan(project="demo", participant="partner", case_id=case,
                              action="cancel", resource=target, expected_effect="executor stopped",
                              verification="read executor confirmation", current=permission(target),
                              interface="cancel-v1", **kwargs)

        first = plan("job-1", "organizer-seeded-incident")
        store.outcome(first, status="failure", effect_status="not_occurred",
                      evidence="synthetic receipt: unsupported version field; no command forwarded")
        rule = store.propose_rule(basis_plan=first, interface="cancel-v1",
                                  statement="Check the current schema; cancel-v1 does not accept version",
                                  counterexample="cancel-v2 requires version; do not generalize omission",
                                  validation_plan="read executor confirmation", reviewers=["demo-owner"])
        validation = plan("job-2", "new-validation-case", validation_rule=rule)
        store.outcome(validation, status="success", effect_status="confirmed",
                      evidence="synthetic executor confirmation for job-2")
        store.validate_rule(rule, validation)
        store.review_rule(rule, reviewer="demo-owner", snapshot_digest=store.rule_snapshot(rule)["digest"],
                          decision="accepted")
        store.remember(project="demo", participant="partner", key="cancel-schema", category="experience",
                       content={"rule_id": rule, "interface": "cancel-v1"}, source="synthetic validated incident")

        # A new object loads only persisted events. Authority is supplied anew.
        store = Continuity(path)
        boot = store.cold_boot(project="demo", participant="partner", current=permission("job-3"))
        next_plan = plan("job-3", "new-session-new-target", applied_rule=rule)
        store.outcome(next_plan, status="success", effect_status="confirmed",
                      evidence="synthetic executor confirmation for job-3")
        store.close(next_plan, diagnosis_closed=True, repair_status="verified", effect_status="confirmed",
                    evidence="job-3 confirmation inspected")
        return {"mode": "deterministic synthetic demonstration, not a model run",
                "boot_sections": ["agreement", "work", "experience"],
                "retrieved_rule": boot["experience"]["rules"][0]["state"],
                "next_case": store._event(next_plan)["data"]["case_id"],
                "next_effect": store._effect(next_plan), "event_count": len(store.events()),
                "authority": "fresh caller-supplied fixture; no permission imported from memory"}


if __name__ == "__main__":
    print(json.dumps(demo(), ensure_ascii=False, indent=2))
