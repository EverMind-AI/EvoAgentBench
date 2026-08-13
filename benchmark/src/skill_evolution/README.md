# Self-Evolution Evaluation

The public release supports two paths:

- **Baseline** runs the benchmark through `src/run.py` without an evolution state.
- **EverOS** uses the public EverOS service to extract reusable skills from training
  trajectories and inject retrieved skills during test evaluation.

Third-party method integrations and experiment outputs are not included.

## Workflow

1. Run `src/run.py --split train` to collect training sessions.
2. Run `evermemos/extract_skills.py` to send those sessions to EverOS.
3. Run `evermemos/eval_with_skills.py --split test` with retrieved skills.
4. Run `src/run.py --split test` as the matched baseline.

See [evermemos/README.md](evermemos/README.md) for setup and command details.
Official paper splits are documented in [data/splits/README.md](../../data/splits/README.md).
