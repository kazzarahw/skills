# Codebase plus web

## Ladder: local first, escalate only on failure

1. Local grep, glob, and file reads for what the code does.
2. Terminal and repo CLI (tests, configs, vendored docs, changelogs).
3. Built-in web search for upstream docs and issues.
4. `gh` for issues, PRs, and releases; semantic or symbol search for conceptual questions.
5. Heavy MCPs (browser, deep docs) last.

Cheap deterministic tools settle most code questions; reaching for heavy tools first wastes context.

## Rules

- Classify first: codebase-understanding, library or API research, bug investigation, or pattern discovery — each maps to a different tool path above.
- Treat the repo as ground truth for what the code does and external sources as ground truth for what it should do or what changed; note version mismatches explicitly.
- Record `path:line` plus the repo or library version for every code-backed claim, cross-checked against changelogs or releases. Untagged or dirty trees: record the commit SHA (plus a `dirty` flag).
- Check the working tree (tests, configs, vendored docs) before the web; the answer may already be local.
- Report missing paths and version skew as findings.
