import subprocess
import sys
import unittest
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / 'wiki.py'


class ChatCommands(unittest.TestCase):
    def run_chat(self, *args, stdin=''):
        return subprocess.run([sys.executable, str(CLI), 'chat', *args],
                              input=stdin, text=True, capture_output=True, timeout=3, check=True).stdout

    def test_one_shot_reset_exits_after_one_acknowledgement(self):
        self.assertEqual(self.run_chat('--message', '/reset').count('Conversation history cleared.'), 1)

    def test_empty_one_shot_does_not_prompt(self):
        self.assertNotIn('You>', self.run_chat('--message', ''))

    def test_interactive_reset_continues_until_exit(self):
        self.assertEqual(self.run_chat(stdin='/reset\n/reset\n/exit\n').count('Conversation history cleared.'), 2)
