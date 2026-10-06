import argparse
import json
import sys
from .core import ROOT, ask, chat_turn, search, expand_query, log_run, Model
from .ingest import ingest


def print_answer(record):
    print(record['answer']['answer'])
    citations = set(record['answer']['citations'])
    for h in record['retrieved']:
        if h['id'] in citations:
            print(f'  [{h["id"]}] {h["path"]} / {h["title"]}\n  {h["url"]}')
    print('Evidence: ' + record['evidence_file'])


def main():
    parser = argparse.ArgumentParser(description='AI Study Wiki — local Gemma + original-source retrieval. No cloud fallback.',
                                     epilog='Config: config/model.json. Sources: vault/raw. Logs: evidence/runs. Requires Python 3.9+, Ollama and gemma4:e2b.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('help', help='Show usage')
    sub.add_parser('doctor', help='Inspect local model and settings')
    p = sub.add_parser('ingest', help='Index original sources and generate wiki notes with Gemma')
    p.add_argument('path', nargs='?', default=str(ROOT / 'vault/raw'))
    p.add_argument('--index-only', action='store_true', help='Rebuild the source index without calling the model')
    p.add_argument('--force', action='store_true', help='Regenerate unchanged sources too; overwrites manual edits to generated notes')
    p.add_argument('--only-source', help='Generate notes for one source ID while rebuilding the full original-source index')
    p = sub.add_parser('search', help='Search original passages without a model call')
    p.add_argument('query')
    p.add_argument('--limit', type=int, choices=range(1, 11), default=6)
    p = sub.add_parser('ask', help='Ask a standalone factual question without chat history')
    p.add_argument('question')
    p.add_argument('--mode', choices=['local'], default='local')
    p.add_argument('--sources', nargs='+', help='Optional source IDs to search, e.g. class2')
    p = sub.add_parser('chat', help='Interactive assistant; use /notes question, /reset or /exit')
    p.add_argument('--message', help='One-off message; otherwise start an interactive session')
    args = parser.parse_args()
    try:
        if args.command == 'help':
            parser.print_help()
        elif args.command == 'doctor':
            print(json.dumps(Model().identity(), ensure_ascii=False, indent=2))
        elif args.command == 'ingest':
            r = ingest(args.path, args.index_only, args.force, args.only_source)
            print(f'Sources: {len(r["sources"])} sources, {r["chunk_count"]} passages. Evidence: {r["evidence_file"]}')
        elif args.command == 'search':
            hits = search(args.query, args.limit)
            for h in hits:
                print(f'[{h["id"]}] {h["path"]} / {h["title"]}\n{h["passage"]}\n{h["url"]}\n')
            if not hits:
                print('No matching source passages.')
            print('Evidence: ' + log_run('search', {'query': args.query, 'expanded_query': expand_query(args.query), 'retrieved': hits, 'model_called': False}))
        elif args.command == 'ask':
            print('ask · local · ' + Model().config['model'])
            print_answer(ask(args.question, sources=args.sources))
        elif args.command == 'chat':
            print('chat · local · ' + Model().config['model'] + ' | /notes question · /reset · /exit')
            history = []
            while True:
                try:
                    message = args.message or input('You> ').strip()
                except EOFError:
                    break
                if message == '/exit':
                    break
                if message == '/reset':
                    history.clear()
                    print('Conversation history cleared.')
                    continue
                if not message:
                    continue
                r = chat_turn(message, history)
                print('Buddy> ' + r['answer'])
                print('Evidence: ' + r['evidence_file'])
                if args.message:
                    break
    except (RuntimeError, ValueError, OSError, KeyError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        log_run('error', {'command': args.command, 'error': str(exc)})
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nInterrupted. Completed records are preserved.', file=sys.stderr)
        sys.exit(130)
