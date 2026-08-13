# Repository Guidelines

## Project Structure & Module Organization

EvoAgentBench is a Python evaluation framework for agent self-evolution. Core execution lives in `src/run.py`, `src/runner.py`, and `src/config.py`. Agent adapters are under `src/agents/` (`nanobot`, `openclaw`), while the four paper-aligned benchmark implementations are under `src/domains/` (`information_retrieval`, `code_implementation`, `software_engineering`, `knowledge_work`). The EverOS integration lives in `src/skill_evolution/evermemos/`. Shared helpers are in `src/utils/`, and tests are in `tests/`. Generated data, logs, skills, and run outputs belong in ignored runtime directories such as `data/`, `jobs/`, and `src/skill_evolution/evermemos/skills/`.

## Build, Test, and Development Commands

- `conda env create -f environment.yml && conda activate evoagentbench`: create the recommended Python 3.12 environment with JDK 21.
- `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`: install the lightweight core; add the selected `requirements-<domain>.txt` file and install JDK 21 separately when needed.
- `pip install -r requirements-dev.txt`: install the pinned test and formatting tools.
- `cp config.yaml.example config.yaml && cp .env.example .env`: create local configuration and secret templates before running evaluations.
- `python src/run.py --agent nanobot --domain software_engineering --task astropy__astropy-8872 --live`: run one paper-split benchmark task interactively.
- `python -m pytest tests`: run the repository test suite.

## Coding Style & Naming Conventions

Use Python 3.12 syntax, 4-space indentation, `snake_case` for functions and modules, and `CamelCase` for classes. Keep adapters aligned with the base interfaces in `src/agents/base.py` and `src/domains/base.py`. Domain configs are YAML files named after their domain, such as `src/domains/information_retrieval/information_retrieval.yaml`. Run `ruff check .` and `ruff format --check .` before submitting changes.

## Testing Guidelines

Tests use pytest and follow `tests/test_*.py` naming. Add focused tests for adapter contracts, config behavior, scheduling, and verifier edge cases. Prefer fast unit tests unless validating a domain that requires Docker, datasets, or external services. Run `python -m pytest tests` before submitting changes; for narrow work, run the affected test file first.

## Commit & Pull Request Guidelines

The visible Git history is minimal, so use concise imperative commit subjects, for example `Validate official split manifest`. In PRs, describe the changed domain or method, list commands run, and call out required datasets, API keys, Docker, or external services. Do not include `.env`, credentials, generated skills, large job outputs, experiment results, or machine-specific config files.

## Security & Configuration Tips

Keep secrets in `.env` or local agent YAML files, never in source. Review `config.yaml.example` and domain YAML paths before long runs, especially when using Docker-backed SWE-Bench or local BrowseComp-Plus indexes.
