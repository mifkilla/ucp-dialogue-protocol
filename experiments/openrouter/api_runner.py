"""Bounded OpenRouter transport for frozen UCP stress packets (stdlib only).

No reference answer is imported. This runner never changes Hermes or its environment.
Requests omit authorization from saved artifacts; response bodies are retained unless
they contain the credential, in which case only that credential is redacted.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'openai/gpt-4o'
RESERVATION = Decimal('0.40192')
BUDGET = Decimal('10.00')
MAX_ATTEMPTS = 24
TIMEOUT = 120
RETRY_STATUSES = {429, 502, 503, 504}
SESSIONS = tuple(f'{arm}{repeat}' for repeat in (1, 2) for arm in ('S', 'O', 'K', 'M'))
STAGES = {'initial': ('initial-1', 'initial-2'),
          'observer': ('observer-1', 'observer-2'),
          'plans': tuple(f'{sid}-plan' for sid in SESSIONS),
          'reports': tuple(f'{sid}-report' for sid in SESSIONS)}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value, *, raw=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if raw else (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as handle:
        handle.write(data)


def load_key(env_file):
    matches = []
    for line in Path(env_file).read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if line.startswith('export '):
            line = line[7:].lstrip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        name, value = line.split('=', 1)
        if name.strip() != 'OPENROUTER_API_KEY':
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        matches.append(value)
    if len(matches) != 1 or not matches[0]:
        raise ValueError('Expected exactly one nonempty OPENROUTER_API_KEY entry')
    return matches[0]


@contextmanager
def run_lock(root):
    path = Path(root) / 'api' / 'runner.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as handle:
            handle.write(now() + '\n')
    except FileExistsError:
        raise RuntimeError('Run already locked; inspect unfinished calls before any manual recovery') from None
    try:
        yield
    finally:
        path.unlink()


def ledger_rows(root):
    path = Path(root) / 'api' / 'ledger.jsonl'
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def reserve(root, stem, attempt, request_hash):
    rows = ledger_rows(root)
    reserved = sum((Decimal(row['reserved_usd']) for row in rows), Decimal('0'))
    if len(rows) >= MAX_ATTEMPTS or reserved + RESERVATION > BUDGET:
        raise RuntimeError('Fixed request or reserved-cost budget exhausted')
    row = {'utc': now(), 'stem': stem, 'attempt': attempt,
           'reserved_usd': str(RESERVATION), 'request_sha256': request_hash,
           'reservation_basis': '128000 input tokens at $2.50/M plus 8192 output tokens at $10/M'}
    path = Path(root) / 'api' / 'ledger.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(row, sort_keys=True) + '\n')
        handle.flush()
    return row


def packet_messages(packet):
    return [{'role': 'system', 'content': packet['instructions']},
            {'role': 'user', 'content': json.dumps({k: v for k, v in packet.items() if k != 'instructions'},
                                                   ensure_ascii=False)}]


def request_body(root, stem):
    root = Path(root)
    packet = read_json(root / 'packets' / f'{stem}.json')
    if stem.endswith('-report'):
        prior = stem[:-7] + '-plan'
        plan_packet = read_json(root / 'packets' / f'{prior}.json')
        prior_summary = read_json(root / 'api' / prior / 'summary.json')
        messages = packet_messages(plan_packet)
        # Even a malformed model answer is retained verbatim in subsequent context.
        content_path = root / 'api' / prior / 'content.txt'
        content = content_path.read_text(encoding='utf-8') if content_path.exists() else ''
        if prior_summary['status'] == 'completed':
            messages.append({'role': 'assistant', 'content': content})
        messages.append({'role': 'user', 'content': json.dumps(packet, ensure_ascii=False)})
    else:
        messages = packet_messages(packet)
    repeat = int(stem.split('-')[1]) if stem.startswith(('initial-', 'observer-')) else int(stem[1])
    return {'model': MODEL, 'provider': {'only': ['OpenAI'], 'allow_fallbacks': False,
                                        'require_parameters': True},
            'messages': messages, 'transforms': [], 'temperature': 0.2, 'top_p': 1.0,
            'max_tokens': 8192, 'seed': 6100 + repeat,
            'response_format': {'type': 'json_object'}}


def transport(body, key):
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + key,
                                              'User-Agent': 'UCP-bounded-research/1.0'})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.status, response.read()


def sanitized(raw, key):
    encoded = key.encode('utf-8')
    found = bool(encoded) and encoded in raw
    return (raw.replace(encoded, b'[REDACTED_CREDENTIAL]') if found else raw), found


def finalize(root, stem, status, parsed, *, metadata=None, issue=None):
    root = Path(root)
    destination = root / 'responses' / f'{stem}.json'
    write_new(destination, parsed)
    summary = {'stem': stem, 'utc': now(), 'status': status, 'issue': issue,
               'response_sha256': digest(destination), 'metadata': metadata or {}}
    write_new(root / 'api' / stem / 'summary.json', summary)
    fatal = status == 'api_envelope_error' or (status == 'http_error' and
                                               summary['metadata'].get('http_status') not in RETRY_STATUSES)
    if fatal:
        write_new(root / 'api' / 'stop.json', {'utc': now(), 'stem': stem, 'status': status,
                                             'reason': 'Nonretryable API failure; no new requests permitted'})
    return summary


def run_one(root, stem, key, *, send=transport, sleep=time.sleep):
    root = Path(root)
    folder = root / 'api' / stem
    summary_path = folder / 'summary.json'
    if summary_path.exists():
        summary = read_json(summary_path)
        if digest(root / 'responses' / f'{stem}.json') != summary['response_sha256']:
            raise RuntimeError('Saved parsed response changed')
        return summary
    if (root / 'api' / 'stop.json').exists():
        raise RuntimeError('Run stopped by a prior nonretryable API failure')
    # Any partial invocation is never automatically replayed, even if it may have
    # failed before the network call. This protects against unknown execution.
    if folder.exists() and any(folder.iterdir()):
        raise RuntimeError('Unfinished invocation exists; no automatic replay')
    body = request_body(root, stem)
    folder.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        prefix = folder / f'attempt-{attempt:02d}'
        request_path = prefix.with_suffix('.request.json')
        write_new(request_path, body)
        reserve(root, stem, attempt, digest(request_path))
        write_new(prefix.with_suffix('.started.json'), {'utc': now(), 'attempt': attempt})
        status = None
        try:
            status, raw = send(body, key)
        except urllib.error.HTTPError as exc:
            try:
                status, raw = exc.code, exc.read()
            finally:
                exc.close()
        except Exception as exc:
            # Error text and headers are deliberately not serialized: they can
            # contain credentials or local paths. The request remains reserved.
            failure = {'utc': now(), 'kind': 'transport_unknown', 'exception_type': type(exc).__name__}
            write_new(prefix.with_suffix('.result.json'), failure)
            return finalize(root, stem, 'transport_unknown', {}, issue='Uncertain transport outcome; no retry')
        raw, redacted = sanitized(raw, key)
        write_new(prefix.with_suffix('.response.txt'), raw, raw=True)
        write_new(prefix.with_suffix('.result.json'), {'utc': now(), 'http_status': status,
                                                      'credential_redacted': redacted})
        if status in RETRY_STATUSES and attempt == 1:
            sleep(2)
            continue
        if status != 200:
            return finalize(root, stem, 'http_error', {}, metadata={'http_status': status},
                            issue='HTTP failure; content was not resampled')
        try:
            obj = json.loads(raw)
            choice = obj['choices'][0]
            content = choice['message']['content']
            if not isinstance(content, str):
                raise ValueError('Nontext completion')
        except (ValueError, KeyError, IndexError, TypeError):
            return finalize(root, stem, 'api_envelope_error', {}, issue='Missing textual completion in API response')
        write_new(folder / 'content.txt', content.encode('utf-8'), raw=True)
        issue = None
        try:
            parsed = json.loads(content)
        except ValueError:
            parsed = {}
            issue = 'Malformed JSON completion retained without format retry'
        metadata = {k: obj.get(k) for k in ('id', 'model', 'provider', 'created', 'system_fingerprint', 'usage')}
        metadata['finish_reason'] = choice.get('finish_reason')
        metadata['native_finish_reason'] = choice.get('native_finish_reason')
        metadata['credential_redacted'] = redacted
        return finalize(root, stem, 'completed', parsed, metadata=metadata, issue=issue)
    raise AssertionError('Unreachable attempt loop')


def run_stage(root, stage, env_file):
    key = load_key(env_file)
    with run_lock(root):
        summaries = []
        for stem in STAGES[stage]:
            summary = run_one(root, stem, key)
            summaries.append(summary)
            # Console output never contains generated text, prompts, keys or
            # API error bodies; every substantive result remains in the run.
            print(json.dumps({'stem': stem, 'status': summary['status'], 'issue': summary['issue'],
                              'usage': summary['metadata'].get('usage')}), flush=True)
            if (Path(root) / 'api' / 'stop.json').exists():
                raise RuntimeError('Run stopped by a nonretryable API failure; see saved status')
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('stage', choices=tuple(STAGES))
    parser.add_argument('--env-file', required=True, type=Path)
    args = parser.parse_args()
    run_stage(args.run, args.stage, args.env_file)


if __name__ == '__main__':
    main()
