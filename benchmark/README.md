# EvoAgentBench

[中文](README_ZH.md) · [Paper](https://arxiv.org/abs/2607.05202) · [Dataset](https://huggingface.co/datasets/EverMind-AI/EvoAgentBench) · [Website](https://evermind-ai.github.io/EvoAgentBench/)

[![arXiv](https://img.shields.io/badge/arXiv-2607.05202-b31b1b.svg)](https://arxiv.org/abs/2607.05202)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

EvoAgentBench evaluates whether an agent can convert prior trajectories into reusable procedural knowledge and transfer it to held-out tasks. This repository follows the four-domain protocol from **EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer**.

The benchmark is stored in the `benchmark/` directory of the website
repository. After cloning the repository, run all commands below from that
directory:

```bash
cd EvoAgentBench/benchmark
```

## Release scope

This public codebase contains:

- a unified runner for four paper domains;
- the official 528/267 train/test task-ID splits;
- Nanobot and OpenClaw adapters;
- the plain **Baseline** path;
- the **EverOS** path for extracting and retrieving procedural memory.

Benchmark payloads, search indexes, Docker images, run outputs, API keys, and third-party self-evolution integrations are not committed.

## Paper domains

| Paper domain | Base benchmark | CLI domain | Ability communities | Train | Test |
| --- | --- | --- | ---: | ---: | ---: |
| Web Research | BrowseComp-Plus | `information_retrieval` | 13 | 154 | 65 |
| Algorithmic Reasoning | LiveCodeBench | `code_implementation` | 22 | 182 | 86 |
| Software Engineering | SWE-Bench Verified | `software_engineering` | 15 | 87 | 56 |
| Knowledge Work | GDPVal | `knowledge_work` | 6 | 105 | 60 |
| **Total** | — | — | **56** | **528** | **267** |

The tracked split files and their pinned source checksums are documented in [`data/splits/README.md`](data/splits/README.md). They contain IDs only, so releasing this repository does not publish benchmark answers or experiment results.

## 1. Install

Conda is recommended because it also installs Java 21 for BrowseComp-Plus:

```bash
conda env create -f environment.yml
conda activate evoagentbench
```

Alternatively:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` installs the lightweight shared runner. Add the pinned file
for every domain you intend to run:

```bash
pip install -r requirements-ir.txt    # Web Research
pip install -r requirements-code.txt  # Algorithmic Reasoning
pip install -r requirements-swe.txt   # Software Engineering
pip install -r requirements-kw.txt    # Knowledge Work
```

The domain files share the same core pins and may be installed in one
environment. BrowseComp-Plus is substantially heavier because it installs the
retrieval model stack; EverOS itself should remain in the separate service
environment shown below.

Install at least one supported agent separately:

```bash
pip install nanobot-ai==0.1.4.post3
# or
# Requires Node.js >= 22.14.0
npm install -g openclaw@2026.3.24
```

## 2. Configure

Create local files from the public templates:

```bash
cp config.yaml.example config.yaml
cp .env.example .env
cp src/agents/nanobot/nanobot.yaml.example src/agents/nanobot/nanobot.yaml
```

Edit `.env` and the selected agent YAML. To use OpenClaw, copy its example instead and set `agent: openclaw` in `config.yaml`. Model-specific vLLM examples are also available as `nanobot-397b.yaml.example` and `openclaw-397b.yaml.example`.

All repository data and output paths in the public configs are relative to the config file that declares them. There are no user-machine paths in the templates. `/var/run/docker.sock`, when used, is the standard Docker daemon socket and can be overridden in `config.yaml`.

## 3. Prepare one domain

The task IDs are already included, but each base benchmark has separate runtime data:

| Domain | Required preparation | Full guide |
| --- | --- | --- |
| Web Research | Download/decrypt BrowseComp-Plus and its FAISS index with `python src/utils/browsecomp-plus-tools/setup_data.py` | [Information Retrieval](src/domains/information_retrieval/README.md) |
| Algorithmic Reasoning | Clone LiveCodeBench into `LiveCodeBench/`; problem data is cached on first run | [Code Implementation](src/domains/code_implementation/README.md) |
| Software Engineering | Download the SWE-Bench Verified parquet file and make its Docker images available | [Software Engineering](src/domains/software_engineering/README.md) |
| Knowledge Work | Download the evaluation meta-prompts; GDPVal tasks and reference files are fetched on demand | [Knowledge Work](src/domains/knowledge_work/README.md) |

Do not run a full benchmark download command blindly: the four adapters intentionally use their upstream benchmark formats and keep large artifacts outside Git.

## 4. Run the Baseline

Use `--domain` to select the paper domain. Start with one task or a small numeric split before launching a full run:

```bash
# First 2 tasks from the configured dataset
python src/run.py --domain information_retrieval --split 2 --job smoke-ir --live

# Official test splits
python src/run.py --domain information_retrieval --split test --parallel 4 --job ir-baseline
python src/run.py --domain code_implementation --split test --parallel 4 --job code-baseline
python src/run.py --domain software_engineering --split test --parallel 2 --job swe-baseline
python src/run.py --domain knowledge_work --split test --parallel 2 --job kw-baseline
```

Useful options:

```text
--agent NAME          override the configured agent
--task ID[,ID...]     run specific task IDs
--split train|test|all
--trials N            trials per task
--parallel N          concurrently scheduled tasks
--live                stream agent activity
--job NAME            output directory name under jobs/
```

Run `python src/run.py --help` for the complete CLI.

## 5. Run EverOS

EverOS uses the same train/test split as the baseline. The following example shows the full matched workflow for Web Research:

The adapter targets the public EverOS `v1.2.3` release and its `/api/v2/memory/*` API. Run the service in a separate Python 3.12 environment and configure its LLM, embedding, and reranker providers as described in the [EverOS v1.2.3 quickstart](https://github.com/EverMind-AI/EverOS/blob/v1.2.3/QUICKSTART.md):

```bash
python3.12 -m venv .everos-venv
source .everos-venv/bin/activate
pip install everos==1.2.3
everos init --root .everos-data
# Edit .everos-data/everos.toml, then start the service:
everos server start --root .everos-data
```

In another terminal, reactivate the EvoAgentBench environment and verify `curl http://127.0.0.1:8000/health` returns `{"status":"ok"}` before continuing.

```bash
# 1. Collect train trajectories
python src/run.py \
  --domain information_retrieval \
  --split train \
  --parallel 4 \
  --job ir-train

# 2. Extract reusable skills through EverOS
python src/skill_evolution/evermemos/extract_skills.py \
  --domain information_retrieval \
  --job-dir jobs/ir-train \
  --api-url http://127.0.0.1:8000

# 3. Run the held-out baseline
python src/run.py \
  --domain information_retrieval \
  --split test \
  --parallel 4 \
  --job ir-baseline

# 4. Evaluate with retrieved skills
python src/skill_evolution/evermemos/eval_with_skills.py \
  --domain information_retrieval \
  --split test \
  --api-url http://127.0.0.1:8000 \
  --agent-id AGENT_ID_FROM_EXTRACTION \
  --top-k 2 \
  --parallel 4 \
  --job ir-everos
```

The extraction command prints the EverOS `agent_id`. By default, memories are isolated under app `evoagentbench` and project `<domain>`; pass the same `--app-id` and `--project-id` to both commands when overriding that scope. Repeat the protocol with any of the four CLI domain names. See the [EverOS integration guide](src/skill_evolution/evermemos/README.md) for skill caches and exported `SKILL.md` files.

## Outputs

Runtime artifacts are written under `jobs/` and ignored by Git:

```text
jobs/{job_name}/
├── {task_id}__trial_1/
│   ├── result.json
│   ├── session.jsonl
│   └── verifier/
└── summary.json
```

`result.json` contains the normalized reward, agent response, timing, and verifier result. Each domain may add verifier artifacts such as extracted code, an agent patch, test output, or rubric details.

## Repository layout

```text
EvoAgentBench/
├── config.yaml.example
├── .env.example
├── requirements-*.txt            # pinned core/domain/dev dependencies
├── THIRD_PARTY_NOTICES.md
├── data/splits/                  # tracked paper split IDs only
├── scripts/                      # public preparation utilities
├── src/
│   ├── run.py                    # Baseline entry point
│   ├── agents/                   # Nanobot and OpenClaw adapters
│   ├── domains/                  # four paper-domain adapters
│   └── skill_evolution/evermemos # EverOS path
└── tests/
```

## Citation

```bibtex
@article{gao2026evoagentbench,
  title   = {EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer},
  author  = {Gao, Xingze and Hu, Chuanrui and Chen, Hongda and Yao, Pengfei and Wang, Zhao and Bai, Yi and Wu, Zhengwei and Han, Yunyun and Cong, Xiaofeng and Gui, Jie and Deng, Yafeng and Li, Teng},
  journal = {arXiv preprint arXiv:2607.05202},
  year    = {2026}
}
```

## License

The repository is released under the [Apache License 2.0](LICENSE). Adapted
third-party source and external dependencies are documented in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Upstream benchmark data
retains its own terms and is not redistributed here.
