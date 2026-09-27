# Finding existing skills

Search before you build. An existing, well-tested skill may solve the need outright, and near-misses still count as research: they show how others scoped the problem, what they named it, and which gotchas they hit.

## Contents
- Where to look, in order
- Judging quality
- Reading a candidate without installing it
- Deciding what to do with what you found
- Presenting options to the user
- Installing on the user's behalf

## Where to look, in order

**1. Skills already installed.** The user may already have a skill that covers this, and a new one would compete with it for the same prompts.

```bash
# Personal, synced, project, cross-agent, and plugin skills, each with its description.
# (find rather than shell globs: zsh aborts on a glob that matches nothing.)
find ~/.claude/skills .claude/skills ~/.agents/skills .agents/skills ~/.claude/plugins/cache \
  -maxdepth 6 -name SKILL.md 2>/dev/null | while read -r f; do
  echo "$f"
  awk '/^description:/{p=1} p && /^[A-Za-z_-]+:/ && !/^description:/{exit} p' "$f" | head -3 | cut -c1-200
done
```

Plugin skills appear whether or not the plugin is enabled.

The skill listing in your own context also shows every skill available in this session.

**2. The skills.sh registry.** `npx skills` is the package manager for the open skills ecosystem. With a query it runs non-interactively:

```bash
npx -y skills find "<domain> <task>"          # e.g. "pdf forms", "react performance"
npx -y skills find "<query>" --owner <org>    # one publisher only
```

Each result prints as `owner/repo@skill  N installs` followed by a skills.sh link. Try two or three phrasings (domain plus task, synonyms, the tool's name), since the search is keyword-based. The leaderboard at https://skills.sh ranks skills by installs.

**3. Well-known publishers.** Official and widely used sources include `anthropics/skills`, `anthropics/claude-plugins-official`, `vercel-labs/agent-skills`, and `openai/skills`. To list a repo's skills without installing anything:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_skill.py <owner/repo> --dest <workspace>/sources --list
```

**4. GitHub code search**, for skills that aren't in the registry:

```bash
gh search code "<keyword>" --filename SKILL.md --limit 30
```

## Judging quality

Weigh these together; no single signal is enough.

| Signal | Prefer | Be cautious |
|---|---|---|
| Installs (skills.sh) | 1K+ | under 100 |
| Publisher | official orgs and known maintainers | unknown account, name imitating a vendor |
| Repo stars and activity | 100+ stars, recent commits | under 100 stars, abandoned |
| License | explicit (MIT, Apache-2.0, ...) | none, which means you may not copy it |
| Vet result (`scripts/vet_skill.py`) | clean, or findings explained by its purpose | unexplained network, credential, or persistence behavior |
| Craft | valid frontmatter, focused scope, evals present | sprawling, generic "best practices" prose |

Popularity measures adoption, not fit or safety. A 100K-install skill can still be wrong for this user's environment.

## Reading a candidate without installing it

Installing a skill makes it live in the agent immediately, with whatever tool grants and shell commands it carries. To read one, copy it into the workspace instead:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_skill.py <source> --dest <workspace>/sources
```

`<source>` can be `owner/repo@skill`, `owner/repo` (with `--skill <name>`), a GitHub URL, a skills.sh URL, any git URL, a raw `SKILL.md` URL, or a local path. The script clones shallowly, copies only skill folders, never follows symlinks out of the repo, never runs anything it fetched, and writes a `.provenance.json` beside each copy (source, commit, license). Then vet it with `references/vetting-skills.md`.

## Deciding what to do with what you found

| Finding | Action |
|---|---|
| A trusted skill that fits the need and passes vetting | Recommend installing it and stop building. Offer to run the user's own prompts against it first (Phase 7 with the existing skill as the candidate). |
| One skill that is close but has gaps | Improve a copy: keep its license and attribution, snapshot it as the baseline, and continue at Phase 6. |
| Several skills that each cover part of the need | Harvest the best parts (`references/cherry-picking.md`). |
| A strong skill that conflicts with the one you would build | Tell the user; two overlapping skills compete for the same prompts. Consider extending the existing one instead. |
| Nothing relevant | Build fresh. Note in `research.md` what adjacent skills cover and how they are named. |

## Presenting options to the user

For each candidate give: the name and what it does in one line, installs and publisher, your vet verdict, the install command, and a link. End with your recommendation.

```
Found one strong match: `react-best-practices` from vercel-labs/agent-skills
(185K installs). It covers React and Next.js performance rules. Vet: clean,
instructions only, no scripts.

Install: npx skills add vercel-labs/agent-skills@react-best-practices -g -a claude-code
More: https://skills.sh/vercel-labs/agent-skills/react-best-practices

My recommendation: install it rather than building; it already covers your
three example prompts.
```

When nothing fits, say so plainly and move on to building; the search was not wasted.

## Installing on the user's behalf

Install only after the user agrees to that specific skill.

```bash
npx -y skills add <owner/repo@skill> -g -a claude-code -y   # -g user scope; omit for this project only
```

`-y` skips the CLI's confirmation prompts, which is why the user's explicit go-ahead matters. By default the CLI symlinks from a canonical copy; `--copy` makes independent copies. Afterwards, check the skill appears (`npx skills list`, or `/skills` in Claude Code). Skills added to `~/.claude/skills/` load in local sessions but not in Cowork or cloud sessions; see `references/platform-reference.md`.
