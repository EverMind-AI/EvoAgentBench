#!/usr/bin/env python3
"""Run evaluation with skills injected into prompts.

Three skill sources (mutually exclusive):

1. **Skill cache** (--skill-cache): reuse previously searched/saved skills JSON.
2. **API search** (--api-url + --agent-id): query the EverOS v2 search API.
3. **Static files** (--skills-dir): load SKILL.md files from disk.

Skills are appended to each domain's prompt under a clearly delimited strategy
section.

Usage:
    # API search
    python eval_with_skills.py --api-url http://127.0.0.1:8000 --agent-id AGENT_ID

    # Static files
    python eval_with_skills.py --skills-dir src/skill_evolution/evermemos/skills

    # Reuse cached skills
    python eval_with_skills.py --skill-cache jobs/prev-run/skill_cache.json
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_EVAL_DIR))

_env_file = _PROJECT_ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

import httpx  # noqa: E402
from config import get_agent, get_domain, get_config, load_config  # noqa: E402
from extract_skills import (  # noqa: E402
    DEFAULT_EVEROS_API_URL,
    EVEROS_MEMORY_API,
    load_splits_from_adapter,
    load_task_clusters,
    resolve_split_file,
)
from domain_info import get_task_query  # noqa: E402
from runner import run_all  # noqa: E402


# ---------------------------------------------------------------------------
# Skill source: Static files
# ---------------------------------------------------------------------------


def _load_skill_dir(skill_dir: Path) -> str:
    if not skill_dir.exists():
        return ""
    parts = []
    for sub_dir in sorted(skill_dir.iterdir()):
        skill_file = sub_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        content = skill_file.read_text()
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3 :].strip()
        parts.append(content)
    return "\n\n".join(parts)


def load_cluster_skills(skills_dir: Path, cluster_name: str) -> str:
    """Load GLOBAL + cluster-specific skills from disk."""
    parts = []
    global_text = _load_skill_dir(skills_dir / "GLOBAL")
    if global_text:
        parts.append(global_text)
    cluster_text = _load_skill_dir(skills_dir / cluster_name)
    if cluster_text:
        parts.append(cluster_text)
    return "\n\n".join(parts)


def load_skills_from_files(skills_dir: Path, task_clusters: dict) -> dict:
    """Load skills from disk for all tasks. Returns {tid: skills_text}."""
    task_skills = {}
    for cluster_name, task_ids in task_clusters.items():
        skills_text = load_cluster_skills(skills_dir, cluster_name)
        if not skills_text:
            print(f"  SKIP {cluster_name}: no skills in {skills_dir / cluster_name}")
            continue
        for tid in task_ids:
            task_skills[tid] = skills_text
        print(f"  {cluster_name}: {len(task_ids)} tasks, skills loaded")
    return task_skills


# ---------------------------------------------------------------------------
# Skill source: EverOS v2 search API
# ---------------------------------------------------------------------------


async def _search_one(
    client,
    api_url,
    agent_id,
    app_id,
    project_id,
    tid,
    question,
    top_k,
    method,
    max_retries=5,
    base_delay=10.0,
    include_cases=True,
    case_score_threshold=0.0,
):
    if not question.strip():
        return tid, ""
    payload = {
        "agent_id": agent_id,
        "app_id": app_id,
        "project_id": project_id,
        "query": question,
        "method": method,
        "top_k": top_k,
    }
    for attempt in range(max_retries):
        try:
            resp = await client.post(
                f"{api_url}{EVEROS_MEMORY_API}/search", json=payload
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            break
        except Exception as e:
            err_repr = repr(e) if not str(e) else str(e)
            if attempt < max_retries - 1:
                # exponential backoff: 10s, 20s, 40s, 60s (capped). Long backoff
                # because LLM provider load spikes can last minutes — short
                # retries just compound the queue pressure.
                delay = min(base_delay * (2**attempt), 60.0)
                print(
                    f"    WARN: search retry {attempt + 1}/{max_retries} for tid={tid} after err={err_repr}; sleeping {delay:.0f}s"
                )
                await asyncio.sleep(delay)
            else:
                # exhausted retries — propagate so caller can log full context
                raise RuntimeError(
                    f"search failed for tid={tid} after {max_retries} attempts: {err_repr}"
                ) from e
    skills = data.get("agent_skills", [])
    cases = data.get("agent_cases", [])
    skill_parts = []
    for skill in skills:
        name = skill.get("name", "")
        description = skill.get("description", "")
        content = skill.get("content", "")
        if content:
            skill_parts.append(
                f"### {name}\ndescription: {description}\ncontent:\n{content}"
            )
    # Cases (past trajectories) are appended after skills when include_cases
    # is True. Toggle is global — set by the caller from EVAL_INCLUDE_CASES.
    # Optional retrieval-score threshold filter via CASE_SCORE_THRESHOLD env
    # var (default 0.0 = no filter). Useful to drop weakly-matching past cases
    # that may distract more than help.
    case_parts = []
    if include_cases:
        for case in cases:
            score = case.get("score")
            if (
                case_score_threshold > 0.0
                and score is not None
                and score < case_score_threshold
            ):
                continue
            intent = (case.get("task_intent") or "").strip()
            approach = (case.get("approach") or "").strip()
            insight = (case.get("key_insight") or "").strip()
            if not approach:
                continue
            block = f"### Past task: {intent}\n\n{approach}"
            if insight:
                block += f"\n\n**Key insight**: {insight}"
            case_parts.append(block)
    text = "\n\n".join(skill_parts)
    if case_parts:
        if text:
            text += "\n\n---\n\n#### Reference past cases\n\n" + "\n\n".join(case_parts)
        else:
            text = "#### Reference past cases\n\n" + "\n\n".join(case_parts)
    return tid, text


async def search_all_skills(
    api_url,
    agent_id,
    app_id,
    project_id,
    task_questions,
    top_k,
    parallel,
    method="vector",
    include_cases=True,
    case_score_threshold=0.0,
):
    sem = asyncio.Semaphore(parallel)
    results = {}
    done = [0]
    total = len(task_questions)

    async def _bounded(tid, question):
        async with sem:
            tid, text = await _search_one(
                client,
                api_url,
                agent_id,
                app_id,
                project_id,
                tid,
                question,
                top_k,
                method,
                include_cases=include_cases,
                case_score_threshold=case_score_threshold,
            )
            done[0] += 1
            if done[0] % 20 == 0 or done[0] == total:
                print(f"    Searched {done[0]}/{total}")
            return tid, text

    fatal_failures = []
    async with httpx.AsyncClient(timeout=900.0) as client:
        tasks = [_bounded(tid, q) for tid, q in task_questions.items()]
        for coro in asyncio.as_completed(tasks):
            try:
                tid, text = await coro
                if text:
                    results[tid] = text
            except Exception as e:
                # _search_one raises RuntimeError with tid + repr(e) once retries
                # exhausted; preserve that diagnostic instead of swallowing it.
                err_repr = repr(e) if not str(e) else str(e)
                print(f"    WARNING: search failed (retries exhausted): {err_repr}")
                fatal_failures.append(err_repr)

    print(f"    final coverage: {len(results)}/{total} tasks have skills")
    if fatal_failures:
        print(
            f"    ERROR_SUMMARY: {len(fatal_failures)}/{total} search calls failed even after retries:"
        )
        for fe in fatal_failures[:5]:
            print(f"      - {fe}")
        # If a substantial fraction failed, surface as a hard error so the run
        # gets re-tried instead of producing scores from a partial cache.
        fail_frac = len(fatal_failures) / max(total, 1)
        if fail_frac > 0.05:
            raise RuntimeError(
                f"search failures exceeded 5% threshold ({len(fatal_failures)}/{total} = {fail_frac:.1%}). "
                "Aborting eval; re-run after LLM provider load subsides."
            )
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _load_eval_config() -> dict:
    cfg_path = Path(__file__).resolve().parent / "config.yaml"
    if cfg_path.exists():
        import yaml

        with open(cfg_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    eval_cfg = _load_eval_config()

    parser = argparse.ArgumentParser(description="Evaluate with skills injected")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--split-file", default=None)
    # Skill source: API
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--agent-id", default=None)
    parser.add_argument("--app-id", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--search-method", default="hybrid")
    # Skill source: static
    parser.add_argument("--skills-dir", default=None)
    # Skill source: cache
    parser.add_argument(
        "--skill-cache", default=None, help="Reuse saved skill_cache.json"
    )
    # Common
    parser.add_argument("--task", default=None)
    parser.add_argument("--clusters", nargs="*")
    parser.add_argument("--split", default=None)
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument(
        "--trials", type=int, default=None, help="Trials per task (pass@k)"
    )
    parser.add_argument(
        "--parallel-trials",
        action="store_true",
        help="Schedule individual task/trial pairs concurrently instead of running trials serially per task",
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--job", default=None)
    args = parser.parse_args()

    config_path = args.config or str(_PROJECT_ROOT / "config.yaml")
    load_config(config_path)
    cfg = get_config()
    domain_name = args.domain or cfg["domain"]["name"]
    split = args.split or eval_cfg.get("split_eval", "test")

    domain = get_domain(domain_name)

    # Resolve task IDs
    if args.task:
        all_task_ids = [t.strip() for t in args.task.split(",")]
        task_clusters = {"default": all_task_ids}
    else:
        split_file = resolve_split_file(args.split_file, domain_name)
        if split_file:
            task_clusters = load_task_clusters(split_file, split, args.clusters)
        else:
            print(f"  No split file for {domain_name}, loading from adapter")
            task_clusters = load_splits_from_adapter(domain, split)
        all_task_ids = list(
            dict.fromkeys(tid for ids in task_clusters.values() for tid in ids)
        )

    # --- Determine skill source ---
    use_api = bool(args.api_url or args.agent_id)
    metadata = {}
    if use_api and not args.agent_id:
        skills_dir = Path(
            args.skills_dir
            or eval_cfg.get("skills_dir", "src/skill_evolution/evermemos/skills")
        )
        meta_files = sorted(
            skills_dir.glob("metadata_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if meta_files:
            metadata = json.loads(meta_files[0].read_text())
            args.agent_id = metadata.get("agent_id")
            if not args.api_url:
                args.api_url = metadata.get("api_url")
            print(f"  Auto-loaded agent_id={args.agent_id} from {meta_files[0].name}")
        if not args.agent_id:
            print("ERROR: --agent-id required for API search mode.")
            return

    api_url = args.api_url or eval_cfg.get("api_url", DEFAULT_EVEROS_API_URL)
    app_id = (
        args.app_id or metadata.get("app_id") or eval_cfg.get("app_id", "evoagentbench")
    )
    project_id = (
        args.project_id
        or metadata.get("project_id")
        or eval_cfg.get("project_id", domain_name)
    )

    if args.skill_cache:
        task_skills = json.loads(Path(args.skill_cache).read_text())
        print(f"Skill source: cache ({args.skill_cache}), {len(task_skills)} tasks")

    elif use_api:
        print(f"Skill source: EverOS search ({args.search_method}, top_k={args.top_k})")
        bench_cfg = {}
        try:
            from config import get_domain_config

            bench_cfg = get_domain_config(domain_name)
        except Exception:
            pass

        tmp_args = argparse.Namespace(
            task=",".join(all_task_ids),
            split=None,
            trials=1,
            parallel=1,
            max_retries=0,
            live=False,
            disk_budget=None,
        )
        tasks_list = domain.load_tasks(tmp_args)
        task_questions = {}
        for t in tasks_list:
            query = get_task_query(domain_name, t, bench_cfg)
            if query:
                task_questions[str(t["name"])] = query

        print(f"  Tasks: {len(task_questions)}")
        # EVAL_INCLUDE_CASES=0 to disable for ablation runs.
        include_cases = os.environ.get("EVAL_INCLUDE_CASES", "1") in (
            "1",
            "true",
            "True",
        )
        case_score_threshold = float(os.environ.get("CASE_SCORE_THRESHOLD", "0.0"))
        print(
            f"  Case injection: include={include_cases} threshold={case_score_threshold} (domain={domain_name})"
        )
        task_skills = asyncio.run(
            search_all_skills(
                api_url,
                args.agent_id,
                app_id,
                project_id,
                task_questions,
                args.top_k,
                args.parallel,
                args.search_method,
                include_cases=include_cases,
                case_score_threshold=case_score_threshold,
            )
        )
        print(f"  {len(task_skills)}/{len(task_questions)} tasks with skills\n")

    else:
        skills_dir = Path(
            args.skills_dir
            or eval_cfg.get("skills_dir", "src/skill_evolution/evermemos/skills")
        )
        print(f"Skill source: static files ({skills_dir})")
        task_skills = load_skills_from_files(skills_dir, task_clusters)

    print(
        f"Skill entries loaded: {len(task_skills)}; selected task ids: {len(all_task_ids)}"
    )
    if not task_skills:
        print("No tasks with skills. Exiting.")
        return

    def _skill_text_for_task(task: dict) -> str:
        name = task.get("name")
        if name is not None:
            text = task_skills.get(str(name))
            if text:
                return text

        task_id = task.get("task_id")
        if task_id is not None:
            task_id = str(task_id)
            # Avoid cross-domain collisions from numeric IDs in a global cache.
            if any(ch in task_id for ch in ("-", "_")):
                text = task_skills.get(task_id)
                if text:
                    return text
        return ""

    _original = domain.__class__.build_prompt

    def _patched(self, task, env_info):
        prompt = _original(self, task, env_info)
        text = _skill_text_for_task(task)
        if text:
            prompt += (
                "\n\n## Domain-Specific Strategies\n\n"
                "The following strategies may help when their trigger conditions match this task. "
                "Use only the applicable parts; the task statement and verifier requirements take priority:\n\n"
                + text
            )
        return prompt

    domain.__class__.build_prompt = _patched

    # --- Run ---
    agent = get_agent(cfg["agent"]["name"])
    from datetime import datetime
    import uuid

    job_name = (
        args.job
        or f"everos-{domain_name}-{datetime.now().strftime('%m%d_%H%M')}-{uuid.uuid4().hex[:4]}"
    )
    job_dir = Path(cfg["job_dir"]) / job_name
    job_dir.mkdir(parents=True, exist_ok=True)

    cache_path = job_dir / "skill_cache.json"
    with open(cache_path, "w") as f:
        json.dump(task_skills, f, ensure_ascii=False, indent=2)

    run_args = argparse.Namespace(
        task=",".join(all_task_ids),
        split=None,
        trials=args.trials or cfg.get("trials", 1),
        parallel=args.parallel,
        max_retries=cfg.get("max_retries", 2),
        live=args.live,
        disk_budget=None,
        parallel_trials=args.parallel_trials,
    )

    tasks = domain.load_tasks(run_args)
    matched_skill_tasks = sum(1 for t in tasks if _skill_text_for_task(t))
    print(f"Resolved skill coverage: {matched_skill_tasks}/{len(tasks)} tasks")

    print(f"Running {len(tasks)} tasks ({matched_skill_tasks} with skills)\n")
    run_all(tasks, domain, agent, job_dir, run_args)


if __name__ == "__main__":
    main()
