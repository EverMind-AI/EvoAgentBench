import Link from "next/link";
import { DomainDivergingBars } from "@/components/DomainDivergingBars";
import { BenchmarkDomains } from "@/components/BenchmarkDomains";
import { SkillMethods } from "@/components/SkillMethods";
import { ResearchNarrative } from "@/components/ResearchNarrative";

export default function Home() {
  return (
    <main className="flex-1">
      {/* Hero */}
      <section className="bg-secondary py-20">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <p className="font-mono text-sm text-muted-foreground mb-4 tracking-wider">
            01 — OVERVIEW
          </p>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
            EvoAgentBench
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mx-auto mb-6 italic whitespace-nowrap">
            Benchmarking Agent Self-Evolution via Ability Transfer
          </p>
          <p className="text-sm text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
            EvoAgentBench evaluates whether agents can transfer reusable
            procedures from past experience to new tasks. Its Ability-guided
            split covers web research, algorithmic reasoning, software
            engineering, and knowledge work, with verified training-side
            support for every test task.
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link
              href="/leaderboard"
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full border border-border bg-background text-sm font-medium hover:bg-secondary transition-colors"
            >
              Full Leaderboard
            </Link>
            <a
              href="#domains"
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full border border-border bg-background text-sm font-medium hover:bg-secondary transition-colors"
            >
              Domains
            </a>
            <a
              href="#methods"
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full border border-border bg-background text-sm font-medium hover:bg-secondary transition-colors"
            >
              Self-Evolution
            </a>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="rounded-xl border bg-card p-6">
            <div className="text-2xl mb-3">🌐</div>
            <h3 className="font-semibold text-foreground mb-2">Multi-Domain Evaluation</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              4 agentic domains — web research, algorithmic reasoning, software
              engineering, and knowledge work — with 528 training tasks and
              267 supported test tasks.
            </p>
          </div>
          <div className="rounded-xl border bg-card p-6">
            <div className="text-2xl mb-3">🤖</div>
            <h3 className="font-semibold text-foreground mb-2">Multi-Agent Support</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Plug in any CLI-based agent — Nanobot, OpenClaw, or your own.
              Each task runs in isolated config with independent workspace,
              supporting concurrent execution and automatic retry.
            </p>
          </div>
          <div className="rounded-xl border bg-card p-6">
            <div className="text-2xl mb-3">🧬</div>
            <h3 className="font-semibold text-foreground mb-2">Self-Evolution Comparison</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              A standardized train → evolve → evaluate protocol comparing
              Memento, ReasoningBank, GEPA, and the diagnostic Anchor Skill†
              reference under matched conditions.
            </p>
          </div>
        </div>
      </section>

      {/* Results — per-configuration diverging bars with filters */}
      <DomainDivergingBars />

      {/* Research narrative — why self-evolution, lessons, what the bench does */}
      <ResearchNarrative />

      {/* Benchmark Domains */}
      <BenchmarkDomains />

      {/* Skill Extraction Methods */}
      <SkillMethods />
    </main>
  );
}
