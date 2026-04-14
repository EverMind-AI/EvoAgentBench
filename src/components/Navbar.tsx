import Link from "next/link";

const CODE_URL = "https://github.com/EverMind-AI/EverOS/tree/feat/readme-redesign/benchmarks/EvoAgentBench";
const HF_URL = "https://huggingface.co/datasets/EverMind-AI/EvoAgentBench";
const BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="text-lg font-bold tracking-tight">
          EvoAgentBench
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          <Link
            href="/leaderboard"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            Leaderboard
          </Link>
          <a
            href={`${BASE}/#results`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            Results
          </a>
          <a
            href={`${BASE}/#domains`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            Domains
          </a>
          <a
            href={`${BASE}/#methods`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            Self-Evolution
          </a>

          <span className="h-4 w-px bg-border" />

          <a
            href={CODE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
            Code
          </a>
          <a
            href={HF_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          >
            🤗 Hugging Face
          </a>
        </nav>
      </div>
    </header>
  );
}
