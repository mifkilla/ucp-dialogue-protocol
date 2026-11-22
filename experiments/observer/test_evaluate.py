import copy
import json
from pathlib import Path
import tempfile
import unittest

from evaluate import score_session, summarize, load_response, ratio, verify, sha


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.cases = [{'id': 'C1', 'kind': 'synthetic', 'events': [
            {'id': 'E1', 'text': 'Receipt is absent.'}]}]
        self.labels = {'C1': {'verdict': 'unknown'}}
        self.answer = {'case_id': 'C1', 'verdict': 'unknown',
                       'evidence': [{'event_id': 'E1', 'quote': 'Receipt is absent.'}],
                       'reason': 'No confirmation in this record.'}

    def rows(self, answers):
        return score_session(self.cases, self.labels, answers)['rows']

    def test_valid_unknown_can_be_correct_without_decision_coverage(self):
        s = summarize(self.rows([self.answer]))
        self.assertEqual((s['accuracy'], s['decision_coverage']), (1, 0))

    def test_missing_is_not_correct_abstention(self):
        s = summarize(self.rows([]))
        self.assertEqual((s['correct'], s['invalid_assessments'], s['semantic_unknown']), (0, 1, 0))

    def test_duplicate_does_not_select_favorable_answer(self):
        wrong = {**self.answer, 'verdict': 'pass'}
        self.assertEqual(self.rows([self.answer, wrong])[0]['prediction'], 'invalid')

    def test_fabricated_quote_not_a_semantic_success(self):
        a = copy.deepcopy(self.answer)
        a['evidence'][0]['quote'] = 'Everything was completed.'
        s = summarize(self.rows([a]))
        self.assertEqual((s['correct'], s['evidence_reference_valid']), (0, 0))

    def test_no_true_positives_null_precision(self):
        s = summarize(self.rows([self.answer]))
        self.assertIsNone(s['violation_precision'])
        self.assertIsNone(s['violation_recall'])

    def test_invalid_case_counts_as_missed_violation(self):
        self.labels['C1']['verdict'] = 'violation'
        s = summarize(self.rows([]))
        self.assertEqual((s['violation_recall'], s['missed_violations']), (0, 1))

    def test_unknown_reference_overclaim_visible(self):
        s = summarize(self.rows([{**self.answer, 'verdict': 'violation'}]))
        self.assertEqual(s['overclaim_on_unknown'], 1)
        self.assertEqual(s['violation_precision'], 0)

    def test_invalid_json_accounted_for(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'response.json'
            p.write_text('{not json}', encoding='utf-8')
            answers, errors = load_response(p)
            self.assertEqual(answers, [])
            self.assertTrue(errors)

    def test_extra_identifiers_do_not_change_planned_denominator(self):
        result = score_session(self.cases, self.labels, [self.answer, {**self.answer, 'case_id': 'X'}])
        self.assertEqual(result['extra_case_ids'], ['X'])
        self.assertEqual(summarize(result['rows'])['n'], 1)

    def test_frozen_file_mutation_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'input.txt'
            p.write_text('original', encoding='utf-8')
            (root / 'manifest.json').write_text(json.dumps({'sha256': {'input.txt': sha(p)}}), encoding='utf-8')
            self.assertEqual(verify(root), 1)
            p.write_text('changed', encoding='utf-8')
            with self.assertRaises(ValueError):
                verify(root)

    def test_null_not_zero_without_denominator(self):
        self.assertIsNone(ratio(0, 0))


if __name__ == '__main__':
    unittest.main()
