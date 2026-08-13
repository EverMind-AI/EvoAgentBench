# Information Retrieval（网络研究）

该 adapter 在 [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) 上评测论文的网络研究领域。Agent 通过 MCP 搜索本地语料库并返回精确答案；主要指标由 LLM judge 给出，judge 不可用时回退到归一化 exact match。

公开 split 为 [`data/splits/information_retrieval.json`](../../../data/splits/information_retrieval.json)，包含 154 个 train task 和 65 个 test task。

先在仓库根目录安装该领域的固定版本依赖：

```bash
pip install -r requirements-ir.txt
```

## 准备数据

在仓库根目录运行：

```bash
python src/utils/browsecomp-plus-tools/setup_data.py
```

脚本会下载并解密 `Tevatron/browsecomp-plus`，同时下载默认的 `qwen3-embedding-8b` FAISS 索引：

```text
data/BrowseComp-Plus/
├── browsecomp_plus_decrypted.jsonl
├── queries.tsv
└── indexes/qwen3-embedding-8b/
    └── corpus.*.pkl
```

这些路径已与 [`information_retrieval.yaml`](information_retrieval.yaml) 对齐。也可以选择较小的 embedding 索引：

```bash
python src/utils/browsecomp-plus-tools/setup_data.py --index qwen3-embedding-0.6b
```

此时需要同时修改 domain YAML 中的 `mcp_server.index_path` 和 `mcp_server.model_name`。Pyserini 依赖 Java；`environment.yml` 已包含 Java 21。

## 配置 judge

在仓库 `.env` 中填写：

```dotenv
JUDGE_MODEL=your-judge-model
JUDGE_API_BASE=http://localhost:8000/v1
JUDGE_API_KEY=your-api-key
```

服务需要提供 OpenAI-compatible chat-completions API。MCP 搜索服务默认在 `http://localhost:9101/mcp` 自动启停；如端口冲突或需要自行管理，可修改 domain YAML 的 `mcp_server`。

## 运行

```bash
# 单个 task
python src/run.py --domain information_retrieval --task 784 --job ir-debug --live

# 官方 split
python src/run.py --domain information_retrieval --split train --parallel 4 --job ir-train
python src/run.py --domain information_retrieval --split test --parallel 4 --job ir-test

# split 文件中已有的 community
python src/run.py --domain information_retrieval --split ACTOR_INDIAN_test --job ir-actor-test
```

每个 task 在 `jobs/{job_name}/{task_id}__trial_1/` 下生成 `result.json`、`session.jsonl` 和 `verifier/details.json`。

## 上游代码

`src/utils/browsecomp-plus-tools/` 中的搜索工具改编自 [texttron/BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus)。公开配置将 FAISS 索引保留在 CPU，并允许 embedding 模型自动选择设备。
