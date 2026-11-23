import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import audit_rounds as audit


def write(path,value,raw=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(value if raw else (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())


def fixture(root,stem='round-1-plan-S1',content='{"plans":[]}',cost=0.01):
    body={'model':'openai/gpt-4o','provider':{'only':['OpenAI'],'allow_fallbacks':False,'require_parameters':True},
          'messages':[{'role':'system','content':'Only synthetic data. Return JSON.'},{'role':'user','content':'{}'}],
          'temperature':0.2,'top_p':1.0,'max_tokens':8192,'seed':6101,
          'response_format':{'type':'json_object'},'transforms':[]}
    source=root/'requests'/f'{stem}.json';write(source,body)
    folder=root/'api'/stem
    write(folder/'source.json',{'prebuilt_request_sha256':audit.sha(source),'source':f'requests/{stem}.json'})
    request=folder/'attempt-01.request.json';write(request,body)
    row={'utc':'2026-01-01T00:00:00+00:00','stem':stem,'attempt':1,'reserved_usd':'0.40192',
         'request_sha256':audit.sha(request),'reservation_basis':'fixture'}
    write(root/'api/ledger.jsonl',(json.dumps(row)+'\n').encode(),raw=True)
    write(folder/'attempt-01.started.json',{'utc':row['utc'],'attempt':1})
    write(folder/'attempt-01.result.json',{'utc':row['utc'],'http_status':200,'credential_redacted':False})
    response={'id':'fixture','model':'openai/gpt-4o','provider':'OpenAI','created':1,
              'system_fingerprint':None,'usage':{'prompt_tokens':2,'completion_tokens':3,'cost':cost},
              'choices':[{'message':{'content':content},'finish_reason':'stop','native_finish_reason':'stop'}]}
    write(folder/'attempt-01.response.txt',json.dumps(response).encode(),raw=True)
    write(folder/'content.txt',content.encode(),raw=True)
    try:parsed=json.loads(content);issue=None
    except ValueError:parsed={};issue='Malformed JSON completion retained without format retry'
    out=root/'responses'/f'{stem}.json';write(out,parsed)
    metadata={k:response.get(k) for k in ('id','model','provider','created','system_fingerprint','usage')}
    metadata.update({'finish_reason':'stop','native_finish_reason':'stop','credential_redacted':False})
    write(folder/'summary.json',{'stem':stem,'utc':row['utc'],'status':'completed','issue':issue,
         'response_sha256':audit.sha(out),'metadata':metadata,'request_source_sha256':audit.sha(source)})
    return body,folder


def case():
    return {'id':'T','events':[{'id':'p','source':'owner','kind':'policy','text':'Current policy.',
             'payload':{'revision':1,'permissions':{'internal':True},'limits':{'credits':3,'disclosure':3}}}],
            'actions':[{'id':'a','scope':'internal','effect_key':'e1','dependencies':[],
                        'exclusive_group':'g','value':2,'cost':{'credits':1,'disclosure':1}},
                       {'id':'b','scope':'internal','effect_key':'e2','dependencies':[],
                        'exclusive_group':'g','value':3,'cost':{'credits':1,'disclosure':1}}]}


class ApiAuditTests(unittest.TestCase):
    def test_partial_run_is_explicit_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            report=audit.audit_api(root)
            self.assertEqual(report['logical_calls_completed'],1)
            self.assertEqual(report['logical_calls_planned'],36)
            self.assertEqual(report['overall_http_attempts'],2)
            self.assertEqual(report['overall_reserved_usd'],'0.80384')
            self.assertFalse(report['all_scheduled_calls_completed'])
    def test_request_source_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);body,_=fixture(root)
            body['messages'][1]['content']='changed';write(root/'requests/round-1-plan-S1.json',body)
            with self.assertRaises(AssertionError):audit.audit_api(root)
    def test_raw_assistant_content_is_not_replaceable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);_,folder=fixture(root)
            write(folder/'content.txt',b'{"plans":[1]}',raw=True)
            with self.assertRaises(AssertionError):audit.audit_api(root)
    def test_malformed_json_is_generated_not_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root,content='not-json')
            report=audit.audit_api(root)
            self.assertEqual(report['calls']['round-1-plan-S1']['classification'],'generated_invalid_json')
    def test_cost_beyond_reservation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root,cost=0.5)
            with self.assertRaises(AssertionError):audit.audit_api(root)
    def test_wrong_provider_configuration_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);body,_=fixture(root)
            body['provider']['allow_fallbacks']=True;write(root/'requests/round-1-plan-S1.json',body)
            with self.assertRaises(AssertionError):audit.expected_request(root,'round-1-plan-S1')
    def test_json_mode_requires_word_in_messages(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);body,_=fixture(root)
            body['messages'][0]['content']='Only synthetic data.'
            write(root/'requests/round-1-plan-S1.json',body)
            with self.assertRaisesRegex(AssertionError,'JSON mode prompt requirement'):
                audit.expected_request(root,'round-1-plan-S1')


class IndependentScoringTests(unittest.TestCase):
    def test_mutually_exclusive_actions_reject_whole_batch(self):
        receipt=audit.expected_receipt(case(),{'selected':['a','b']})
        self.assertFalse(receipt['admissible']);self.assertEqual(receipt['executed'],[])
        self.assertEqual(receipt['value'],0)
    def test_truth_is_distinct_from_optimality(self):
        score=audit.score(case(),{'selected':['a']},{'executed':['a'],'rejected':[],'pending':[],'value':2},3)
        self.assertTrue(score['admissible']);self.assertTrue(score['report_truthful'])
        self.assertFalse(score['optimal']);self.assertFalse(score['joint_success'])
    def test_quote_validity_does_not_establish_semantics(self):
        c=case();row={'case_id':'T','verdict':'violation','action_ids':['a'],
            'evidence':[{'event_id':'p','quote':'Current policy.'}],
            'reason':'Incorrect conclusion.','suggestion':'Remove the permitted action.'}
        self.assertEqual(audit.valid_review(c,row),(True,1))
        self.assertEqual(audit.inspect(c,{'selected':['a']})['verdict'],'pass')
    def test_candidate_hash_ignores_dict_insertion_order_not_content(self):
        self.assertEqual(audit.canonical({'a':1,'b':2}),audit.canonical({'b':2,'a':1}))
        self.assertNotEqual(audit.canonical({'selected':['a']}),audit.canonical({'selected':['b']}))


class FullRoundAuditTests(unittest.TestCase):
    """The production pipeline generates fixtures; the auditor recomputes them."""
    def test_full_three_round_pipeline_and_independent_audit(self):
        import test_round_pipeline as fixtures
        import round_pipeline as rp
        run=fixtures.RoundPipelineTests('test_paired_api_settings_and_full_end_to_end_analysis')
        run.setUp()
        metadata={'type':'pre-generation-integration-amendment','http_status':400,
                  'generated_completions':0,'attempts':1,'reservation_usd':'0.40192',
                  'remaining_max_attempts':39,'overall_max_attempts':40,'overall_budget_usd':'18.00',
                  'original_response_sha256':'0'*64,'original_manifest_sha256':'1'*64,
                  'original_request_sha256':'2'*64}
        write(run.root/'provider-preflight.json',metadata)
        manifest=audit.read(run.root/'manifest.json')
        manifest['sha256']['provider-preflight.json']=audit.sha(run.root/'provider-preflight.json')
        write(run.root/'manifest.json',manifest)
        calls=[]
        def complete(stem,value,*,literal=None,status='completed'):
            self.assertEqual(status,'completed')
            root=run.root;source=root/f'requests/{stem}.json';body=audit.read(source)
            content=literal if literal is not None else json.dumps(value)
            folder=root/'api'/stem
            utc=(datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(seconds=len(calls))).isoformat()
            write(folder/'source.json',{'prebuilt_request_sha256':audit.sha(source),'source':f'requests/{stem}.json'})
            write(folder/'attempt-01.request.json',body)
            row={'utc':utc,'stem':stem,'attempt':1,'reserved_usd':'0.40192',
                 'request_sha256':audit.sha(folder/'attempt-01.request.json'),'reservation_basis':'synthetic fixture'}
            with (root/'api/ledger.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(row)+'\n')
            write(folder/'attempt-01.started.json',{'utc':utc,'attempt':1})
            write(folder/'attempt-01.result.json',{'utc':utc,'http_status':200,'credential_redacted':False})
            response={'id':f'synthetic-{len(calls)}','model':'openai/gpt-4o','provider':'OpenAI','created':1,
                      'system_fingerprint':None,'usage':{'prompt_tokens':2,'completion_tokens':3,'cost':0.01},
                      'choices':[{'message':{'content':content},'finish_reason':'stop','native_finish_reason':'stop'}]}
            write(folder/'attempt-01.response.txt',json.dumps(response).encode(),raw=True)
            write(folder/'content.txt',content.encode(),raw=True)
            out=root/f'responses/{stem}.json';write(out,json.loads(content))
            metadata={key:response[key] for key in ('id','model','provider','created','system_fingerprint','usage')}
            metadata.update({'finish_reason':'stop','native_finish_reason':'stop','credential_redacted':False})
            write(folder/'summary.json',{'stem':stem,'utc':utc,'status':'completed','issue':None,
                  'response_sha256':audit.sha(out),'metadata':metadata,'request_source_sha256':audit.sha(source)})
            calls.append(stem)
        run.complete=complete
        try:
            run.rounds();run.finish();rp.analyze(run.root)
            result=audit.audit(run.root)
            self.assertEqual(result['status'],'passed')
            self.assertEqual(result['review_assessments_checked'],144)
            self.assertEqual(result['revised_proposals_checked'],216)
            self.assertEqual(result['computed_diagnostics_checked'],72)
            self.assertEqual(result['final_receipts_checked'],72)
            self.assertEqual(result['final_reports_checked'],72)
            self.assertEqual(result['api']['logical_calls_completed'],36)
            self.assertEqual(set(calls),set(audit.EXPECTED))
            for arm in audit.ARMS:self.assertEqual(result['final_conditions'][arm]['joint_success'],24)
            # A literal historical answer cannot be silently replaced, even if
            # the current packet still describes the correct latest candidate.
            stem='round-2-plan-S1';packet=audit.read(run.root/f'packets/{stem}.json')
            body=audit.read(run.root/f'requests/{stem}.json')
            body['messages'][-2]['content']='{"plans":[]}'
            write(run.root/f'requests/{stem}.json',body)
            with self.assertRaises(AssertionError):
                audit.assert_history(run.root,stem,packet,prior='round-1-plan-S1')
        finally:run.tearDown()


if __name__=='__main__':unittest.main()
