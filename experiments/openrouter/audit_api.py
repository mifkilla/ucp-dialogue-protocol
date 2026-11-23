"""Independent API provenance audit; no runner import, credentials or network calls."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

SESSIONS = tuple(f'{arm}{r}' for r in (1, 2) for arm in ('S', 'O', 'K', 'M'))
EXPECTED = ('initial-1', 'initial-2', 'observer-1', 'observer-2') + tuple(
    f'{sid}-plan' for sid in SESSIONS) + tuple(f'{sid}-report' for sid in SESSIONS)
RETRY = {429, 502, 503, 504}
RESERVATION = Decimal('0.40192')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def base_messages(packet):
    return [{'role': 'system', 'content': packet['instructions']},
            {'role': 'user', 'content': json.dumps({k: v for k, v in packet.items()
                                                   if k != 'instructions'}, ensure_ascii=False)}]


def expected_request(root, stem):
    packet = read(root/'packets'/f'{stem}.json')
    if stem.endswith('-report'):
        prior = stem[:-7] + '-plan'
        messages = base_messages(read(root/'packets'/f'{prior}.json'))
        summary = read(root/'api'/prior/'summary.json')
        if summary['status'] == 'completed':
            # Raw assistant bytes are the auditable previous reply. Do not
            # manufacture a corrected or scorer-normalized answer here.
            content = (root/'api'/prior/'content.txt').read_bytes().decode('utf-8')
            messages.append({'role': 'assistant', 'content': content})
        messages.append({'role': 'user', 'content': json.dumps(packet, ensure_ascii=False)})
    else:
        messages = base_messages(packet)
    repeat = int(stem.split('-')[1]) if stem.startswith(('initial-', 'observer-')) else int(stem[1])
    return {'model': 'openai/gpt-4o',
            'provider': {'only': ['OpenAI'], 'allow_fallbacks': False, 'require_parameters': True},
            'messages': messages, 'temperature': 0.2, 'top_p': 1.0, 'max_tokens': 8192,
            'seed': 6100+repeat, 'response_format': {'type': 'json_object'}, 'transforms': []}


def audit(root):
    root = Path(root)
    ledger_path = root/'api/ledger.jsonl'
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding='utf-8').splitlines() if line]
    assert len(ledger) <= 24, 'HTTP attempt cap exceeded'
    assert len({(r['stem'], r['attempt']) for r in ledger}) == len(ledger), 'Duplicate reservation'
    assert all(r['stem'] in EXPECTED for r in ledger), 'Unplanned logical request'
    assert all(Decimal(r['reserved_usd']) == RESERVATION for r in ledger), 'Reservation amount'
    reserved = sum((Decimal(r['reserved_usd']) for r in ledger), Decimal(0))
    assert reserved <= Decimal('10'), 'Reserved budget exceeded'
    by_stem = {stem: [r for r in ledger if r['stem'] == stem] for stem in EXPECTED}
    results = {}; attempts = []; bindings = {}; reported_cost = Decimal(0)
    costs_present = 0; total_prompt = 0; total_completion = 0
    provider_names = Counter(); model_names = Counter(); finish_reasons = Counter()
    raw_returned_costs = []
    for stem, rows in by_stem.items():
        folder = root/'api'/stem
        if not rows:
            assert not (folder/'summary.json').exists(), ('Unreserved completion', stem)
            results[stem] = {'status': 'not_scheduled', 'classification': 'unavailable'}
            continue
        assert [r['attempt'] for r in rows] in ([1], [1, 2]), ('Attempt ordering', stem)
        expected = expected_request(root, stem)
        prior_status = None
        final_body = None; final_result = None
        for row in rows:
            prefix = folder/f"attempt-{row['attempt']:02d}"
            request_path = prefix.with_suffix('.request.json')
            assert sha(request_path) == row['request_sha256'], ('Request ledger hash', stem)
            assert read(request_path) == expected, ('Request body mismatch', stem)
            bindings[request_path.relative_to(root).as_posix()] = sha(request_path)
            if row['attempt'] == 2:
                assert prior_status in RETRY, ('Retry without explicit qualifying status', stem)
            started_path = prefix.with_suffix('.started.json')
            result_path = prefix.with_suffix('.result.json')
            if not started_path.exists() or not result_path.exists():
                assert row == rows[-1], ('Continued after unfinished attempt', stem)
                final_result = None
                attempts.append({'stem': stem, 'attempt': row['attempt'], 'status': 'unfinished'})
                continue
            started = read(started_path)
            assert started['attempt'] == row['attempt']
            assert row['utc'] <= started['utc'], ('Reservation after start', stem)
            final_result = read(result_path)
            assert started['utc'] <= final_result['utc'], ('Completion before start', stem)
            if final_result.get('kind') == 'transport_unknown':
                assert row == rows[-1], ('Retried unknown transport', stem)
                assert not prefix.with_suffix('.response.txt').exists()
                prior_status = None; final_body = None
                attempts.append({'stem': stem, 'attempt': row['attempt'], 'status': 'transport_unknown'})
                continue
            status = final_result['http_status']; prior_status = status
            body_path = prefix.with_suffix('.response.txt')
            final_body = body_path.read_bytes()
            bindings[body_path.relative_to(root).as_posix()] = sha(body_path)
            assert type(final_result['credential_redacted']) is bool
            attempts.append({'stem': stem, 'attempt': row['attempt'], 'status': status,
                             'credential_redacted': final_result['credential_redacted']})
            try:
                envelope = json.loads(final_body)
            except (ValueError, UnicodeDecodeError):
                envelope = None
            usage = envelope.get('usage') if isinstance(envelope, dict) else None
            if isinstance(usage, dict) and usage.get('cost') is not None:
                cost = Decimal(str(usage['cost']))
                assert cost >= 0 and cost <= RESERVATION, ('Returned cost exceeds reservation', stem)
                reported_cost += cost; costs_present += 1
                raw_returned_costs.append({'stem': stem, 'attempt': row['attempt'], 'cost_usd': str(cost)})
        summary_path = folder/'summary.json'
        if not summary_path.exists():
            results[stem] = {'status': 'unfinished', 'classification': 'unavailable'}
            continue
        summary = read(summary_path)
        assert summary['stem'] == stem
        parsed_path = root/'responses'/f'{stem}.json'
        assert sha(parsed_path) == summary['response_sha256'], ('Normalized response hash', stem)
        bindings[parsed_path.relative_to(root).as_posix()] = sha(parsed_path)
        parsed = read(parsed_path)
        status = summary['status']
        assert final_result is not None, ('Finalized without attempt result', stem)
        if status != 'completed':
            assert parsed == {}, ('Failure placeholder changed', stem)
            if status == 'transport_unknown':
                assert final_result.get('kind') == 'transport_unknown'
            elif status == 'http_error':
                assert final_result.get('http_status') != 200
                assert summary['metadata']['http_status'] == final_result['http_status']
            elif status == 'api_envelope_error':
                assert final_result.get('http_status') == 200
                try:
                    response = json.loads(final_body)
                    content = response['choices'][0]['message']['content']
                except (ValueError, KeyError, IndexError, TypeError, UnicodeDecodeError):
                    content = None
                assert not isinstance(content, str), ('Textual completion mislabeled unavailable', stem)
            else:
                raise AssertionError(('Unknown call status', status))
            results[stem] = {'status': status, 'classification': 'unavailable', 'issue': summary['issue']}
            continue
        assert final_result['http_status'] == 200
        envelope = json.loads(final_body); choice = envelope['choices'][0]
        content = choice['message']['content']
        assert isinstance(content, str)
        assert (folder/'content.txt').read_bytes().decode('utf-8') == content, ('Assistant content changed', stem)
        metadata = {k: envelope.get(k) for k in ('id', 'model', 'provider', 'created', 'system_fingerprint', 'usage')}
        metadata.update({'finish_reason': choice.get('finish_reason'),
                         'native_finish_reason': choice.get('native_finish_reason'),
                         'credential_redacted': final_result['credential_redacted']})
        assert summary['metadata'] == metadata, ('Returned metadata mismatch', stem)
        try:
            decoded = json.loads(content)
        except ValueError:
            decoded = {}; classification = 'generated_invalid_json'
            assert summary['issue'] == 'Malformed JSON completion retained without format retry'
        else:
            classification = 'generated_json'
            assert summary['issue'] is None
        assert parsed == decoded, ('Parsed answer altered', stem)
        provider_names[str(metadata['provider'])] += 1
        model_names[str(metadata['model'])] += 1
        finish_reasons[str(metadata['finish_reason'])] += 1
        usage = metadata.get('usage') or {}
        for name in ('prompt_tokens', 'completion_tokens'):
            if name in usage:
                assert type(usage[name]) is int and usage[name] >= 0, ('Invalid token usage', stem)
        total_prompt += usage.get('prompt_tokens', 0)
        total_completion += usage.get('completion_tokens', 0)
        results[stem] = {'status': status, 'classification': classification,
                         'generation_id': metadata['id'], 'returned_model': metadata['model'],
                         'returned_provider': metadata['provider'], 'finish_reason': metadata['finish_reason']}
    complete = sum(r['status'] == 'completed' for r in results.values())
    return {'status': 'passed', 'logical_calls_planned': len(EXPECTED),
            'logical_calls_completed': complete, 'all_scheduled_calls_completed': complete == len(EXPECTED),
            'http_attempts': len(ledger), 'reserved_usd': str(reserved),
            'returned_cost_sum_usd': str(reported_cost), 'attempts_with_returned_cost': costs_present,
            'attempts_without_returned_cost': len(ledger)-costs_present,
            'prompt_tokens_reported': total_prompt, 'completion_tokens_reported': total_completion,
            'returned_providers': dict(provider_names), 'returned_models': dict(model_names),
            'finish_reasons': dict(finish_reasons), 'calls': results, 'attempts': attempts,
            'returned_costs': raw_returned_costs, 'artifact_sha256': bindings,
            'limits': 'Independent saved-artifact check, not provider attestation or exact backend identity. '
                      'Unavailable calls differ from model-generated malformed JSON. Valid JSON can still violate the task schema. '
                      'Returned costs may omit failed/unknown attempt charges; reservations are not account-level limits.'}


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    report = audit(root)
    (root/'api-audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'logical_calls_completed', 'http_attempts',
                                          'reserved_usd', 'returned_cost_sum_usd')}, indent=2))
