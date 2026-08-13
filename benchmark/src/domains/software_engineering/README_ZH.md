# Software Engineering（软件工程）

该 adapter 在 [SWE-Bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) 上评测论文的软件工程领域。每个 task 在官方 Docker 镜像中运行，agent 通过容器 wrapper 修改仓库，adapter 使用 SWE-bench harness 对最终 patch 评分。

公开 split 为 [`data/splits/software_engineering.json`](../../../data/splits/software_engineering.json)，包含 87 个 train instance 和 56 个 test instance。

先在仓库根目录安装该领域的固定版本依赖：

```bash
pip install -r requirements-swe.txt
```

## 前置条件

- Linux x86_64 主机上可访问的 Docker daemon；
- 足够容纳所选 instance 镜像的磁盘空间；
- 在下载镜像或测试依赖时可访问网络。

在仓库根目录下载官方 task table：

```bash
hf download princeton-nlp/SWE-bench_Verified \
  --repo-type dataset \
  --local-dir data/swebench
```

命令会生成 `data/swebench/data/test-00000-of-00001.parquet`，与 [`software_engineering.yaml`](software_engineering.yaml) 一致。

## Docker 镜像

Runner 会依次检查本地 Docker cache、可选的 `SWEBENCH_REGISTRY`、`data/swebench-images/` 下匹配的 tar 文件，最后尝试普通 Docker registry。

如果已经把 image tar 传到机器上，可在批跑前校验并预加载官方 split：

```bash
# 只显示缺少的 archive/image，不执行加载
python scripts/preload_swe_images.py --split test --dry-run

# 并行加载；任何必需 archive 失败时返回非零退出码
python scripts/preload_swe_images.py --split test --parallel 4
```

`owner__repo-123` 对应的 tar 文件名必须为 `sweb.eval.x86_64.owner_1776_repo-123.tar`，其中镜像 tag 必须为 `swebench/sweb.eval.x86_64.owner_1776_repo-123:latest`。

## 运行

```bash
# 单个论文 task
python src/run.py \
  --domain software_engineering \
  --task astropy__astropy-8872 \
  --job swe-debug \
  --live

# 官方 split
python src/run.py --domain software_engineering --split train --parallel 2 --job swe-train
python src/run.py --domain software_engineering --split test --parallel 2 --job swe-test
```

`EVOAGENT_SWE_IMAGE_PARALLEL` 控制并行准备镜像的数量，`EVOAGENT_SWE_SETUP_PARALLEL` 控制并行创建容器的数量；runner 中二者默认均为 `1`。

每个 task 的 agent patch、评测脚本输出、官方报告和 reward 都保存在 `jobs/{job_name}/{instance_id}__trial_1/verifier/`。Trial 完成后容器会删除，镜像继续保留在 cache 中。
