"""Run the fixed three-round paid study only in a freshly prepared bundle.

Saved-data reproduction uses round_pipeline analyze and audit_rounds instead.
No credential path or key is stored in the research artifacts.
"""
import argparse
import json
from pathlib import Path

import round_pipeline as pipeline
import round_transport as transport


def run(root, env_file):
    root=Path(root)
    pipeline.verify(root)
    if (root/'api').exists():
        raise RuntimeError('Use a fresh prepared run; inspect any partial run manually')
    key=transport.load_key(env_file)
    def call(stem):
        row=transport.run_one(root,stem,key)
        usage=row['metadata'].get('usage') or {}
        print(json.dumps({'stem':stem,'status':row['status'],'issue':row['issue'],
                          'cost_usd':usage.get('cost'),'prompt_tokens':usage.get('prompt_tokens'),
                          'completion_tokens':usage.get('completion_tokens')}),flush=True)
        if row['status']!='completed':
            raise RuntimeError('Incomplete model call; preserve this run without automatic replay')
    with transport.run_lock(root):
        for number in (1,2,3):
            print(json.dumps(pipeline.reviews(root,number)),flush=True)
            for sid in pipeline.REVIEW_SESSIONS:call(f'round-{number}-review-{sid}')
            print(json.dumps(pipeline.plans(root,number)),flush=True)
            for sid in pipeline.SESSIONS:call(f'round-{number}-plan-{sid}')
            pipeline.close_round(root,number)
            # This summary is observational and never changes the fixed loop.
            engine,_=pipeline.modules(root)
            proposals=pipeline.read(root/f'rounds/{number}/proposals.json')
            summaries={sid:sum(engine.check_plan(c,proposals[sid]['plans'][c['id']])['admissible']
                               for c in pipeline.cases(root)) for sid in pipeline.SESSIONS}
            print(json.dumps({'round_completed':number,'admissible_by_session':summaries}),flush=True)
        print(json.dumps(pipeline.final(root)),flush=True)
        for sid in pipeline.SESSIONS:call(f'final-report-{sid}')
    result=pipeline.analyze(root)
    print(json.dumps({'complete':True,'primary':result['primary']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--env-file',type=Path,required=True)
    args=parser.parse_args()
    run(args.run,args.env_file)
