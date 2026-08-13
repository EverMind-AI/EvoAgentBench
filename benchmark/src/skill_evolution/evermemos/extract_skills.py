#!/usr/bin/env python3
"""Extract skills from train sessions using the public EverOS API.

Sends session trajectories to EverOS, triggers clustering, waits for skill
stabilization, and saves extracted skills as SKILL.md files.

Supports split files in two formats:

1. Cluster format:
    {"clusters": {"CLUSTER_A": {"train": [...], "test": [...]}, ...}}

2. Flat format (auto-wrapped into a "default" cluster):
    {"train": [...], "test": [...]}

For domains without a split file, tasks are loaded from the domain adapter.

Usage:
    python extract_skills.py --job-dir jobs/web-research-XXX --api-url http://127.0.0.1:8000
    python extract_skills.py --domain information_retrieval --job-dir jobs/bcp-XXX
    python extract_skills.py --job-dir jobs/... --success-only
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

_env_file = _PROJECT_ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

import httpx  # noqa: E402
from config import get_domain, get_domain_config, get_config, load_config  # noqa: E402

log = logging.getLogger("evoagentbench")

DEFAULT_EVEROS_API_URL = "http://127.0.0.1:8000"
EVEROS_MEMORY_API = "/api/v2/memory"
EVEROS_MAX_MESSAGE_BATCH = 500


# ---------------------------------------------------------------------------
# Split file loading
# ---------------------------------------------------------------------------


def load_task_clusters(
    split_file: str | Path, split_name: str, clusters: list[str] | None = None
) -> dict[str, list[str]]:
    """Load {cluster_name: [task_id, ...]} from a split file.

    Supports cluster format and flat format (auto-wrapped into "default").
    """
    with open(split_file) as f:
        data = json.load(f)

    if "clusters" in data:
        result = {}
        for name, splits in data["clusters"].items():
            if clusters and name not in clusters:
                continue
            task_ids = splits.get(split_name, [])
            if task_ids:
                result[name] = [str(tid) for tid in task_ids]
        return result

    if split_name in data:
        return {"default": [str(tid) for tid in data[split_name]]}

    raise ValueError(
        f"Split file has neither 'clusters' key nor '{split_name}' key. "
        f"Keys found: {list(data.keys())}"
    )


def load_splits_from_adapter(domain, split_name: str) -> dict[str, list[str]]:
    """Fallback: load task IDs from domain adapter (no split file needed)."""
    tmp_args = argparse.Namespace(
        task=None,
        split=split_name,
        trials=1,
        parallel=1,
        max_retries=0,
        live=False,
        disk_budget=None,
    )
    tasks = domain.load_tasks(tmp_args)
    return {"default": [str(t["name"]) for t in tasks]}


# ---------------------------------------------------------------------------
# Session loading & normalization
# ---------------------------------------------------------------------------


def load_session_messages(path: Path) -> list:
    """Load and normalize session messages from a JSONL file.

    Supports nanobot (flat role/content) and openclaw (nested message blocks).

    Reasoning/thinking handling:
      - Multi-turn (has tool calls): reasoning dropped (tool selection noise).
      - Single-turn (no tools): reasoning chunked into simulated tool_call/
        tool_result pairs so EverOS can extract MemCells from them.
    """
    messages = []
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("role"):
                messages.append(_normalize_nanobot_message(entry))
            elif entry.get("type") == "message" and entry.get("message"):
                msg = _normalize_openclaw_message(entry["message"])
                if msg:
                    messages.append(msg)

    has_tools = any(m.get("tool_calls") or m["role"] == "tool" for m in messages)

    if has_tools:
        for m in messages:
            m.pop("_reasoning", "")
    else:
        expanded = []
        for m in messages:
            reasoning = m.pop("_reasoning", "")
            if not reasoning:
                expanded.append(m)
                continue
            chunks = _split_thinking_to_blocks(reasoning, block_size=1000)
            if len(chunks) <= 1:
                m["content"] = (
                    (reasoning + "\n\n" + m["content"]) if m["content"] else reasoning
                )
                expanded.append(m)
            else:
                for i, chunk in enumerate(chunks):
                    call_id = f"think_{i:03d}"
                    expanded.append(
                        {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": call_id,
                                    "type": "function",
                                    "function": {
                                        "name": "reasoning_step",
                                        "arguments": json.dumps(
                                            {"step": i + 1, "total": len(chunks)}
                                        ),
                                    },
                                }
                            ],
                        }
                    )
                    expanded.append(
                        {"role": "tool", "content": chunk, "tool_call_id": call_id}
                    )
                if m["content"].strip():
                    expanded.append({"role": "assistant", "content": m["content"]})
        messages = expanded

    # Filter out ghost messages (empty content AND no tool_calls).
    # In multi-turn sessions, some assistant messages had only reasoning which
    # got stripped above, leaving empty content. The server rejects these
    # (422: "messages[].content must not be empty").
    messages = [
        m
        for m in messages
        if (m.get("content") or "").strip()
        or (m["role"] == "assistant" and m.get("tool_calls"))
    ]

    return messages


def _split_thinking_to_blocks(text: str, block_size: int = 1000) -> list[str]:
    if not text or len(text) <= block_size:
        return [text] if text else []
    return [text[i : i + block_size] for i in range(0, len(text), block_size)]


def _normalize_nanobot_message(msg: dict) -> dict:
    result = {"role": msg["role"]}
    content = msg.get("content")
    tool_calls = msg.get("tool_calls")
    reasoning = msg.get("reasoning_content")

    if content:
        result["content"] = str(content)
    elif tool_calls:
        parts = [
            f"[call {tc.get('function', {}).get('name', '?')}(...)]"
            for tc in tool_calls
        ]
        result["content"] = " ".join(parts)
    else:
        result["content"] = ""

    if reasoning:
        result["_reasoning"] = str(reasoning)
    if tool_calls:
        result["tool_calls"] = tool_calls
    if msg.get("tool_call_id"):
        result["tool_call_id"] = msg["tool_call_id"]
    return result


def _normalize_openclaw_message(msg: dict) -> dict | None:
    role = msg.get("role", "")
    if not role:
        return None

    content_blocks = msg.get("content", [])
    if not isinstance(content_blocks, list):
        return {"role": role, "content": str(content_blocks)}

    text_parts, thinking_parts, tool_calls = [], [], []
    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        btype = block.get("type", "")
        if btype == "text":
            text_parts.append(block.get("text", ""))
        elif btype == "thinking":
            thinking_parts.append(block.get("thinking", ""))
        elif btype in ("toolCall", "toolUse", "tool_use"):
            tool_calls.append(
                {
                    "id": block.get("id", block.get("toolCallId", "")),
                    "type": "function",
                    "function": {
                        "name": block.get("name", block.get("toolName", "")),
                        "arguments": json.dumps(
                            block.get("arguments", block.get("input", {}))
                        ),
                    },
                }
            )

    normalized_role = "tool" if role == "toolResult" else role
    content = "\n".join(text_parts)
    reasoning = "\n".join(thinking_parts)
    if not content.strip() and not tool_calls and not reasoning.strip():
        return None
    result = {"role": normalized_role, "content": content}
    if reasoning:
        result["_reasoning"] = reasoning
    if tool_calls:
        result["tool_calls"] = tool_calls
    tool_call_id = msg.get("toolCallId") or msg.get("tool_call_id")
    if tool_call_id:
        result["tool_call_id"] = tool_call_id
    return result


def find_sessions(job_dir: Path, task_ids: list[str]) -> dict[str, Path]:
    """Find session.jsonl for each task_id. Falls back to 8-char prefix match
    (some benchmarks like GDPVal truncate UUIDs in dir names)."""
    found = {}
    for tid in task_ids:
        session_file = job_dir / f"{tid}__trial_1" / "session.jsonl"
        if session_file.exists():
            found[tid] = session_file
            continue
        # Short-id fallback: first 8 chars (GDPVal UUID truncation)
        short = str(tid)[:8]
        short_file = job_dir / f"{short}__trial_1" / "session.jsonl"
        if short_file.exists():
            found[tid] = short_file
    return found


# ---------------------------------------------------------------------------
# Task feedback
# ---------------------------------------------------------------------------


def load_task_feedback(job_dir: Path, task_id: str) -> dict:
    """Load evaluation feedback from result.json + verifier/."""
    trial_dir = job_dir / f"{task_id}__trial_1"
    reward, status, feedback_text = 0.0, "unknown", ""

    result_file = trial_dir / "result.json"
    if result_file.exists():
        try:
            data = json.loads(result_file.read_bytes())
            reward = float(data.get("verifier_result", {}).get("reward", 0.0))
            status = data.get("agent_result", {}).get("completion_status", "unknown")
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    verifier_dir = trial_dir / "verifier"
    if verifier_dir.is_dir():
        for fname in ("eval_details.json", "details.json"):
            f = verifier_dir / fname
            if not f.exists():
                continue
            try:
                details = json.loads(f.read_bytes())
                feedback_text = details.get("feedback", "")
                if not feedback_text:
                    jr = details.get("judge_result", {})
                    if isinstance(jr, dict):
                        feedback_text = jr.get("reasoning") or ""
                break
            except (json.JSONDecodeError, ValueError):
                continue

    return {"reward": reward, "status": status, "feedback": feedback_text}


# ---------------------------------------------------------------------------
# EverOS v2 API (EverOS 1.2.3)
# ---------------------------------------------------------------------------


def _sender_id_for_role(role: str, agent_id: str) -> str:
    if role == "assistant":
        return agent_id
    if role == "tool":
        return "tool_runner"
    return "benchmark_user"


async def check_everos_health(client, base_url: str) -> None:
    resp = await client.get(f"{base_url}/health")
    resp.raise_for_status()
    if resp.json().get("status") != "ok":
        raise RuntimeError(f"Unexpected EverOS health response: {resp.text}")


async def send_session(
    client,
    messages,
    session_id,
    agent_id,
    base_url,
    app_id="evoagentbench",
    project_id="default",
):
    """Send and flush one trajectory using the public EverOS v2 contract."""
    ts_base = int(datetime.now(timezone.utc).timestamp() * 1000)
    api_msgs = []
    for i, msg in enumerate(messages):
        source_role = msg.get("role", "user")
        role = source_role if source_role in {"user", "assistant", "tool"} else "user"
        content = msg.get("content") or ""
        if role != source_role:
            content = f"[{source_role} message]\n{content}"
        api_msg = {
            "sender_id": _sender_id_for_role(role, agent_id),
            "role": role,
            "content": content,
            "timestamp": ts_base + i,
        }
        if msg.get("tool_calls"):
            api_msg["tool_calls"] = msg["tool_calls"]
        if msg.get("tool_call_id"):
            api_msg["tool_call_id"] = msg["tool_call_id"]
        api_msgs.append(api_msg)

    for start in range(0, len(api_msgs), EVEROS_MAX_MESSAGE_BATCH):
        resp = await client.post(
            f"{base_url}{EVEROS_MEMORY_API}/add",
            json={
                "session_id": session_id,
                "app_id": app_id,
                "project_id": project_id,
                "messages": api_msgs[start : start + EVEROS_MAX_MESSAGE_BATCH],
            },
        )
        resp.raise_for_status()

    resp = await client.post(
        f"{base_url}{EVEROS_MEMORY_API}/flush",
        json={
            "session_id": session_id,
            "app_id": app_id,
            "project_id": project_id,
        },
    )
    resp.raise_for_status()


async def fetch_skills(
    client,
    agent_id,
    base_url,
    app_id="evoagentbench",
    project_id="default",
) -> list[dict]:
    all_skills, page = [], 1
    while True:
        resp = await client.post(
            f"{base_url}{EVEROS_MEMORY_API}/get",
            json={
                "agent_id": agent_id,
                "app_id": app_id,
                "project_id": project_id,
                "memory_type": "agent_skill",
                "page": page,
                "page_size": 100,
                "sort_by": "updated_at",
                "sort_order": "desc",
            },
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        skills = data.get("agent_skills", [])
        all_skills.extend(skills)
        if len(all_skills) >= data.get("total_count", 0) or not skills:
            break
        page += 1
    return all_skills


def _skills_fingerprint(skills: list[dict]) -> str:
    parts = [
        f"{s.get('id')}:{s.get('cluster_id')}:{s.get('content', '')}"
        for s in sorted(skills, key=lambda x: x.get("id", ""))
    ]
    return hashlib.md5("|".join(parts).encode()).hexdigest()


async def wait_for_skills_stable(
    client,
    agent_id,
    base_url,
    app_id="evoagentbench",
    project_id="default",
    poll_interval=60,
    max_wait=3600,
) -> list[dict]:
    prev_fp, elapsed = None, 0
    while max_wait <= 0 or elapsed < max_wait:
        skills = await fetch_skills(client, agent_id, base_url, app_id, project_id)
        fp = _skills_fingerprint(skills)
        print(f"    Poll: {len(skills)} skills, fp={fp[:8]}, elapsed={elapsed}s")
        if skills and fp == prev_fp:
            return skills
        prev_fp = fp
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    log.warning(f"Skills not stable after {max_wait}s, returning latest")
    return await fetch_skills(client, agent_id, base_url, app_id, project_id)


# ---------------------------------------------------------------------------
# Skill saving
# ---------------------------------------------------------------------------


def save_skills(skills: list[dict], output_dir: Path):
    from collections import defaultdict

    by_cluster = defaultdict(list)
    for skill in skills:
        # The public v2 response does not expose EverOS's internal cluster ID.
        # Export such skills globally so static-file evaluation remains usable.
        by_cluster[skill.get("cluster_id") or "GLOBAL"].append(skill)

    for cluster_id, cluster_skills in by_cluster.items():
        cluster_dir = output_dir / cluster_id
        cluster_dir.mkdir(parents=True, exist_ok=True)
        for i, skill in enumerate(cluster_skills, 1):
            slug = (
                skill.get("name", f"skill_{i}")
                .lower()
                .replace(" ", "_")
                .replace("/", "-")
                .replace(".", "")[:60]
            )
            skill_dir = cluster_dir / slug
            skill_dir.mkdir(parents=True, exist_ok=True)
            desc = skill.get("description", "")
            content = skill.get("content", "")
            md = f"---\nname: {slug}\ndescription: >\n  {desc}\nalways: true\n---\n\n{content}"
            (skill_dir / "SKILL.md").write_text(md)
        print(f"    {cluster_id}: {len(cluster_skills)} skills")

    print(
        f"  Saved {len(skills)} skills across {len(by_cluster)} clusters to {output_dir}"
    )


# ---------------------------------------------------------------------------
# Resolve helpers
# ---------------------------------------------------------------------------


def resolve_split_file(args_split_file: str | None, domain_name: str) -> Path | None:
    """Resolve split file: CLI arg > domain config > None."""
    if args_split_file:
        p = Path(args_split_file)
        if not p.exists():
            raise FileNotFoundError(f"Split file not found: {p}")
        return p

    bench_cfg = get_domain_config(domain_name)
    split_file = bench_cfg.get("split_file")
    if split_file:
        p = Path(split_file)
        if p.exists():
            return p

    return None


def _load_eval_config() -> dict:
    cfg_path = Path(__file__).resolve().parent / "config.yaml"
    if cfg_path.exists():
        import yaml

        with open(cfg_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def _resolve_job_dir(job_dir_str: str, global_cfg: dict) -> Path:
    if job_dir_str == "latest":
        jobs_root = Path(global_cfg.get("job_dir", "./jobs"))
        candidates = [p for p in jobs_root.iterdir() if p.is_dir()]
        if not candidates:
            raise FileNotFoundError(f"No job directories found in {jobs_root}")
        return max(candidates, key=lambda p: p.stat().st_mtime)
    return Path(job_dir_str)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main():
    eval_cfg = _load_eval_config()

    parser = argparse.ArgumentParser(description="Extract skills via EverOS 1.2.3+")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    parser.add_argument("--job-dir", default=None)
    parser.add_argument("--domain", default=None)
    parser.add_argument("--split-file", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument(
        "--api-url",
        default=None,
        help=f"EverOS API (default: {DEFAULT_EVEROS_API_URL})",
    )
    parser.add_argument("--agent-id", default=None)
    parser.add_argument("--app-id", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--clusters", nargs="*")
    parser.add_argument("--split", default=None, help="Which split (default: train)")
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="(deprecated) sessions are now sent serially",
    )
    parser.add_argument("--poll-interval", type=int, default=None)
    parser.add_argument(
        "--max-wait",
        type=int,
        default=None,
        help="Maximum seconds to wait for stable skills; <=0 waits indefinitely",
    )
    parser.add_argument(
        "--success-only", action="store_true", help="Only send successful sessions"
    )
    args = parser.parse_args()

    config_path = args.config or str(_PROJECT_ROOT / "config.yaml")
    load_config(config_path)
    cfg = get_config()
    domain_name = args.domain or cfg["domain"]["name"]

    api_url = args.api_url or eval_cfg.get("api_url", DEFAULT_EVEROS_API_URL)
    app_id = args.app_id or eval_cfg.get("app_id", "evoagentbench")
    project_id = args.project_id or eval_cfg.get("project_id", domain_name)
    poll_interval = args.poll_interval or eval_cfg.get("poll_interval", 60)
    max_wait = args.max_wait
    if max_wait is None:
        max_wait = eval_cfg.get("max_wait", 3600)
    output_dir_str = args.output_dir or eval_cfg.get(
        "skills_dir", "src/skill_evolution/evermemos/skills"
    )
    split = args.split or eval_cfg.get("split_extract", "train")
    job_dir_str = args.job_dir or eval_cfg.get("job_dir", "latest")

    split_file = resolve_split_file(args.split_file, domain_name)
    job_dir = _resolve_job_dir(job_dir_str, cfg)
    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)

    if split_file:
        task_clusters = load_task_clusters(split_file, split, args.clusters)
    else:
        print(f"  No split file for {domain_name}, loading from adapter")
        domain = get_domain(domain_name)
        task_clusters = load_splits_from_adapter(domain, split)

    all_sessions = {}
    for cluster_name, task_ids in task_clusters.items():
        sessions = find_sessions(job_dir, task_ids)
        missing = set(task_ids) - set(sessions.keys())
        if missing:
            print(f"  WARNING: {cluster_name} missing {len(missing)} sessions")
        all_sessions.update(sessions)

    if not all_sessions:
        print("No sessions found. Run train split first.")
        return

    agent_id = args.agent_id or f"evoagentbench_{domain_name}_{uuid.uuid4().hex[:6]}"

    metadata_path = output_dir / f"metadata_{agent_id}.json"
    with open(metadata_path, "w") as f:
        json.dump(
            {
                "agent_id": agent_id,
                "api_url": api_url,
                "app_id": app_id,
                "project_id": project_id,
                "domain": domain_name,
                "job_dir": str(job_dir),
                "sessions": len(all_sessions),
            },
            f,
            indent=2,
        )

    print("EverOS Skill Extraction (v2 API)")
    print(f"  Domain: {domain_name}")
    print(f"  API: {api_url}")
    print(f"  Job: {job_dir}")
    print(f"  Sessions: {len(all_sessions)}")
    print(f"  Agent ID: {agent_id}")
    print(f"  Scope: {app_id}/{project_id}")
    print(f"  Success only: {args.success_only}")

    async with httpx.AsyncClient(timeout=1800.0) as client:
        try:
            await check_everos_health(client, api_url)
        except Exception as e:
            print(f"\n  ERROR: Cannot connect to EverOS at {api_url}: {e}")
            sys.exit(1)

        print(f"\n  Phase 1: Sending {len(all_sessions)} sessions (serial)...")
        sent = skipped = empty = failed = 0
        failures = []

        async def _send_one(tid, session_path):
            nonlocal sent, skipped, empty, failed
            messages = load_session_messages(session_path)
            if not messages:
                empty += 1
                print(f"    [empty] {tid}: no messages loaded")
                return

            if args.success_only:
                feedback = load_task_feedback(job_dir, tid)
                if feedback["reward"] <= 0:
                    skipped += 1
                    return

            try:
                await send_session(
                    client,
                    messages,
                    f"session_{tid}",
                    agent_id,
                    api_url,
                    app_id,
                    project_id,
                )
            except Exception as e:
                failed += 1
                failures.append((tid, type(e).__name__, str(e)[:200]))
                print(f"    [FAIL] {tid}: {type(e).__name__}: {str(e)[:200]}")
                return
            sent += 1
            if sent % 20 == 0:
                print(f"    Sent {sent}/{len(all_sessions)}")

        for tid, p in all_sessions.items():
            try:
                await _send_one(tid, p)
            except Exception as e:
                failed += 1
                failures.append((tid, type(e).__name__, str(e)[:200]))
                print(f"    [FAIL] {tid}: {type(e).__name__}: {str(e)[:200]}")
            await asyncio.sleep(1)
        print(
            f"    Sent {sent}/{len(all_sessions)}"
            f"{f', skipped {skipped}' if skipped else ''}"
            f"{f', empty {empty}' if empty else ''}"
            f"{f', failed {failed}' if failed else ''}"
        )
        if failures:
            print(f"\n  Failed sessions ({len(failures)}):")
            for tid, etype, emsg in failures[:20]:
                print(f"    {tid}: {etype}: {emsg}")

        # Each flush starts EverOS's asynchronous case/cluster/skill pipeline.

        print(f"\n  Phase 2: Waiting for skills (poll every {poll_interval}s)...")
        skills = await wait_for_skills_stable(
            client,
            agent_id,
            api_url,
            app_id,
            project_id,
            poll_interval=poll_interval,
            max_wait=max_wait,
        )
        print(f"    Final: {len(skills)} skills")

        if skills:
            save_skills(skills, output_dir)

    print(f"\nDone! Agent ID: {agent_id}")


if __name__ == "__main__":
    asyncio.run(main())
