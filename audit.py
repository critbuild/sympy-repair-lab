"""Verify frozen evaluators, prompts, session identity, and final-message provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from common import HERE, frozen_hashes, save


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(batch='primary'):
    directory = HERE/'results'/batch
    protocol = json.loads((directory/'PROTOCOL.json').read_text(encoding='utf-8'))
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    check('evaluators_match_frozen_protocol', frozen_hashes() == protocol['frozen_hashes'])
    preflight = json.loads((HERE/'validation/PREFLIGHT.json').read_text(encoding='utf-8'))
    for name, digest in preflight['input_asset_hashes'].items():
        check('preflight_asset:'+name, sha(HERE/name) == digest)
    discovery = HERE/'prior_evidence/trials/screen-b__13091-gpt-6-astra-1/changed'
    for path in (HERE/'assets/geometry-seed').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            relative = path.relative_to(HERE/'assets/geometry-seed')
            check('recorded_seed:'+relative.as_posix(), path.read_bytes() == (discovery/relative).read_bytes())
    ids = []
    records = []
    normalized_prompts = {}
    for artifact in sorted(directory.iterdir()):
        if not (artifact/'result.json').is_file():
            continue
        result = json.loads((artifact/'result.json').read_text(encoding='utf-8'))
        settings = json.loads((artifact/'settings.json').read_text(encoding='utf-8'))
        records.append(result)
        events = [json.loads(line) for line in (artifact/'events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        session_ids = [e['thread_id'] for e in events if e.get('type') == 'thread.started']
        ids.extend(session_ids)
        items = [e.get('item', {}) for e in events if e.get('type') == 'item.completed']
        messages = [i.get('text', '') for i in items if i.get('type') == 'agent_message']
        prefix = artifact.name + ':'
        command = settings['command']
        checkout = command[command.index('-C')+1]
        prompt_text = (artifact/'prompt.txt').read_text(encoding='utf-8')
        normalized = prompt_text.replace(checkout, '<CHECKOUT>').replace(checkout.replace('\\', '/'), '<CHECKOUT>')
        normalized_prompts.setdefault(result['case'], set()).add(normalized)
        check(prefix+'unique_session_recorded', len(session_ids) == 1 and result['thread_ids'] == session_ids)
        check(prefix+'prompt_digest', sha(artifact/'prompt.txt') == settings.get('distributed_prompt_sha256', settings['prompt_sha256']))
        check(prefix+'frozen_source', settings['source_hashes'] == protocol['frozen_hashes'])
        check(prefix+'actual_tools', any(i.get('type') == 'command_execution' and i.get('exit_code') == 0 for i in items))
        check(prefix+'final_from_transcript', bool(messages) and messages[-1] == (artifact/'final.txt').read_text(encoding='utf-8'))
        check(prefix+'grade_matches', json.loads((artifact/'checks/grade.json').read_text(encoding='utf-8')) == result['checks'])
    planned = {(case, model, repeat) for case in protocol['cases'] for model in protocol['models'] for repeat in range(1, protocol['repeats']+1)}
    observed = [(r['case'], r['model'], r['repeat']) for r in records]
    check('all_planned_trials_present_once', set(observed) == planned and len(observed) == len(planned))
    check('all_session_ids_distinct', len(ids) == len(set(ids)) == len(records))
    for case, prompts in normalized_prompts.items():
        check('same_prompt_except_checkout:'+case, len(prompts) == 1)
    manifest_path = HERE/'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for name, digest in manifest['files'].items():
            path = HERE/name
            check('manifest:'+name, path.is_file() and sha(path) == digest)
    return {'all_pass': all(c['passed'] for c in checks), 'trial_count': len(records),
            'check_count': len(checks), 'checks': checks}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', default='primary')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    result = audit(args.batch)
    if args.output:
        save(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, indent=2))
    for check in result['checks']:
        if not check['passed']:
            print('FAILED', check['name'])
    sys.exit(0 if result['all_pass'] else 1)
