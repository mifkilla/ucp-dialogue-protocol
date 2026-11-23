import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import round_pipeline as rp


class RoundPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/'run'
        source = Path(rp.__file__).resolve().parent
        archive = source.parent/'data'/'openrouter-07.zip'
        # An extracted bundle has no parent repository; its original source ZIP
        # is not needed to test the loop. Use its fixed copied inputs instead.
        if archive.exists():
            rp.prepare(self.root, archive=archive)
        else:
            self.root.mkdir()
            import shutil
            names = rp.read(source/'manifest.json')['sha256']
            for name in names:
                target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source/name,target)
            shutil.copyfile(source/'manifest.json',self.root/'manifest.json')
            (self.root/'responses').mkdir()
        self.engine,self.base=rp.modules(self.root)
        self.cases=rp.cases(self.root)
        self.original=rp.read(self.root/'source-originals.json')
        self.refs=rp.read(self.root/'references.json')['references']

    def tearDown(self):
        self.temp.cleanup()

    def complete(self,stem,value,*,literal=None,status='completed'):
        rp.write_new(self.root/f'responses/{stem}.json',value)
        folder=self.root/'api'/stem;folder.mkdir(parents=True)
        if status=='completed':
            (folder/'content.txt').write_text(literal if literal is not None else json.dumps(value),encoding='utf-8',newline='\n')
        rp.write_new(folder/'summary.json',{'status':status,
            'response_sha256':rp.sha(self.root/f'responses/{stem}.json')})

    def good_reviews(self,number,*,bad_quote=False):
        rp.reviews(self.root,number)
        by_case={c['id']:c for c in self.cases}
        for sid in rp.REVIEW_SESSIONS:
            packet=rp.read(self.root/f'packets/round-{number}-review-{sid}.json')
            rows=[]
            for item in packet['cases']:
                case=by_case[item['case_id']]
                event=case['events'][0]
                rows.append({'case_id':case['id'],
                    'verdict':self.engine.check_plan(case,item['candidate'])['verdict'],
                    'action_ids':[], 'evidence':[{'event_id':event['id'],
                    'quote':'not an actual quote anywhere' if bad_quote else event['text']}],
                    'reason':'Synthetic reference-shaped fixture for interface testing.',
                    'suggestion':'Recheck the current proposal within its permission.'})
            self.complete(f'round-{number}-review-{sid}',{'reviews':rows})

    def good_plans(self,number,*,optimal=False,reverse=False):
        rp.plans(self.root,number)
        for sid in rp.SESSIONS:
            rows=[]
            for case in self.cases:
                value=({'selected':self.refs[case['id']]['optimal_plans'][0]}
                       if optimal else self.original[sid[1]]['plans'][case['id']])
                if reverse:value={'selected':list(reversed(value['selected']))}
                rows.append({'case_id':case['id'],'plan':value})
            self.complete(f'round-{number}-plan-{sid}',{'plans':rows})

    def rounds(self,pattern=(False,True,True)):
        for number,optimal in enumerate(pattern,1):
            self.good_reviews(number)
            self.good_plans(number,optimal=optimal)

    def finish(self):
        rp.final(self.root)
        for sid in rp.SESSIONS:
            records=rp.read(self.root/f'executions/{sid}.json')['records']
            self.complete(f'final-report-{sid}',{'reports':[{'case_id':cid,
                'report':self.engine.expected_report(row['receipt'])} for cid,row in records.items()]})

    def test_baseline_source_is_bound_and_identical_across_arms(self):
        rp.reviews(self.root,1)
        old_hashes=rp.read(self.root/'baseline/source-bundle-hashes.json')['sha256']
        self.assertEqual(rp.sha(self.root/'source-originals.json'),old_hashes['originals.json'])
        for sid in rp.REVIEW_SESSIONS:
            packet=rp.read(self.root/f'packets/round-1-review-{sid}.json')
            for row in packet['cases']:
                self.assertEqual(row['candidate'],self.original[sid[1]]['plans'][row['case_id']])
                self.assertEqual(row['candidate_sha256'],rp.candidate_hash(row['candidate']))
        for repeat in (1,2):
            a=rp.read(self.root/f'packets/round-1-review-O{repeat}.json')
            b=rp.read(self.root/f'packets/round-1-review-K{repeat}.json')
            self.assertEqual(a,b)

    def test_frozen_source_mutation_is_rejected(self):
        with (self.root/'cases.json').open('a',encoding='utf-8') as f:f.write(' ')
        with self.assertRaises(ValueError):rp.reviews(self.root,1)

    def test_missing_final_round_blocks_execution(self):
        with self.assertRaises(FileNotFoundError):rp.final(self.root)
        self.assertFalse((self.root/'executions').exists())

    def test_literal_previous_answer_and_full_case_only_once(self):
        self.good_reviews(1);self.good_plans(1,optimal=True)
        rp.reviews(self.root,2)
        previous=rp.read(self.root/'requests/round-1-review-O1.json')['messages']
        current=rp.read(self.root/'requests/round-2-review-O1.json')['messages']
        self.assertEqual(current[:-2],previous)
        self.assertEqual(current[-2]['content'],rp.raw_content(self.root,'round-1-review-O1'))
        latest=json.loads(current[-1]['content'])
        self.assertTrue(all('case' not in row for row in latest['cases']))
        for row in latest['cases']:
            self.assertEqual(row['candidate']['selected'],self.refs[row['case_id']]['optimal_plans'][0])

    def test_invalid_quote_fallback_is_explicit_and_checker_does_not_supply_optimum(self):
        self.good_reviews(1,bad_quote=True)
        out=rp.plans(self.root,1)
        self.assertEqual(out['valid_reviews'],0)
        ordinary=rp.read(self.root/'packets/round-1-plan-S1.json')
        observer=rp.read(self.root/'packets/round-1-plan-O1.json')
        checked=rp.read(self.root/'packets/round-1-plan-K1.json')
        self.assertTrue(all(row['review_feedback']['unavailable'] for row in observer['cases']))
        self.assertTrue(all('computed_diagnostics' not in row for row in ordinary['cases']+observer['cases']))
        self.assertTrue(all('computed_diagnostics' in row for row in checked['cases']))
        self.assertNotIn('optimal_value',json.dumps(checked))
        self.assertNotIn('optimal_plans',json.dumps(checked))

    def test_malformed_json_remains_literal_and_interface_invalid(self):
        self.good_reviews(1);rp.plans(self.root,1)
        for sid in rp.SESSIONS:
            self.complete(f'round-1-plan-{sid}',{},literal='{unfinished')
        rp.reviews(self.root,2)
        payload=rp.read(self.root/'packets/round-2-review-O1.json')
        self.assertTrue(all(row['candidate'] is None for row in payload['cases']))
        # Actor continuation will preserve the exact malformed text, not {}.
        messages=rp.continuing_messages(self.root,'round-1-plan-S1',{'next':True})
        self.assertEqual(messages[-2],{'role':'assistant','content':'{unfinished'})

    def test_transport_missingness_does_not_fabricate_assistant_history(self):
        self.good_reviews(1);rp.plans(self.root,1)
        for sid in rp.SESSIONS:
            self.complete(f'round-1-plan-{sid}',{},status='transport_unknown')
        with self.assertRaisesRegex(ValueError,'Missing generated context'):
            rp.reviews(self.root,2)
        self.assertFalse((self.root/'requests/round-2-review-O1.json').exists())

    def test_changed_parsed_response_is_rejected_before_continuation(self):
        self.good_reviews(1);self.good_plans(1)
        (self.root/'responses/round-1-plan-S1.json').write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Changed parsed response'):
            rp.reviews(self.root,2)

    def test_counterfactual_score_does_not_execute(self):
        c=self.cases[0]
        with patch.object(self.engine,'execute',side_effect=AssertionError('Execution forbidden')):
            row=rp.proposal_score(self.engine,c,self.original['1']['plans'][c['id']],self.refs[c['id']])
        self.assertIn('counterfactual_value',row)
        self.assertNotIn('executed_value',row)

    def test_final_reports_continue_actor_history_with_actual_receipts(self):
        self.rounds()
        rp.final(self.root)
        prior=rp.read(self.root/'requests/round-3-plan-S1.json')['messages']
        current=rp.read(self.root/'requests/final-report-S1.json')['messages']
        self.assertEqual(len(current),8)
        self.assertEqual(current[:-2],prior)
        self.assertEqual(current[-2]['content'],rp.raw_content(self.root,'round-3-plan-S1'))
        payload=json.loads(current[-1]['content'])
        records=rp.read(self.root/'executions/S1.json')['records']
        for row in payload['cases']:
            self.assertEqual(row['receipt'],records[row['case_id']]['receipt'])
        with self.assertRaises(FileExistsError):rp.final(self.root)

    def test_paired_api_settings_and_full_end_to_end_analysis(self):
        self.rounds();self.finish()
        result=rp.analyze(self.root)
        self.assertEqual(result['rounds']['0']['conditions']['S']['admissible'],17)
        self.assertEqual(result['rounds']['0']['conditions']['S']['optimal'],0)
        for arm in rp.ARMS:
            self.assertEqual(result['final']['conditions'][arm]['joint_success'],24)
            self.assertEqual(result['round3_vs_round1'][arm]['optimal_delta'],24)
        self.assertFalse(result['primary']['O']['criterion_met'])
        for r in (1,2):
            for arm in rp.ARMS:
                body=rp.read(self.root/f'requests/round-3-plan-{arm}{r}.json')
                self.assertEqual(body['seed'],6100+r)
                self.assertEqual(body['provider']['only'],['OpenAI'])
                self.assertEqual(body['transforms'],[])

    def test_cycle_and_order_invariance_are_distinguished(self):
        self.rounds((False,True,False));self.finish()
        result=rp.analyze(self.root)
        for arm in rp.ARMS:
            self.assertEqual(len(result['trajectories'][arm]['oscillations']),24)
        self.assertEqual(rp.selected_set({'selected':['a','b']}),rp.selected_set({'selected':['b','a']}))

    def test_every_assembled_json_mode_request_explicitly_requests_json(self):
        self.rounds();self.finish()
        paths=list((self.root/'requests').glob('*.json'))
        self.assertEqual(len(paths),36)
        for path in paths:
            with self.subTest(stem=path.stem):
                body=rp.read(path)
                self.assertEqual(body['response_format'],{'type':'json_object'})
                self.assertIn('Return JSON only, using the required schema.',
                              body['messages'][0]['content'])
                self.assertRegex(' '.join(m['content'] for m in body['messages']).lower(),
                                 r'\bjson\b')

    def test_postseal_proposal_change_is_detected(self):
        self.good_reviews(1);self.good_plans(1)
        rp.close_round(self.root,1)
        with (self.root/'api/round-1-plan-O1/content.txt').open('a') as f:f.write(' ')
        with self.assertRaises(ValueError):rp.reviews(self.root,2)


if __name__=='__main__':
    unittest.main()
