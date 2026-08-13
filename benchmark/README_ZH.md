# EvoAgentBench

[English](README.md) · [论文](https://arxiv.org/abs/2607.05202) · [数据集](https://huggingface.co/datasets/EverMind-AI/EvoAgentBench) · [项目主页](https://evermind-ai.github.io/EvoAgentBench/)

[![arXiv](https://img.shields.io/badge/arXiv-2607.05202-b31b1b.svg)](https://arxiv.org/abs/2607.05202)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

EvoAgentBench 评测 agent 能否把历史轨迹转化为可复用的程序性知识，并迁移到未见任务。本仓库按照论文 **EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer** 的四领域协议发布。

Benchmark 代码位于网页仓库的 `benchmark/` 目录。克隆仓库后，请先进入该
目录，再执行下文命令：

```bash
cd EvoAgentBench/benchmark
```

## 公开范围

公开代码包含：

- 四个论文领域的统一 runner；
- 论文使用的 528/267 train/test task ID；
- Nanobot 和 OpenClaw 适配器；
- 不加载进化状态的 **Baseline** 路径；
- 通过 EverOS 提取、检索程序性记忆的 **EverOS** 路径。

Benchmark 原始数据、搜索索引、Docker 镜像、运行结果、API key 和第三方自进化方法适配均不提交。

## 论文领域

| 论文领域 | 基础 Benchmark | CLI domain | Ability communities | Train | Test |
| --- | --- | --- | ---: | ---: | ---: |
| 网络研究 | BrowseComp-Plus | `information_retrieval` | 13 | 154 | 65 |
| 算法推理 | LiveCodeBench | `code_implementation` | 22 | 182 | 86 |
| 软件工程 | SWE-Bench Verified | `software_engineering` | 15 | 87 | 56 |
| 知识工作 | GDPVal | `knowledge_work` | 6 | 105 | 60 |
| **总计** | — | — | **56** | **528** | **267** |

仓库内的 split 文件只包含 task ID；固定来源版本和校验和见 [`data/splits/README.md`](data/splits/README.md)。因此发布本仓库不会上传 benchmark 答案或实验结果。

## 1. 安装环境

推荐 Conda，它会同时安装 BrowseComp-Plus 需要的 Java 21：

```bash
conda env create -f environment.yml
conda activate evoagentbench
```

也可以使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` 只安装轻量的共享 runner。再为需要运行的领域安装固定版本的
依赖文件：

```bash
pip install -r requirements-ir.txt    # 网络研究
pip install -r requirements-code.txt  # 算法推理
pip install -r requirements-swe.txt   # 软件工程
pip install -r requirements-kw.txt    # 知识工作
```

各领域文件使用相同的 core 固定版本，可以安装在同一环境中。BrowseComp-Plus
会额外安装较重的检索模型栈；EverOS 服务仍建议使用下文所示的独立环境。

至少单独安装一个支持的 agent：

```bash
pip install nanobot-ai==0.1.4.post3
# 或
# 需要 Node.js >= 22.14.0
npm install -g openclaw@2026.3.24
```

## 2. 配置

从公开模板创建本地配置：

```bash
cp config.yaml.example config.yaml
cp .env.example .env
cp src/agents/nanobot/nanobot.yaml.example src/agents/nanobot/nanobot.yaml
```

编辑 `.env` 和选中的 agent YAML。如果使用 OpenClaw，复制它的 example，并在 `config.yaml` 中设置 `agent: openclaw`。仓库还提供 `nanobot-397b.yaml.example` 和 `openclaw-397b.yaml.example` 两个 vLLM 模型示例。

公开配置中的数据和输出路径都相对于声明它的配置文件解析，不包含个人机器路径。`/var/run/docker.sock` 是标准 Docker daemon 接口，如有需要可在 `config.yaml` 中覆盖。

## 3. 准备一个领域

Task ID 已经随仓库提供，但每个基础 benchmark 的运行数据需要单独准备：

| 领域 | 必要准备 | 完整说明 |
| --- | --- | --- |
| 网络研究 | 用 `python src/utils/browsecomp-plus-tools/setup_data.py` 下载并解密 BrowseComp-Plus，同时下载 FAISS 索引 | [Information Retrieval](src/domains/information_retrieval/README_ZH.md) |
| 算法推理 | 将 LiveCodeBench 克隆到 `LiveCodeBench/`；题目数据首次运行时缓存 | [Code Implementation](src/domains/code_implementation/README_ZH.md) |
| 软件工程 | 下载 SWE-Bench Verified parquet，并准备对应 Docker 镜像 | [Software Engineering](src/domains/software_engineering/README_ZH.md) |
| 知识工作 | 下载评测 meta-prompts；GDPVal 任务和引用文件按需获取 | [Knowledge Work](src/domains/knowledge_work/README_ZH.md) |

不要无区分地下载整个数据仓库：四个 adapter 使用各自上游 benchmark 的原始格式，大文件应保留在 Git 之外。

## 4. 运行 Baseline

通过 `--domain` 选择论文领域。正式批跑前，先运行单个 task 或数字形式的小 split：

```bash
# 配置数据中的前 2 个任务
python src/run.py --domain information_retrieval --split 2 --job smoke-ir --live

# 四个官方 test split
python src/run.py --domain information_retrieval --split test --parallel 4 --job ir-baseline
python src/run.py --domain code_implementation --split test --parallel 4 --job code-baseline
python src/run.py --domain software_engineering --split test --parallel 2 --job swe-baseline
python src/run.py --domain knowledge_work --split test --parallel 2 --job kw-baseline
```

常用参数：

```text
--agent NAME          覆盖配置中的 agent
--task ID[,ID...]     指定一个或多个 task ID
--split train|test|all
--trials N            每个 task 的 trial 数
--parallel N          并行调度的 task 数
--live                实时显示 agent 活动
--job NAME            jobs/ 下的输出目录名
```

完整参数见 `python src/run.py --help`。

## 5. 运行 EverOS

EverOS 和 Baseline 必须使用相同的 train/test split。以下是网络研究领域的完整对照流程：

适配器固定对接公开的 EverOS `v1.2.3` 及其 `/api/v2/memory/*` API。请按照 [EverOS v1.2.3 快速开始](https://github.com/EverMind-AI/EverOS/blob/v1.2.3/QUICKSTART.md)，在独立的 Python 3.12 环境中配置 LLM、embedding 和 reranker 服务：

```bash
python3.12 -m venv .everos-venv
source .everos-venv/bin/activate
pip install everos==1.2.3
everos init --root .everos-data
# 编辑 .everos-data/everos.toml，然后启动服务：
everos server start --root .everos-data
```

在另一个终端重新激活 EvoAgentBench 环境；继续前先确认 `curl http://127.0.0.1:8000/health` 返回 `{"status":"ok"}`。

```bash
# 1. 收集 train 轨迹
python src/run.py \
  --domain information_retrieval \
  --split train \
  --parallel 4 \
  --job ir-train

# 2. 通过 EverOS 提取 skill
python src/skill_evolution/evermemos/extract_skills.py \
  --domain information_retrieval \
  --job-dir jobs/ir-train \
  --api-url http://127.0.0.1:8000

# 3. 运行 held-out baseline
python src/run.py \
  --domain information_retrieval \
  --split test \
  --parallel 4 \
  --job ir-baseline

# 4. 使用检索到的 skill 评测
python src/skill_evolution/evermemos/eval_with_skills.py \
  --domain information_retrieval \
  --split test \
  --api-url http://127.0.0.1:8000 \
  --agent-id AGENT_ID_FROM_EXTRACTION \
  --top-k 2 \
  --parallel 4 \
  --job ir-everos
```

提取命令会输出 EverOS `agent_id`。默认记忆空间为 app `evoagentbench`、project `<domain>`；如果覆盖该空间，两个命令必须传入相同的 `--app-id` 和 `--project-id`。将 domain 替换成另外三个 CLI 名称即可复用同一协议。Skill cache 和导出的 `SKILL.md` 用法见 [EverOS 说明](src/skill_evolution/evermemos/README_ZH.md)。

## 输出

运行产物写入 `jobs/`，并由 Git 忽略：

```text
jobs/{job_name}/
├── {task_id}__trial_1/
│   ├── result.json
│   ├── session.jsonl
│   └── verifier/
└── summary.json
```

`result.json` 包含统一 reward、agent 响应、耗时和 verifier 结果。各领域还可能生成提取后的代码、agent patch、测试输出或 rubric 详情。

## 仓库结构

```text
EvoAgentBench/
├── config.yaml.example
├── .env.example
├── requirements-*.txt            # 固定版本的 core/领域/dev 依赖
├── THIRD_PARTY_NOTICES.md
├── data/splits/                  # 只跟踪论文 split ID
├── scripts/                      # 公开的数据准备工具
├── src/
│   ├── run.py                    # Baseline 入口
│   ├── agents/                   # Nanobot / OpenClaw 适配
│   ├── domains/                  # 四个论文领域
│   └── skill_evolution/evermemos # EverOS 路径
└── tests/
```

## 引用

```bibtex
@article{gao2026evoagentbench,
  title   = {EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer},
  author  = {Gao, Xingze and Hu, Chuanrui and Chen, Hongda and Yao, Pengfei and Wang, Zhao and Bai, Yi and Wu, Zhengwei and Han, Yunyun and Cong, Xiaofeng and Gui, Jie and Deng, Yafeng and Li, Teng},
  journal = {arXiv preprint arXiv:2607.05202},
  year    = {2026}
}
```

## License

仓库代码采用 [Apache License 2.0](LICENSE)。改编的第三方源码和外部依赖见
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。上游 benchmark 数据仍受
各自条款约束，本仓库不重新分发这些数据。
