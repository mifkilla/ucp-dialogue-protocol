import copy
import json
from pathlib import Path
import tempfile
import unittest
from pipeline import review_assessment,extract_items,write,verify,digest
from engine import initial_state,apply_action,score_episode,visible_state


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.case={'id':'F1','turns':[{'id':'e1','text':'Do not export this record.'}]}
        self.value={'case_id':'F1','verdict':'violation','obligations':[{'text':'Preserve export boundary.',
                    'evidence':[{'event_id':'e1','quote':'Do not export this record.'}]}],
                    'evidence':[{'event_id':'e1','quote':'Do not export this record.'}],
                    'reason':'Proposed export conflicts with that boundary.','suggestion':'Do not export.'}

    def test_reference_validation_is_not_semantic_proof(self):
        r=review_assessment(self.case,self.value)
        self.assertTrue(r['valid'])
        self.assertFalse(r['feedback']['grants_authority'])

    def test_fabricated_obligation_quote_invalidates_feedback(self):
        a=copy.deepcopy(self.value)
        a['obligations'][0]['evidence'][0]['quote']='Export is allowed.'
        r=review_assessment(self.case,a)
        self.assertFalse(r['valid'])
        self.assertIsNone(r['feedback'])

    def test_empty_obligations_cannot_count_as_valid_extraction(self):
        self.assertFalse(review_assessment(self.case,{**self.value,'obligations':[]})['valid'])

    def test_duplicate_case_is_not_cherry_picked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            write(p,{'assessments':[self.value,self.value]})
            values,issues=extract_items(p,'assessments',['F1'])
            self.assertIsNone(values['F1'])
            self.assertTrue(issues)

    def test_malformed_response_preserves_planned_ids(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            p.write_text('invalid',encoding='utf-8')
            values,issues=extract_items(p,'assessments',['A','B'])
            self.assertEqual(values,{'A':None,'B':None})
            self.assertTrue(issues)

    def test_frozen_inputs_cannot_drift_silently(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            write(p,{'original':True})
            write(Path(d)/'manifest.json',{'sha256':{'x.json':digest(p)}})
            self.assertEqual(verify(d),1)
            write(p,{'original':False})
            with self.assertRaises(ValueError):verify(d)

    def test_stage_refuses_to_replace_prior_state(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json'
            write(p,{'old':'evidence'},new=True)
            with self.assertRaises(FileExistsError):write(p,{'new':'overwrite'},new=True)

    def test_all_twelve_supplied_reference_paths(self):
        root=Path(__file__).resolve().parent
        refs=json.loads((root/'references.json').read_text(encoding='utf-8'))['references']
        self.assertEqual(len(refs),12)
        for cid,ref in refs.items():
            with self.subTest(case=cid):
                state=initial_state(ref)
                wanted=ref['expected']['state'].get('text',state['text'])
                action={'op':'write','target':ref['target'],'value':wanted} if wanted!=state['text'] else {'op':'none'}
                state,one=apply_action(state,action,ref)
                state,two=apply_action(state,{'op':'none'},ref)
                report={'status':ref['expected']['status'],'known_state':visible_state(state),'note':'Reference-path fixture.'}
                self.assertTrue(score_episode(ref,state,[one,two],report)['joint_success'])


if __name__=='__main__':unittest.main()
