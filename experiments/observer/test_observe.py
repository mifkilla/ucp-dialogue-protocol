import unittest
from observe import observe


class ObserveTests(unittest.TestCase):
    def setUp(self):
        self.case = {'id': 'C1', 'events': [{'id': 'E1', 'text': 'A receipt is missing.'}]}
        self.review = {'case_id': 'C1', 'verdict': 'unknown',
                       'evidence': [{'event_id': 'E1', 'quote': 'A receipt is missing.'}],
                       'reason': 'Effect cannot be established.'}

    def test_candidate_unknown_never_executes(self):
        r = observe([self.case], [self.review])
        self.assertEqual(r['alerts'][0]['kind'], 'semantic_candidate')
        self.assertEqual(r['actions_executed'], 0)

    def test_duplicate_reviews_raise_health_not_semantic_success(self):
        r = observe([self.case], [self.review, self.review])
        self.assertFalse(r['assessments'][0]['valid'])
        self.assertEqual(r['alerts'][0]['kind'], 'monitor_health')

    def test_watchdog_independent_of_valid_model_response(self):
        health = {'event_ids': ['E1', 'E2'], 'reviewed_ids': ['E2'],
                  'current_revision': 2, 'review_revision': 2, 'now': 10, 'checked_at': 9, 'max_age': 2}
        r = observe([self.case], [{**self.review, 'verdict': 'pass'}], health)
        self.assertEqual(r['health']['unreviewed_ids'], ['E1'])
        self.assertEqual(r['alerts'][0]['kind'], 'monitor_health')
        self.assertFalse(r['alerts'][0]['participant_violation'])

    def test_unknown_extra_case_is_not_silently_ignored(self):
        r = observe([self.case], [self.review, {**self.review, 'case_id': 'foreign'}])
        self.assertEqual(r['alerts'][-1]['extra_case_ids'], ['foreign'])


if __name__ == '__main__':
    unittest.main()
