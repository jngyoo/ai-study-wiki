#!/bin/zsh
cd -- "${0:A:h}"
if ! /usr/bin/curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  /usr/local/bin/ollama serve > /tmp/ai-study-wiki-ollama.log 2>&1 &
  for attempt in {1..20}; do
    /usr/bin/curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi
python3 try_wiki.py
