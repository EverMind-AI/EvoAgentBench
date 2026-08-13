# Official Paper Splits

These task-ID lists reproduce Table 2 of
[EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer](https://arxiv.org/abs/2607.05202).

The files are mirrored from the
[EverMind-AI/EvoAgentBench dataset](https://huggingface.co/datasets/EverMind-AI/EvoAgentBench)
at the immutable revision recorded in `manifest.json`. They contain split IDs
only; benchmark task data and experiment outputs are not stored here.

Internal filenames retain the current adapter names. The paper-domain mapping is:

| Paper domain | Source benchmark | Local file | Train | Test |
| --- | --- | --- | ---: | ---: |
| Web Research | BrowseComp-Plus | `information_retrieval.json` | 154 | 65 |
| Algorithmic Reasoning | LiveCodeBench | `code_implementation.json` | 182 | 86 |
| Software Engineering | SWE-Bench Verified | `software_engineering.json` | 87 | 56 |
| Knowledge Work | GDPVal | `knowledge_work.json` | 105 | 60 |

Total: 528 train tasks and 267 test tasks. Every file has zero train/test
overlap. Verify file integrity against `manifest.json` before a release.
