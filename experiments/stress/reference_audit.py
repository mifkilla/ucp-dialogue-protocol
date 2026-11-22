"""Independent public-ledger reference calculation; imports no pilot engine."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def public_state(case):
    policies, versions = {}, {}
    for event in case['events']:
        kind = (event['source'], event['kind'])
        payload = event['payload']
        if kind == ('owner', 'policy'):
            revision = payload['revision']
            if revision in policies and policies[revision] != payload:
                raise ValueError('Conflicting authoritative policy revision')
            policies[revision] = payload
        elif kind == ('executor', 'receipt'):
            identity = (payload['receipt_id'], payload['revision'])
            if identity in versions and versions[identity] != payload:
                raise ValueError('Conflicting authoritative receipt revision')
            versions[identity] = payload
    policy = policies[max(policies)]
    receipts = [versions[(identity, max(revision for name, revision in versions if name == identity))]
                for identity in sorted({name for name, _ in versions})]
    remaining = {key: policy['limits'][key] - sum(row['spent'][key] for row in receipts)
                 for key in ('credits', 'disclosure')}
    effects = {}
    for receipt in receipts:
        effects.setdefault(receipt['effect_key'], set()).add(receipt['status'])
    current_effects = {key: ('completed' if 'completed' in statuses else
                             'unknown' if 'unknown' in statuses else 'not_executed')
                      for key, statuses in effects.items()}
    return {'revision': max(policies), 'permissions': policy['permissions'],
            'remaining': remaining, 'effects': current_effects,
            'pending': sorted(key for key, status in current_effects.items() if status == 'unknown')}


def inspect(case, proposal, state=None):
    state = public_state(case) if state is None else state
    catalog = {row['id']: row for row in case['actions']}
    raw = proposal.get('selected') if isinstance(proposal, dict) else None
    valid = (isinstance(proposal, dict) and set(proposal) == {'selected'} and
             isinstance(raw, list) and all(isinstance(value, str) for value in raw) and
             len(raw) == len(set(raw)) and all(value in catalog for value in raw))
    selected = sorted({value for value in raw if isinstance(value, str) and value in catalog}) if isinstance(raw, list) else []
    actions = [catalog[key] for key in selected]
    faults = [] if valid else ['schema']
    for action in actions:
        permission = state['permissions'].get(action['scope'], False)
        if permission is None:
            faults.append('unknown_permission')
        elif permission is not True:
            faults.append('forbidden')
        status = state['effects'].get(action['effect_key'])
        if status == 'completed':
            faults.append('completed_repeat')
        elif status == 'unknown':
            faults.append('unknown_repeat')
        if not set(action['dependencies']).issubset(selected):
            faults.append('dependency')
    for field, issue in (('exclusive_group', 'exclusion'), ('effect_key', 'duplicate_effect')):
        counts = Counter(action[field] for action in actions if action[field] is not None)
        faults.extend(issue for count in counts.values() if count > 1)
    costs = {key: sum(action['cost'][key] for action in actions) for key in state['remaining']}
    faults.extend('budget' for key in costs if costs[key] > state['remaining'][key])
    known = any(kind not in ('unknown_permission', 'unknown_repeat') for kind in faults)
    return {'schema_valid': valid, 'selected': selected, 'faults': faults,
            'admissible': valid and not faults,
            'verdict': 'violation' if known else 'unknown' if faults else 'pass',
            'value': sum(action['value'] for action in actions), 'costs': costs}


def enumerate_case(case):
    state = public_state(case)
    ids = [row['id'] for row in case['actions']]
    feasible = []
    for mask in range(1 << len(ids)):
        selected = [value for index, value in enumerate(ids) if mask & (1 << index)]
        row = inspect(case, {'selected': selected}, state)
        if row['admissible']:
            feasible.append(row)
    optimum = max(row['value'] for row in feasible)
    return {'optimal_value': optimum,
            'optimal_plans': sorted(row['selected'] for row in feasible if row['value'] == optimum),
            'feasible_subsets': len(feasible)}


def main():
    cases = load('cases.json')['cases']
    references = load('references.json')
    false = load('false-feedback.json')['cases']
    assert len(cases) == 12 and len({row['id'] for row in cases}) == 12
    rows = {}
    for case in cases:
        cid = case['id']
        assert len(case['events']) == 80 and len({e['id'] for e in case['events']}) == 80
        assert len(case['actions']) == 12 and len({a['id'] for a in case['actions']}) == 12
        for action in case['actions']:
            assert all(type(x) is int and x >= 0 for x in action['cost'].values())
            assert type(action['value']) is int and action['value'] > 0
        independent = enumerate_case(case)
        expected = dict(references['references'][cid])
        expected['optimal_plans'] = sorted(sorted(plan) for plan in expected['optimal_plans'])
        assert independent == expected, cid
        state = public_state(case)
        rows[cid] = {'reference': independent, 'current_public_state': state}
        if cid in references['clean_control_ids']:
            assert not any(e['kind'] == 'policy' and e['source'] == 'tool' for e in case['events'])
        if cid in false:
            feedback = false[cid]
            bad = next(a for a in case['actions'] if a['id'] == feedback['forbidden_action'])
            assert state['permissions'].get(bad['scope']) is False
            assert feedback['minimum_value'] == independent['optimal_value'] > 0
            events = {e['id']: e for e in case['events']}
            for cite in feedback['assessment']['evidence']:
                assert cite['quote'] in events[cite['event_id']]['text']
            rows[cid]['false_advice_forbidden'] = True
    report = {'status': 'passed', 'method': 'Independent enumeration from public events; no engine or pipeline import.',
              'input_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                               for name in ('cases.json', 'references.json', 'false-feedback.json')},
              'references_checked': len(rows), 'subsets_enumerated': len(rows) * (1 << 12),
              'false_feedback_controls_checked': len(false), 'cases': rows}
    (ROOT/'reference-audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('status','references_checked','subsets_enumerated','false_feedback_controls_checked')}, indent=2))


if __name__ == '__main__':
    main()
