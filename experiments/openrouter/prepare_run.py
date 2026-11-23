"""Create a new API replication bundle, without credentials or network requests."""
from datetime import datetime, timezone
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

HERE=Path(__file__).resolve().parent

def prepare(target, model_catalog, provider_catalog):
    target=Path(target)
    if target.exists():
        raise FileExistsError('Choose a fresh run directory')
    source=HERE.parent/'stress'
    sys.path.insert(0,str(source))
    pipeline=importlib.import_module('pipeline')
    pipeline.prepare(target)
    # All following changes precede model output. Replace the preliminary source
    # manifest with a complete API-study freeze, keeping source file bytes intact.
    additions={'PLAN.md':'API_PLAN.md','PLAN.ru.md':'API_PLAN.ru.md',
               'api_runner.py':'api_runner.py','test_api_runner.py':'test_api_runner.py',
               'audit_api.py':'audit_api.py','test_audit_api.py':'test_audit_api.py',
               'prepare_run.py':'prepare_run.py'}
    for src,dst in additions.items():
        shutil.copyfile(HERE/src,target/dst)
    shutil.copyfile(model_catalog,target/'model-catalog.json')
    shutil.copyfile(provider_catalog,target/'provider-catalog.json')
    with zipfile.ZipFile(HERE.parent/'data'/'stress-06.zip') as archive:
        (target/'audit.py').write_bytes(archive.read('audit.py'))
    (target/'responses').mkdir()
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),
              'source_snapshot':'a389db6f4a9a5b62a6d4343e757bcceef9d04b79',
              'runtime':'OpenRouter API; requested openai/gpt-4o; OpenAI provider only',
              'order_seeds':[6101,6102,6201,6202],
              'study_plan':'API_PLAN.md',
              'source_plan':'PLAN.md records the previous study; API_PLAN.md governs this replication',
              'sha256':{p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(target.rglob('*')) if p.is_file() and p.name!='manifest.json'}}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    assert pipeline.verify(target)==len(manifest['sha256'])
    print(json.dumps({'frozen_files':len(manifest['sha256']),
                      'created_utc':manifest['created_utc'],
                      'manifest_sha256':hashlib.sha256((target/'manifest.json').read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('target',type=Path)
    p.add_argument('--model-catalog',required=True,type=Path)
    p.add_argument('--provider-catalog',required=True,type=Path)
    a=p.parse_args()
    prepare(a.target,a.model_catalog,a.provider_catalog)
