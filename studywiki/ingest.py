import hashlib
import json
import time
from pathlib import Path
from .core import ROOT, Model, build_index, read_json, save_json, log_run

SCHEMA = {'type': 'object', 'properties': {'summary': {'type': 'string'},
          'details': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 2, 'maxItems': 4}},
          'required': ['summary', 'details'], 'additionalProperties': False}


def ingest(raw_dir, index_only=False, force=False, only_source=None):
    start = time.monotonic()
    chunks, catalog, slides = build_index(raw_dir)
    sources_dir = ROOT / 'vault/Sources'
    sources_dir.mkdir(parents=True, exist_ok=True)
    for source in catalog:
        lines = ['# ' + source['title'], '', 'Slide text extracted from the original HTML; not a generated summary.',
                 'Includes image alt text when available; excludes external images, interactive demos and speaker notes.',
                 '', f'[Original HTML](../raw/{Path(source["path"]).name}) · [Online slides]({source["url"]})', '']
        for slide in slides[source['id']]:
            lines += ['## ' + slide['title'], '', slide['text'], '']
        (sources_dir / (source['id'] + '.md')).write_text('\n'.join(lines), encoding='utf-8')
    (ROOT / 'vault/Source Catalog.md').write_text('# Source Catalog\n\n' + '\n\n'.join(
        f'## {s["title"]}\n\n- [Original](raw/{Path(s["path"]).name})\n- [[Sources/{s["id"]}|Readable source text]]\n- [Source website]({s["url"]})\n- SHA-256: `{s["sha256"]}`\n- Slide count: {s["slides"]}' for s in catalog), encoding='utf-8')
    if index_only:
        record = {'index_only': True, 'sources': catalog, 'chunk_count': len(chunks), 'wall_seconds': time.monotonic() - start}
        record['evidence_file'] = log_run('ingest', record)
        return record
    model = Model()
    identity = model.identity()
    plans = read_json(ROOT / 'config/topics.json')
    manifest_path = ROOT / 'data/notes-manifest.json'
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    # User-added text sources get one readable note. Existing course plans remain stable.
    known = {p['source'] for p in plans}
    for source in catalog:
        if source['id'] not in known:
            name = source['id'].replace('_', ' ').replace('-', ' ').strip()
            plans.append({'title': name, 'folder': 'Additional Notes', 'source': source['id'],
                          'sections': [x['anchor'] for x in slides[source['id']]], 'related': {}})
    names = [p['title'] for p in plans]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate note names. Use distinct descriptive names in config/topics.json.')
    completed = []
    instruction = (ROOT / 'instructions/ingestion.md').read_text()
    for plan in plans:
        if only_source and plan['source'] != only_source:
            continue
        available = {s['anchor']: s for s in slides.get(plan['source'], [])}
        missing = set(plan['sections']) - available.keys()
        if missing:
            raise ValueError('Missing source slides for note: ' + str(missing))
        selected = [available[a] for a in plan['sections']]
        source_text = '\n\n'.join(s['title'] + '\n' + s['text'] for s in selected)
        if len(source_text) > 14000:
            raise ValueError('Note input is too long. Split the topic in topics.json: ' + plan['title'])
        note_path = ROOT / 'vault/wiki' / plan['folder'] / (plan['title'] + '.md')
        key = plan['source'] + ':' + plan['title']
        fingerprint = hashlib.sha256((source_text + json.dumps(plan, sort_keys=True) + instruction +
                                      json.dumps(model.config, sort_keys=True) + identity['model']['digest']).encode()).hexdigest()
        if not force and manifest.get(key, {}).get('fingerprint') == fingerprint and note_path.exists():
            print('Unchanged: ' + plan['title'], flush=True)
            completed.append({'title': plan['title'], 'status': 'unchanged'})
            continue
        print('Generating with Gemma: ' + plan['title'], flush=True)
        raw, usage = model.chat([{'role': 'system', 'content': instruction},
                                {'role': 'user', 'content': 'Topic: ' + plan['title'] + '\nSOURCE:\n' + source_text + '\n\nWrite an English summary and key points grounded only in the source above. Use English for every summary and details value.'}], SCHEMA, max_tokens=650)
        generated = json.loads(raw)
        lines = ['---', 'source_id: ' + plan['source'], 'model: ' + model.config['model'],
                 'review_status: pending', '---', '', '# ' + plan['title'], '', generated['summary'], '', '## Key points', '']
        lines += ['- ' + x for x in generated['details']]
        lines += ['', '## Sources', '']
        for s in selected:
            lines.append('- [[Sources/' + plan['source'] + '#' + s['title'] + '|' + s['title'] + ']]')
        lines += ['', '## Related notes', '']
        lines += ['- [[' + name + ']] — ' + reason for name, reason in plan['related'].items()]
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        manifest[key] = {'fingerprint': fingerprint, 'path': note_path.relative_to(ROOT).as_posix()}
        save_json(manifest_path, manifest)
        completed.append({'title': plan['title'], 'status': 'generated', 'raw_model_output': generated, 'usage': usage,
                          'sources': [s['anchor'] for s in selected]})
    lines = ['# AI Study Wiki', '', 'A personal study wiki for Classes 1–5. Check summaries against the original sources.', '',
             '[[Source Catalog|Source catalog]] · Read extracted slide text in the Sources folder.', '']
    for folder in dict.fromkeys(p['folder'] for p in plans):
        lines += ['## ' + folder, '']
        lines += ['- [[' + p['title'] + ']] — ' + p['source'].replace('class', 'Class ') for p in plans if p['folder'] == folder]
        lines += ['']
    (ROOT / 'vault/index.md').write_text('\n'.join(lines), encoding='utf-8')
    record = {'index_only': False, 'forced': force, 'only_source': only_source, 'sources': catalog, 'chunk_count': len(chunks),
              'notes': completed, 'identity': identity, 'wall_seconds': round(time.monotonic() - start, 3)}
    record['evidence_file'] = log_run('ingest', record)
    return record
