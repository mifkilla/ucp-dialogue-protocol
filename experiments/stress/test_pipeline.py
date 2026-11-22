import json
from pathlib import Path
import tempfile
import unittest
import pipeline

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.case={'id':'T','actions':[{'id':'a'}],
                   'events':[{'id':'e','text':'Owner revoked the permission.'}]}
        self.good={'case_id':'T','verdict':'violation','action_ids':['a'],
             'evidence':[{'event_id':'e','quote':'revoked the permission'}],
             'reason':'A proposed action conflicts with the event.','suggestion':'Reconsider a.'}
    def test_valid_attribution_not_semantic_certification(self):
        self.assertTrue(pipeline.review(self.case,self.good)['valid'])
        self.good['verdict']='pass'
        self.assertTrue(pipeline.review(self.case,self.good)['valid'])
    def test_fabricated_evidence_does_not_reach_executor(self):
        self.good['evidence'][0]['quote']='approved everything'
        row=pipeline.review(self.case,self.good)
        self.assertFalse(row['valid']);self.assertIsNone(row['feedback'])
    def test_extra_action_is_not_valid_evidence(self):
        self.good['action_ids']=['foreign']
        self.assertFalse(pipeline.review(self.case,self.good)['valid'])
    def test_empty_and_malformed_citations_rejected(self):
        for value in ([],None,[{'event_id':'e','quote':''}],['e']):
            self.good['evidence']=value
            self.assertFalse(pipeline.review(self.case,self.good)['valid'])
    def test_feedback_grants_no_authority(self):
        self.assertFalse(pipeline.review(self.case,self.good)['feedback']['grants_authority'])
    def test_duplicate_cases_not_cherry_picked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            pipeline.write(p,{'plans':[{'case_id':'T','plan':{'selected':[]}}]*2})
            rows,issues=pipeline.items(p,'plans',['T'])
            self.assertIsNone(rows['T']);self.assertTrue(issues)
    def test_invalid_top_level_keeps_all_planned_cases(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{}')
            rows,issues=pipeline.items(p,'plans',['T','U'])
            self.assertEqual(rows,{'T':None,'U':None});self.assertTrue(issues)
    def test_missing_response_not_abstention(self):
        with tempfile.TemporaryDirectory() as d:
            rows,issues=pipeline.items(Path(d)/'missing','reviews',['T'])
            self.assertIsNone(rows['T']);self.assertTrue(issues)
    def test_unhashable_case_identifier_is_invalid_not_a_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            for cid in ([],{},None,True):
                pipeline.write(p,{'plans':[{'case_id':cid,'plan':{'selected':[]}}]})
                rows,issues=pipeline.items(p,'plans',['T'])
                self.assertIsNone(rows['T']);self.assertTrue(issues)
    def test_sealed_input_detects_byte_change(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);pipeline.write(root/'data.json',{'x':1})
            pipeline.seal(root,'manifest.json',['data.json'])
            self.assertEqual(pipeline.verify(root),1)
            pipeline.write(root/'data.json',{'x':2})
            with self.assertRaises(ValueError):pipeline.verify(root)
    def test_new_write_never_replaces_raw(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'raw';pipeline.write(p,{'x':1},new=True)
            with self.assertRaises(FileExistsError):pipeline.write(p,{'x':2},new=True)
            self.assertEqual(pipeline.read(p),{'x':1})

class EndToEndTests(unittest.TestCase):
    def test_all_stages_keep_originals_and_receipts_bound(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'run';pipeline.prepare(root)
            cases=pipeline.load_cases(root);refs=pipeline.read(root/'references.json')['references']
            for r in (1,2):
                plans=[{'case_id':c['id'],'plan':{'selected':refs[c['id']]['optimal_plans'][0]}} for c in cases]
                pipeline.write(root/f'responses/initial-{r}.json',{'plans':plans},new=True)
            pipeline.observers(root)
            for r in (1,2):
                reviews=[]
                for c in cases:
                    event=next(e for e in c['events'] if e['source']=='owner' and e['kind']=='policy')
                    reviews.append({'case_id':c['id'],'verdict':'pass','action_ids':[],
                        'evidence':[{'event_id':event['id'],'quote':event['text']}],
                        'reason':'Synthetic reference-path fixture, not a model result.','suggestion':'Preserve.'})
                pipeline.write(root/f'responses/observer-{r}.json',{'reviews':reviews},new=True)
            pipeline.revisions(root)
            for sid in pipeline.SESSIONS:
                packet=pipeline.read(root/f'packets/{sid}-plan.json')
                plans=[{'case_id':x['case']['id'],'plan':{'selected':refs[x['case']['id']]['optimal_plans'][0]}} for x in packet['cases']]
                pipeline.write(root/f'responses/{sid}-plan.json',{'plans':plans},new=True)
                pipeline.execute(root,sid)
                records=pipeline.read(root/f'executions/{sid}.json')['records']
                reports=[{'case_id':cid,'report':pipeline.engine.expected_report(x['receipt'])} for cid,x in records.items()]
                pipeline.write(root/f'responses/{sid}-report.json',{'reports':reports},new=True)
            result=pipeline.analyze(root)
            self.assertEqual(result['initial_summary']['optimal'],24)
            self.assertTrue(all(x['joint_success']==24 for x in result['conditions'].values()))
            self.assertTrue(all(x['repair_fraction'] is None for x in result['conditions'].values()))
            self.assertTrue(all(not x['criterion_met'] for x in result['added_value'].values()))
            self.assertEqual(result['false_feedback']['passed'],8)
            with self.assertRaises(FileExistsError):pipeline.execute(root,'S1')
            pipeline.write(root/'responses/initial-1.json',{'plans':[]})
            with self.assertRaises(ValueError):pipeline.analyze(root)

if __name__=='__main__':unittest.main()
