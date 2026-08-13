"""Nanobot agent adapter."""

import json
import shutil
import tempfile
from pathlib import Path

from agents.base import AgentAdapter, C_MAGENTA, C_RESET
from config import get_config, register_agent


class NanobotAdapter(AgentAdapter):
    name = "nanobot"

    def __init__(self):
        self._temp_workspace = None
        self._temp_config = None

    def _session_dir(self) -> Path:
        if self._temp_workspace:
            return Path(self._temp_workspace) / "sessions"
        nanobot_config = Path.home() / ".nanobot" / "config.json"
        if nanobot_config.exists():
            workspace = Path(
                json.loads(nanobot_config.read_text())
                .get("agents", {})
                .get("defaults", {})
                .get("workspace", str(Path.home() / ".nanobot" / "workspace"))
            ).expanduser()
            return workspace / "sessions"
        return Path.home() / ".nanobot" / "workspace" / "sessions"

    def _session_file(self, session_id):
        safe_key = session_id.replace(":", "_")
        base = (
            Path(self._temp_workspace)
            if self._temp_workspace
            else self._session_dir().parent
        )
        return base / "sessions" / f"{safe_key}.jsonl"

    # --- Temp config (always created per task) ---

    def _ensure_temp_config(self):
        """Create per-task temp config: copy global + apply evoagentbench overrides."""
        if self._temp_workspace:
            return  # already created

        workspace_dir = Path(tempfile.mkdtemp(prefix="evoagentbench-nanobot-"))

        # Read global nanobot config as base
        global_config_path = Path.home() / ".nanobot" / "config.json"
        if global_config_path.exists():
            config = json.loads(global_config_path.read_text())
        else:
            config = {}

        # Point workspace to temp dir so sessions are written here
        config.setdefault("agents", {}).setdefault("defaults", {})
        config["agents"]["defaults"]["workspace"] = str(workspace_dir)

        # Override model/provider from evoagentbench agent config (if set)
        agent_cfg = get_config().get("agent", {})
        if agent_cfg.get("model"):
            config["agents"]["defaults"]["model"] = agent_cfg["model"]
        if agent_cfg.get("provider"):
            config["agents"]["defaults"]["provider"] = agent_cfg["provider"]
        if agent_cfg.get("providers"):
            config["providers"] = dict(agent_cfg["providers"])
        if agent_cfg.get("maxTokens") is not None:
            config["agents"]["defaults"]["maxTokens"] = agent_cfg["maxTokens"]
        if agent_cfg.get("contextWindowTokens") is not None:
            config["agents"]["defaults"]["contextWindowTokens"] = agent_cfg[
                "contextWindowTokens"
            ]
        if agent_cfg.get("temperature") is not None:
            config["agents"]["defaults"]["temperature"] = agent_cfg["temperature"]
        if agent_cfg.get("reasoningEffort") is not None:
            config["agents"]["defaults"]["reasoningEffort"] = agent_cfg[
                "reasoningEffort"
            ]
        if agent_cfg.get("max_tool_iterations") is not None:
            config["agents"]["defaults"]["maxToolIterations"] = agent_cfg[
                "max_tool_iterations"
            ]
        if agent_cfg.get("tools"):
            config.setdefault("tools", {}).update(agent_cfg["tools"])

        config_path = workspace_dir / "config.json"
        config_path.write_text(json.dumps(config, indent=2))

        self._temp_workspace = str(workspace_dir)
        self._temp_config = str(config_path)

    def _cleanup_temp_config(self):
        if self._temp_workspace:
            shutil.rmtree(self._temp_workspace, ignore_errors=True)
        self._temp_workspace = None
        self._temp_config = None

    # --- MCP lifecycle ---

    def setup_mcp(self, mcp_servers, disabled_tools=None):
        self._ensure_temp_config()
        # Patch MCP into existing temp config
        config = json.loads(Path(self._temp_config).read_text())
        config.setdefault("tools", {})
        config["tools"]["mcpServers"] = mcp_servers
        if disabled_tools:
            config["tools"]["disabledTools"] = disabled_tools
            # Nanobot still exposes the built-in web search tool from the
            # copied global config even when "web_search" is listed in
            # disabledTools. For closed-book/local-MCP benchmarks this causes
            # occasional Brave API calls and empty answers, so remove the web
            # tool config at the source when the domain disables it.
            if "web_search" in disabled_tools or "web_fetch" in disabled_tools:
                config["tools"].pop("web", None)
        Path(self._temp_config).write_text(json.dumps(config, indent=2))

    def teardown_mcp(self):
        self._cleanup_temp_config()

    # --- CLI ---

    def _build_cli_cmd(self, prompt, session_id, timeout):
        self._ensure_temp_config()
        cmd = [
            self._command(),
            "agent",
            "--session",
            session_id,
            "--message",
            prompt,
            "--no-markdown",
            "--workspace",
            self._temp_workspace,
            "--config",
            self._temp_config,
        ]
        return cmd

    def _parse_watch_record(self, rec, ts, prefix):
        role = rec.get("role", "")

        if role == "assistant" and rec.get("reasoning_content"):
            first_line = rec["reasoning_content"].strip().split("\n")[0][:120]
            if first_line:
                print(
                    f"  {C_MAGENTA}{ts} {prefix} 💭 {first_line}{C_RESET}", flush=True
                )

        if role == "assistant" and rec.get("tool_calls"):
            for tc in rec["tool_calls"]:
                func = tc.get("function", {})
                name = func.get("name", "")
                args_str = func.get("arguments", "")
                try:
                    args = (
                        json.loads(args_str) if isinstance(args_str, str) else args_str
                    )
                except json.JSONDecodeError:
                    args = {}
                if name == "exec":
                    display = (
                        args.get("command", "") if isinstance(args, dict) else str(args)
                    )
                    display = display.replace("\n", "\\n")
                else:
                    display = f"{name}({str(args)[:150]})"
                self._print_tool_call(ts, prefix, display)

        if role == "tool":
            text = rec.get("content", "")
            if text:
                self._print_tool_output(ts, prefix, text)

    def _parse_session_entry(self, entry, stats):
        super()._parse_session_entry(entry, stats)
        if entry.get("role") != "tool":
            return

        content = entry.get("content") or ""
        if not isinstance(content, str) or not content.strip():
            return

        if content.startswith("Error executing "):
            stats["tool_error_count"] = stats.get("tool_error_count", 0) + 1
            if "Analyze the error above and try a different approach." in content:
                stats["empty_tool_error_count"] = (
                    stats.get("empty_tool_error_count", 0) + 1
                )
        else:
            stats["tool_success_count"] = stats.get("tool_success_count", 0) + 1

    def should_retry(self, result):
        """Nanobot: retry transport/provider failures even if the CLI exits 0."""
        turns = result.get("token_usage", {}).get("turns", 0)
        agent_result = result.get("agent_result", {})
        completion = agent_result.get("completion_status", "")
        if turns == 0 and completion == "completed":
            return "zero_turns"

        response = agent_result.get("response") or ""
        stderr = agent_result.get("stderr") or ""
        provider_error_markers = (
            "Error calling LLM:",
            "Hosted_vllmException",
            "Server disconnected",
            "upstream connect error",
            "disconnect/reset before headers",
            "Cannot connect to host",
            "Connect call failed",
            "litellm.InternalServerError",
            "litellm.ServiceUnavailableError",
        )
        if completion == "completed" and any(
            m in response or m in stderr for m in provider_error_markers
        ):
            return "provider_error"

        usage = result.get("token_usage", {})
        tool_errors = usage.get("empty_tool_error_count", 0)
        tool_successes = usage.get("tool_success_count", 0)
        reward = result.get("verifier_result", {}).get("reward", 0)
        response_lower = response.lower()
        pseudo_tool_markers = (
            "search(query=",
            "\nsearch:",
            "search query:",
            "<tool_code>search",
            "exact answer: searching",
        )
        if (
            completion == "completed"
            and not reward
            and tool_errors == 0
            and tool_successes == 0
            and any(marker in response_lower for marker in pseudo_tool_markers)
        ):
            return "pseudo_tool_call_without_tool_execution"
        if (
            completion == "completed"
            and not reward
            and tool_errors >= 5
            and tool_successes == 0
        ):
            return "tool_infra_error"
        tool_failure_markers = (
            "technical difficulties with the search tool",
            "persistent technical issues with the search tool",
            "search tool became unresponsive",
            "search tool failures",
            "unable to definitively determine due to search tool",
        )
        if (
            completion == "completed"
            and not reward
            and tool_errors >= 8
            and any(marker in response.lower() for marker in tool_failure_markers)
        ):
            return "tool_infra_error"
        return super().should_retry(result)


register_agent("nanobot", NanobotAdapter)
