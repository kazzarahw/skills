# Description optimization

The description decides whether the skill loads. This procedure measures how often it triggers on prompts where it should and shouldn't, then improves it without overfitting. Run it once the body is stable, since a changing body changes what the description should promise.

## Contents
- How triggering works
- Step 1: Write the trigger queries
- Step 2: Review them with the user
- Step 3: Choose a runner
- Step 4: Run the optimization loop
- Step 5: Apply and verify
- Gotchas
- Without an agent CLI

## How triggering works

An agent sees each skill's name and description in its skill catalog and decides from those alone whether to load one. Agents consult skills mainly for work they can't easily do alone: a one-step request like "read this PDF" may not trigger even a perfectly described PDF skill, because the agent just does it. So trigger queries must be substantive enough that a skill would genuinely help; trivial queries make poor tests whatever the description says.

Agents differ in how readily they reach for skills. If the skill will run in several agents, measure in each of them; a description tuned only against one may under- or over-trigger in another.

## Step 1: Write the trigger queries

Write about 20 queries, 8–10 that should trigger and 8–10 that should not, and save them as JSON:

```json
[
  {"query": "ok so my boss sent me 'Q4 sales FINAL v2.xlsx' (in downloads) and wants a profit margin column, revenue is col C costs col D i think", "should_trigger": true},
  {"query": "can you write a python script that reads a csv and loads each row into our postgres db", "should_trigger": false}
]
```

**Make them realistic**: file paths, personal context, column and company names, casual phrasing, abbreviations, the occasional typo, and a mix of short and long.

**Should-trigger queries** test coverage. Vary the phrasing (formal and casual), the explicitness (some name the domain, others only describe the need), and the complexity (a single step, or the relevant task buried inside a larger one). The most valuable are those where the skill would help but the connection isn't obvious from the wording.

**Should-not-trigger queries** test precision. The valuable ones are near-misses: they share keywords or concepts with the skill but need something else (an adjacent domain, the same file type for a different job, a task another tool handles better). "Write a fibonacci function" as a negative for a PDF skill tests nothing.

## Step 2: Review them with the user

Bad queries produce a bad description, so have the user check them.

1. Read `assets/eval_review.html`.
2. Replace `__EVAL_DATA_PLACEHOLDER__` with the JSON array (unquoted, since it is a JavaScript assignment), `__SKILL_NAME_PLACEHOLDER__` with the skill name, and `__SKILL_DESCRIPTION_PLACEHOLDER__` with the current description.
3. Write the result to the workspace (`<workspace>/trigger-review.html`) and open it, or give the user the path.
4. The user edits queries, flips `should_trigger`, adds or removes rows, and clicks "Export Eval Set", which downloads `eval_set.json`.
5. Take the newest copy from the Downloads folder (`eval_set (1).json` and so on if there are several; on WSL, the Windows Downloads folder under `/mnt/c/Users/<name>/Downloads/`) and save it into the workspace.

## Step 3: Choose a runner

The scripts run each query through a real agent with a temporary copy of the skill installed, and check whether the agent loaded it.

| Runner | Use when | How it works |
|---|---|---|
| `--runner command` | Any agent with a non-interactive CLI that loads skills from a folder (Codex, OpenCode, Gemini CLI, Copilot CLI, ...) | Installs the temporary skill in `--skills-dir` (default `.agents/skills`, relative to where you run it), runs `--agent-cmd`, and counts a trigger when the output mentions the temporary skill's unique name |
| `--runner claude` (default) | Claude Code | Installs the temporary skill as a command file and watches `claude -p` stream output for the skill call |

For the command runner, use the agent's JSON or verbose output mode so skill loads are visible, and a read-only sandbox so negative queries can't change anything. Tested templates:

| Agent | `--agent-cmd` | `--trigger-regex` (optional, stricter) |
|---|---|---|
| Codex | `codex exec --json --sandbox read-only --skip-git-repo-check {query}` | `{name}/SKILL\.md` (Codex reads the file with a shell command) |
| OpenCode | `opencode run --format json {query}` | `"tool":"skill".*{name}` (OpenCode loads skills through a `skill` tool) |

`{query}` is shell-quoted for you; `{model}` is substituted if you pass `--model`. For another agent, run one query by hand with a probe skill installed and look at how its output shows the skill being loaded, then pick a template and, if file listings could mention the name without the skill being used, a stricter `--trigger-regex`. Command-runner agents are slower than `claude -p`: raise `--timeout` (90–180 seconds) and lower `--num-workers` to what the agent's rate limits allow.

The loop also needs an LLM to propose new descriptions. It uses `claude -p` by default; `--llm-cmd` takes any command that reads a prompt on stdin and prints the reply, such as `codex exec --skip-git-repo-check -` or `opencode run`.

## Step 4: Run the optimization loop

Tell the user it takes a while and runs in the background. The loop:
- splits the queries 60/40 into train and held-out test sets, stratified by label;
- runs each query 3 times to get a trigger rate;
- asks an LLM for an improved description based only on the train-set failures;
- repeats for up to 5 iterations;
- returns the best description as judged by the *test* score, not the train score, to avoid overfitting.

Run it from the workspace, as a background command:

```bash
cd <workspace> && PYTHONPATH="<skill-dir>" python3 -B -m scripts.run_loop \
  --eval-set <abs-path>/eval_set.json --skill-path <abs-path-to-skill> \
  --runner command --agent-cmd 'codex exec --json --sandbox read-only --skip-git-repo-check {query}' \
  --llm-cmd 'codex exec --skip-git-repo-check -' --timeout 150 --num-workers 4 \
  --max-iterations 5 --results-dir <workspace>/trigger-opt --report none --verbose
```

For Claude Code, drop the runner options and pass `--model <the session's model ID>` so the test matches what the user experiences. Without `--report none`, a live HTML report opens in the browser. While it runs, check the output periodically and tell the user which iteration it's on and how the scores look. To measure a single description without optimizing, use `scripts.run_eval` with the same runner options.

## Step 5: Apply and verify

1. Take `best_description` from the JSON output and update the frontmatter. Show the user the before and after, with the train and test scores.
2. Re-run `validate_skill.py`; descriptions tend to grow during optimization.
3. Sanity-check it on 5–10 fresh queries that were not in the optimization set, and in each target agent, because only unseen queries show whether the description generalizes.

## Gotchas

- **Temporary files.** Each query runs in its own `<cwd>/.skill-eval-runs/<id>/` folder holding only its temporary copy of the skill, so parallel runs can't load each other's copies; the folder is deleted afterwards. Run from the workspace.
- **An installed copy competes with the test copy.** If the skill under test (or an older version of it) is installed where the agent can see it, the agent may load that instead, which scores as a miss. Agents often read other agents' folders too (OpenCode reads `~/.claude/skills/`, for example). The scripts warn when they find a same-named installed copy; optimize before installing, or with the user's agreement move the installed copy aside for the duration.
- **Queries that depend on earlier conversation** ("turn what we just did into a skill") are hard to test in a single fresh turn: with no prior conversation, the agent often asks what the user means instead of loading the skill. Judge such queries by reading the transcript rather than trusting the score, or give them enough context in the query itself.
- **Neighboring skills compete too.** Every skill installed for the agent is part of the test, including skills the agent ships with (Codex has a built-in skill-creator, for example). That is realistic, but when a near-miss query triggers a different skill, that's a pass for this skill, not a problem to fix.
- **Scores are noisy.** 3 runs per query at a 0.5 threshold is a coarse measure, and the same query can go either way run to run. If performance isn't improving after several iterations, suspect the queries (too easy, too hard, mislabeled) before the description.
- **Keep it general.** Adding keywords from failed queries overfits. Name the category of intent those queries represent. If you're stuck, try a structurally different description rather than another tweak.

## Without an agent CLI

Where no agent can be run non-interactively (for example a chat product without a shell), optimize by reasoning instead. For each query, judge honestly whether the current description would make you load the skill if you saw it in a list of 50 skills. Revise against the misses using the rules in `references/writing-guide.md` (Part 1), and tell the user the result is unmeasured.
