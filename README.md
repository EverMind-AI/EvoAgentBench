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

## EverMind Ecosystem

EverMind connects memory research, production-ready products, and practical
integrations into one open-source ecosystem.

<table>
<tr>
<th colspan="2">Products</th>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/EverOS">EverOS</a></strong></td>
<td>A local-first, Markdown-native long-term memory runtime for agents and users.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/Raven">Raven</a></strong></td>
<td>A memory-first, self-improving agent harness with proactivity, context control, and skill evolution.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/EverMe">EverMe (CLI)</a></strong></td>
<td>A CLI and agent plugin suite for cross-device, cross-agent personal memory.</td>
</tr>
<tr>
<th colspan="2">Research &amp; Evaluation</th>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/SkillCorpus">SkillCorpus</a></strong></td>
<td>Curated, retrieval-ready agent skill corpora with retrieval and evaluation tooling.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/EverAlgo">EverAlgo</a></strong></td>
<td>Stateless extraction, ranking, parsing, and memory operators that power EverOS.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/HyperMem">HyperMem</a></strong></td>
<td>Hypergraph-based hierarchical memory for coarse-to-fine long-term conversation retrieval.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/MSA">MSA</a></strong></td>
<td>Memory Sparse Attention for scalable latent memory and 100M-token contexts.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/EverMemBench">EverMemBench</a></strong></td>
<td>Evaluation of factual recall, applied reasoning, and personalized generalization in memory systems.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/EverMind-AI/EvoAgentBench">EvoAgentBench</a></strong></td>
<td>Longitudinal evaluation of agent self-evolution, transfer efficiency, error avoidance, and skill use.</td>
</tr>
<tr>
<th colspan="2"><a href="https://github.com/EverMind-AI/plugins">Integrations</a></th>
</tr>
<tr>
<td><strong><a href="https://docs.openclaw.ai">OpenClaw</a></strong></td>
<td><a href="https://github.com/EverMind-AI/plugins/tree/main/openclaw">OpenClaw plugin</a> for automatic recall, capture, and session-memory lifecycle management.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a></strong></td>
<td><a href="https://github.com/EverMind-AI/plugins/tree/main/hermes">Hermes plugin</a> for persistent memory across Hermes sessions.</td>
</tr>
<tr>
<td><strong><a href="https://github.com/deepseek-ai/DeepSeek-Harness">DeepSeek Harness</a></strong></td>
<td><a href="https://github.com/EverMind-AI/plugins/tree/main/dsh">DSH plugin</a> for memory-aware DeepSeek Harness agents.</td>
</tr>
<tr>
<td><strong><a href="https://dify.ai">Dify</a></strong></td>
<td><a href="https://github.com/EverMind-AI/plugins/tree/main/dify">Self-hosted</a> and <a href="https://github.com/EverMind-AI/plugins/tree/main/dify_cloud">cloud</a> tools for explicit memory search and storage in workflows and agents.</td>
</tr>
</table>

Together, these projects form EverMind's research-to-runtime stack: methods
and benchmarks become reusable memory infrastructure, products, and agent
integrations.

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
