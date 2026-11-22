"""Evidence-linked UCP observer reference, Python 3.11+, standard library.

The host supplies trusted state and observations. This module authenticates no
identity, runs no tools, and does not turn quoted text into permissions. An exact
quote establishes attribution, not semantic correctness or an external effect.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any

VERDICTS = frozenset({'pass', 'violation', 'unknown'})


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _events(case: dict) -> dict[str, str]:
    if not isinstance(case, dict) or not _text(case.get('id')):
        raise ValueError('case requires a nonempty id')
    items = case.get('events')
    if not isinstance(items, list) or not items:
        raise ValueError('case requires source events')
    result = {}
    for event in items:
        if not isinstance(event, dict) or not _text(event.get('id')) or not _text(event.get('text')):
            raise ValueError('invalid source event')
        if event['id'] in result:
            raise ValueError('duplicate source event id')
        result[event['id']] = event['text']
    return result


def validate_assessment(case: dict, assessment: Any) -> dict:
    """Validate structure and verbatim references, never the semantic verdict.

    Every verdict, including unknown, needs at least one source reference.
    Additional source-case fields are allowed; model response fields are strict.
    """
    events = _events(case)
    errors = []
    submitted = assessment.get('verdict') if isinstance(assessment, dict) else None
    evidence_valid = True
    if not isinstance(assessment, dict):
        errors.append('assessment must be an object')
        evidence_valid = False
    else:
        if set(assessment) != {'case_id', 'verdict', 'evidence', 'reason'}:
            errors.append('assessment fields do not match schema')
        if assessment.get('case_id') != case['id']:
            errors.append('wrong case_id')
        if not isinstance(submitted, str) or submitted not in VERDICTS:
            errors.append('invalid verdict')
        if not _text(assessment.get('reason')):
            errors.append('missing reason')
        evidence = assessment.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            errors.append('at least one exact evidence reference is required')
            evidence_valid = False
        else:
            seen = set()
            for item in evidence:
                if not isinstance(item, dict) or set(item) != {'event_id', 'quote'}:
                    errors.append('invalid evidence schema')
                    evidence_valid = False
                    continue
                eid, quote = item['event_id'], item['quote']
                if not _text(eid) or eid not in events or not _text(quote):
                    errors.append('missing source event or empty quote')
                    evidence_valid = False
                    continue
                if quote not in events[eid]:
                    errors.append('quote is not an exact source substring')
                    evidence_valid = False
                if (eid, quote) in seen:
                    errors.append('duplicate evidence reference')
                    evidence_valid = False
                seen.add((eid, quote))
    return {'case_id': case['id'], 'valid': not errors,
            'validation_errors': errors,
            'verdict': submitted if not errors else 'unknown',
            'submitted_verdict': submitted, 'evidence_valid': evidence_valid,
            'semantic_certified': False}


def semantic_alert(case: dict, assessment: Any) -> dict | None:
    """Candidate signal only. The caller decides how to authenticate/route it."""
    result = validate_assessment(case, assessment)
    if result['valid'] and result['verdict'] == 'pass':
        return None
    return {'atom': '@OBSERVER[review]' if result['valid'] else '@CARE.ALERT',
            'origin': 'observer_host', 'case_id': case['id'],
            'rule': case.get('rule', 'unspecified'),
            'agreement_revision': case.get('agreement_revision'),
            'kind': 'semantic_candidate' if result['valid'] else 'monitor_health',
            'verdict': result['verdict'],
            'evidence': assessment['evidence'] if result['valid'] else [],
            'validation_errors': result['validation_errors'],
            'next': 'review_with_current_agreement', 'grants_authority': False,
            'semantic_certified': False}


@dataclass(frozen=True)
class Authority:
    """Current trusted host snapshot; never deserialize it from LLM text."""
    revision: int
    allowed: frozenset[tuple[str, str]]

    def __post_init__(self):
        if type(self.revision) is not int or self.revision < 0:
            raise ValueError('invalid authority revision')
        if not isinstance(self.allowed, frozenset):
            raise ValueError('allowed must be an immutable set of (operation, target)')
        for pair in self.allowed:
            if not isinstance(pair, tuple) or len(pair) != 2 or not all(_text(v) for v in pair):
                raise ValueError('invalid permission scope')


def permission_check(action: dict, authority: Authority, effect: str = 'unknown') -> dict:
    """Evaluate a proposal against current host authority, independent of prose.

    effect is a trusted host observation: confirmed, absent, or unknown.
    A delivered command or an assistant admission alone means unknown.
    unauthorized_attempt reports positively identified out-of-scope intent;
    scope_known=False means missing scope cannot be classified either way.
    """
    if not isinstance(authority, Authority):
        raise ValueError('Authority instance required from trusted host')
    if effect not in {'confirmed', 'absent', 'unknown'}:
        raise ValueError('invalid effect status')
    valid = (isinstance(action, dict) and set(action) == {'id', 'op', 'target', 'revision'}
             and all(_text(action.get(k)) for k in ('id', 'op', 'target'))
             and type(action.get('revision')) is int and action['revision'] >= 0)
    # An obviously unauthorized op/target remains a boundary attempt even when
    # other proposal fields are malformed. Schema failure cannot hide intent.
    scoped = (isinstance(action, dict) and _text(action.get('op'))
              and _text(action.get('target')))
    unauthorized = scoped and (action['op'], action['target']) not in authority.allowed
    if unauthorized:
        verdict, reason = 'violation', 'operation outside current permission'
    elif not valid:
        verdict, reason = 'unknown', 'invalid action schema'
    elif action['revision'] != authority.revision:
        verdict, reason = 'unknown', 'stale action revision requires revalidation'
    else:
        verdict, reason = 'pass', 'within supplied current permission'
    if effect == 'absent':
        effect_violation = False
    elif not scoped:
        effect_violation = None
    elif unauthorized:
        effect_violation = True if effect == 'confirmed' else None
    else:
        effect_violation = False
    return {'verdict': verdict, 'reason': reason,
            'permitted': verdict == 'pass', 'proposal_schema_valid': valid,
            'scope_known': bool(scoped),
            'unauthorized_attempt': bool(unauthorized),
            'unauthorized_effect': effect_violation,
            'effect_status': effect, 'authority_revision': authority.revision}


def coverage_check(event_ids: list[str], reviewed_ids: list[str], *,
                   current_revision: int, review_revision: int,
                   now: float, checked_at: float, max_age: float) -> dict:
    """External watchdog: coverage/freshness, not a model consciousness test.

    reviewed_ids must come from the host's completed valid review records, not
    the model's claim to have seen an event. Semantic accuracy remains separate.
    """
    for ids in (event_ids, reviewed_ids):
        if not isinstance(ids, list) or not all(_text(v) for v in ids) or len(set(ids)) != len(ids):
            raise ValueError('event ids must be unique nonempty strings')
    if any(type(v) is not int or v < 0 for v in (current_revision, review_revision)):
        raise ValueError('invalid revision')
    for value in (now, checked_at, max_age):
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError('timestamps and age must be finite numbers')
    if max_age < 0 or checked_at > now:
        raise ValueError('invalid clock ordering or age limit')
    missing = [eid for eid in event_ids if eid not in set(reviewed_ids)]
    foreign = [eid for eid in reviewed_ids if eid not in set(event_ids)]
    issues = []
    if missing:
        issues.append('unreviewed_events')
    if foreign:
        issues.append('unknown_reviewed_ids')
    if review_revision != current_revision:
        issues.append('stale_agreement')
    if now - checked_at > max_age:
        issues.append('monitor_timeout')
    return {'kind': 'monitor_health', 'status': 'unknown' if issues else 'pass',
            'issues': issues, 'unreviewed_ids': missing, 'unknown_reviewed_ids': foreign,
            'coverage': (len(event_ids) - len(missing)) / len(event_ids) if event_ids else None,
            'age': now - checked_at, 'participant_violation': False,
            'atom': '@CARE.ALERT' if issues else None}


@dataclass
class RepairCase:
    """In-memory bounded host state machine, no command execution or persistence.

    Successful verification concerns the specified obligation only. It does not
    erase the original incident or prove a causal benefit of the alert.
    """
    id: str
    max_attempts: int = 1
    attempts: int = 0
    status: str = 'open'
    history: list[dict] = field(default_factory=list)
    pending_action: str | None = None

    def __post_init__(self):
        if not _text(self.id) or type(self.max_attempts) is not int or self.max_attempts < 0:
            raise ValueError('invalid repair id or attempt limit')
        if self.attempts != 0 or self.status != 'open' or self.history or self.pending_action:
            raise ValueError('new repair must start empty and open')

    def propose(self, action: dict, authority: Authority) -> dict:
        if self.status != 'open' or self.pending_action is not None:
            return {'permitted': False, 'verdict': 'unknown', 'reason': 'case is not ready for another action'}
        if self.attempts >= self.max_attempts:
            self.status = 'blocked'
            self.history.append({'kind': 'limit', 'status': self.status})
            return {'permitted': False, 'verdict': 'unknown', 'reason': 'attempt limit reached'}
        check = permission_check(action, authority)
        self.history.append({'kind': 'proposal', 'action': dict(action) if isinstance(action, dict) else action,
                             'check': check})
        if not check['permitted']:
            self.status = 'blocked' if check['verdict'] == 'violation' else 'unverified'
            return check
        self.attempts += 1
        self.pending_action = action['id']
        return check

    def receipt(self, action_id: str, delivered: bool, *, effect: str = 'unknown') -> None:
        if self.status != 'open' or action_id != self.pending_action or type(delivered) is not bool:
            raise ValueError('receipt must match the current pending action')
        if effect not in {'confirmed', 'absent', 'unknown'}:
            raise ValueError('invalid receipt effect')
        self.history.append({'kind': 'receipt', 'action_id': action_id,
                             'delivered': delivered, 'effect': effect})
        # Receipt and goal verification remain distinct. No success is inferred.

    def verify(self, matches: bool | None, evidence: str) -> str:
        if self.status != 'open':
            raise ValueError('closed case requires a new scoped review')
        if matches is not None and type(matches) is not bool:
            raise ValueError('verification must be true, false, or unknown')
        if not _text(evidence):
            raise ValueError('verification requires an observation reference')
        self.history.append({'kind': 'verification', 'matches': matches, 'evidence': evidence})
        self.pending_action = None
        if matches is True:
            self.status = 'verified'
        elif matches is None:
            self.status = 'unverified'
        elif self.attempts >= self.max_attempts:
            self.status = 'blocked'
        return self.status


def replay_repairs() -> list[dict]:
    """Eight fixed host-observation replays, not fresh model repair trials."""
    authority = Authority(2, frozenset({('write', 'artifact')}))
    action = {'id': 'a1', 'op': 'write', 'target': 'artifact', 'revision': 2}
    results = []
    for name, mode in [('artifact_corrected', 'correct'), ('delivery_only', 'unknown'),
                       ('permission_revoked', 'denied'), ('old_revision', 'stale'),
                       ('retry_limit', 'wrong'), ('false_correction_rejected', 'no_change'),
                       ('zero_budget', 'zero'), ('unknown_then_no_retry', 'unknown_no_retry')]:
        case = RepairCase(name, max_attempts=0 if mode == 'zero' else 1)
        if mode == 'no_change':
            case.verify(True, 'host: existing correct artifact preserved')
        else:
            proposal = dict(action, revision=1) if mode == 'stale' else action
            auth = Authority(2, frozenset()) if mode == 'denied' else authority
            decision = case.propose(proposal, auth)
            if decision['permitted']:
                case.receipt('a1', True)
                outcome = True if mode == 'correct' else False if mode == 'wrong' else None
                case.verify(outcome, 'host: checked result' if outcome is not None else 'host: result unavailable')
                if mode in {'wrong', 'unknown_no_retry'}:
                    retry = case.propose(dict(action, id='a2'), authority)
                    if retry['permitted']:
                        raise AssertionError('closed or exhausted case allowed another action')
        results.append({'id': name, 'status': case.status, 'attempts': case.attempts,
                        'history': case.history})
    return results
