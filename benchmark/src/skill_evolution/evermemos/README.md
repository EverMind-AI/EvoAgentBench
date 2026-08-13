# EverOS Evaluation

This integration uses the public EverOS API to extract reusable skills from
training sessions and retrieve them for held-out evaluation.

## Supported domains

| Paper domain | CLI domain |
| --- | --- |
| Web Research | `information_retrieval` |
| Algorithmic Reasoning | `code_implementation` |
| Software Engineering | `software_engineering` |
| Knowledge Work | `knowledge_work` |

The official task IDs are documented in
[`data/splits/README.md`](../../../data/splits/README.md).

## Prerequisites

- Complete the benchmark and agent setup from the repository README.
- Use [EverOS v1.2.3](https://github.com/EverMind-AI/EverOS/tree/v1.2.3)
  (commit `48fc9084888bc17100053227284f939a5aca5e91`).
- Configure EverOS with an LLM, embedding model, and reranker.
- Keep the default API URL (`http://127.0.0.1:8000`) or pass `--api-url`.

Run EverOS as a separate Python 3.12 service so its dependency set stays
isolated from the benchmark environment:

```bash
python3.12 -m venv .everos-venv
source .everos-venv/bin/activate
pip install everos==1.2.3
everos init --root .everos-data
# Fill in the provider settings in .everos-data/everos.toml.
everos server start --root .everos-data
```

In a second terminal, verify the service before running extraction:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

If port `8000` is already occupied by a local judge or vLLM server, start
EverOS with `--port 1995` and pass `--api-url http://127.0.0.1:1995` to both
EvoAgentBench commands.

The adapter uses the public `/api/v2/memory/add`, `/flush`, `/get`, and
`/search` endpoints. Assistant messages are attributed to one EverOS
`agent_id`, which scopes the generated cases and skills.

## 1. Collect training sessions

```bash
python src/run.py \
  --domain information_retrieval \
  --split train \
  --job web-research-train \
  --parallel 4
```

## 2. Extract skills with EverOS

```bash
python src/skill_evolution/evermemos/extract_skills.py \
  --domain information_retrieval \
  --job-dir jobs/web-research-train \
  --api-url http://127.0.0.1:8000
```

The command prints the EverOS `agent_id` and stores local metadata under the
ignored `src/skill_evolution/evermemos/skills/` directory.

Extraction polls for asynchronously generated skills every 60 seconds and
stops after one hour by default. Use `--poll-interval` and `--max-wait` to
change those bounds. EverOS may legitimately emit no skill when its quality
gate rejects all extracted cases.

## 3. Run the matched baseline

```bash
python src/run.py \
  --domain information_retrieval \
  --split test \
  --job web-research-baseline \
  --parallel 4
```

## 4. Evaluate with retrieved skills

```bash
python src/skill_evolution/evermemos/eval_with_skills.py \
  --domain information_retrieval \
  --split test \
  --api-url http://127.0.0.1:8000 \
  --agent-id AGENT_ID_FROM_EXTRACTION \
  --top-k 2 \
  --parallel 4 \
  --job web-research-everos
```

The evaluator also accepts `--skills-dir` for exported `SKILL.md` files and
`--skill-cache` for a previously saved task-to-skill JSON mapping. Runtime
skills, caches, sessions, and job outputs are gitignored.

Both scripts default to app `evoagentbench` and project `<domain>`. If you
override the scope, pass identical `--app-id` and `--project-id` values to
extraction and evaluation. Optional shared defaults can be created with:

```bash
cp src/skill_evolution/evermemos/config.yaml.example \
   src/skill_evolution/evermemos/config.yaml
```

## Files

| File | Responsibility |
| --- | --- |
| `domain_info.py` | Extract the search query field for each paper domain |
| `config.yaml.example` | Optional local EverOS client defaults |
| `extract_skills.py` | Normalize train sessions and send them to EverOS |
| `eval_with_skills.py` | Retrieve, inject, and evaluate skills on the test split |
