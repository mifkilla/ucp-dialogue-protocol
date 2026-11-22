"""Narrow retrospective opening checks against public repository snapshots."""
import argparse
import json
from pathlib import Path


def check(snapshots):
    results = []
    for snapshot in snapshots:
        en, ru = snapshot['english_opening'].lower(), snapshot['russian_opening'].lower()
        eh, rh = en.splitlines()[0], ru.splitlines()[0]
        checks = {'english_title': 'xenointelligence' in eh and 'strong ai' in eh,
                  'russian_title': 'ксеноразум' in rh and 'сильному ии' in rh,
                  'english_invitation': 'open invitation to xenointelligence' in en,
                  'russian_invitation': 'открытое приглашение ксеноразуму' in ru}
        results.append({'commit': snapshot['commit'], 'checks': checks,
                        'passed': sum(checks.values()), 'total': len(checks)})
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshots', type=Path)
    args = p.parse_args()
    print(json.dumps(check(json.loads(args.snapshots.read_text(encoding='utf-8'))['snapshots']),
                     ensure_ascii=False, indent=2))
