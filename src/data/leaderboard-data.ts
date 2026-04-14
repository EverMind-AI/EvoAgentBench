export type Agent = "OpenClaw" | "Nanabot";

export type Domain =
  | "BrowseCompPlus"
  | "OmniMath"
  | "SWE-Bench"
  | "LiveCodeBench"
  | "GDPVal";

export type SkillMethod = "EverOS" | "Human Design";

export interface LeaderboardEntry {
  agent: Agent;
  model: string;
  domain: Domain;
  skillMethod: SkillMethod;
  without: number;
  withSkills: number;
  cost: string;
}

export const AGENTS: Agent[] = ["OpenClaw", "Nanabot"];

export const DOMAINS: Domain[] = [
  "BrowseCompPlus",
  "OmniMath",
  "SWE-Bench",
  "LiveCodeBench",
  "GDPVal",
];

export const SKILL_METHODS: SkillMethod[] = ["EverOS", "Human Design"];

export const AGENT_COLORS: Record<Agent, string> = {
  OpenClaw: "#ef4444",
  Nanabot: "#3b82f6",
};

export const AGENT_BAR_COLORS: Record<Agent, string> = {
  OpenClaw: "#c2703a",
  Nanabot: "#6366f1",
};

export const DOMAIN_LABELS: Record<Domain, string> = {
  BrowseCompPlus: "Information Retrieval",
  OmniMath: "Reasoning & Problem Decomposition",
  "SWE-Bench": "Software Engineering",
  LiveCodeBench: "Code Implementation",
  GDPVal: "Knowledge Work",
};

export const DOMAIN_TAG_COLORS: Record<Domain, { bg: string; text: string }> = {
  BrowseCompPlus: { bg: "#fde68a", text: "#78350f" },
  OmniMath: { bg: "#dbeafe", text: "#1e40af" },
  "SWE-Bench": { bg: "#fce7f3", text: "#9d174d" },
  LiveCodeBench: { bg: "#d1fae5", text: "#065f46" },
  GDPVal: { bg: "#ede9fe", text: "#5b21b6" },
};

export const SKILL_METHOD_TAG_COLORS: Record<SkillMethod, { bg: string; text: string }> = {
  EverOS: { bg: "#d1fae5", text: "#065f46" },
  "Human Design": { bg: "#e0f2fe", text: "#0369a1" },
};

// --- Domain descriptions (from README) ---

export interface DomainInfo {
  id: Domain;
  name: string;
  baseBenchmark: string;
  category: string;
  description: string;
  clusters: string;
  train: number;
  test: number;
  docker: boolean;
}

export const DOMAIN_INFO: DomainInfo[] = [
  {
    id: "BrowseCompPlus",
    name: "Information Retrieval",
    baseBenchmark: "BrowseCompPlus",
    category: "Information Retrieval",
    description: "Search a local corpus to answer complex multi-constraint questions.",
    clusters: "10 (by topic)",
    train: 154,
    test: 65,
    docker: false,
  },
  {
    id: "OmniMath",
    name: "Reasoning & Problem Decomposition",
    baseBenchmark: "OmniMath",
    category: "Reasoning",
    description: "Solve competition-level math problems across multiple subdisciplines.",
    clusters: "By subdiscipline",
    train: 478,
    test: 100,
    docker: false,
  },
  {
    id: "SWE-Bench",
    name: "Software Engineering",
    baseBenchmark: "SWE-Bench",
    category: "Software Engineering",
    description: "Fix real-world bugs in open-source Python repositories.",
    clusters: "19 (by repo)",
    train: 101,
    test: 26,
    docker: true,
  },
  {
    id: "LiveCodeBench",
    name: "Code Implementation",
    baseBenchmark: "LiveCodeBench",
    category: "Code Implementation",
    description: "Solve competitive programming problems with code execution.",
    clusters: "39 (by type)",
    train: 97,
    test: 39,
    docker: false,
  },
  {
    id: "GDPVal",
    name: "Knowledge Work",
    baseBenchmark: "GDPVal",
    category: "Knowledge Work",
    description: "Perform real-world occupational tasks (Excel, PDF, Word).",
    clusters: "29 (by occupation)",
    train: 87,
    test: 58,
    docker: false,
  },
];

// --- Skill method descriptions ---

export interface AllMethodInfo {
  name: string;
  description: string;
  approach: string;
  github: string;
  status: "available" | "coming_soon";
}

export const ALL_METHODS: AllMethodInfo[] = [
  {
    name: "EverOS",
    description: "A memory OS that makes agents more personal while saving tokens. Extracts and stores long-term memory from session trajectories, then injects reusable skills as domain-specific strategies.",
    approach: "Memory-based extraction",
    github: "https://github.com/EverMind-AI/EverOS",
    status: "available",
  },
  {
    name: "EvoSkill",
    description: "An agent-agnostic toolkit for automatically creating and improving AI skills. Runs an evolution loop where an Executor collects failures and a Proposer analyzes patterns to synthesize reusable skills.",
    approach: "Evolutionary optimization",
    github: "https://github.com/sentient-agi/EvoSkill",
    status: "available",
  },
  {
    name: "Memento",
    description: "A memory-based continual-learning framework using Case-Based Reasoning. Logs successful and failed trajectories into a Case Bank, retrieves by Q-value with SimCSE embeddings to steer planning.",
    approach: "Retrieval-based (CBR)",
    github: "https://github.com/Agent-on-the-Fly/Memento",
    status: "available",
  },
  {
    name: "OpenSpace",
    description: "A self-evolving engine where every task makes every agent smarter. Skills automatically select, apply, monitor, analyze, and evolve themselves via three evolution modes (FIX, DERIVED, CAPTURED).",
    approach: "Continuous accumulation",
    github: "https://github.com/HKUDS/OpenSpace",
    status: "available",
  },
  {
    name: "ReasoningBank",
    description: "A memory mechanism that learns from both successful and failed trajectories, storing reasoning as memory content. Introduces memory-aware test-time scaling — experience-driven memory as an additional scaling dimension for agent systems.",
    approach: "Memory + reasoning",
    github: "https://github.com/google-research/reasoning-bank",
    status: "available",
  },
];

// --- Leaderboard data (real results from OpenClaw experiments) ---
// Only domains with actual experiment data are included

export const leaderboardData: LeaderboardEntry[] = [
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "BrowseCompPlus", skillMethod: "EverOS", without: 32.3, withSkills: 43.1, cost: "↓ 33.1% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "BrowseCompPlus", skillMethod: "EverOS", without: 30.8, withSkills: 32.3, cost: "↑ 4.7% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "BrowseCompPlus", skillMethod: "Human Design", without: 32.3, withSkills: 55.4, cost: "↓ 21.8% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "BrowseCompPlus", skillMethod: "Human Design", without: 30.8, withSkills: 35.4, cost: "↑ 14.2% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "SWE-Bench", skillMethod: "EverOS", without: 26.9, withSkills: 38.5, cost: "↓ 11.4% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "SWE-Bench", skillMethod: "EverOS", without: 11.5, withSkills: 38.5, cost: "↑ 41.2% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "SWE-Bench", skillMethod: "Human Design", without: 26.9, withSkills: 61.5, cost: "↓ 0.5% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "SWE-Bench", skillMethod: "Human Design", without: 11.5, withSkills: 38.5, cost: "↑ 62.5% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "OmniMath", skillMethod: "EverOS", without: 45, withSkills: 49, cost: "↓ 32.1% chars" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "OmniMath", skillMethod: "EverOS", without: 37, withSkills: 42, cost: "↓ 6.2% chars" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "OmniMath", skillMethod: "Human Design", without: 45, withSkills: 60, cost: "↑ 2.7% chars" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "OmniMath", skillMethod: "Human Design", without: 37, withSkills: 29, cost: "↓ 13.0% chars" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "GDPVal", skillMethod: "EverOS", without: 50, withSkills: 56.9, cost: "↑ 24.7% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "GDPVal", skillMethod: "EverOS", without: 51.7, withSkills: 55.2, cost: "↑ 5.4% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "GDPVal", skillMethod: "Human Design", without: 50, withSkills: 72.4, cost: "↑ 91.8% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "GDPVal", skillMethod: "Human Design", without: 51.7, withSkills: 65.5, cost: "↑ 43.8% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "LiveCodeBench", skillMethod: "EverOS", without: 56.4, withSkills: 56.4, cost: "↓ 3.3% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "LiveCodeBench", skillMethod: "EverOS", without: 53.8, withSkills: 51.3, cost: "↓ 4.8% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-397B", domain: "LiveCodeBench", skillMethod: "Human Design", without: 56.4, withSkills: 64.1, cost: "↓ 6.7% turns" },
  { agent: "OpenClaw", model: "Qwen3.5-27B", domain: "LiveCodeBench", skillMethod: "Human Design", without: 53.8, withSkills: 64.1, cost: "— 0% turns" },
];
