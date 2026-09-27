# Description optimization

The description decides whether the skill loads. This procedure measures how often it triggers on prompts where it should and shouldn't, then improves it without overfitting. Run it once the body is stable, since a changing body changes what the description should promise.

## Contents
- How triggering works
- Step 1: Write the trigger queries
- Step 2: Review them with the user
- Step 3: Run the optimization loop
- Step 4: Apply and verify
- Gotchas
- Without the claude CLI

## How triggering works

Claude sees each skill's name and description in its skill listing and decides from those alone whether to load one. It consults skills mainly for work it can't easily do alone: a one-step request like "read this PDF" may not trigger even a perfectly described PDF skill, because Claude just does it. So trigger queries must be substantive enough that a skill would genuinely help; trivial queries make poor tests whatever the description says.

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

## Step 3: Run the optimization loop

Tell the user it takes a while and runs in the background. The loop:
- splits the queries 60/40 into train and held-out test sets, stratified by label;
- runs each query 3 times through `claude -p` to get a trigger rate;
- asks Claude for an improved description based only on the train-set failures;
- repeats for up to 5 iterations;
- returns the best description as judged by the *test* score, not the train score, to avoid overfitting.

Run it from the workspace, after giving the workspace its own `.claude/` folder (see Gotchas for why):

```bash
mkdir -p <workspace>/.claude && cd <workspace> && \
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -B -m scripts.run_loop \
  --eval-set <abs-path>/eval_set.json \
  --skill-path <abs-path-to-skill> \
  --model <the model ID powering this session> \
  --max-iterations 5 --results-dir <workspace>/trigger-opt --verbose
```

Run it as a background command. Use the model ID of the current session so the test matches what the user will experience. Add `--report none` in headless environments; otherwise a live HTML report opens in the browser. While it runs, check the output periodically and tell the user which iteration it's on and how the scores look.

## Step 4: Apply and verify

1. Take `best_description` from the JSON output and update the frontmatter. Show the user the before and after, with the train and test scores.
2. Re-run `validate_skill.py`; descriptions tend to grow during optimization.
3. Sanity-check it on 5–10 fresh queries that were not in the optimization set, because only unseen queries show whether the description generalizes.

## Gotchas

- **Project root discovery.** `run_eval.py` writes a temporary command file into the nearest ancestor folder that contains `.claude/`, and runs `claude -p` there. Under your home directory that is usually `~/.claude/` itself, so the temporary files would land in the user's personal commands folder. Creating `<workspace>/.claude/` and running from the workspace keeps them there.
- **An installed copy competes with the test copy.** If the skill under test (or an older version of it) is already installed where `claude -p` can see it, Claude may invoke the installed one, which counts as not triggering the test copy and depresses the scores. Optimize before installing, or with the user's agreement move the installed copy aside for the duration.
- **Neighboring skills compete too.** Every skill installed for the user is part of the test environment. That is realistic, but when a near-miss query triggers a different installed skill, that's a pass for this skill, not a problem to fix.
- **Scores are noisy.** 3 runs per query at a 0.5 threshold is a coarse measure. If performance isn't improving after several iterations, suspect the queries (too easy, too hard, mislabeled) before the description.
- **Keep it general.** Adding keywords from failed queries overfits. Name the category of intent those queries represent. If you're stuck, try a structurally different description rather than another tweak.

## Without the claude CLI

On claude.ai, or wherever `claude -p` is unavailable, optimize by reasoning instead. For each query, judge honestly whether the current description would make you load the skill if you saw it in a list of 50 skills. Revise against the misses using the rules in `references/writing-guide.md` (Part 1), and tell the user the result is unmeasured.
