# Sources

What this skill's guidance rests on. Read this when the user asks where a practice comes from, or wants the guidance re-checked against the current docs; platform details change, and these are the pages to re-read.

## Specification and platform documentation
- Agent Skills specification: https://agentskills.io/specification (frontmatter fields, name rules, progressive disclosure). Index of all pages: https://agentskills.io/llms.txt
- agentskills.io authoring guides: best practices, optimizing descriptions, evaluating skills, and using scripts, under https://agentskills.io/skill-creation/
- Claude Code skills documentation: https://code.claude.com/docs/en/skills (extension fields, locations, substitutions, dynamic context injection, content lifecycle and compaction, listing budget)
- Claude platform, skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Claude platform, skills overview (security considerations, runtime constraints by surface): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude prompting best practices (newer models over-trigger on aggressive wording): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## Skills this one draws on
- Anthropic's skill-creator (Apache-2.0), the base for the eval loop, grader, comparator, analyzer, viewer, benchmark, and description-optimization scripts: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- Vercel's find-skills, and the `npx skills` CLI it teaches (discovery and quality signals): https://skills.sh/vercel-labs/skills/find-skills and https://github.com/vercel-labs/skills
- obra/superpowers `writing-skills` (baseline-first testing, matching the form of guidance to the failure, pressure scenarios, wording micro-tests): https://github.com/obra/superpowers
- mattpocock `writing-for-agents` (context pointers, completion criteria, leading words, prohibitions that backfire, pruning no-ops): https://github.com/mattpocock/skills
- OpenAI's skill-creator (scaffolding, what not to include in a skill): https://github.com/openai/skills
- superagent-ai `skill-security` (threat categories for vetting; ideas only, no code copied): https://github.com/superagent-ai/skills
- Research skills: mattpocock `research`, affaan-m `deep-research` (primary sources, sub-questions, citations, flagging single-source claims)

## Research
- SkillsBench (arXiv 2602.12670): curated skills raised pass rates by about 16 points on average, but many tasks got worse; self-generated skills gave no average benefit; focused skills with 2–3 modules beat exhaustive ones.
- SkillRevise (arXiv 2606.01139): revising skills from execution traces raised success from 36% to 62%.
- Skill Coverage (arXiv 2606.20659): test runs exercised only about 40% of skills' behavioral constraints; emphasizing ignored instructions recovered a meaningful share of failures.
- SkillJuror (arXiv 2606.11543): hierarchical progressive disclosure changed how agents used skill resources and modestly improved pass rates, most for tasks needing guidance and repair rather than exact formatting.
