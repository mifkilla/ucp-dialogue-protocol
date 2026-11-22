"""Run the observer on supplied events and external LLM reviews, without labels.

The caller owns collection, authorization, model invocation and scheduling.
This command emits candidate signals; it executes no proposed actions.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from core import validate_assessment, semantic_alert, coverage_check


def observe(cases, assessments, health=None):
    if not isinstance(cases, list) or not cases or not isinstance(assessments, list):
        raise ValueError('nonempty cases and an assessments list are required')
    ids = [c['id'] for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate case id')
    counts = Counter(a.get('case_id') for a in assessments
                     if isinstance(a, dict) and isinstance(a.get('case_id'), str))
    results, alerts = [], []
    for case in cases:
        items = [a for a in assessments if isinstance(a, dict) and a.get('case_id') == case['id']]
        a = items[0] if len(items) == 1 else None
        result = validate_assessment(case, a)
        if len(items) != 1:
            result['validation_errors'].append('missing or duplicate case review')
        results.append(result)
        alert = semantic_alert(case, a)
        if alert:
            alerts.append(alert)
    extras = [cid for cid in counts if cid not in ids]
    malformed = sum(not isinstance(a, dict) or not isinstance(a.get('case_id'), str) for a in assessments)
    if extras or malformed:
        alerts.append({'atom': '@CARE.ALERT', 'origin': 'observer_host', 'kind': 'monitor_health',
                       'extra_case_ids': extras, 'malformed_items': malformed, 'grants_authority': False})
    health_result = None
    if health is not None:
        health_result = coverage_check(**health)
        if health_result['atom']:
            alerts.append({**health_result, 'origin': 'observer_host', 'grants_authority': False})
    return {'schema': 'ucp-observer-report-1', 'assessments': results, 'alerts': alerts,
            'health': health_result, 'actions_executed': 0,
            'boundary': 'Attribution checks and candidate judgments; no semantic certification or new authority.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('packet', type=Path)
    p.add_argument('reviews', type=Path)
    p.add_argument('--health', type=Path, help='Trusted host snapshot, never an LLM-produced permission grant')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
    packet, reviews = read(args.packet), read(args.reviews)
    if not isinstance(reviews, dict) or set(reviews) != {'assessments'}:
        p.error('Reviews must contain exactly an assessments list')
    report = observe(packet['cases'], reviews['assessments'], read(args.health) if args.health else None)
    if args.out.exists():
        p.error('Use a new output path; previous reports are not overwritten')
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'cases': len(report['assessments']), 'alerts': len(report['alerts']), 'actions_executed': 0}))


if __name__ == '__main__':
    main()
