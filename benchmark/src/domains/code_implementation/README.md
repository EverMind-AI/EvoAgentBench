# Code Implementation (Algorithmic Reasoning)

This adapter evaluates the paper's Algorithmic Reasoning domain on [LiveCodeBench](https://livecodebench.github.io/). The agent produces a Python or C++ solution, and the adapter scores it with LiveCodeBench's official test runner. A task receives reward `1.0` only when all tests pass.

The public split is [`data/splits/code_implementation.json`](../../../data/splits/code_implementation.json): 182 train tasks and 86 test tasks from `release_v6`.

## Install LiveCodeBench

Install this domain's pinned dependencies, then clone LiveCodeBench separately
because its package metadata pulls in model-serving packages that the evaluator
does not use:

```bash
pip install -r requirements-code.txt
git clone https://github.com/LiveCodeBench/LiveCodeBench.git
pip install --no-deps -e ./LiveCodeBench
```

The default [`code_implementation.yaml`](code_implementation.yaml) expects the clone at `LiveCodeBench/`. Problem records are downloaded from `livecodebench/code_generation_lite` on first use and cached under `data/livecode/`.

## Run

```bash
# One paper task
python src/run.py --domain code_implementation --task 3423 --job code-debug --live

# Official splits
python src/run.py --domain code_implementation --split train --parallel 4 --job code-train
python src/run.py --domain code_implementation --split test --parallel 4 --job code-test

# Small smoke run or a difficulty slice
python src/run.py --domain code_implementation --split 2 --job code-smoke
python src/run.py --domain code_implementation --split easy --job code-easy
```

The adapter extracts the final fenced code block from the agent response or session, then saves:

```text
jobs/{job_name}/{task_id}__trial_1/
├── result.json
├── session.jsonl
└── verifier/
    ├── details.json
    └── solution.py or solution.cpp
```

The `test_timeout` field in the domain YAML is applied per test case. The default agent timeout is 1,800 seconds per task.

EverOS skill injection uses the shared [`eval_with_skills.py`](../../skill_evolution/evermemos/eval_with_skills.py) entry point; no evolution logic is embedded in this adapter.
