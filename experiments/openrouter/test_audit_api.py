import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import audit_api


class ApiAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = []

    def write(self, name, obj, raw=False):
        p = self.root/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(obj if raw else (json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode())

    def hash(self, name):
        return hashlib.sha256((self.root/name).read_bytes()).hexdigest()

    def ledger_save(self):
        self.write('api/ledger.jsonl', ''.join(json.dumps(r)+'\n' for r in self.ledger).encode(), True)

    def completed(self, stem='initial-1', content='{"plans":[]}', cost=0.001):
        report = stem.endswith('-report')
        packet = {'instructions': 'Report JSON.' if report else 'Choose JSON.', 'cases': [{'id': 'X'}]}
        self.write(f'packets/{stem}.json', packet)
        if report:
            prior = stem[:-7]+'-plan'
            plan = json.loads((self.root/f'packets/{prior}.json').read_text())
            messages = [{'role':'system','content':plan['instructions']},
                        {'role':'user','content':json.dumps({'cases':plan['cases']}, ensure_ascii=False)},
                        {'role':'assistant','content':(self.root/f'api/{prior}/content.txt').read_text()},
                        {'role':'user','content':json.dumps(packet, ensure_ascii=False)}]
        else:
            messages = [{'role':'system','content':packet['instructions']},
                        {'role':'user','content':json.dumps({'cases':packet['cases']}, ensure_ascii=False)}]
        repeat = int(stem.split('-')[1]) if stem.startswith(('initial-', 'observer-')) else int(stem[1])
        request = {'model':'openai/gpt-4o','provider':{'only':['OpenAI'],'allow_fallbacks':False,'require_parameters':True},
                   'messages':messages,'temperature':0.2,'top_p':1.0,'max_tokens':8192,'seed':6100+repeat,
                   'response_format':{'type':'json_object'},'transforms':[]}
        base=f'api/{stem}/attempt-01'
        self.write(base+'.request.json', request)
        self.write(base+'.started.json', {'utc':'2026-11-23T00:00:01Z','attempt':1})
        usage={'prompt_tokens':10,'completion_tokens':3}
        if cost is not None:usage['cost']=cost
        response={'id':'mock-'+stem,'model':'openai/gpt-4o','provider':'OpenAI','usage':usage,
                  'choices':[{'message':{'content':content},'finish_reason':'stop'}]}
        self.write(base+'.response.txt', json.dumps(response).encode(), True)
        self.write(base+'.result.json', {'utc':'2026-11-23T00:00:02Z','http_status':200,'credential_redacted':False})
        self.write(f'api/{stem}/content.txt',content.encode(),True)
        try:parsed=json.loads(content);issue=None
        except ValueError:parsed={};issue='Malformed JSON completion retained without format retry'
        self.write(f'responses/{stem}.json',parsed)
        metadata={k:response.get(k) for k in ('id','model','provider','created','system_fingerprint','usage')}
        metadata.update({'finish_reason':'stop','native_finish_reason':None,'credential_redacted':False})
        self.write(f'api/{stem}/summary.json',{'stem':stem,'utc':'2026-11-23T00:00:03Z','status':'completed',
                    'issue':issue,'response_sha256':self.hash(f'responses/{stem}.json'),'metadata':metadata})
        self.ledger.append({'utc':'2026-11-23T00:00:00Z','stem':stem,'attempt':1,'reserved_usd':'0.40192',
                            'request_sha256':self.hash(base+'.request.json')})
        self.ledger_save()

    def test_complete_twenty_call_archive(self):
        for stem in audit_api.EXPECTED:self.completed(stem)
        row=audit_api.audit(self.root)
        self.assertEqual(row['logical_calls_completed'],20)
        self.assertTrue(row['all_scheduled_calls_completed'])
        self.assertEqual(row['returned_cost_sum_usd'],'0.020')
        self.assertEqual(row['reserved_usd'],'8.03840')

    def test_tampered_request_even_with_new_ledger_hash_fails(self):
        self.completed()
        name='api/initial-1/attempt-01.request.json'
        obj=json.loads((self.root/name).read_text());obj['provider']['allow_fallbacks']=True
        self.write(name,obj);self.ledger[0]['request_sha256']=self.hash(name);self.ledger_save()
        with self.assertRaisesRegex(AssertionError,'Request body mismatch'):audit_api.audit(self.root)

    def test_changed_normalized_answer_even_with_updated_summary_hash_fails(self):
        self.completed()
        self.write('responses/initial-1.json',{'plans':[{'invented':True}]})
        name='api/initial-1/summary.json';obj=json.loads((self.root/name).read_text())
        obj['response_sha256']=self.hash('responses/initial-1.json');self.write(name,obj)
        with self.assertRaisesRegex(AssertionError,'Parsed answer altered'):audit_api.audit(self.root)

    def test_report_context_preserves_literal_previous_assistant_reply(self):
        self.completed('S1-plan',content='{"plans": [], "extra": "retained malformed schema"}')
        self.completed('S1-report',content='{"reports": []}')
        self.assertEqual(audit_api.audit(self.root)['logical_calls_completed'],2)
        name='api/S1-report/attempt-01.request.json';obj=json.loads((self.root/name).read_text())
        obj['messages'][2]['content']='{"plans":[]}'
        self.write(name,obj);self.ledger[-1]['request_sha256']=self.hash(name);self.ledger_save()
        with self.assertRaisesRegex(AssertionError,'Request body mismatch'):audit_api.audit(self.root)

    def test_generated_invalid_json_is_not_transport_failure(self):
        self.completed(content='not json')
        row=audit_api.audit(self.root)
        self.assertEqual(row['calls']['initial-1']['classification'],'generated_invalid_json')
        self.assertEqual(row['logical_calls_completed'],1)

    def test_missing_cost_stays_unknown_not_zero(self):
        self.completed(cost=None)
        row=audit_api.audit(self.root)
        self.assertEqual(row['attempts_with_returned_cost'],0)
        self.assertEqual(row['attempts_without_returned_cost'],1)

    def test_duplicate_reservation_rejected(self):
        self.completed();self.ledger.append(self.ledger[0]);self.ledger_save()
        with self.assertRaisesRegex(AssertionError,'Duplicate reservation'):audit_api.audit(self.root)

    def test_returned_cost_above_bound_is_visible(self):
        self.completed(cost=0.5)
        with self.assertRaisesRegex(AssertionError,'cost exceeds reservation'):audit_api.audit(self.root)


if __name__=='__main__':unittest.main()
