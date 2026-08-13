# EverOS 评测

该适配使用公开 EverOS API，从训练 session 提取可复用 skill，并在测试集
评测时检索和注入这些 skill。

## 支持领域

| 论文领域 | CLI domain |
| --- | --- |
| 网络研究 | `information_retrieval` |
| 算法推理 | `code_implementation` |
| 软件工程 | `software_engineering` |
| 知识工作 | `knowledge_work` |

论文正式任务划分见
[`data/splits/README.md`](../../../data/splits/README.md)。

## 前置条件

- 按仓库主 README 完成 benchmark 和 agent 配置。
- 使用 [EverOS v1.2.3](https://github.com/EverMind-AI/EverOS/tree/v1.2.3)
  （commit `48fc9084888bc17100053227284f939a5aca5e91`）。
- 为 EverOS 配置 LLM、embedding 模型和 reranker。
- 使用默认 API 地址 `http://127.0.0.1:8000`，或通过 `--api-url` 指定。

建议在独立的 Python 3.12 环境中运行 EverOS，避免它与 benchmark 依赖互相影响：

```bash
python3.12 -m venv .everos-venv
source .everos-venv/bin/activate
pip install everos==1.2.3
everos init --root .everos-data
# 填写 .everos-data/everos.toml 中的 provider 配置。
everos server start --root .everos-data
```

在另一个终端中先验证服务：

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

如果本地 judge 或 vLLM 已占用 `8000` 端口，可用 `--port 1995` 启动 EverOS，
并在两个 EvoAgentBench 命令中传入 `--api-url http://127.0.0.1:1995`。

适配器调用公开的 `/api/v2/memory/add`、`/flush`、`/get` 和 `/search`
接口。所有 assistant 消息归属于同一个 EverOS `agent_id`，生成的 case 和
skill 也以该 ID 隔离。

## 1. 收集训练 session

```bash
python src/run.py \
  --domain information_retrieval \
  --split train \
  --job web-research-train \
  --parallel 4
```

## 2. 通过 EverOS 提取 skill

```bash
python src/skill_evolution/evermemos/extract_skills.py \
  --domain information_retrieval \
  --job-dir jobs/web-research-train \
  --api-url http://127.0.0.1:8000
```

命令会打印 EverOS `agent_id`，并将本地元数据写入已被 Git 忽略的
`src/skill_evolution/evermemos/skills/`。

默认每 60 秒轮询一次异步生成的 skill，最多等待一小时；可通过
`--poll-interval` 和 `--max-wait` 调整。若所有 case 都未通过 EverOS 的
质量门槛，最终没有生成 skill 也可能是正常结果。

## 3. 运行匹配的 baseline

```bash
python src/run.py \
  --domain information_retrieval \
  --split test \
  --job web-research-baseline \
  --parallel 4
```

## 4. 使用检索到的 skill 评测

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

评测器也支持通过 `--skills-dir` 读取导出的 `SKILL.md`，或通过
`--skill-cache` 复用任务到 skill 的 JSON 映射。运行时 skill、缓存、
session 和 job 输出均不会进入 Git。

两个脚本默认使用 app `evoagentbench` 和 project `<domain>`。如果需要覆盖，
提取和评测必须传入完全相同的 `--app-id` 与 `--project-id`。可从模板创建
共享的本地默认配置：

```bash
cp src/skill_evolution/evermemos/config.yaml.example \
   src/skill_evolution/evermemos/config.yaml
```

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `domain_info.py` | 提取四个论文领域各自的检索 query |
| `config.yaml.example` | 可选的本地 EverOS client 默认配置 |
| `extract_skills.py` | 规范化训练 session 并发送给 EverOS |
| `eval_with_skills.py` | 在测试集检索、注入并评测 skill |
