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
            Three things to watch out for if you&rsquo;re building one
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed mb-5">
            We ran a lot of combinations. If you&rsquo;re working on a
            self-evolution method, three patterns showed up over and over.
            They&rsquo;re worth thinking about before you start optimizing.
          </p>

          <div className="space-y-4">
            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                The bottleneck is usually <em>what you remember</em>, not{" "}
                <em>how you search</em>.
              </span>{" "}
              When skills help, it&rsquo;s mostly because what got captured had
              real structure to it, not because the search step got smarter.
              Tuning the retriever, swapping rerankers, hybrid search &mdash;
              none of them make a difference if the stored skills are vague to
              begin with. Better to spend that energy on{" "}
              <em>what to write down</em> in the first place.
            </NotePoint>

            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                When different problems look alike but need different methods,
                search will mislead you.
              </span>{" "}
              Math is the cleanest example: combinatorics, generating-function
              problems, and group-theory problems all use words like
              &ldquo;triangle&rdquo;, &ldquo;vertex&rdquo;,
              &ldquo;configuration&rdquo;. A search-based system matches on the
              words, pulls up a skill from a different family, the agent
              follows it, and a problem it would have gotten right at baseline
              now gets wrong. The fix isn&rsquo;t a better retriever. It&rsquo;s
              giving each skill a way to say{" "}
              <em>&ldquo;I&rsquo;m for this kind of problem&rdquo;</em>.
            </NotePoint>

            <NotePoint icon="⚠️">
              <span className="font-semibold text-foreground">
                Don&rsquo;t inject by default.
              </span>{" "}
              A wrong skill can take a problem the agent would have solved and
              break it. A missing skill just leaves things where they were. So
              on tricky domains, the safer default isn&rsquo;t &ldquo;always
              use a skill&rdquo;, it&rsquo;s &ldquo;use one only when
              you&rsquo;re sure it fits&rdquo;. Most methods today inject too
              eagerly.
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
              For each domain, we grouped problems by what they have in common:
              jobs (for knowledge work), topics (for web search), repository
              patterns (for software issues), problem neighborhoods (for code
              challenges). Then we made sure every test problem has training
              problems in the same group. That way, if a method doesn&rsquo;t
              help, you can&rsquo;t blame it on the test being unrelated to
              anything the agent ever saw.
            </NotePoint>

            <NotePoint icon="🔹">
              <span className="font-semibold text-foreground">
                Every cell on the leaderboard is real.
              </span>{" "}
              Two agent frameworks, two model sizes, five domains, four
              self-evolution methods: that&rsquo;s 80 combinations, each
              measured against the same no-skill baseline. Every cell ran with
              its method&rsquo;s default settings and the same task, tool, and
              scoring setup, and we tracked how many turns it took alongside
              accuracy. No placeholders, no &ldquo;not evaluated under this
              setting&rdquo; gaps.
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
