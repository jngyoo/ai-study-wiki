# English verification

Submission prose, prompts, CLI outputs, generated notes, and evaluation questions are English. The source HTML is preserved unchanged. Obsidian's native interface remains in the computer's Korean locale.

## Successful disconnected run

[Summary](evaluations/20261005T225923.840881Z/summary.json) · [Chat checks](evaluations/20261005T225923.840881Z/chat-checks.json) · [Search](evaluations/20261005T225923.840881Z/search-transcript.txt) · [Offline result](offline/20261005T225904.513397Z/result.json)

| Test | Evidence | Mechanical checks | Wall time (seconds) |
|---|---|---|---|
| q1 | [Answer and original passages](evaluations/20261005T225923.840881Z/q1.md) | Passed | 3.597 |
| q2 | [Answer and original passages](evaluations/20261005T225923.840881Z/q2.md) | Passed | 3.711 |
| q3 | [Answer and original passages](evaluations/20261005T225923.840881Z/q3.md) | Passed | 5.909 |
| q4 | [Answer and original passages](evaluations/20261005T225923.840881Z/q4.md) | Passed | 1.987 |

Q1 explicitly scopes retrieval to Class 2 using `--sources class2`; Q2–Q4 use the full lecture collection. Q3 now retrieves evidence for each part and cites both Classes 4 and 5. All four mode checks passed: ordinary chat without forced retrieval, follow-up history, ask isolation from chat-only claims, and model-free search. The evidence cards include an assistant review comparing each answer with its cited passages. This is not independent human grading.

## Offline and wiki evidence

The 43.607-second demonstration saved 39 network-state samples, all disconnected. External connection probes failed before and after the tests. Fresh CLI subprocesses regenerated two Class 2 notes locally, checked stable re-ingestion across all sources, ran evaluation and conversation, and searched after unloading Gemma. Ten notes remained with unchanged paths and content on the repeated unchanged ingest. Wi-Fi service and power were restored. See [recording and network evidence](../OFFLINE-DEMO.md).

[Actual Obsidian screenshots](obsidian/README.md) show the grouped index, an English note, its source and related links, the ten-note graph, and navigation to original slide text. The vault checker finds 10 notes and 69 valid links.

## Interpretation and limitations

Times above are observed per-question wall times from this run, not a general benchmark. Model allocation snapshots in the question JSON records are not whole-system peak RAM. Initial full English generation produced ten notes and 413 passages in 51.807 seconds ([record](runs/20261005T180729.917714Z-ingest.json)).

Earlier citation and network-verification failures remain saved. The fixed evaluation questions informed retrieval changes, so these are development checks. Citation structure alone cannot guarantee semantic correctness. Generated study notes retain a student-review marker. Public GitHub publication and course-portal submission remain outstanding.
