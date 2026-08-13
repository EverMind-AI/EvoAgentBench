# Information Retrieval (Web Research)

This adapter evaluates the paper's Web Research domain on [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus). The agent searches a local corpus through an MCP server, returns an exact answer, and is scored by an LLM judge with normalized exact match as a fallback.

The public split is [`data/splits/information_retrieval.json`](../../../data/splits/information_retrieval.json): 154 train tasks and 65 test tasks.

Install this domain's pinned Python dependencies from the repository root:

```bash
pip install -r requirements-ir.txt
```

## Prepare data

From the repository root:

```bash
python src/utils/browsecomp-plus-tools/setup_data.py
```

The command downloads and decrypts `Tevatron/browsecomp-plus` and downloads the default `qwen3-embedding-8b` FAISS index into:

```text
data/BrowseComp-Plus/
├── browsecomp_plus_decrypted.jsonl
├── queries.tsv
└── indexes/qwen3-embedding-8b/
    └── corpus.*.pkl
```

These paths already match [`information_retrieval.yaml`](information_retrieval.yaml). To choose a smaller embedding index:

```bash
python src/utils/browsecomp-plus-tools/setup_data.py --index qwen3-embedding-0.6b
```

Then update both `mcp_server.index_path` and `mcp_server.model_name` in the domain YAML. Pyserini requires Java; `environment.yml` installs Java 21.

## Configure the judge

Set these values in the repository `.env`:

```dotenv
JUDGE_MODEL=your-judge-model
JUDGE_API_BASE=http://localhost:8000/v1
JUDGE_API_KEY=your-api-key
```

The endpoint must expose an OpenAI-compatible chat-completions API. The MCP search service starts and stops automatically by default on `http://localhost:9101/mcp`; change `mcp_server` in the domain YAML if the port is occupied or the service is managed separately.

## Run

```bash
# One task
python src/run.py --domain information_retrieval --task 784 --job ir-debug --live

# Official splits
python src/run.py --domain information_retrieval --split train --parallel 4 --job ir-train
python src/run.py --domain information_retrieval --split test --parallel 4 --job ir-test

# A named community present in the split file
python src/run.py --domain information_retrieval --split ACTOR_INDIAN_test --job ir-actor-test
```

Each task writes `result.json`, `session.jsonl`, and `verifier/details.json` under `jobs/{job_name}/{task_id}__trial_1/`.

## Upstream code

The search utilities under `src/utils/browsecomp-plus-tools/` are adapted from [texttron/BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus). The public configuration keeps the FAISS index on CPU and allows the embedding model to use automatic device placement.
