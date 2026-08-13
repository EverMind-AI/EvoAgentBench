#!/usr/bin/env python3
"""Preload Docker images for the official SWE-bench split."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPLIT_FILE = PROJECT_ROOT / "data" / "splits" / "software_engineering.json"
DEFAULT_TAR_DIR = PROJECT_ROOT / "data" / "swebench-images"


def image_name(instance_id: str) -> str:
    docker_id = instance_id.replace("__", "_1776_").lower()
    return f"swebench/sweb.eval.x86_64.{docker_id}:latest"


def tar_path(tar_dir: Path, instance_id: str) -> Path:
    docker_id = instance_id.replace("__", "_1776_").lower()
    return tar_dir / f"sweb.eval.x86_64.{docker_id}.tar"


def run_docker(
    docker: str, *args: str, timeout: int
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [docker, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def image_exists(docker: str, name: str) -> bool:
    result = run_docker(docker, "image", "inspect", name, timeout=30)
    return result.returncode == 0


def load_one(
    docker: str, instance_id: str, tar_dir: Path, dry_run: bool
) -> tuple[str, str]:
    name = image_name(instance_id)
    if image_exists(docker, name):
        return "present", name

    archive = tar_path(tar_dir, instance_id)
    if not archive.is_file():
        return "failed", f"{name}: archive not found: {archive}"
    if dry_run:
        return "pending", f"{name} <- {archive}"

    result = run_docker(docker, "load", "--input", str(archive), timeout=1200)
    if result.returncode != 0:
        detail = (
            result.stderr.strip() or result.stdout.strip() or "unknown Docker error"
        )
        return "failed", f"{name}: {detail}"
    if not image_exists(docker, name):
        return "failed", f"{name}: archive loaded, but the expected image tag is absent"
    return "loaded", name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load SWE-bench Docker image tar files for a paper split.",
    )
    parser.add_argument(
        "--split-file",
        type=Path,
        default=DEFAULT_SPLIT_FILE,
        help="split JSON (default: data/splits/software_engineering.json)",
    )
    parser.add_argument(
        "--split",
        choices=("train", "test", "all"),
        default="test",
        help="which split to preload (default: test)",
    )
    parser.add_argument(
        "--tar-dir",
        type=Path,
        default=DEFAULT_TAR_DIR,
        help="directory containing image tar files (default: data/swebench-images)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=int(os.environ.get("EVOAGENT_SWE_IMAGE_PARALLEL", "4")),
        help="parallel Docker loads (default: 4)",
    )
    parser.add_argument(
        "--docker",
        default="docker",
        help="Docker CLI command (default: docker)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate inputs and print images without loading them",
    )
    return parser.parse_args()


def load_ids(split_file: Path, split: str) -> list[str]:
    with split_file.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if split == "all":
        ids = [*payload.get("train", []), *payload.get("test", [])]
    else:
        ids = payload.get(split, [])
    if not ids:
        raise ValueError(f"split '{split}' is empty or absent in {split_file}")
    if not all(isinstance(instance_id, str) and instance_id for instance_id in ids):
        raise ValueError(f"split '{split}' contains an invalid instance ID")
    return ids


def main() -> int:
    args = parse_args()
    if args.parallel < 1:
        print("error: --parallel must be at least 1", file=sys.stderr)
        return 2
    if shutil.which(args.docker) is None:
        print(f"error: Docker CLI not found: {args.docker}", file=sys.stderr)
        return 2
    probe = run_docker(
        args.docker, "info", "--format", "{{.ServerVersion}}", timeout=30
    )
    if probe.returncode != 0:
        detail = (
            probe.stderr.strip() or probe.stdout.strip() or "Docker daemon unavailable"
        )
        print(f"error: cannot reach Docker daemon: {detail}", file=sys.stderr)
        return 2

    split_file = args.split_file.expanduser().resolve()
    tar_dir = args.tar_dir.expanduser().resolve()
    try:
        instance_ids = load_ids(split_file, args.split)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    counts = {"present": 0, "loaded": 0, "pending": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {
            executor.submit(
                load_one, args.docker, instance_id, tar_dir, args.dry_run
            ): instance_id
            for instance_id in instance_ids
        }
        for future in as_completed(futures):
            try:
                status, detail = future.result()
            except (OSError, subprocess.SubprocessError) as exc:
                status, detail = "failed", f"{futures[future]}: {exc}"
            counts[status] += 1
            print(f"[{status}] {detail}")

    action = "would load" if args.dry_run else "loaded"
    print(
        f"summary: total={len(instance_ids)}, present={counts['present']}, "
        f"{action}={counts['pending'] if args.dry_run else counts['loaded']}, "
        f"failed={counts['failed']}"
    )
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
