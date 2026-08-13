# Software Engineering

This adapter evaluates the paper's Software Engineering domain on [SWE-Bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified). Each task runs in its official Docker image. The agent edits the repository through a container wrapper, and the adapter grades the resulting patch with the SWE-bench harness.

The public split is [`data/splits/software_engineering.json`](../../../data/splits/software_engineering.json): 87 train instances and 56 test instances.

Install this domain's pinned Python dependencies from the repository root:

```bash
pip install -r requirements-swe.txt
```

## Prerequisites

- A reachable Docker daemon on a Linux x86_64 host.
- Enough disk for the selected instance images.
- Network access when images or test dependencies must be downloaded.

Download the official task table from the repository root:

```bash
hf download princeton-nlp/SWE-bench_Verified \
  --repo-type dataset \
  --local-dir data/swebench
```

This creates `data/swebench/data/test-00000-of-00001.parquet`, which matches [`software_engineering.yaml`](software_engineering.yaml).

## Docker images

For each instance, the runner checks the local Docker cache, an optional `SWEBENCH_REGISTRY`, a matching tar file under `data/swebench-images/`, and finally the normal Docker registry.

If image tar files have already been transferred to the machine, validate and preload the official split before a batch:

```bash
# Show missing archives/images without loading
python scripts/preload_swe_images.py --split test --dry-run

# Load available archives; returns non-zero if any required archive fails
python scripts/preload_swe_images.py --split test --parallel 4
```

The tar filename for `owner__repo-123` must be `sweb.eval.x86_64.owner_1776_repo-123.tar`. The image inside it must provide the tag `swebench/sweb.eval.x86_64.owner_1776_repo-123:latest`.

## Run

```bash
# One paper task
python src/run.py \
  --domain software_engineering \
  --task astropy__astropy-8872 \
  --job swe-debug \
  --live

# Official splits
python src/run.py --domain software_engineering --split train --parallel 2 --job swe-train
python src/run.py --domain software_engineering --split test --parallel 2 --job swe-test
```

`EVOAGENT_SWE_IMAGE_PARALLEL` limits concurrent image preparation and `EVOAGENT_SWE_SETUP_PARALLEL` limits concurrent container setup. Both default to `1` in the runner.

Each task writes the agent patch, evaluation script output, official report, and reward under `jobs/{job_name}/{instance_id}__trial_1/verifier/`. Containers are removed after each trial; images remain cached.
