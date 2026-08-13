"""Contract tests for the public EverOS v2 integration."""

import asyncio
import sys
from pathlib import Path

EVEROS_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "skill_evolution" / "evermemos"
)
sys.path.insert(0, str(EVEROS_DIR))

from eval_with_skills import _search_one  # noqa: E402
from extract_skills import (  # noqa: E402
    check_everos_health,
    fetch_skills,
    send_session,
)


class StubResponse:
    def __init__(self, payload):
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class RecordingClient:
    def __init__(self, post_payloads=None):
        self.post_payloads = list(post_payloads or [])
        self.posts = []
        self.gets = []

    async def get(self, url):
        self.gets.append(url)
        return StubResponse({"status": "ok"})

    async def post(self, url, json):
        self.posts.append((url, json))
        payload = self.post_payloads.pop(0) if self.post_payloads else {"data": {}}
        return StubResponse(payload)


def test_health_uses_public_endpoint():
    client = RecordingClient()

    asyncio.run(check_everos_health(client, "http://127.0.0.1:8000"))

    assert client.gets == ["http://127.0.0.1:8000/health"]


def test_send_session_uses_v2_contract_and_batches_messages():
    client = RecordingClient()
    messages = [{"role": "user", "content": "question"}]
    messages.extend({"role": "assistant", "content": f"answer-{i}"} for i in range(500))

    asyncio.run(
        send_session(
            client,
            messages,
            "session_task-1",
            "agent_eval",
            "http://127.0.0.1:8000",
            "evoagentbench",
            "software_engineering",
        )
    )

    assert [url for url, _ in client.posts] == [
        "http://127.0.0.1:8000/api/v2/memory/add",
        "http://127.0.0.1:8000/api/v2/memory/add",
        "http://127.0.0.1:8000/api/v2/memory/flush",
    ]
    first_batch = client.posts[0][1]
    second_batch = client.posts[1][1]
    assert len(first_batch["messages"]) == 500
    assert len(second_batch["messages"]) == 1
    assert first_batch["messages"][0]["sender_id"] == "benchmark_user"
    assert first_batch["messages"][1]["sender_id"] == "agent_eval"
    assert "message_id" not in first_batch["messages"][0]
    assert first_batch["app_id"] == "evoagentbench"
    assert first_batch["project_id"] == "software_engineering"


def test_fetch_skills_uses_agent_owner_and_v2_response_shape():
    skills = [{"id": "agent_eval_planner", "name": "planner", "content": "plan"}]
    client = RecordingClient(
        [{"data": {"agent_skills": skills, "total_count": 1, "count": 1}}]
    )

    result = asyncio.run(
        fetch_skills(
            client,
            "agent_eval",
            "http://127.0.0.1:8000",
            "evoagentbench",
            "code_implementation",
        )
    )

    assert result == skills
    url, payload = client.posts[0]
    assert url == "http://127.0.0.1:8000/api/v2/memory/get"
    assert payload["agent_id"] == "agent_eval"
    assert payload["memory_type"] == "agent_skill"
    assert "filters" not in payload


def test_search_reads_public_agent_skill_and_case_arrays():
    client = RecordingClient(
        [
            {
                "data": {
                    "agent_skills": [
                        {
                            "name": "debug systematically",
                            "description": "Use evidence before edits",
                            "content": "Reproduce, isolate, then patch.",
                            "score": 0.9,
                        }
                    ],
                    "agent_cases": [
                        {
                            "task_intent": "Fix a regression",
                            "approach": "Add a focused reproduction.",
                            "key_insight": "Test the failing boundary.",
                            "score": 0.8,
                        }
                    ],
                }
            }
        ]
    )

    task_id, text = asyncio.run(
        _search_one(
            client,
            "http://127.0.0.1:8000",
            "agent_eval",
            "evoagentbench",
            "software_engineering",
            "task-1",
            "How should I debug this regression?",
            2,
            "hybrid",
            max_retries=1,
        )
    )

    assert task_id == "task-1"
    assert "debug systematically" in text
    assert "Fix a regression" in text
    url, payload = client.posts[0]
    assert url == "http://127.0.0.1:8000/api/v2/memory/search"
    assert payload == {
        "agent_id": "agent_eval",
        "app_id": "evoagentbench",
        "project_id": "software_engineering",
        "query": "How should I debug this regression?",
        "method": "hybrid",
        "top_k": 2,
    }
