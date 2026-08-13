"use client";

import { useMemo, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FilterButton } from "@/components/FilterButton";
import {
  leaderboardData,
  turnCostData,
  AGENTS,
  DOMAINS,
  SKILL_METHODS,
  AGENT_COLORS,
  AGENT_BAR_COLORS,
  DOMAIN_LABELS,
  DOMAIN_TAG_COLORS,
  SKILL_METHOD_TAG_COLORS,
  type Agent,
  type Domain,
  type SkillMethod,
  type LeaderboardEntry,
} from "@/data/leaderboard-data";

type SortKey = "methodScore" | "delta" | "vanilla";

interface DisplayRow {
  agent: Agent | "Both";
  model: string;
  domain: string;
  skillMethod: string;
  vanilla: number;
  methodScore: number;
  isOverall: boolean;
  domainTag?: Domain;
}

function averageToOneDecimal(values: number[]) {
  const sumInTenths = values.reduce(
    (sum, value) => sum + Math.round(value * 10),
    0,
  );
  return Math.round(sumInTenths / values.length) / 10;
}

function buildOverallRows(data: LeaderboardEntry[]): DisplayRow[] {
  const groups = new Map<string, LeaderboardEntry[]>();
  for (const entry of data) {
    const key = `${entry.model}|${entry.skillMethod}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(entry);
  }

  return Array.from(groups.values())
    .filter((entries) => entries.length === DOMAINS.length * AGENTS.length)
    .map((entries) => ({
      agent: "Both",
      model: entries[0].model,
      domain: "Overall",
      skillMethod: entries[0].skillMethod,
      vanilla: averageToOneDecimal(entries.map((entry) => entry.vanilla)),
      methodScore: averageToOneDecimal(
        entries.map((entry) => entry.methodScore),
      ),
      isOverall: true,
    }));
}

function signed(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}

function CostValue({ value }: { value: number }) {
  const color =
    value < 0
      ? "text-emerald-600"
      : value > 0
        ? "text-red-500"
        : "text-muted-foreground";
  return (
    <span className={`font-mono font-semibold tabular-nums ${color}`}>
      {signed(value)}%
    </span>
  );
}

export function Leaderboard() {
  const [agentFilter, setAgentFilter] = useState<Agent | "All">("All");
  const [domainFilter, setDomainFilter] = useState<Domain | "All" | "Overall">(
    "All",
  );
  const [methodFilter, setMethodFilter] = useState<SkillMethod | "All">("All");
  const [sortBy, setSortBy] = useState<SortKey>("methodScore");

  const filtered = useMemo(() => {
    let data = [...leaderboardData];
    if (methodFilter !== "All") {
      data = data.filter((entry) => entry.skillMethod === methodFilter);
    }

    if (domainFilter === "Overall") {
      const overalls = buildOverallRows(data);
      overalls.sort((a, b) => {
        if (sortBy === "delta") {
          return b.methodScore - b.vanilla - (a.methodScore - a.vanilla);
        }
        return sortBy === "vanilla"
          ? b.vanilla - a.vanilla
          : b.methodScore - a.methodScore;
      });
      return overalls;
    }

    if (agentFilter !== "All") {
      data = data.filter((entry) => entry.agent === agentFilter);
    }
    if (domainFilter !== "All") {
      data = data.filter((entry) => entry.domain === domainFilter);
    }

    const individual: DisplayRow[] = data.map((entry) => ({
      ...entry,
      domain: DOMAIN_LABELS[entry.domain],
      isOverall: false,
      domainTag: entry.domain,
    }));
    const rows = individual;

    rows.sort((a, b) => {
      if (sortBy === "delta") {
        return (
          b.methodScore - b.vanilla - (a.methodScore - a.vanilla)
        );
      }
      return sortBy === "vanilla"
        ? b.vanilla - a.vanilla
        : b.methodScore - a.methodScore;
    });
    return rows;
  }, [agentFilter, domainFilter, methodFilter, sortBy]);

  const maxBarValue = Math.max(
    ...filtered.map((entry) =>
      Math.abs(entry.methodScore - entry.vanilla),
    ),
    1,
  );
  const bestScore = Math.max(
    ...leaderboardData.map((entry) => entry.methodScore),
  );
  const avgDelta =
    leaderboardData.reduce(
      (sum, entry) => sum + entry.methodScore - entry.vanilla,
      0,
    ) / leaderboardData.length;

  return (
    <div>
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="text-center">
          <p className="font-mono text-3xl font-bold text-foreground">
            {bestScore.toFixed(1)}%
          </p>
          <p className="text-sm text-muted-foreground mt-1">Best Method Score</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-3xl font-bold text-foreground">
            {signed(avgDelta)}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Mean Transfer Gain</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-3xl font-bold text-foreground">
            {leaderboardData.length}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Method Comparisons</p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-6 mb-6">
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground uppercase tracking-widest font-medium">
            Filter · Agent
          </span>
          <div className="flex gap-1.5">
            <FilterButton
              active={agentFilter === "All"}
              onClick={() => setAgentFilter("All")}
            >
              All
            </FilterButton>
            {AGENTS.map((agent) => (
              <FilterButton
                key={agent}
                active={agentFilter === agent}
                onClick={() => {
                  setAgentFilter(agent);
                  if (domainFilter === "Overall") setDomainFilter("All");
                }}
              >
                {agent}
              </FilterButton>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground uppercase tracking-widest font-medium">
            Filter · Domain
          </span>
          <div className="flex gap-1.5 flex-wrap">
            <FilterButton
              active={domainFilter === "All"}
              onClick={() => setDomainFilter("All")}
            >
              All
            </FilterButton>
            <FilterButton
              active={domainFilter === "Overall"}
              onClick={() => {
                setDomainFilter("Overall");
                setAgentFilter("All");
              }}
            >
              Overall
            </FilterButton>
            {DOMAINS.map((domain) => (
              <FilterButton
                key={domain}
                active={domainFilter === domain}
                onClick={() => setDomainFilter(domain)}
              >
                {DOMAIN_LABELS[domain]}
              </FilterButton>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground uppercase tracking-widest font-medium">
            Filter · Method
          </span>
          <div className="flex gap-1.5 flex-wrap">
            <FilterButton
              active={methodFilter === "All"}
              onClick={() => setMethodFilter("All")}
            >
              All
            </FilterButton>
            {SKILL_METHODS.map((method) => (
              <FilterButton
                key={method}
                active={methodFilter === method}
                onClick={() => setMethodFilter(method)}
              >
                {method}
              </FilterButton>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-[11px] text-muted-foreground uppercase tracking-widest font-medium">
            Sort by
          </span>
          <div className="flex gap-1.5">
            <FilterButton
              active={sortBy === "methodScore"}
              onClick={() => setSortBy("methodScore")}
            >
              Method score
            </FilterButton>
            <FilterButton
              active={sortBy === "delta"}
              onClick={() => setSortBy("delta")}
            >
              Δ gain
            </FilterButton>
            <FilterButton
              active={sortBy === "vanilla"}
              onClick={() => setSortBy("vanilla")}
            >
              Vanilla
            </FilterButton>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <Table className="min-w-[1160px]">
          <TableHeader>
            <TableRow className="border-b-2">
              <TableHead className="w-10 text-center">#</TableHead>
              <TableHead>Agent</TableHead>
              <TableHead>Base Model</TableHead>
              <TableHead className="min-w-52">Domain</TableHead>
              <TableHead className="min-w-40">Method</TableHead>
              <TableHead className="text-right min-w-24">Vanilla</TableHead>
              <TableHead className="text-right font-semibold min-w-32 pr-6">
                Method Score
              </TableHead>
              <TableHead className="text-right min-w-20">Δ</TableHead>
              <TableHead className="w-32" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((row, index) => {
              const delta = row.methodScore - row.vanilla;
              const barWidth = (Math.abs(delta) / maxBarValue) * 100;
              const deltaColor =
                delta >= 0 ? "text-emerald-600" : "text-red-500";
              return (
                <TableRow
                  key={`${row.agent}-${row.model}-${row.domain}-${row.skillMethod}`}
                  className={
                    row.isOverall
                      ? "bg-muted/60 font-semibold border-t-2"
                      : ""
                  }
                >
                  <TableCell className="text-center font-mono text-muted-foreground">
                    {index + 1}
                  </TableCell>
                  <TableCell className="font-semibold">
                    {row.agent !== "Both" && (
                      <span
                        className="inline-block w-2.5 h-2.5 rounded-full mr-2 align-middle"
                        style={{ background: AGENT_COLORS[row.agent] }}
                      />
                    )}
                    {row.agent}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {row.model}
                  </TableCell>
                  <TableCell>
                    {row.isOverall ? (
                      <span className="inline-block px-3 py-0.5 rounded-md text-xs font-bold bg-foreground text-background">
                        Overall
                      </span>
                    ) : row.domainTag ? (
                      <span
                        className="inline-block px-3 py-0.5 rounded-md text-xs font-medium"
                        style={{
                          background: DOMAIN_TAG_COLORS[row.domainTag].bg,
                          color: DOMAIN_TAG_COLORS[row.domainTag].text,
                        }}
                      >
                        {row.domain}
                      </span>
                    ) : null}
                  </TableCell>
                  <TableCell>
                    <span
                      className="inline-block px-3 py-0.5 rounded-md text-xs font-medium"
                      style={{
                        background: SKILL_METHOD_TAG_COLORS[row.skillMethod].bg,
                        color: SKILL_METHOD_TAG_COLORS[row.skillMethod].text,
                      }}
                    >
                      {row.skillMethod}
                    </span>
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground min-w-24">
                    {row.vanilla.toFixed(1)}%
                  </TableCell>
                  <TableCell className="text-right font-bold text-lg min-w-32 pr-6">
                    {row.methodScore.toFixed(1)}%
                  </TableCell>
                  <TableCell
                    className={`text-right font-semibold min-w-20 ${deltaColor}`}
                  >
                    {signed(delta)}
                  </TableCell>
                  <TableCell>
                    <div
                      className="h-2.5 rounded-full transition-all duration-500"
                      style={{
                        width: `${barWidth}%`,
                        background:
                          row.agent === "Both"
                            ? "#64748b"
                            : AGENT_BAR_COLORS[row.agent],
                      }}
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <p className="mt-4 text-xs text-muted-foreground">
        Means from Table 3 of the paper; standard errors are intentionally
        omitted. Overall is derived by equally weighting four domains and both
        scaffolds. † Anchor Skill is a diagnostic reference, not a deployable
        automatic method.
      </p>

      <section className="mt-16" id="cost-analysis">
        <h2 className="text-2xl font-bold mb-2">Turn Cost Analysis</h2>
        <p className="text-sm text-muted-foreground mb-6 max-w-3xl">
          Percentage change in agent turns relative to Vanilla, equal-weighted
          across the four domains. Negative values mean fewer turns; positive
          values mean additional overhead.
        </p>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-b-2">
                <TableHead>Agent</TableHead>
                <TableHead>Base Model</TableHead>
                <TableHead>Method</TableHead>
                <TableHead className="text-right">All</TableHead>
                <TableHead className="text-right">Solved</TableHead>
                <TableHead className="text-right">Unsolved</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {turnCostData.map((row) => (
                <TableRow
                  key={`${row.agent}-${row.model}-${row.skillMethod}-cost`}
                >
                  <TableCell className="font-semibold">
                    <span
                      className="inline-block w-2.5 h-2.5 rounded-full mr-2 align-middle"
                      style={{ background: AGENT_COLORS[row.agent] }}
                    />
                    {row.agent}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {row.model}
                  </TableCell>
                  <TableCell>{row.skillMethod}</TableCell>
                  <TableCell className="text-right">
                    <CostValue value={row.all} />
                  </TableCell>
                  <TableCell className="text-right">
                    <CostValue value={row.solved} />
                  </TableCell>
                  <TableCell className="text-right">
                    <CostValue value={row.unsolved} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <p className="mt-4 text-xs text-muted-foreground">
          Values reproduce Table 4 of the paper. All, Solved, and Unsolved are
          separately averaged across domains, so All need not lie between the
          other two columns. † Diagnostic reference.
        </p>
      </section>
    </div>
  );
}
