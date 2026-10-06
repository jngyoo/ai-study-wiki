# AI Study Wiki

A personal study assistant for Classes 1–5 of **From Zero to AI Agents**. It preserves five original lecture files, generates ten linked English study notes with local Gemma, and provides a command-line interface for conversation, factual questions, and original-source search.

## Project status

The local application and English submission materials are implemented. Actual English model outputs are saved in `evidence/`. **Citation fixes, the disconnected-internet demonstration, and Obsidian screenshots are complete.** See [English verification](evidence/ENGLISH-VERIFICATION.md), [offline evidence](OFFLINE-DEMO.md), and [Obsidian screenshots](evidence/obsidian/README.md).

## Quick start

Use Python 3.9 or later and [Ollama](https://ollama.com/download). The application uses only the Python standard library; no Python packages or hosted embeddings are required. On another computer, download the model before disconnecting:

```sh
ollama pull gemma4:e2b
```

The tested machine already has this model. Open the Ollama app, open a terminal in this project folder, and run:

```sh
python3 wiki.py --help
python3 wiki.py doctor
python3 wiki.py ingest vault/raw
python3 wiki.py search "localhost"
python3 wiki.py ask "Why can my friend not open my localhost link?" --mode local
python3 wiki.py chat
```

In chat, try `What can you help me with?`, ask for a short plan, and then say `Make that shorter.` Use `/notes <question>` for explicit retrieval, `/reset` to clear conversation, and `/exit` to quit.

```sh
python3 evaluate.py
python3 check_vault.py
python3 -m unittest discover -s tests -v
```

Missing files, unavailable models, and invalid citations produce explicit errors. Settings are in [`config/model.json`](config/model.json). The application accepts only a loopback Ollama endpoint and has no cloud fallback.

## Purpose and original sources

The wiki supports review of programming, software systems, machine learning, embeddings, attention, context, and retrieval. Each source is a local copy of one lecture:

| Source | Subject |
|---|---|
| [Class 1](https://haas-ai-classes-fall-26.vercel.app/class1.html) | Code and programming foundations |
| [Class 2](https://haas-ai-classes-fall-26.vercel.app/class2.html) | Software systems and deployment |
| [Class 3](https://haas-ai-classes-fall-26.vercel.app/class3.html) | Machine learning foundations |
| [Class 4](https://haas-ai-classes-fall-26.vercel.app/class4.html) | Deep learning, embeddings, and transformers |
| [Class 5](https://haas-ai-classes-fall-26.vercel.app/class5.html) | LLM behavior, prompting, and retrieval |

See the [source catalog](vault/Source%20Catalog.md) for original paths and SHA-256 hashes. Original HTML remains unchanged in `vault/raw/`. `vault/Sources/` contains readable extracted slide text, and `vault/wiki/` contains generated summaries. Extraction includes text and available image alt text but excludes scripts, speaker notes, and interactive controls. External images and videos were not downloaded; the original slide websites are not fully reproduced offline.

## Modes and harness

| Command | Behavior |
|---|---|
| `ingest` | Parse originals, rebuild the local index, call Gemma to generate linked notes, and update the topic index. |
| `search` | Return matching original passages and locations without a model call. |
| `ask` | Retrieve evidence for an independent factual question; return citations or acknowledge missing evidence. Chat history and personality are excluded. |
| `chat` | Brainstorm, draft, plan, and respond to follow-ups. Retrieve only when course-related terms or `/notes` trigger it. |
| `help` | Explain usage and configuration. |

[`wiki.py`](wiki.py) starts the CLI; [`studywiki/cli.py`](studywiki/cli.py) selects a command. [`studywiki/core.py`](studywiki/core.py) manages retrieval, model calls, conversation, citation checks, errors, and output logging. [`studywiki/ingest.py`](studywiki/ingest.py) organizes sources into wiki notes. This connecting application code is the **harness**. Gemma is the text generator; it does not automatically read files or operate tools.

A factual question follows this path: CLI → query terms → local BM25 search → up to four original passages combined from subquestions and research instructions → local Gemma → citation validation → displayed answer and saved record. This is the **RAG workflow**. Retrieval adds context at inference time and does not retrain the model.

## Design choices

- **Passages:** split at slide and paragraph boundaries, with a maximum of 1,700 characters. Source path, slide title, anchor, and passage ID stay attached.
- **Retrieval:** BM25 keyword search, with general bilingual terminology expansion available. English is the submission language. Plural normalization, terminology expansion, definition matching, and subquestion retrieval improve coverage. The answer key and generated answers are never indexed. `ask --sources class2` explicitly scopes retrieval; Q1 uses this visible scope because the evaluation requires Class 2 despite overlapping Class 1 material.
- **Context:** an 8,192-token model context; ask retrieves up to three passages per subquestion with a two-per-source cap in each search, then combines up to four passages, and chat retains at most six recent messages capped at 1,800 characters each. Long sessions are intentionally bounded.
- **Instructions:** [`research.md`](instructions/research.md) separates factual evidence rules from [`persona.md`](instructions/persona.md), the friendly AI-course study assistant persona. [`ingestion.md`](instructions/ingestion.md) guides summaries.
- **Citations:** the harness verifies that cited IDs belong to retrieved originals and that inline citations match the citation list. One bounded format-repair call is allowed and both outputs are logged. This is a structural check, not an automatic proof of semantic correctness.
- **Wiki organization:** short subject-based filenames with matching headings, three topic folders, a grouped [index](vault/index.md), and explicit meaningful links in [`topics.json`](config/topics.json). Machine IDs remain in metadata and the external index.
- **Re-ingestion:** source content, model digest, settings, instructions, and topic plan form a fingerprint. Unchanged notes are retained; changed notes update the same path. `--force` regenerates notes and overwrites manual edits, so back up reviewed notes first.

## Device and model

Tested on a MacBook Air, Apple M4, 10 CPU cores, 8 GPU cores, 16 GB unified memory, macOS 15.5. Initial free disk space was approximately 28 GiB. See [`evidence/device.json`](evidence/device.json).

Runtime: **Ollama 0.34.3**. Model: **`gemma4:e2b`**, **Q4_K_M**. Exact digest: `7fbdbf8f5e45a75bb122155ed546e765b4d9c53a1285f62fd9f506baa1c5a47e`. [Official Ollama model listing](https://ollama.com/library/gemma4). Model weights are not included in this project.

The existing small quantized model successfully ran on this device, avoiding another large download. The E2B name differs from Ollama's total-parameter display of 5.1B; neither name alone establishes the runtime memory footprint. The harness uses temperature 0.2, seed 42, thinking disabled, and a bounded context. The seed is not a guarantee of identical output across runtime versions.

Actual ingestion and answer durations, model identity, and `/api/ps` memory snapshots are saved with each run. Model allocation snapshots are not whole-system peak memory measurements. Available memory changes as other applications run.

## Evaluation and evidence

The four fixed English questions test a direct fact, paraphrased evaluation practice, synthesis across Classes 4 and 5, and a missing personal-device measurement. See [`tests/questions.json`](tests/questions.json). Every evidence card includes expected behavior, retrieved passages, actual output, citations, and mechanical checks. Chat tests cover capabilities, a contextual follow-up, and isolation of chat-only claims from ask.

The latest English run and its results are linked in [English verification](evidence/ENGLISH-VERIFICATION.md). Earlier Korean development files were preserved in a local backup outside the submission folder. They were not translated and presented as new model outputs.

## Observed limitations and improvements

During development, the first localhost answer overgeneralized about network access and missed the intended Class 2 citation. Explicit source scoping resolved the required Class 2 coverage. Q3 originally missed Class 4; retrieval now decomposes the compound question and combines evidence across its parts. The successful recorded rerun cites Classes 4 and 5. The assistant initially misunderstood its role as language tutoring; its persona now explicitly identifies an AI and software course assistant.

Keyword retrieval can miss unfamiliar paraphrases, and chat retrieval uses a simple trigger rule. Citation validation checks IDs, not entailment. The fixed questions informed revisions, so these results are development checks rather than independent generalization estimates. A next experiment would compare this baseline against local multilingual embeddings on a separate held-out question set.

## Demonstration artifacts

The [offline demonstration](OFFLINE-DEMO.md) completed with all four question checks and chat/search checks passing, unchanged filenames after re-ingestion, and 39 disconnected network samples. Wi-Fi was restored afterward. Earlier failed attempts are retained: powering Wi-Fi off alone did not keep it disconnected, so the final runner disabled the Wi-Fi service for the test and verified connection state throughout.

Actual Obsidian captures show the [index](evidence/obsidian/index.png), [note](evidence/obsidian/note.png), [sources and related links](evidence/obsidian/note-links.png), [graph](evidence/obsidian/graph-readable.png), and [original source](evidence/obsidian/source.png). Open `vault/` in Obsidian. The application UI uses the computer's Korean locale; submission content is English.

## Try it yourself

Double-click `Try Wiki.command` in this folder. Choose **Ask** for cited course answers, **Chat** for a conversation, or **Search** for original passages. Everything runs locally using the installed Gemma model.

Try asking: `What is an embedding, and how does RAG use it?` In chat, try `Suggest a study plan for classes 1 to 5`, then `Make it shorter.` Choose Exit when finished.
