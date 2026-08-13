# Knowledge Work

This adapter evaluates the paper's Knowledge Work domain on [GDPVal](https://huggingface.co/datasets/openai/gdpval). The agent creates occupational deliverables such as spreadsheets, documents, PDFs, or presentations in an isolated workspace. A multimodal LLM evaluator scores those files against occupation-specific rubrics.

The public split is [`data/splits/knowledge_work.json`](../../../data/splits/knowledge_work.json): 105 train tasks and 60 test tasks.

Install this domain's pinned Python dependencies from the repository root:

```bash
pip install -r requirements-kw.txt
```

## Prepare evaluation prompts

GDPVal task rows are loaded from `openai/gdpval` on first use. Download the occupation meta-prompts from the pinned EvoAgentBench dataset revision:

```bash
hf download EverMind-AI/EvoAgentBench \
  --repo-type dataset \
  --revision 3ac46d860f2f89ff4000f03c9936b618d10570ad \
  --include "Knowledge Work/meta_prompts/*" \
  --local-dir data/gdpval
```

The resulting path, `data/gdpval/Knowledge Work/meta_prompts/`, matches [`knowledge_work.yaml`](knowledge_work.yaml). Reference files are downloaded from the URLs in GDPVal when a task first needs them and cached beside this directory.

## Evaluator dependencies

By default, set an OpenRouter key in `.env`:

```dotenv
OPENROUTER_API_KEY=your-api-key
```

The default evaluator is `openai/gpt-4o`. Change `eval_model_owner` and
`eval_model_name` in the domain YAML, or set `EVALUATION_MODEL` to override the
full model name. To use another OpenAI-compatible endpoint, set
`EVALUATION_API_BASE` and `EVALUATION_API_KEY`; `EMPTY` is accepted by local
servers that do not require authentication.

For PDF and presentation deliverables:

```bash
# PDF rendering (required when a task produces PDF)
apt install poppler-utils

# PPTX rendering (required when a task produces PPTX)
apt install libreoffice
```

Text, Word, and spreadsheet evaluation does not require those two system packages.

## Run

```bash
# One paper task; full IDs and their first 8 characters are both accepted
python src/run.py \
  --domain knowledge_work \
  --task 045aba2e \
  --job kw-debug \
  --live

# Official splits
python src/run.py --domain knowledge_work --split train --parallel 2 --job kw-train
python src/run.py --domain knowledge_work --split test --parallel 2 --job kw-test
```

Agent deliverables are written under the gitignored `workspaces/knowledge_work/` tree. Each task result contains `verifier/eval_details.json`; the default pass threshold is `0.6` and is configurable in the domain YAML.

The evaluator is adapted from the [ClawWork](https://github.com/HKUDS/ClawWork) LLM-evaluation approach.
