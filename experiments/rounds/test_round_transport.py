import copy
from decimal import Decimal
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import round_transport as runner


class RoundTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stem = 'round-1-plan-S1'
        self.body(self.stem)

    def body(self, stem, messages=None):
        messages = messages or [{'role': 'system', 'content': 'Return the requested JSON.'},
                                {'role': 'user', 'content': '{"cases":[]}'}]
        value = {'model': runner.MODEL,
                 'provider': {'only': ['OpenAI'], 'allow_fallbacks': False, 'require_parameters': True},
                 'messages': messages, 'transforms': [], 'temperature': 0.2, 'top_p': 1.0,
                 'max_tokens': 8192, 'seed': 6100 + int(stem[-1]),
                 'response_format': {'type': 'json_object'}}
        runner.write_new(self.root / 'requests' / f'{stem}.json', value)
        return value

    def response(self, content='{"plans":[]}', **extra):
        return 200, json.dumps({'id': 'mock-id', 'model': runner.MODEL, 'provider': 'OpenAI',
                               'usage': {'prompt_tokens': 10, 'completion_tokens': 3, 'cost': 0.001},
                               'choices': [{'message': {'content': content}, 'finish_reason': 'stop'}],
                               **extra}).encode()

    def forbidden_send(self, *_):
        self.fail('Unexpected transport invocation')

    def test_exactly_36_logical_requests_are_permitted(self):
        self.assertEqual(len(runner.STEMS), 36)
        self.assertEqual(len(set(runner.STEMS)), 36)
        self.assertIn('round-3-review-K2', runner.STEMS)
        self.assertIn('final-report-S2', runner.STEMS)
        for value in ('../escape', 'round-4-plan-S1', 'round-1-review-S1', 'final-report-M1'):
            with self.assertRaisesRegex(ValueError, 'Unplanned'):
                runner.run_one(self.root, value, 'mock-secret', send=self.forbidden_send)

    def test_fixed_configuration_rejects_drift_and_extra_fields(self):
        valid = runner.request_body(self.root, self.stem)
        changes = [('model', 'different'), ('provider', {'only': ['Azure']}),
                   ('temperature', 0.3), ('top_p', True), ('max_tokens', 8193),
                   ('seed', 6102), ('transforms', ['middle-out']),
                   ('response_format', {'type': 'text'}), ('tools', [])]
        for name, value in changes:
            altered = copy.deepcopy(valid);altered[name] = value
            with self.subTest(field=name), self.assertRaises(ValueError):
                runner.validate_body(altered, self.stem)
        altered = copy.deepcopy(valid);altered['provider']['allow_fallbacks'] = 0
        with self.assertRaisesRegex(ValueError, 'Boolean'):
            runner.validate_body(altered, self.stem)

    def test_invalid_message_history_is_rejected(self):
        valid = runner.request_body(self.root, self.stem)
        malformed = [[], [{'role': 'user', 'content': 'x'}],
                     [{'role': 'system', 'content': 'x'}, {'role': 'tool', 'content': 'x'}],
                     [{'role': 'system', 'content': ''}, {'role': 'user', 'content': 'x'}],
                     [{'role': 'system', 'content': 'x'}, {'role': 'user', 'content': ['image']}],
                     [{'role': 'system', 'content': 'x'}, {'role': 'user', 'content': 'x', 'name': 'owner'}]]
        for messages in malformed:
            altered = copy.deepcopy(valid);altered['messages'] = messages
            with self.assertRaises(ValueError):runner.validate_body(altered, self.stem)

    def test_report_preserves_literal_prebuilt_conversation(self):
        stem = 'final-report-O2'
        messages = [{'role': 'system', 'content': 'Plan under the contract.'},
                    {'role': 'user', 'content': '{"original":"unchanged source"}'},
                    {'role': 'assistant', 'content': ' { "plans": [] }\n'},
                    {'role': 'user', 'content': '{"receipt":{"executed":[],"value":0}}'}]
        expected = self.body(stem, messages)
        captured = []
        def send(body, key):
            captured.append(copy.deepcopy(body))
            return self.response('{"reports":[]}')
        runner.run_one(self.root, stem, 'mock-secret', send=send)
        self.assertEqual(captured, [expected])
        saved = runner.read_json(self.root / 'api' / stem / 'attempt-01.request.json')
        self.assertEqual(saved['messages'], messages)
        invalid = copy.deepcopy(expected);invalid['messages'] = messages[:2]
        with self.assertRaisesRegex(ValueError, 'preceding assistant'):
            runner.validate_body(invalid, stem)

    def test_completed_resume_verifies_source_and_never_sends_again(self):
        first = runner.run_one(self.root, self.stem, 'mock-secret', send=lambda *_: self.response())
        second = runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)
        self.assertEqual(first, second)
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)
        self.assertEqual(first['request_source_sha256'], runner.digest(self.root / 'requests' / f'{self.stem}.json'))
        path = self.root / 'requests' / f'{self.stem}.json'
        path.write_text(path.read_text() + '\n')
        with self.assertRaisesRegex(RuntimeError, 'source changed'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)

    def test_changed_saved_response_is_detected(self):
        runner.run_one(self.root, self.stem, 'mock-secret', send=lambda *_: self.response())
        (self.root / 'responses' / f'{self.stem}.json').write_text('{}')
        with self.assertRaisesRegex(RuntimeError, 'response changed'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)

    def test_credential_is_absent_from_all_saved_artifacts(self):
        key = 'mock-private-credential-123'
        summary = runner.run_one(self.root, self.stem, key,
                                 send=lambda *_: self.response(json.dumps({'echo': key})))
        self.assertTrue(summary['metadata']['credential_redacted'])
        for path in self.root.rglob('*'):
            if path.is_file():self.assertNotIn(key.encode(), path.read_bytes())

    def test_credential_in_request_content_is_blocked(self):
        path = self.root / 'requests' / f'{self.stem}.json'
        body = runner.read_json(path);body['messages'][1]['content'] = 'mock-secret'
        path.write_text(json.dumps(body))
        with self.assertRaisesRegex(ValueError, 'credential present'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)
        self.assertEqual(runner.ledger_rows(self.root), [])

    def test_reservation_precedes_network(self):
        def send(*_):
            self.assertEqual(len(runner.ledger_rows(self.root)), 1)
            self.assertTrue((self.root / 'api' / self.stem / 'attempt-01.request.json').exists())
            return self.response()
        runner.run_one(self.root, self.stem, 'mock-secret', send=send)

    def test_attempt_cap_and_cost_budget_fail_before_send(self):
        for number in range(39):runner.reserve(self.root, 'synthetic', number, 'hash')
        with self.assertRaisesRegex(RuntimeError, 'budget'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)
        self.assertEqual(len(runner.ledger_rows(self.root)), 39)
        with tempfile.TemporaryDirectory() as directory, patch.object(runner, 'BUDGET', Decimal('0.7')):
            runner.reserve(Path(directory), 'synthetic', 1, 'hash')
            with self.assertRaisesRegex(RuntimeError, 'budget'):
                runner.reserve(Path(directory), 'synthetic', 2, 'hash')

    def test_one_retry_only_for_explicit_qualifying_http(self):
        calls = []
        def send(*_):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError('https://example.invalid', 429, 'retry', {}, io.BytesIO(b'busy'))
            return self.response()
        result = runner.run_one(self.root, self.stem, 'mock-secret', send=send, sleep=lambda _: None)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(runner.ledger_rows(self.root)), 2)

    def test_request_mutation_before_retry_blocks_further_dispatch(self):
        calls = []
        def send(*_):
            calls.append(1)
            return 429, b'busy'
        def sleep(_):
            path = self.root / 'requests' / f'{self.stem}.json'
            path.write_text(path.read_text() + '\n')
        with self.assertRaisesRegex(RuntimeError, 'source changed'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=send, sleep=sleep)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)
        with self.assertRaisesRegex(RuntimeError, 'Unfinished'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)

    def test_two_retryable_failures_preserve_missingness_without_third_call(self):
        calls = []
        def send(*_):calls.append(1);return 503, b'temporary'
        summary = runner.run_one(self.root, self.stem, 'mock-secret', send=send, sleep=lambda _: None)
        self.assertEqual(len(calls), 2)
        self.assertEqual(summary['status'], 'http_error')
        self.assertEqual(runner.read_json(self.root / 'responses' / f'{self.stem}.json'), {})

    def test_fatal_http_and_api_envelope_persist_global_stop(self):
        summary = runner.run_one(self.root, self.stem, 'mock-secret', send=lambda *_: (402, b'exhausted'))
        self.assertEqual(summary['status'], 'http_error')
        next_stem = 'round-1-plan-S2';self.body(next_stem)
        with self.assertRaisesRegex(RuntimeError, 'stopped'):
            runner.run_one(self.root, next_stem, 'mock-secret', send=self.forbidden_send)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner.write_new(root / 'requests' / f'{self.stem}.json', runner.request_body(self.root, self.stem))
            result = runner.run_one(root, self.stem, 'mock-secret', send=lambda *_: (200, b'{"error":{}}'))
            self.assertEqual(result['status'], 'api_envelope_error')
            self.assertTrue((root / 'api/stop.json').exists())

    def test_unknown_transport_is_not_retried_or_logged_verbatim(self):
        def send(*_):raise TimeoutError('mock-secret private diagnostic')
        summary = runner.run_one(self.root, self.stem, 'mock-secret', send=send)
        self.assertEqual(summary['status'], 'transport_unknown')
        self.assertEqual(len(runner.ledger_rows(self.root)), 1)
        runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)
        for path in self.root.rglob('*'):
            if path.is_file():self.assertNotIn(b'mock-secret', path.read_bytes())

    def test_partial_invocation_has_no_automatic_replay(self):
        runner.write_new(self.root / 'api' / self.stem / 'attempt-01.started.json', {'utc': 'unknown'})
        with self.assertRaisesRegex(RuntimeError, 'Unfinished'):
            runner.run_one(self.root, self.stem, 'mock-secret', send=self.forbidden_send)

    def test_malformed_and_schema_invalid_json_are_not_repaired(self):
        summary = runner.run_one(self.root, self.stem, 'mock-secret', send=lambda *_: self.response('not JSON'))
        self.assertEqual(summary['status'], 'completed')
        self.assertIn('Malformed', summary['issue'])
        self.assertEqual(runner.read_json(self.root / 'responses' / f'{self.stem}.json'), {})
        self.assertEqual((self.root / 'api' / self.stem / 'content.txt').read_text(), 'not JSON')
        next_stem = 'round-1-plan-S2';self.body(next_stem)
        runner.run_one(self.root, next_stem, 'mock-secret', send=lambda *_: self.response('[42]'))
        self.assertEqual(runner.read_json(self.root / 'responses' / f'{next_stem}.json'), [42])

    def test_paired_seed_applies_to_all_roles_and_rounds(self):
        for stem in runner.STEMS:
            if stem == self.stem:continue
            messages = None
            if stem.startswith('final-report-'):
                messages = [{'role': 'system', 'content': 'JSON'}, {'role': 'user', 'content': 'plan'},
                            {'role': 'assistant', 'content': '{}'}, {'role': 'user', 'content': 'receipt'}]
            self.body(stem, messages)
            self.assertEqual(runner.request_body(self.root, stem)['seed'], 6100 + int(stem[-1]))

    def test_run_lock_prevents_concurrent_spending(self):
        with runner.run_lock(self.root):
            with self.assertRaisesRegex(RuntimeError, 'locked'):
                with runner.run_lock(self.root):self.fail('Concurrent sender')
        self.assertFalse((self.root / 'api/runner.lock').exists())

    def test_key_file_is_read_only_and_duplicate_key_is_rejected(self):
        path = self.root / 'synthetic.env'
        path.write_text('# comment\nOTHER=ignore\nexport OPENROUTER_API_KEY="mock-only"\n')
        original = path.read_bytes()
        self.assertEqual(runner.load_key(path), 'mock-only')
        self.assertEqual(path.read_bytes(), original)
        path.write_text('OPENROUTER_API_KEY=a\nOPENROUTER_API_KEY=b\n')
        with self.assertRaisesRegex(ValueError, 'exactly one'):runner.load_key(path)


if __name__ == '__main__':
    unittest.main()
