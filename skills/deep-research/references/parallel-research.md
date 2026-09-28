# Parallel research

For broad topics, split the 3-5 sub-questions across parallel subagents where the client supports them; otherwise run the same plan sequentially in one session.

## Split

- Assign 1-2 sub-questions per worker with the shared scope, output template, and citation rules.
- Each worker searches, deep-reads, and returns findings with sources plus versions/dates — no cross-worker coordination needed mid-run.

## Synthesize

- The main session merges worker outputs, removes duplicates, resolves conflicts (primary source wins; unresolved stays flagged), and writes the single final report.
- If no subagents exist, follow the same split as sequential passes over one sub-question at a time; the log template in `search-strategy.md` keeps state across passes.
