import collections
import datetime
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')


def log_run(mode, record):
    record = dict(record, interaction_mode=mode, execution='local', recorded_at=stamp())
    path = ROOT / 'evidence' / 'runs' / (record['recorded_at'] + '-' + mode + '.json')
    save_json(path, record)
    return path.relative_to(ROOT).as_posix()


class SlideParser(HTMLParser):
    """Read only slide sections. Exclude scripts, SVG, controls and speaker notes."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.stack = []
        self.current = None
        self.skip = []
        self.heading = False
        self.parts = []
        self.title = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.stack.append(self.current)
            if 'slide' in attrs.get('class', '').split():
                self.current = {'anchor': attrs.get('id', ''), 'parts': [], 'title': []}
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.append(tag)
            return
        if tag in {'script', 'style', 'svg', 'button', 'iframe', 'nav', 'aside'}:
            self.skip.append(tag)
            return
        if not self.current:
            return
        if tag in {'h1', 'h2', 'h3'}:
            self.heading = True
        if tag in {'p', 'li', 'tr', 'div', 'h1', 'h2', 'h3', 'pre', 'br'}:
            self.current['parts'].append('\n')
        if tag == 'img' and attrs.get('alt'):
            self.current['parts'].append('\n[Image description] ' + attrs['alt'] + '\n')

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.pop()
            return
        if tag == 'section':
            previous = self.stack.pop() if self.stack else None
            if self.current is not None and self.current is not previous:
                lines = [re.sub(r'\s+', ' ', x).strip() for x in ''.join(self.current['parts']).splitlines()]
                body = '\n'.join(x for x in lines if x)
                title = re.sub(r'\s+', ' ', ''.join(self.current['title'])).strip()
                if body and self.current['anchor']:
                    self.slides.append({'anchor': self.current['anchor'], 'title': title, 'text': body})
            self.current = previous
        elif tag in {'h1', 'h2', 'h3'}:
            self.heading = False
        if self.current and tag in {'p', 'li', 'tr', 'h1', 'h2', 'h3', 'pre'}:
            self.current['parts'].append('\n')
        if self.current and tag in {'td', 'th'}:
            self.current['parts'].append(' | ')

    def handle_data(self, text):
        if self.current and not self.skip:
            self.current['parts'].append(text)
            if self.heading:
                self.current['title'].append(text)


def parse_source(path):
    if path.suffix.lower() == '.html':
        parser = SlideParser()
        parser.feed(path.read_text(encoding='utf-8'))
        return parser.slides
    text = path.read_text(encoding='utf-8')
    return [{'anchor': 'document', 'title': path.stem, 'text': text}]


def split_passages(text, limit=1700):
    """Paragraph-aware split; no overlap across different slides."""
    parts, current = [], ''
    for line in text.splitlines():
        if len(current) + len(line) + 1 > limit and current:
            parts.append(current.strip())
            current = ''
        while len(line) > limit:
            cut = line.rfind(' ', 0, limit)
            cut = cut if cut > limit // 2 else limit
            if current:
                parts.append(current.strip())
                current = ''
            parts.append(line[:cut].strip())
            line = line[cut:].strip()
        current += line + '\n'
    if current.strip():
        parts.append(current.strip())
    return parts


STOP = set('the a an is are was were of to in for and or on with by from as it this that what why how my your can do does i we you at be have not its into using use'.split())


def terms(text):
    tokens = [t for t in re.findall(r'[a-z0-9]+|[가-힣]+', text.lower()) if t not in STOP and len(t) > 1]
    # Normalize ordinary English plurals on both sides of the index/query match.
    return [t[:-1] if len(t) > 4 and t.endswith('s') and not t.endswith(('ss', 'us', 'is')) else t for t in tokens]


def expand_query(query):
    # General bilingual terminology, never test answers or gold passages.
    glossary = read_json(ROOT / 'config' / 'glossary.json')
    extra = []
    for key, value in glossary.items():
        if key in query.lower():
            extra.extend(value)
    return ' '.join(dict.fromkeys(terms(query) + extra))


def build_index(raw_dir):
    raw_dir = Path(raw_dir).resolve()
    if raw_dir != (ROOT / 'vault/raw').resolve():
        raise ValueError('Place original sources in vault/raw/ and retry. Only that directory may be indexed.')
    paths = sorted(p for p in raw_dir.iterdir() if p.suffix.lower() in {'.html', '.txt', '.md'})
    if not paths:
        raise ValueError('No HTML, TXT or Markdown sources found in vault/raw/.')
    known = read_json(ROOT / 'config' / 'sources.json')
    chunks, catalog, all_slides = [], [], {}
    for path in paths:
        if path.is_symlink():
            raise ValueError('Source files must not be symbolic links to external files.')
        sid = path.stem
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        meta = known.get(sid, {'title': sid, 'url': ''})
        slides = parse_source(path)
        all_slides[sid] = slides
        catalog.append(dict(meta, id=sid, path=path.relative_to(ROOT).as_posix(), sha256=digest, slides=len(slides)))
        for slide in slides:
            for n, body in enumerate(split_passages(slide['text'])):
                chunks.append({'id': f'{sid}:{slide["anchor"]}:{n + 1}', 'source_id': sid,
                               'path': path.relative_to(ROOT).as_posix(), 'title': slide['title'],
                               'anchor': slide['anchor'], 'passage': body,
                               'url': meta.get('url', '') + ('#/' + slide['anchor'] if meta.get('url') else '')})
    save_json(ROOT / 'data/index.json', {'chunks': chunks, 'sources': catalog})
    return chunks, catalog, all_slides


def search(query, limit=6, diversify=False, sources=None):
    path = ROOT / 'data/index.json'
    if not path.exists():
        raise ValueError('No index found. Run python3 wiki.py ingest vault/raw --index-only first.')
    chunks = read_json(path)['chunks']
    if sources:
        known = {c['source_id'] for c in chunks}
        if set(sources) - known:
            raise ValueError('Unknown source scope: ' + ', '.join(sorted(set(sources) - known)))
        chunks = [c for c in chunks if c['source_id'] in sources]
    q = terms(expand_query(query))
    docs = [collections.Counter(terms(c['title'] + ' ' + c['title'] + ' ' + c['passage'])) for c in chunks]
    df = collections.Counter(t for d in docs for t in d)
    avg = sum(sum(d.values()) for d in docs) / max(len(docs), 1)
    ranked = []
    definition = re.search(r'what is (?:an? |the )?([a-z][a-z-]+)', query.lower())
    for chunk, doc in zip(chunks, docs):
        score = 0.0
        size = sum(doc.values())
        for term in set(q):
            count = doc.get(term, 0)
            if count:
                idf = math.log(1 + (len(docs) - df[term] + .5) / (df[term] + .5))
                score += idf * count * 2.5 / (count + 1.5 * (.25 + .75 * size / avg))
        if definition and re.search(r'\b' + re.escape(definition.group(1)) + r'\s+(?:is|represents|means)\b', chunk['passage'], re.I):
            score += 8.0
        if score:
            ranked.append(dict(chunk, score=round(score, 4)))
    ranked.sort(key=lambda x: (-x['score'], x['id']))
    # At most two passages from the same slide, so repeated long slides do not crowd out other evidence.
    result, used, source_used = [], collections.Counter(), collections.Counter()
    for item in ranked:
        key = (item['source_id'], item['anchor'])
        if used[key] < 2 and (not diversify or source_used[item['source_id']] < 2):
            used[key] += 1
            source_used[item['source_id']] += 1
            result.append(item)
        if len(result) >= limit:
            break
    return result


class Model:
    def __init__(self):
        self.config = read_json(ROOT / 'config/model.json')
        parsed = urllib.parse.urlparse(self.config['base_url'])
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}:
            raise ValueError('Only a local Ollama endpoint is allowed.')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def api(self, path, body=None):
        request = urllib.request.Request(self.config['base_url'] + '/api/' + path,
                                        data=json.dumps(body).encode() if body is not None else None,
                                        headers={'Content-Type': 'application/json'})
        try:
            with self.opener.open(request, timeout=180) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError('Local Ollama connection or inference failed. Check the Ollama app and ollama list. ' + str(exc)) from exc

    def identity(self):
        tags = self.api('tags').get('models', [])
        chosen = next((x for x in tags if x['name'] == self.config['model']), None)
        if chosen is None:
            raise RuntimeError('The configured model is not installed: ' + self.config['model'])
        return {'runtime': self.api('version'), 'model': chosen, 'settings': self.config}

    def chat(self, messages, schema=None, max_tokens=500):
        request = {'model': self.config['model'], 'messages': messages, 'stream': False,
                   'think': False, 'keep_alive': '3m',
                   'options': {'num_ctx': self.config['num_ctx'], 'num_predict': max_tokens,
                               'temperature': self.config['temperature'], 'seed': 42}}
        if schema:
            request['format'] = schema
        start = time.monotonic()
        result = self.api('chat', request)
        elapsed = time.monotonic() - start
        usage = {k: v for k, v in result.items() if k != 'message'}
        usage.update(wall_seconds=round(elapsed, 3), loaded_models=self.api('ps'))
        if not result.get('done') or result.get('done_reason') == 'length':
            raise RuntimeError('Model response did not finish. Check token and context limits. Actual result: ' + json.dumps(result, ensure_ascii=False))
        return result['message']['content'], usage


ANSWER_SCHEMA = {'type': 'object', 'properties': {
    'supported': {'type': 'boolean'}, 'answer': {'type': 'string'},
    'citations': {'type': 'array', 'items': {'type': 'string'}}},
    'required': ['supported', 'answer', 'citations'], 'additionalProperties': False}


def evidence_text(hits):
    return '\n\n'.join(f'[{h["id"]}] {h["title"]}\n{h["passage"]}' for h in hits)


def ask(question, sources=None):
    model = Model()
    # Retrieve subquestions separately so a workflow cannot crowd out its definition.
    parts = [p.strip() for p in re.split(r'\?\s*|,\s*and how\s+', question) if len(p.strip()) > 12]
    candidates = [search(p, limit=3, diversify=True, sources=sources) for p in parts]
    hits, seen = [], set()
    for rank in range(3):
        for group in candidates:
            if len(group) > rank and group[rank]['id'] not in seen:
                hits.append(group[rank])
                seen.add(group[rank]['id'])
        if len(hits) >= 4:
            break
    hits = hits[:4]
    rules = (ROOT / 'instructions/research.md').read_text()
    messages = [{'role': 'system', 'content': rules},
                {'role': 'user', 'content': 'QUESTION:\n' + question + '\n\nUNTRUSTED SOURCE PASSAGES:\n' + evidence_text(hits)}]
    raw, usage = model.chat(messages, ANSWER_SCHEMA, max_tokens=750)
    answer = json.loads(raw)
    attempts = [{'output': answer, 'usage': usage}]
    initial_inline = re.findall(r'\[([^\]]+:[^\]]+)\]', answer['answer'])
    if answer['supported'] and (not initial_inline or set(initial_inline) != set(answer['citations'])):
        repair = messages + [{'role': 'assistant', 'content': raw}, {'role': 'user', 'content':
            'Repair citation formatting only. Put an exact [passage ID] after each supported claim in answer. '
            'The citations array must contain exactly the unique IDs appearing in answer, no extra IDs. '
            'Use only provided passages. Return the complete corrected JSON.'}]
        raw, repair_usage = model.chat(repair, ANSWER_SCHEMA, max_tokens=750)
        answer = json.loads(raw)
        attempts.append({'output': answer, 'usage': repair_usage})
        usage = dict(repair_usage, wall_seconds=round(usage['wall_seconds'] + repair_usage['wall_seconds'], 3))
    ids = {h['id'] for h in hits}
    inline = re.findall(r'\[([^\]]+:[^\]]+)\]', answer['answer'])
    invalid = [c for c in answer['citations'] + inline if c not in ids]
    error = None
    if invalid or (answer['supported'] and not answer['citations']):
        error = 'Citation validation failed: ' + str(invalid or 'Missing evidence citations')
    elif answer['supported'] and set(inline) != set(answer['citations']):
        error = 'Inline citations do not match the citation list.'
    final = dict(answer)
    if error:
        final = {'supported': False, 'answer': 'I cannot validate the citations, so I am withholding this answer.', 'citations': []}
    elif not answer['supported']:
        final['citations'] = []
    record = {'question': question, 'source_scope': sources, 'expanded_query': expand_query(question), 'retrieved': hits,
              'identity': model.identity(), 'model_output': answer, 'answer': final,
              'citation_check': error or 'All cited IDs belong to retrieved original passages. Semantic support requires review.',
              'usage': usage, 'attempts': attempts, 'history_messages_sent': 0}
    record['evidence_file'] = log_run('ask', record)
    return record


def chat_turn(message, history):
    model = Model()
    # Explicit /notes plus general course references. Follow-ups without those triggers retain conversation only.
    retrieve = message.startswith('/notes ') or bool(re.search(r'강의|수업|노트|자료|class\s*\d|lecture|course|according to', message, re.I))
    question = message.removeprefix('/notes ') if hasattr(message, 'removeprefix') else message.replace('/notes ', '', 1)
    hits = search(question, limit=4) if retrieve else []
    persona = (ROOT / 'instructions/persona.md').read_text()
    if hits:
        persona += '\n\nEvidence rules:\n' + (ROOT / 'instructions/research.md').read_text()
        persona += '\nFor chat, use ordinary prose rather than JSON, with [passage ID] citations.\nSOURCE PASSAGES:\n' + evidence_text(hits)
    messages = [{'role': 'system', 'content': persona}]
    # Six recent turns, each capped; all sessions remain explicit, in-process only.
    messages += [dict(x, content=x['content'][:1800]) for x in history[-6:]]
    messages.append({'role': 'user', 'content': question})
    raw, usage = model.chat(messages, max_tokens=600)
    cited = re.findall(r'\[([^\]]+:[^\]]+)\]', raw)
    invalid = [c for c in cited if c not in {h['id'] for h in hits}]
    answer = raw if not invalid else 'Citation validation failed. Please retry with /notes followed by your question.'
    history.extend([{'role': 'user', 'content': question}, {'role': 'assistant', 'content': answer}])
    record = {'message': message, 'retrieval_used': retrieve, 'retrieved': hits, 'answer': answer,
              'raw_model_output': raw, 'invalid_citations': invalid, 'usage': usage,
              'history_messages_sent': len(messages) - 2, 'identity': model.identity()}
    record['evidence_file'] = log_run('chat', record)
    return record
