# Knowledge Work（知识工作）

该 adapter 在 [GDPVal](https://huggingface.co/datasets/openai/gdpval) 上评测论文的知识工作领域。Agent 在独立 workspace 中生成表格、文档、PDF 或演示文稿等职业交付物，多模态 LLM evaluator 根据职业 rubric 对文件评分。

公开 split 为 [`data/splits/knowledge_work.json`](../../../data/splits/knowledge_work.json)，包含 105 个 train task 和 60 个 test task。

先在仓库根目录安装该领域的固定版本依赖：

```bash
pip install -r requirements-kw.txt
```

## 准备评测 prompt

GDPVal task 首次使用时直接从 `openai/gdpval` 加载。Occupation meta-prompts 从固定版本的 EvoAgentBench 数据集下载：

```bash
hf download EverMind-AI/EvoAgentBench \
  --repo-type dataset \
  --revision 3ac46d860f2f89ff4000f03c9936b618d10570ad \
  --include "Knowledge Work/meta_prompts/*" \
  --local-dir data/gdpval
```

生成的 `data/gdpval/Knowledge Work/meta_prompts/` 与 [`knowledge_work.yaml`](knowledge_work.yaml) 一致。某个 task 首次需要 reference file 时，adapter 会根据 GDPVal 中的 URL 下载，并缓存在相邻目录。

## Evaluator 依赖

默认情况下，在 `.env` 中填写 OpenRouter key：

```dotenv
OPENROUTER_API_KEY=your-api-key
```

默认 evaluator 为 `openai/gpt-4o`。可以修改 domain YAML 中的
`eval_model_owner`、`eval_model_name`，或用 `EVALUATION_MODEL` 覆盖完整模型名。
如果使用其他 OpenAI-compatible 端点，设置 `EVALUATION_API_BASE` 和
`EVALUATION_API_KEY`；无需鉴权的本地服务可将 key 设为 `EMPTY`。

如果 task 会生成 PDF 或演示文稿，还需安装：

```bash
# 生成 PDF 预览图时需要
apt install poppler-utils

# 生成 PPTX 预览图时需要
apt install libreoffice
```

纯文本、Word 和 spreadsheet 评测不需要这两个系统包。

## 运行

```bash
# 单个论文 task；完整 ID 或前 8 位都可以
python src/run.py \
  --domain knowledge_work \
  --task 045aba2e \
  --job kw-debug \
  --live

# 官方 split
python src/run.py --domain knowledge_work --split train --parallel 2 --job kw-train
python src/run.py --domain knowledge_work --split test --parallel 2 --job kw-test
```

Agent 交付物写入 Git 忽略的 `workspaces/knowledge_work/`。每个 task 的评测详情保存在 `verifier/eval_details.json`；默认通过阈值为 `0.6`，可在 domain YAML 中修改。

Evaluator 改编自 [ClawWork](https://github.com/HKUDS/ClawWork) 的 LLM evaluation 方案。
