# EvoAgentBench Website

Leaderboard and project website for **EvoAgentBench** — a benchmark for evaluating AI agent self-evolution across diverse task domains.

- **Live site**: https://evermind-ai.github.io/EvoAgentBench/
- **Paper**: [EvoAgentBench: Benchmarking Agent Self-Evolution via Ability Transfer](https://arxiv.org/abs/2607.05202)
- **Dataset**: [EverMind-AI/EvoAgentBench](https://huggingface.co/datasets/EverMind-AI/EvoAgentBench) on Hugging Face

## Features

- Interactive leaderboard with filtering and sorting
- Filter by agent (OpenClaw, Nanobot) and domain (Information Retrieval, Reasoning, Software Engineering, Code Implementation, Knowledge Work)
- Sort by score with skills, improvement delta, or baseline score
- Overall aggregation for same agent + model + method combinations
- Efficiency column showing cost change after skill injection
- 5 self-evolution methods with GitHub links (EverOS, EvoSkill, Memento, OpenSpace, ReasoningBank)
- Domain overview table with cluster/train/test statistics

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

`src/data/leaderboard.csv` is the source of truth for benchmark results. It is converted to `src/data/leaderboard-data.ts` by `scripts/csv-to-data.js`, which runs automatically before `dev` and `build` (or manually via `npm run sync-data`). Edit the CSV, not the generated results in the TS file.

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
    └── leaderboard-data.ts      # Domain info, method info, generated results
scripts/
└── csv-to-data.js               # Syncs leaderboard.csv into leaderboard-data.ts
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

MIT
