import io
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error

import api_runner as runner


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet('initial-1')

    def packet(self, stem, **extra):
        runner.write_new(self.root / 'packets' / f'{stem}.json',
                         {'instructions': 'Return JSON.', 'cases': [{'id': 'X'}], **extra})

    def response(self, content='{"plans":[]}', **extra):
        return 200, json.dumps({'id': 'mock-id', 'model': runner.MODEL, 'provider': 'OpenAI',
                                'usage': {'prompt_tokens': 10, 'completion_tokens': 3, 'cost': 0.001},
                                'choices': [{'message': {'content': content}, 'finish_reason': 'stop'}],
                                **extra}).encode()

    def test_complete_resume_does_not_call_again(self):
        first = runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: self.response())
        second = runner.run_one(self.root, 'initial-1', 'mock-secret',
                                send=lambda *_: self.fail('Completed call replayed'))
        self.assertEqual(first, second)
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)

    def test_changed_saved_response_detected(self):
        runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: self.response())
        (self.root / 'responses' / 'initial-1.json').write_text('{}')
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            runner.run_one(self.root, 'initial-1', 'mock-secret')

    def test_credential_never_written_even_if_reflected(self):
        key = 'mock-private-credential-123'
        runner.run_one(self.root, 'initial-1', key,
                       send=lambda *_: self.response(json.dumps({'reflected': key})))
        for path in self.root.rglob('*'):
            if path.is_file():
                self.assertNotIn(key.encode(), path.read_bytes(), str(path))
        self.assertTrue(runner.read_json(self.root / 'api/initial-1/summary.json')['metadata']['credential_redacted'])

    def test_budget_reservation_before_network_and_no_overrun(self):
        for number in range(24):
            runner.reserve(self.root, 'mock', number, 'hash')
        with self.assertRaisesRegex(RuntimeError, 'budget'):
            runner.run_one(self.root, 'initial-1', 'mock-secret',
                           send=lambda *_: self.fail('Budget exceeded'))
        self.assertEqual(len(runner.ledger_rows(self.root)), 24)

    def test_retry_only_explicit_retryable_http(self):
        calls = []
        def send(*_):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError('https://example.invalid', 429, 'retry', {}, io.BytesIO(b'busy'))
            return self.response()
        result = runner.run_one(self.root, 'initial-1', 'mock-secret', send=send, sleep=lambda _: None)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(runner.ledger_rows(self.root)), 2)
        self.assertEqual((self.root / 'api/initial-1/attempt-01.response.txt').read_bytes(), b'busy')

    def test_second_retryable_failure_is_not_retried(self):
        calls = []
        def send(*_):
            calls.append(1)
            return 503, b'temporary'
        result = runner.run_one(self.root, 'initial-1', 'mock-secret', send=send, sleep=lambda _: None)
        self.assertEqual(result['status'], 'http_error')
        self.assertEqual(len(calls), 2)

    def test_nonretryable_http_failure_preserves_denominator(self):
        calls = []
        def send(*_):
            calls.append(1)
            return 401, b'not authorized'
        result = runner.run_one(self.root, 'initial-1', 'mock-secret', send=send)
        self.assertEqual(result['status'], 'http_error')
        self.assertEqual(len(calls), 1)
        self.assertEqual(runner.read_json(self.root / 'responses/initial-1.json'), {})

    def test_nonretryable_failure_persistently_stops_new_calls(self):
        runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: (402, b'exhausted'))
        self.packet('initial-2')
        with self.assertRaisesRegex(RuntimeError, 'stopped'):
            runner.run_one(self.root, 'initial-2', 'mock-secret',
                           send=lambda *_: self.fail('New request after fatal failure'))
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)

    def test_api_error_envelope_stops_new_calls(self):
        result = runner.run_one(self.root, 'initial-1', 'mock-secret',
                                send=lambda *_: (200, b'{"error":{"code":400}}'))
        self.assertEqual(result['status'], 'api_envelope_error')
        self.assertTrue((self.root / 'api/stop.json').exists())

    def test_unknown_transport_is_not_retried_or_logged_verbatim(self):
        def send(*_):
            raise TimeoutError('mock-secret must never leak')
        result = runner.run_one(self.root, 'initial-1', 'mock-secret', send=send)
        self.assertEqual(result['status'], 'transport_unknown')
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)
        for path in self.root.rglob('*'):
            if path.is_file():
                self.assertNotIn(b'mock-secret', path.read_bytes())

    def test_partial_attempt_cannot_be_replayed(self):
        runner.write_new(self.root / 'api/initial-1/attempt-01.started.json', {'utc': 'unknown'})
        with self.assertRaisesRegex(RuntimeError, 'Unfinished'):
            runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: self.fail('Replayed unknown call'))

    def test_malformed_completion_is_saved_without_format_retry(self):
        result = runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: self.response('not JSON'))
        self.assertEqual(result['status'], 'completed')
        self.assertIn('Malformed', result['issue'])
        self.assertEqual(runner.read_json(self.root / 'responses/initial-1.json'), {})
        self.assertEqual((self.root / 'api/initial-1/content.txt').read_text(), 'not JSON')

    def test_schema_invalid_json_is_not_silently_corrected(self):
        runner.run_one(self.root, 'initial-1', 'mock-secret', send=lambda *_: self.response('[42]'))
        self.assertEqual(runner.read_json(self.root / 'responses/initial-1.json'), [42])

    def test_report_uses_plan_conversation_and_receipt(self):
        self.packet('S1-plan', review_feedback='review')
        self.packet('S1-report', receipts={'executed': []})
        runner.run_one(self.root, 'S1-plan', 'mock-secret', send=lambda *_: self.response())
        body = runner.request_body(self.root, 'S1-report')
        self.assertEqual([m['role'] for m in body['messages']], ['system', 'user', 'assistant', 'user'])
        self.assertIn('review_feedback', body['messages'][1]['content'])
        self.assertEqual(body['messages'][2]['content'], '{"plans":[]}')
        self.assertIn('receipts', body['messages'][3]['content'])
        self.assertEqual(body['seed'], 6101)
        self.assertEqual(body['provider']['only'], ['OpenAI'])
        self.assertFalse(body['provider']['allow_fallbacks'])
        self.assertEqual(body['transforms'], [])
        self.assertNotIn('tools', body)

    def test_repeat_seed_is_paired_across_conditions(self):
        for stem in ('observer-2', 'S2-plan', 'O2-plan', 'K2-plan', 'M2-plan'):
            self.packet(stem)
            self.assertEqual(runner.request_body(self.root, stem)['seed'], 6102)

    def test_lock_excludes_concurrent_stage_and_cleans_up(self):
        with runner.run_lock(self.root):
            with self.assertRaisesRegex(RuntimeError, 'locked'):
                with runner.run_lock(self.root):
                    self.fail('Concurrent stage entered')
        self.assertFalse((self.root / 'api/runner.lock').exists())

    def test_env_key_parser_unique_quoted_and_read_only(self):
        path = self.root / 'synthetic.env'
        path.write_text('# comment\nOTHER=ignore\nexport OPENROUTER_API_KEY="mock-only"\n')
        original = path.read_bytes()
        self.assertEqual(runner.load_key(path), 'mock-only')
        self.assertEqual(path.read_bytes(), original)
        path.write_text('OPENROUTER_API_KEY=a\nOPENROUTER_API_KEY=b\n')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            runner.load_key(path)


if __name__ == '__main__':
    unittest.main()
