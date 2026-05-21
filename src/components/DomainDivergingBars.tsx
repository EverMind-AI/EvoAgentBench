"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  leaderboardData,
  AGENTS,
  DOMAINS,
  DOMAIN_LABELS,
  type Agent,
  type Domain,
  type LeaderboardEntry,
  type SkillMethod,
} from "@/data/leaderboard-data";

type AgentFilter = "All" | Agent;
type ModelFilter = "All" | string;
type DomainFilter = "All" | Domain;

interface PanelRow {
  method: SkillMethod;
  without: number;
  withSkills: number;
  delta: number;
}

interface ConfigPanel {
  agent: Agent;
  model: string;
  domain: Domain;
  rows: PanelRow[];
}

const DOMAIN_ACCENT: Record<Domain, string> = {
  BrowseCompPlus: "bg-emerald-500",
  OmniMath: "bg-indigo-500",
  "SWE-Bench": "bg-amber-500",
  LiveCodeBench: "bg-sky-500",
  GDPVal: "bg-rose-500",
};

const AGENT_DOT: Record<Agent, string> = {
  OpenClaw: "bg-red-500",
  Nanobot: "bg-blue-500",
};

function buildPanels(data: LeaderboardEntry[]): ConfigPanel[] {
  const groups = new Map<string, ConfigPanel>();
  for (const e of data) {
    const key = `${e.agent}|${e.model}|${e.domain}`;
    if (!groups.has(key)) {
      groups.set(key, {
        agent: e.agent,
        model: e.model,
        domain: e.domain,
        rows: [],
      });
    }
    groups.get(key)!.rows.push({
      method: e.skillMethod,
      without: e.without,
      withSkills: e.withSkills,
      delta: e.withSkills - e.without,
    });
  }

  const panels = Array.from(groups.values());
  // Sort rows within each panel by delta descending
  for (const p of panels) p.rows.sort((a, b) => b.delta - a.delta);
  // Panel display order
  panels.sort((a, b) => {
    const ag = AGENTS.indexOf(a.agent) - AGENTS.indexOf(b.agent);
    if (ag !== 0) return ag;
    if (a.model !== b.model) return a.model.localeCompare(b.model);
    return DOMAINS.indexOf(a.domain) - DOMAINS.indexOf(b.domain);
  });
  return panels;
}

function FilterChips<T extends string>({
  label,
  value,
  options,
  onChange,
  displayLabel,
}: {
  label: string;
  value: T;
  options: T[];
  onChange: (v: T) => void;
  displayLabel?: (v: T) => string;
}) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-xs font-mono text-muted-foreground tracking-wider uppercase mr-1">
        {label}
      </span>
      {options.map((opt) => {
        const active = opt === value;
        return (
          <button
            key={opt}
            type="button"
            onClick={() => onChange(opt)}
            className={`px-3 py-1 rounded-full text-xs border transition-colors ${
              active
                ? "bg-foreground text-background border-foreground"
                : "border-border text-muted-foreground hover:bg-secondary"
            }`}
          >
            {displayLabel ? displayLabel(opt) : opt}
          </button>
        );
      })}
    </div>
  );
}

export function DomainDivergingBars() {
  // Discover available models from data (e.g., Qwen3.5-27B / Qwen3.5-397B)
  const allModels = useMemo(() => {
    const s = new Set<string>();
    for (const e of leaderboardData) s.add(e.model);
    return Array.from(s).sort();
  }, []);
  // Compact label for filter chips (drop "Qwen3.5-" prefix)
  const modelChip = (m: string) => m.replace(/^Qwen3\.5-/, "");

  const [agentF, setAgentF] = useState<AgentFilter>("All");
  const [modelF, setModelF] = useState<ModelFilter>("All");
  const [domainF, setDomainF] = useState<DomainFilter>("All");

  const allPanels = useMemo(() => buildPanels(leaderboardData), []);

  const filtered = useMemo(() => {
    return allPanels.filter((p) => {
      if (agentF !== "All" && p.agent !== agentF) return false;
      if (modelF !== "All" && p.model !== modelF) return false;
      if (domainF !== "All" && p.domain !== domainF) return false;
      return true;
    });
  }, [allPanels, agentF, modelF, domainF]);

  // Normalize bar width by the max |delta| across visible panels so bars stay
  // comparable when filters change.
  const maxAbs = useMemo(() => {
    let m = 1;
    for (const p of filtered)
      for (const r of p.rows) m = Math.max(m, Math.abs(r.delta));
    return m;
  }, [filtered]);

  return (
    <section id="results" className="bg-background py-16">
      <div className="mx-auto max-w-6xl px-6">
        <p className="font-mono text-sm text-muted-foreground mb-3 tracking-wider">
          02 — LEADERBOARD
        </p>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">
          Method ranking per configuration
        </h2>
        <p className="text-sm text-muted-foreground mb-6 max-w-3xl">
          For each (agent, model, domain) cell, methods are sorted by Δ gain
          (with-skills − without). Baseline pass-rate is shown next to each
          method.
        </p>

        {/* Filters */}
        <div className="flex flex-col gap-3 mb-6 p-4 bg-secondary/60 rounded-lg">
          <FilterChips
            label="Agent"
            value={agentF}
            options={["All", ...AGENTS] as AgentFilter[]}
            onChange={setAgentF}
          />
          <FilterChips
            label="Model"
            value={modelF === "All" ? "All" : modelChip(modelF)}
            options={["All", ...allModels.map(modelChip)] as ModelFilter[]}
            onChange={(v) => {
              if (v === "All") setModelF("All");
              else {
                const full = allModels.find((m) => modelChip(m) === v);
                if (full) setModelF(full);
              }
            }}
          />
          <FilterChips
            label="Domain"
            value={domainF}
            options={["All", ...DOMAINS] as DomainFilter[]}
            onChange={setDomainF}
            displayLabel={(v) =>
              v === "All" ? "All" : DOMAIN_LABELS[v as Domain]
            }
          />
        </div>

        {/* Legend */}
        <div className="flex items-center gap-5 text-xs text-muted-foreground mb-6">
          <span className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-sm bg-emerald-500" />
            positive Δ
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-sm bg-rose-300" />
            negative Δ
          </span>
          <span className="ml-auto text-muted-foreground">
            {filtered.length} configuration{filtered.length === 1 ? "" : "s"}
          </span>
        </div>

        {/* Panels grid */}
        {filtered.length === 0 ? (
          <p className="text-sm text-muted-foreground italic">
            No configurations match the current filters.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((p) => (
              <ConfigPanelView
                key={`${p.agent}|${p.model}|${p.domain}`}
                panel={p}
                maxAbs={maxAbs}
                modelChip={modelChip}
              />
            ))}
          </div>
        )}

        <p className="mt-10 text-xs text-muted-foreground italic max-w-3xl border-l-2 border-border pl-3">
          Bar length encodes Δ magnitude. See the{" "}
          <Link
            href="/leaderboard"
            className="underline underline-offset-2 hover:text-foreground"
          >
            full leaderboard
          </Link>{" "}
          for per-cell numbers including cost.
        </p>
      </div>
    </section>
  );
}

function ConfigPanelView({
  panel,
  maxAbs,
  modelChip,
}: {
  panel: ConfigPanel;
  maxAbs: number;
  modelChip: (m: string) => string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-sm hover:shadow transition-shadow">
      <h3 className="flex items-center gap-2 text-sm font-semibold mb-1">
        <span
          className={`inline-block w-1 h-4 rounded-sm ${DOMAIN_ACCENT[panel.domain]}`}
        />
        {DOMAIN_LABELS[panel.domain]}
      </h3>
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3 ml-3 pb-2 border-b border-border/60">
        <span
          className={`inline-block w-2 h-2 rounded-full ${AGENT_DOT[panel.agent]}`}
        />
        {panel.agent} · {modelChip(panel.model)}
      </div>
      {/* tiny column header so the base-rate column is unambiguous */}
      <div
        className="grid items-center gap-2 text-[10px] uppercase tracking-wider text-muted-foreground/70 mb-1"
        style={{ gridTemplateColumns: "84px 38px 1fr 38px" }}
      >
        <div className="text-right pr-1">method</div>
        <div className="text-right">base</div>
        <div />
        <div className="text-right">Δ</div>
      </div>
      <div className="space-y-2">
        {panel.rows.map((r) => (
          <MethodRow key={r.method} row={r} maxAbs={maxAbs} />
        ))}
      </div>
    </div>
  );
}

function MethodRow({
  row,
  maxAbs,
}: {
  row: PanelRow;
  maxAbs: number;
}) {
  const pct = Math.min(100, (Math.abs(row.delta) / maxAbs) * 100);
  const isPos = row.delta > 0.05;
  const isNeg = row.delta < -0.05;
  const rounded = Math.round(row.delta);
  const label =
    rounded === 0 ? "—" : rounded > 0 ? `+${rounded}` : `${rounded}`;
  const labelColor =
    rounded > 0
      ? "text-emerald-700"
      : rounded < 0
        ? "text-rose-600"
        : "text-muted-foreground";
  const deltaText = `${row.delta >= 0 ? "+" : ""}${row.delta.toFixed(1)}`;

  return (
    // group/row enlarges the hit area and shows a custom tooltip on the entire
    // row, with no native title delay.
    <div className="group/row relative -my-0.5 py-0.5 rounded hover:bg-secondary/60 transition-colors">
      <div
        className="grid items-center gap-2 text-xs"
        style={{ gridTemplateColumns: "84px 38px 1fr 38px" }}
      >
        <div className="text-foreground truncate text-right pr-1">
          {row.method}
        </div>
        <div className="text-right font-mono text-[11px] text-muted-foreground tabular-nums">
          {row.without.toFixed(1)}
        </div>
        <div className="flex h-3.5 items-stretch">
          <div className="flex-1 flex justify-end">
            {isNeg && (
              <div
                className="h-full bg-rose-300 rounded-l-sm"
                style={{ width: `${pct}%` }}
              />
            )}
          </div>
          <div className="w-px h-full bg-border" />
          <div className="flex-1">
            {isPos && (
              <div
                className="h-full bg-emerald-500 rounded-r-sm"
                style={{ width: `${pct}%` }}
              />
            )}
          </div>
        </div>
        <div className={`text-right font-mono ${labelColor} tabular-nums`}>
          {label}
        </div>
      </div>

      {/* Custom tooltip — CSS-driven, no JS, no native delay */}
      <div
        role="tooltip"
        className="pointer-events-none absolute z-20 left-1/2 -translate-x-1/2 -top-1 -translate-y-full
                   opacity-0 group-hover/row:opacity-100 transition-opacity duration-75
                   bg-foreground text-background text-[11px] leading-tight
                   rounded-md px-2.5 py-1.5 shadow-md whitespace-nowrap
                   font-mono"
      >
        <span className="font-sans font-semibold">{row.method}</span>
        <span className="mx-2 opacity-50">|</span>
        base {row.without.toFixed(1)}
        <span className="mx-1.5 opacity-50">→</span>
        with {row.withSkills.toFixed(1)}
        <span className="mx-1.5 opacity-50">|</span>
        <span
          className={
            row.delta > 0.05
              ? "text-emerald-300"
              : row.delta < -0.05
                ? "text-rose-300"
                : ""
          }
        >
          Δ {deltaText}
        </span>
      </div>
    </div>
  );
}
