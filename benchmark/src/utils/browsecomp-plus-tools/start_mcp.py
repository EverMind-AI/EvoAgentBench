#!/usr/bin/env python3
"""Start the BrowseComp-Plus MCP search server from a domain YAML."""

import argparse
import os
import sys
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SEARCHER_DIR = SCRIPT_DIR / "searcher"
DEFAULT_CONFIG = (
    SCRIPT_DIR
    / ".."
    / ".."
    / "domains"
    / "information_retrieval"
    / "information_retrieval.yaml"
).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the BrowseComp-Plus MCP search server.",
    )
    parser.add_argument(
        "config",
        type=Path,
        nargs="?",
        default=DEFAULT_CONFIG,
        help="domain YAML (default: information_retrieval.yaml)",
    )
    return parser.parse_args()


def resolve_local_path(value: str, config_dir: Path) -> str:
    """Resolve explicit relative paths while leaving model IDs unchanged."""
    if not value or Path(value).is_absolute():
        return value
    candidate = config_dir / value
    prefix = str(candidate).split("*", 1)[0]
    if value.startswith(".") or Path(prefix).exists():
        return str(candidate.resolve())
    return value


def configure_java() -> None:
    """Use a Conda-provided JDK when JAVA_HOME/JVM_PATH are unset."""
    prefix = Path(sys.prefix)
    if not os.environ.get("JAVA_HOME") and (prefix / "bin" / "java").exists():
        os.environ["JAVA_HOME"] = str(prefix)
    jvm = prefix / "lib" / "jvm" / "lib" / "server" / "libjvm.so"
    if not os.environ.get("JVM_PATH") and jvm.exists():
        os.environ["JVM_PATH"] = str(jvm)


def main() -> None:
    args = parse_args()
    config_path = args.config.expanduser().resolve()
    with config_path.open(encoding="utf-8") as handle:
        root = yaml.safe_load(handle) or {}
    cfg = root.get("mcp_server")
    if not isinstance(cfg, dict):
        raise ValueError(f"Missing mcp_server mapping in {config_path}")
    if not cfg.get("index_path"):
        raise ValueError(f"Missing mcp_server.index_path in {config_path}")

    config_dir = config_path.parent
    for key in ("index_path", "model_name"):
        cfg[key] = resolve_local_path(cfg.get(key, ""), config_dir)

    configure_java()
    searcher_dir = str(SEARCHER_DIR)
    if searcher_dir not in sys.path:
        sys.path.insert(0, searcher_dir)

    argv = [
        "mcp_server",
        "--searcher-type",
        cfg.get("searcher_type", "faiss"),
        "--index-path",
        cfg["index_path"],
        "--transport",
        "sse",
        "--port",
        str(cfg.get("port", 9100)),
        "--k",
        str(cfg.get("k", 5)),
        "--snippet-max-tokens",
        str(cfg.get("snippet_max_tokens", 512)),
    ]
    if cfg.get("model_name"):
        argv += ["--model-name", cfg["model_name"]]
    if cfg.get("get_document", False):
        argv.append("--get-document")
    sys.argv = argv

    from mcp_server import main as mcp_main

    mcp_main()


if __name__ == "__main__":
    main()
