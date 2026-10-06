"""Interactive entry point for trying the existing CLI commands."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print('\nAI Study Wiki | Local Gemma\n')
    print('Try: What is an embedding, and how does RAG use it?')
    while True:
        print('\n1. Ask a course question (with citations)\n2. Chat (follow-ups supported)\n3. Search original lectures\n4. Exit')
        choice = input('\nChoose 1–4: ').strip()
        if choice == '4':
            return
        if choice == '2':
            subprocess.run([sys.executable, str(ROOT / 'wiki.py'), 'chat'], cwd=ROOT)
        elif choice in ('1', '3'):
            question = input('Question: ' if choice == '1' else 'Search: ').strip()
            if question:
                print('\nWorking locally…\n', flush=True)
                subprocess.run([sys.executable, str(ROOT / 'wiki.py'), 'ask' if choice == '1' else 'search', question], cwd=ROOT)
        else:
            print('Please choose 1, 2, 3, or 4.')

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nGoodbye.')
