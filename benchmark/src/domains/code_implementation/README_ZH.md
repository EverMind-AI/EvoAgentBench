# Code Implementation（算法推理）

该 adapter 在 [LiveCodeBench](https://livecodebench.github.io/) 上评测论文的算法推理领域。Agent 输出 Python 或 C++ 解法，由 LiveCodeBench 官方测试 runner 评分；只有全部测试通过时 reward 才为 `1.0`。

公开 split 为 [`data/splits/code_implementation.json`](../../../data/splits/code_implementation.json)，对应 `release_v6` 的 182 个 train task 和 86 个 test task。

## 安装 LiveCodeBench

先在仓库根目录安装该领域的固定版本依赖。LiveCodeBench 的 package metadata
还会引入本评测器不需要的模型服务包，因此单独克隆并使用 `--no-deps` 安装：

```bash
pip install -r requirements-code.txt
git clone https://github.com/LiveCodeBench/LiveCodeBench.git
pip install --no-deps -e ./LiveCodeBench
```

默认 [`code_implementation.yaml`](code_implementation.yaml) 期望源码位于 `LiveCodeBench/`。题目记录首次运行时从 `livecodebench/code_generation_lite` 下载，并缓存到 `data/livecode/`。

## 运行

```bash
# 单个论文 task
python src/run.py --domain code_implementation --task 3423 --job code-debug --live

# 官方 split
python src/run.py --domain code_implementation --split train --parallel 4 --job code-train
python src/run.py --domain code_implementation --split test --parallel 4 --job code-test

# 小规模 smoke run 或按难度筛选
python src/run.py --domain code_implementation --split 2 --job code-smoke
python src/run.py --domain code_implementation --split easy --job code-easy
```

Adapter 会从 agent 响应或 session 中提取最后一个 fenced code block，并保存：

```text
jobs/{job_name}/{task_id}__trial_1/
├── result.json
├── session.jsonl
└── verifier/
    ├── details.json
    └── solution.py 或 solution.cpp
```

Domain YAML 中的 `test_timeout` 按单个测试用例计算；默认 agent task 超时为 1,800 秒。

EverOS skill 注入使用共享入口 [`eval_with_skills.py`](../../skill_evolution/evermemos/eval_with_skills.py)，本 adapter 内不包含进化逻辑。
