"""Per-domain metadata for the EverOS integration.

New domain? Add one entry to BENCHMARK_DESCRIPTORS — everything else adapts.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class DomainInfo:
    query_field: str | None = "problem"
    query_extractor: Callable | None = None  # overrides query_field


BENCHMARK_DESCRIPTORS: dict[str, DomainInfo] = {
    "information_retrieval": DomainInfo(query_field="problem"),
    "code_implementation": DomainInfo(query_field="question_content"),
    "software_engineering": DomainInfo(query_field="problem_statement"),
    "knowledge_work": DomainInfo(query_field="prompt"),
}


def get_task_query(domain_name: str, task: dict, bench_cfg: dict = None) -> str:
    """Extract search query text from a task dict, using the registry."""
    info = BENCHMARK_DESCRIPTORS.get(domain_name, DomainInfo())

    if info.query_extractor:
        return info.query_extractor(task, bench_cfg)

    if info.query_field and info.query_field in task:
        return str(task[info.query_field])

    # Fallback: try common field names
    for key in ("problem", "query", "question", "prompt", "description"):
        if key in task:
            return str(task[key])
    return str(task.get("name", ""))
