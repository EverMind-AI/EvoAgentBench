# EvoAgentBench Website

Leaderboard and project website for **EvoAgentBench** — a benchmark for evaluating AI agent self-evolution across diverse task domains.

- **Live site**: https://evermind-ai.github.io/EvoAgentBench/
- **Paper**: [EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer](https://arxiv.org/abs/2607.05202)
- **Dataset**: [EverMind-AI/EvoAgentBench](https://huggingface.co/datasets/EverMind-AI/EvoAgentBench) on Hugging Face
- **Benchmark code**: [`benchmark/`](benchmark/README.md)

## Benchmark Code

The public benchmark implementation lives in [`benchmark/`](benchmark/README.md).
After cloning this repository, enter that directory before following its setup
instructions:

```bash
git clone https://github.com/EverMind-AI/EvoAgentBench.git
cd EvoAgentBench/benchmark
```

The website and benchmark are versioned together but remain separate projects:
the website root uses the MIT License, while `benchmark/` uses Apache License 2.0.

## Features

- Interactive leaderboard with filtering and sorting
- Filter by agent (OpenClaw, Nanobot), model, domain, and evolution condition
- Sort by method score, transfer gain, or Vanilla score
- Derived Overall across both scaffolds and four equally weighted domains
- Separate turn-cost table reproducing the paper's All/Solved/Unsolved analysis
- Paper conditions: Memento, ReasoningBank, GEPA, and Anchor Skill†
- Domain overview table with Ability/train/test statistics

## Tech Stack

- [Next.js](https://nextjs.org/) 16 (App Router, static export)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/) v4
- [shadcn/ui](https://ui.shadcn.com/) components

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the site.

## Updating Leaderboard Data

`src/data/leaderboard.csv` and `src/data/leaderboard-cost.csv` are the sources of truth for the paper's per-cell scores and turn-cost results. Overall leaderboard rows are derived from the per-cell scores by equally weighting both scaffolds and all four domains. The CSV files are converted to `src/data/leaderboard-data.ts` by `scripts/csv-to-data.js`, which runs automatically before `dev` and `build` (or manually via `npm run sync-data`). Edit the CSV files, not the generated result arrays in the TS file.

## Project Structure

```
src/
├── app/
│   ├── layout.tsx               # Root layout with Navbar + Footer
│   ├── page.tsx                 # Home: hero, features, results, domains, methods
│   └── leaderboard/
│       └── page.tsx             # Full leaderboard page
├── components/
│   ├── Leaderboard.tsx          # Main leaderboard with filters, sorting, overall rows
│   ├── BenchmarkDomains.tsx     # Domain overview table
│   ├── DomainDivergingBars.tsx  # Per-domain improvement chart
│   ├── ResearchNarrative.tsx    # Research findings section
│   ├── SkillMethods.tsx         # Self-evolution method cards with GitHub links
│   ├── FilterButton.tsx         # Reusable filter toggle button
│   ├── Navbar.tsx               # Top navigation bar
│   ├── Footer.tsx               # Page footer
│   └── ui/                      # shadcn/ui primitives
└── data/
    ├── leaderboard.csv          # Benchmark results (source of truth)
    ├── leaderboard-cost.csv     # Turn-cost results (source of truth)
    └── leaderboard-data.ts      # Domain info, method info, generated results
scripts/
└── csv-to-data.js               # Syncs result CSVs into leaderboard-data.ts
benchmark/                       # Public benchmark runner, adapters, and docs
```

## Deployment

### GitHub Pages

Push to main branch — GitHub Actions will automatically build and deploy.

### Vercel / Netlify

Import the GitHub repository. No extra configuration needed.

## Citation

```bibtex
@misc{gao2026evoagentbench,
  title={EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer},
  author={Xingze Gao and Chuanrui Hu and Hongda Chen and Pengfei Yao and Zhao Wang and Yi Bai and Zhengwei Wu and Yunyun Han and Xiaofeng Cong and Jie Gui and Yafeng Deng and Teng Li},
  year={2026},
  eprint={2607.05202},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2607.05202}
}
```

## License

The website is released under the MIT License. The implementation under
[`benchmark/`](benchmark/) is released under the
[Apache License 2.0](benchmark/LICENSE).
