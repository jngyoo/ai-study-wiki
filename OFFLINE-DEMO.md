# Disconnected-internet demonstration

Completed on October 5, 2026. The actual recorded run lasted 43.607 seconds. Wi-Fi service and radio were disabled; no active network interfaces appeared in any of 39 samples, and external connection probes failed before and after. Wi-Fi was restored afterward.

- [Run result](evidence/offline/20261005T225904.513397Z/result.json)
- [Terminal transcript](evidence/offline/20261005T225904.513397Z/terminal.txt)
- [Timed terminal recording (asciicast v2)](evidence/offline/20261005T225904.513397Z/terminal.cast)
- [Network before tests](evidence/offline/20261005T225904.513397Z/network-before-tests.json)
- [Network samples throughout execution](evidence/offline/20261005T225904.513397Z/network-samples.json)
- [Network after tests](evidence/offline/20261005T225904.513397Z/network-after-tests.json)
- [Evaluation summary](evidence/evaluations/20261005T225923.840881Z/summary.json)

The recording contains actual subprocess commands and outputs, not a screen video. Open the transcript directly or play the `.cast` in a compatible asciicast player.

## What ran

Fresh CLI subprocesses displayed help and device/model status, forced local re-ingestion of Class 2 (two generated notes), reran unchanged ingestion across all five sources, evaluated four questions, tested normal chat and follow-ups, unloaded the model, searched originals without a loaded model, and checked wiki links. All four evaluation questions and all chat/search mode checks passed. Re-ingestion kept ten notes with identical content and paths.

## Reproduction

Download Ollama, Gemma, sources, and Obsidian before disconnecting. Open a terminal in this project folder. The runner below intentionally disables Wi-Fi temporarily and restores its previous enabled/on state in a cleanup handler; it also schedules a recovery watchdog. The interface name must match the computer. Do not run it during a call or download.

```sh
python3 offline_demo.py --disconnect-wifi en0
```

`--force` replaces generated notes, so retain reviewed copies before rerunning. This recorded run regenerated only Class 2; all five originals and the complete index were already local. The network evidence establishes this run's disconnected state, not the state of earlier development runs. Previous attempts that reconnected during execution are retained as failures.

Obsidian captures were taken separately after connectivity was restored; they demonstrate wiki structure and link navigation, not network isolation. See [screenshots](evidence/obsidian/README.md).
