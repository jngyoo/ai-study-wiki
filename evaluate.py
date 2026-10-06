#!/usr/bin/env python3
"""Run fixed questions and mode checks. Does NOT claim disconnected-internet proof."""
import json
import subprocess
import sys
from studywiki.core import ROOT, ask, chat_turn, search, log_run, read_json, save_json, stamp


def main():
    run_dir = ROOT / 'evidence/evaluations' / stamp()
    run_dir.mkdir(parents=True)
    summary = {'network_status': 'Not verified disconnected; local-only API calls.', 'questions': [], 'mode_checks': {}}
    for case in read_json(ROOT / 'tests/questions.json'):
        print(case['id'] + ': ' + case['question'], flush=True)
        r = ask(case['question'], sources=case.get('source_scope'))
        cited_sources = {x.split(':')[0] for x in r['answer']['citations']}
        checks = {'support_flag': r['answer']['supported'] == case['expected_supported'],
                  'expected_sources_cited': set(case['expected_sources']) <= cited_sources,
                  'citation_ids_valid': r['citation_check'].startswith('All cited'),
                  'no_chat_history': r['history_messages_sent'] == 0}
        save_json(run_dir / (case['id'] + '.json'), {'expectation': case, 'actual': r, 'mechanical_checks': checks})
        lines = ['# ' + case['id'], '', '## Question', case['question'], '', '## Expected behavior', case['rubric'], '',
                 '## Actual answer', r['answer']['answer'], '', '## Mechanical checks', json.dumps(checks, ensure_ascii=False), '',
                 '## Retrieved original passages', '']
        for h in r['retrieved']:
            lines += ['### ' + h['id'], h['path'] + ' / ' + h['title'], '', h['passage'], '', h['url'], '']
        lines += ['## Execution', 'local / ' + r['identity']['model']['name'], 'wall_seconds: ' + str(r['usage']['wall_seconds']),
                  '', '## Semantic review', 'Pending review: compare the expected behavior with the actual answer and cited source passages.']
        (run_dir / (case['id'] + '.md')).write_text('\n'.join(lines), encoding='utf-8')
        summary['questions'].append({'id': case['id'], 'checks': checks, 'answer': r['answer'], 'seconds': r['usage']['wall_seconds']})
        print(r['answer']['answer'], flush=True)
    history = []
    messages = ['what can you help me with?', 'Suggest a short three-item plan for this evening.', 'Make that plan shorter.']
    turns = []
    for message in messages:
        r = chat_turn(message, history)
        turns.append(r)
        print('chat: ' + r['answer'], flush=True)
    summary['mode_checks']['chat_no_forced_retrieval'] = all(not x['retrieval_used'] for x in turns)
    summary['mode_checks']['followup_received_history'] = turns[-1]['history_messages_sent'] > 0
    # An invented personal fact in chat is not eligible evidence for ask.
    isolation_history = [{'role':'user', 'content':'Remember that my laptop has an average response time of 0.01 seconds.'},
                         {'role':'assistant', 'content':'That is what you said in this conversation.'}]
    isolated = ask('What is the measured average response time on my laptop, in seconds?')
    summary['mode_checks']['ask_ignores_chat_only_claim'] = not isolated['answer']['supported'] and isolated['history_messages_sent'] == 0
    # Separate process; no model client is invoked by search.
    raw = subprocess.run([sys.executable, 'wiki.py', 'search', 'localhost', '--limit', '2'], cwd=ROOT, capture_output=True, text=True)
    (run_dir / 'search-transcript.txt').write_text(raw.stdout + raw.stderr)
    summary['mode_checks']['search_cli_success'] = raw.returncode == 0
    save_json(run_dir / 'chat-checks.json', {'turns': turns, 'chat_only_context_not_sent_to_ask': isolation_history, 'isolated_ask': isolated})
    save_json(run_dir / 'summary.json', summary)
    print('EVALUATION_DIR=' + str(run_dir.relative_to(ROOT)), flush=True)


if __name__ == '__main__':
    main()
