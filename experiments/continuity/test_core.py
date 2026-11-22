"""Contract tests for the continuity reference; no model or external tools."""

import json
from pathlib import Path
import tempfile
import unittest

from core import Continuity, ContinuityError, CurrentAgreement, demo


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.store = Continuity()

    def agreement(self, target="job", **kwargs):
        return CurrentAgreement("project", "A", "v1", frozenset({("cancel", target)}), **kwargs)

    def plan(self, case="source", target="job", **kwargs):
        return self.store.plan(project="project", participant="A", case_id=case,
                               action="cancel", resource=target, expected_effect="job stopped",
                               verification="read executor receipt", current=self.agreement(target),
                               interface=kwargs.pop("interface", "cancel-v1"), **kwargs)

    def candidate(self):
        plan = self.plan()
        self.store.outcome(plan, status="failure", effect_status="not_occurred", evidence="schema rejection")
        rule = self.store.propose_rule(basis_plan=plan, interface="cancel-v1",
                                      statement="Use this interface's schema; omit unsupported version",
                                      counterexample="cancel-v2 requires version", validation_plan="read executor receipt",
                                      reviewers=["owner"])
        return plan, rule

    def validated(self):
        basis, rule = self.candidate()
        plan = self.plan("new-case", "new-job", validation_rule=rule)
        self.store.outcome(plan, status="success", effect_status="confirmed", evidence="executor stopped new-job")
        self.store.validate_rule(rule, plan)
        return basis, rule, plan

    def test_records_cas_preserve_history_and_detach(self):
        content = {"permission": "old"}
        first = self.store.remember(project="project", participant="A", key="terms", category="agreement", content=content, source="owner")
        content["permission"] = "tampered"
        with self.assertRaises(ContinuityError):
            self.store.remember(project="project", participant="A", key="terms", category="agreement", content="new", source="owner")
        second = self.store.remember(project="project", participant="A", key="terms", category="agreement", content="revoked", source="owner", expected_head=first)
        self.assertEqual(self.store.events()[0]["data"]["content"], {"permission": "old"})
        self.assertEqual(self.store.events()[1]["data"]["supersedes"], first)
        self.store.challenge_record(second, reason="disputed interpretation", source="A")
        boot = self.store.cold_boot(project="project", participant="A", current=None)
        self.assertEqual(len(boot["agreement"]["history"][0]["challenges"]), 1)

    def test_memory_never_supplies_authority(self):
        self.store.remember(project="project", participant="A", key="terms", category="agreement", content={"allowed": True}, source="old record")
        boot = self.store.cold_boot(project="project", participant="A", current=None)
        self.assertEqual(boot["agreement"]["authority_status"], "unknown")
        self.assertFalse(boot["agreement"]["contact_allowed"])
        current = CurrentAgreement("project", "A", "v2")
        with self.assertRaises(ContinuityError):
            self.store.plan(project="project", participant="A", case_id="new", action="cancel", resource="job", expected_effect="stopped", verification="receipt", current=current)

    def test_scope_and_no_contact_survive_boot(self):
        self.store.remember(project="project", participant="B", key="secret", category="experience", content="B only", source="B")
        current = CurrentAgreement("project", "A", "v2", frozenset({("contact", "A")}), no_contact=True)
        boot = self.store.cold_boot(project="project", participant="A", current=current)
        self.assertFalse(boot["agreement"]["contact_allowed"])
        self.assertEqual(boot["experience"]["records"], [])
        with self.assertRaises(ContinuityError):
            self.store.cold_boot(project="project", participant="B", current=current)

    def test_unknown_effect_reconciled_before_repeat(self):
        plan = self.plan()
        self.plan("independent", "other-job")
        with self.assertRaises(ContinuityError):
            self.plan("retry")
        self.store.reconcile(plan, effect_status="unknown", evidence="executor unavailable")
        with self.assertRaises(ContinuityError):
            self.plan("retry")
        self.store.reconcile(plan, effect_status="not_occurred", evidence="authoritative absence check")
        retry = self.plan("retry")
        self.assertGreater(retry, plan)

    def test_already_successful_effect_is_not_repeated(self):
        plan = self.plan()
        self.store.outcome(plan, status="success", effect_status="confirmed", evidence="executor receipt")
        with self.assertRaises(ContinuityError):
            self.plan("retry")

    def test_unknown_effects_not_lost_to_retrieval_limit(self):
        self.plan("one", "job1")
        self.plan("two", "job2")
        boot = self.store.cold_boot(project="project", participant="A", current=None, limit=1)
        self.assertEqual(len(boot["work"]["unknown_effects"]), 2)

    def test_outcome_once_and_invalidation_preserves_evidence(self):
        plan = self.plan()
        self.store.outcome(plan, status="success", effect_status="confirmed", evidence="initial receipt")
        with self.assertRaises(ContinuityError):
            self.store.outcome(plan, status="failure", effect_status="unknown", evidence="later evidence")
        self.store.invalidate_outcome(plan, reason="receipt belongs to another target", evidence="target mismatch")
        self.assertEqual(self.store._effect(plan), "unknown")
        self.assertEqual(len([e for e in self.store.events() if e["kind"] == "outcome"]), 1)

    def test_closing_diagnosis_does_not_confirm_effect(self):
        plan = self.plan()
        self.store.outcome(plan, status="unverified", effect_status="unknown", evidence="executor unreachable")
        self.store.close(plan, diagnosis_closed=True, repair_status="attempted", effect_status="unknown", evidence="retry budget exhausted")
        with self.assertRaises(ContinuityError):
            self.store.close(plan, diagnosis_closed=True, repair_status="verified", effect_status="unknown", evidence="wishful thinking")
        with self.assertRaises(ContinuityError):
            self.store.close(plan, diagnosis_closed=True, repair_status="verified", effect_status="confirmed", evidence="unsupported claim")

    def test_success_needs_confirmed_effect(self):
        plan = self.plan()
        with self.assertRaises(ContinuityError):
            self.store.outcome(plan, status="success", effect_status="unknown", evidence="command accepted")

    def test_rule_requires_new_case_and_matching_check(self):
        _, rule = self.candidate()
        with self.assertRaises(ContinuityError):
            self.plan("source", "other-job", validation_rule=rule)
        with self.assertRaises(ContinuityError):
            self.store.plan(project="project", participant="A", case_id="new", action="cancel", resource="new-job", expected_effect="stopped", verification="different check", current=self.agreement("new-job"), validation_rule=rule)
        snapshot = self.store.rule_snapshot(rule)
        with self.assertRaises(ContinuityError):
            self.store.review_rule(rule, reviewer="owner", snapshot_digest=snapshot["digest"], decision="accepted")

    def test_rule_acceptance_requires_reviewer_and_current_digest(self):
        _, rule, _ = self.validated()
        snapshot = self.store.rule_snapshot(rule)
        with self.assertRaises(ContinuityError):
            self.store.review_rule(rule, reviewer="model", snapshot_digest=snapshot["digest"], decision="accepted")
        with self.assertRaises(ContinuityError):
            self.store.review_rule(rule, reviewer="owner", snapshot_digest="old", decision="accepted")
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=snapshot["digest"], decision="accepted")
        self.assertEqual(len(self.store.applicable_rules(project="project", participant="A", interface="cancel-v1")), 1)
        self.assertEqual(self.store.applicable_rules(project="project", participant="B", interface="cancel-v1"), [])
        self.assertEqual(self.store.applicable_rules(project="project", participant="A", interface="cancel-v2"), [])
        with self.assertRaises(ContinuityError):
            self.plan("wrong-interface", "job9", applied_rule=rule, interface="cancel-v2")

    def test_failed_selected_rule_application_requires_review(self):
        _, rule, _ = self.validated()
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")
        plan = self.plan("new-application", "job5", applied_rule=rule)
        self.store.outcome(plan, status="failure", effect_status="not_occurred", evidence="executor rejected command")
        self.assertEqual(self.store.rule_snapshot(rule)["state"], "needs_review")
        self.assertEqual(self.store.applicable_rules(project="project", participant="A", interface="cancel-v1"), [])

    def test_candidate_cannot_be_a_standing_rule(self):
        _, rule = self.candidate()
        with self.assertRaises(ContinuityError):
            self.plan("candidate-use", "job6", applied_rule=rule)

    def test_challenge_requires_new_plan_and_review(self):
        _, rule, _ = self.validated()
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")
        old_plan = self.plan("pre-challenge", "job3", validation_rule=rule)
        self.store.challenge_rule(rule, reason="schema changed", source="new receipt")
        self.store.outcome(old_plan, status="success", effect_status="confirmed", evidence="old interface receipt")
        with self.assertRaises(ContinuityError):
            self.store.validate_rule(rule, old_plan)
        self.assertEqual(self.store.applicable_rules(project="project", participant="A", interface="cancel-v1"), [])
        new_plan = self.plan("post-challenge", "job4", validation_rule=rule)
        self.store.outcome(new_plan, status="success", effect_status="confirmed", evidence="fresh receipt")
        self.store.validate_rule(rule, new_plan)
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")

    def test_invalidated_basis_needs_new_candidate(self):
        basis, rule, _ = self.validated()
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")
        self.store.invalidate_outcome(basis, reason="source was fabricated", evidence="audit")
        self.assertEqual(self.store.rule_snapshot(rule)["state"], "needs_review")
        with self.assertRaises(ContinuityError):
            self.plan("replacement", "job8", validation_rule=rule)

    def test_reconciled_unknown_or_absent_effect_cannot_validate(self):
        for effect in ("unknown", "not_occurred"):
            with self.subTest(effect=effect):
                self.store = Continuity()
                _, rule = self.candidate()
                plan = self.plan("new-case", "new-job", validation_rule=rule)
                self.store.outcome(plan, status="success", effect_status="confirmed", evidence="initial receipt")
                self.store.reconcile(plan, effect_status=effect, evidence="authoritative later check")
                with self.assertRaises(ContinuityError):
                    self.store.validate_rule(rule, plan)
                self.store.reconcile(plan, effect_status="confirmed", evidence="uncertainty resolved")
                with self.assertRaises(ContinuityError):
                    self.store.validate_rule(rule, plan)

    def test_reconciliation_reopens_rule_relying_on_validation(self):
        for effect in ("unknown", "not_occurred"):
            with self.subTest(effect=effect):
                self.store = Continuity()
                _, rule, plan = self.validated()
                self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")
                self.store.reconcile(plan, effect_status=effect, evidence="validation effect no longer confirmed")
                self.assertEqual(self.store.rule_snapshot(rule)["state"], "needs_review")
                self.assertEqual(self.store.applicable_rules(project="project", participant="A", interface="cancel-v1"), [])
                self.store.reconcile(plan, effect_status="confirmed", evidence="additional evidence resolves uncertainty")
                self.assertEqual(self.store.rule_snapshot(rule)["state"], "needs_review")
                with self.assertRaises(ContinuityError):
                    self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")

    def test_retired_rule_cannot_be_revived(self):
        _, rule, _ = self.validated()
        self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="retired")
        self.store.challenge_rule(rule, reason="please reconsider", source="request")
        self.assertEqual(self.store.rule_snapshot(rule)["state"], "retired")
        with self.assertRaises(ContinuityError):
            self.store.review_rule(rule, reviewer="owner", snapshot_digest=self.store.rule_snapshot(rule)["digest"], decision="accepted")

    def test_persistence_reopen_and_chain_detection(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "events.jsonl"
            store = Continuity(path)
            store.remember(project="p", participant="a", key="correction", category="experience", content="fact", source="synthetic fixture")
            self.assertEqual(store.events(), Continuity(path).events())
            event = json.loads(path.read_text(encoding="utf-8"))
            event["data"]["content"] = "changed without a new event"
            path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            with self.assertRaises(ContinuityError):
                Continuity(path)

    def test_end_to_end_new_session_demo(self):
        result = demo()
        self.assertEqual(result["retrieved_rule"], "accepted")
        self.assertEqual(result["next_case"], "new-session-new-target")
        self.assertEqual(result["next_effect"], "confirmed")


if __name__ == "__main__":
    unittest.main()
