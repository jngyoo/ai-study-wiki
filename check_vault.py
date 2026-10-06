#!/usr/bin/env python3
"""Check human-readable note paths, heading targets and links. No model calls."""
import re
from collections import defaultdict
from studywiki.core import ROOT, save_json


def check():
    vault = ROOT / 'vault'
    by_name = defaultdict(list)
    for p in vault.rglob('*.md'):
        by_name[p.stem].append(p)
    errors = []
    notes = sorted((vault / 'wiki').rglob('*.md'))
    links = 0
    for p in [vault / 'index.md'] + notes:
        text = p.read_text()
        if p in notes and ('# ' + p.stem + '\n') not in text:
            errors.append('Missing matching heading: ' + str(p))
        for target in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', text):
            links += 1
            file, _, heading = target.partition('#')
            matches = [vault / (file + '.md')] if '/' in file else by_name[file]
            if len(matches) != 1 or not matches[0].exists():
                errors.append('Missing/ambiguous link: ' + target)
            elif heading and not any(x.lstrip('# ').strip() == heading for x in matches[0].read_text().splitlines() if x.startswith('#')):
                errors.append('Missing heading: ' + target)
    result = {'notes': len(notes), 'links_checked': links, 'errors': errors}
    save_json(ROOT / 'evidence/vault-check.json', result)
    print(result)
    return result


if __name__ == '__main__':
    raise SystemExit(bool(check()['errors']))
