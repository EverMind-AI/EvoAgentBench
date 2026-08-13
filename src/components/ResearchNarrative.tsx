export function ResearchNarrative() {
  return (
    <section id="research" className="py-16 md:py-24 px-6 bg-background">
      <div className="max-w-4xl mx-auto">
        <p className="font-mono text-sm text-muted-foreground mb-2 tracking-wider">
          03 — WHY THIS MATTERS
        </p>
        <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-10">
          Why Self-Evolution Matters, and What We Learned Running This
        </h2>

        {/* ---- Why ---- */}
        <div className="mb-12">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            Why self-evolution matters
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed mb-4">
            If an agent solves a problem today, it shouldn&rsquo;t have to start
            from zero on a similar one tomorrow. Useful experience isn&rsquo;t
            just a log of what happened &mdash;{" "}
            <span className="text-foreground font-medium">
              it&rsquo;s a way of working
            </span>
            : a search habit, a debugging move, a verification step, a recipe
            for producing something useful.{" "}
            <span className="text-foreground font-medium">Self-evolution</span>{" "}
            is the question of whether an agent can pick up these habits on its
            own, from its own past attempts, without retraining the model
            underneath.
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Most benchmarks today don&rsquo;t really test this. They either ask
            &ldquo;can the agent solve a fresh task?&rdquo; or &ldquo;can the
            agent remember what it saw?&rdquo; Neither tells you whether
            yesterday&rsquo;s way of working actually shows up when the agent
            tries something new today. EvoAgentBench is built around that
            specific question.
          </p>
        </div>

        {/* ---- Lessons ---- */}
        <div className="mb-12">
          <h3 className="text-lg font-semibold text-foreground mb-2">
          What the experiments show
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed mb-5">
            Across two agent scaffolds, three backbones, and four domains, the
            results expose where current self-evolution systems still break.
          </p>

          <div className="space-y-4">
            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                Ability content transfers across model families.
              </span>{" "}
              Anchor Skill† improves every scaffold&ndash;backbone&ndash;domain
              cell even though its construction backbones are disjoint from
              the evaluation backbones. The procedural content is transferable
              when it is extracted and routed correctly.
            </NotePoint>

            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                Every automatic method still shows negative transfer.
              </span>{" "}
              Memento, ReasoningBank, and GEPA each improve some settings, but
              none remains positive in every cell. One striking mismatch is
              Memento on Nanobot / Qwen3.5-27B / software engineering, where
              performance drops by 36.3 points.
            </NotePoint>

            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                Extraction and routing remain the bottleneck.
              </span>{" "}
              Automatic methods see the same training prompts, trajectories,
              and verifier outcomes. Their uneven gains therefore point to how
              reusable content is extracted, indexed, and delivered at test
              time, not to missing training-side support.
            </NotePoint>
          </div>
        </div>

        {/* ---- What we do ---- */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            What we did to make the comparisons fair
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed mb-5">
            For numbers to be worth comparing, the setup has to be tight. Three
            things we cared about most:
          </p>

          <div className="space-y-4">
            <NotePoint icon="🔹">
              <span className="font-semibold text-foreground">
                Nobody gets to peek at the answers.
              </span>{" "}
              Methods can only look at training tasks: the question, what the
              agent tried, and whether it worked. The actual test answers, and
              the test trajectories that succeeded, are off-limits during
              evolution. We didn&rsquo;t make this a rule for people to follow;
              we wired it in so the two paths simply don&rsquo;t meet.
            </NotePoint>

            <NotePoint icon="🔹">
              <span className="font-semibold text-foreground">
                Training and test tasks are related, not random.
              </span>{" "}
              The Ability Graph links tasks through trace-grounded procedural
              overlap. Every test task has verified support from training-side
              Abilities, so a failed transfer cannot be dismissed as an
              unsupported test case.
            </NotePoint>

            <NotePoint icon="🔹">
              <span className="font-semibold text-foreground">
                Every cell on the leaderboard is real.
              </span>{" "}
              Two agent frameworks, three backbones, four domains, and four
              evolution conditions produce 96 method comparisons, all measured
              against matched Vanilla baselines. Tasks, tools, timeouts,
              scoring, and base agent configuration are fixed across methods;
              results are averaged over three independent runs per instance.
            </NotePoint>
          </div>
        </div>
      </div>
    </section>
  );
}

function NotePoint({
  icon,
  children,
}: {
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-3 items-start">
      <span className="text-sm leading-relaxed shrink-0 mt-0.5" aria-hidden>
        {icon}
      </span>
      <p className="text-sm text-muted-foreground leading-relaxed">{children}</p>
    </div>
  );
}
