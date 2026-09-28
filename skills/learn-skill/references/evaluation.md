# Evaluation

Seeing a skill trigger shows the agent found it, not that it helped. Evaluation answers whether the skill beats the baseline (no skill, or the previous version), on which prompts, and at what cost in time and tokens.

## Contents
- Designing test cases
- Coverage matrix
- Tests by skill type
- Workspace layout (the scripts depend on it)
- Step 1: Launch every run together
- Step 2: Draft assertions while the runs work
- Step 3: Capture timing as each run finishes
- Step 4: Grade, aggregate, analyze, and open the viewer
- Step 5: Read the feedback
- Variance, blind comparison, and wording micro-tests
- Testing on other models
- Environment adaptations

## Designing test cases

Start with 2–3 prompts at Standard rigor, or 5–10 at Deep. Each is something a real user would type, with realistic context: file paths, column names, a bit of backstory, casual phrasing. Vary them in formality, detail, and difficulty, and make at least one probe an edge case (malformed input, an ambiguous request, the boundary of the skill's scope).

Share the prompts with the user before running them ("Here are the test cases I'd like to try. Do these look right, or should we add any?"). Then save them to `<skill>/evals/evals.json`, prompts only for now:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {"id": 1, "prompt": "...", "expected_output": "What success looks like", "files": ["evals/files/sample.csv"]}
  ]
}
```

Assertions come later, once you've seen outputs. The full schema is in `references/schemas.md`.

## Coverage matrix

Passing tasks doesn't mean the skill's instructions were exercised; in one study, agent runs touched only about 40% of a skill's behavioral constraints. At Deep rigor, check coverage:

```bash
python3 <skill-dir>/scripts/extract_units.py <skill-dir> --source-id S --format md
```

Map each `step`, `rule`, and `gotcha` unit to the evals that would exercise it. Add evals for high-risk units with no coverage, and delete units no plausible prompt would ever exercise.

## Tests by skill type

| Type | What to test |
|---|---|
| Technique | Applying it to new cases, variations, and cases with missing information |
| Reference | Retrieval (does the agent find the right fact?) and correct application |
| Discipline | Pressure scenarios (below): does the agent comply when it wants not to? |
| Generator | The output itself: structure, required content, that it renders or parses |
| Task or workflow | End to end in a safe environment, including failure paths |
| Triggering | Should and should-not-trigger queries (`references/description-optimization.md`) |

**Pressure scenarios** for discipline skills: realistic situations combining three or more pressures (time, sunk cost, authority, exhaustion, "be pragmatic"), with concrete file paths and a forced choice between options, phrased as real work ("choose and act"), not a quiz. Record the rationalizations from baseline runs word for word; they become the skill's rationalization table.

## Workspace layout (the scripts depend on it)

```
<workspace>/iteration-N/
├── eval-<descriptive-name>/          # must start with "eval-"
│   ├── eval_metadata.json
│   ├── with_skill/                   # candidate
│   │   └── run-1/                    # "run-" plus a number; run-2, run-3 for variance
│   │       ├── outputs/              # files the run produced, plus transcript.md and user_notes.md
│   │       ├── timing.json
│   │       └── grading.json
│   └── without_skill/                # baseline
│       └── run-1/...
├── benchmark.json
└── benchmark.md
```

- New skill: configurations `with_skill` (candidate) and `without_skill` (baseline).
- Improving an existing skill: `new_skill` (candidate) and `old_skill` (baseline, pointing at `<workspace>/skill-snapshot/`).
- `aggregate_benchmark.py` finds evals only in `eval-*` folders and runs only in `run-*` folders; the viewer finds any folder that holds an `outputs/` folder. Other names give an empty benchmark.
- Name each eval for what it tests (`eval-missing-emails`), not `eval-0`.

`eval_metadata.json` per eval (write a fresh one for each new or changed eval in every iteration):

```json
{"eval_id": 1, "eval_name": "missing-emails", "prompt": "The user's task prompt", "assertions": []}
```

## Step 1: Launch every run together

For each eval, launch the candidate and the baseline run together, so they finish around the same time; don't launch candidates first and come back for baselines. Each run is a fresh session (see "Environment adaptations" for how to get one in your client), so no context from building the skill leaks into it.

Candidate run prompt:

```
Execute this task:
- Skill path: <absolute path to the skill>. Read its SKILL.md first and follow it.
- Task: <eval prompt>
- Input files: <absolute paths, or "none">
- Save outputs to: <workspace>/iteration-N/eval-<name>/with_skill/run-1/outputs/
- Outputs to save: <what the user cares about, e.g. "the final .xlsx">
- Also write outputs/transcript.md (each step you took, with the commands you ran
  and their key results) and outputs/user_notes.md (anything you were unsure of,
  workarounds you used, anything a reviewer should check).
```

Keep eval runs free of real side effects. If the task would normally install, deploy, send, publish, or edit the user's files, add a line such as "Write anything you would install or send into the outputs folder instead; don't modify anything outside it", and generate input fixtures into the run folder rather than pointing runs at the user's real files.

The baseline prompt is identical except for the skill line: omit it for `without_skill`, or point it at `<workspace>/skill-snapshot/` for `old_skill`, and change the output path to match.

Before improving an existing skill, snapshot it first: `cp -r <skill> <workspace>/skill-snapshot/`.

## Step 2: Draft assertions while the runs work

Use the waiting time. Draft assertions for each eval and explain them to the user; if assertions already exist, review them.

Good assertions are objectively checkable and **discriminating**: they pass when the skill does its job and fail when it doesn't.

- Good: "The output file is valid JSON", "Both chart axes are labeled", "At least 3 recommendations, each citing a line of the input".
- Weak: "The output is good" (ungradable), "Uses exactly the phrase 'Total Revenue: $X'" (brittle), "A file named report.pdf exists" (passes on an empty file).

Check subjective qualities such as style or design in the human review, not with forced assertions. Write assertions into each `eval_metadata.json` and into `evals/evals.json`.

## Step 3: Capture timing as each run finishes

Record each run's cost as soon as it finishes, in `run-1/timing.json`. Where the numbers come from depends on the client: Claude Code's subagent completion notification includes `total_tokens` and `duration_ms` (and they aren't stored anywhere else, so save them immediately); agent CLIs usually report token usage in their JSON output (for example Codex's `turn.completed` event); otherwise record wall-clock time and leave tokens out.

```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

## Step 4: Grade, aggregate, analyze, and open the viewer

1. **Grade** each run in a fresh session briefed with `agents/grader.md`, or inline. Save `grading.json` in the run folder. The `expectations` entries must use the fields `text`, `passed`, and `evidence`, because the viewer reads those exact names. Check anything mechanical (valid JSON, row counts, file properties) with a script rather than by eye; scripts are more reliable and reusable across iterations. The grader also critiques the assertions; act on its suggestions.
2. **Aggregate**, using absolute paths, since the command runs from the skill folder:
   ```bash
   cd <skill-dir> && python3 -B -m scripts.aggregate_benchmark <abs-workspace>/iteration-N --skill-name <name>
   ```
   This writes `benchmark.json` and `benchmark.md` with pass rate, time, and tokens per configuration (mean ± stddev) and the candidate-minus-baseline delta.
3. **Analyze.** Read the benchmark as `agents/analyzer.md` ("Analyzing Benchmark Results") describes, and add your observations to the `notes` array in `benchmark.json`: assertions that pass in both configurations (they don't measure the skill), assertions that fail in both (broken or too hard), high-variance evals, and time or token outliers.
4. **Open the viewer** before you evaluate the outputs yourself; get them in front of the human quickly.
   ```bash
   nohup python3 <skill-dir>/eval-viewer/generate_review.py <workspace>/iteration-N \
     --skill-name <name> --benchmark <workspace>/iteration-N/benchmark.json \
     --previous-workspace <workspace>/iteration-<N-1> > /dev/null 2>&1 &
   echo $! > <workspace>/viewer.pid   # shell variables don't survive between tool calls
   ```
   Leave out `--previous-workspace` on the first iteration.
   Without a display (headless, remote, Cowork), add `--static <path>/review.html` to write a standalone file and give the user its path. Use `generate_review.py` rather than hand-built HTML.
5. **Tell the user**: "The results are open in your browser. 'Outputs' lets you step through each test case and leave feedback; 'Benchmark' shows the numbers. Let me know when you're done."

## Step 5: Read the feedback

When the user is done, read `feedback.json` from the iteration folder (from the server), or from where the browser downloaded it (static mode; on WSL look in the Windows Downloads folder, `/mnt/c/Users/<name>/Downloads/`):

```json
{"reviews": [{"run_id": "eval-missing-emails-with_skill-run-1", "feedback": "the chart has no axis labels", "timestamp": "..."}], "status": "complete"}
```

Empty feedback means the output looked fine. Focus on the runs with specific complaints, then stop the viewer: `kill $(cat <workspace>/viewer.pid)`. Continue with Phase 8 in SKILL.md.

## Variance, blind comparison, and wording micro-tests

**Variance.** Single runs lie. At Deep rigor, run each configuration three times (`run-1` to `run-3`). High stddev means either a flaky assertion or instructions ambiguous enough that runs interpret them differently; read those transcripts.

**Blind comparison.** To answer "is the new version actually better?", give both outputs to a comparator session (`agents/comparator.md`) without saying which is which, then have `agents/analyzer.md` explain why the winner won. This catches quality differences that assertions miss, for example when both outputs pass every assertion.

**Wording micro-tests.** Before a full eval round, check that a specific instruction's wording changes behavior:
1. Use one fresh-context sample per call, with the realistic surrounding context (the whole skill, not the instruction alone) and a task that tempts the failure.
2. Always include a no-guidance control. If the control doesn't fail, there is nothing to fix; drop the instruction.
3. Run at least 5 repetitions per variant, and read every flagged output yourself instead of trusting a regex count.
4. Treat convergence as the signal: when wording lands, repetitions produce the same shape.

## Testing on other models

A skill tuned on a large model may be too terse for a smaller one; one written for a small model may over-explain to a large one. If the skill will run on other models, repeat a subset of evals on each of them (a subagent model override, or the agent CLI's model flag). If it will run in several agents (Codex, Cursor, Claude Code, ...), run a subset in each, since agents differ in how they load and follow skills.

## Environment adaptations

**Fresh sessions.** Use whatever gives each run a clean context:
- Subagents, where the client has them (Claude Code, and others with an agent or task tool). Launch all runs in one turn.
- Otherwise, an agent CLI in non-interactive mode, one process per run, launched in parallel as background commands. Put the run prompt in the query and make the agent work in the run folder, for example `cd <run-dir> && codex exec --json --skip-git-repo-check "<run prompt>" > outputs/transcript.jsonl`, or `opencode run --format json "<run prompt>"`. The JSON stream doubles as the transcript and usually carries token counts.

**No way to start fresh sessions** (for example a chat product without subagents or a shell). Run each test prompt yourself, one at a time, after reading the skill's SKILL.md. This is less rigorous, since you wrote the skill and know its intent, so lean on human review. Skip baselines and benchmarks. Show each prompt and its output in the chat, save files the user must inspect, and ask for feedback inline. Skip blind comparison, and optimize the description by reasoning (`references/description-optimization.md`).

**No display** (headless, remote, containers). Use the viewer's `--static` mode and give the user the file path; feedback then arrives as a downloaded `feedback.json`. On WSL, `explorer.exe <path>` or `wslview <path>` opens a file in the Windows browser.

**CI.** Claude Code plugins can use `claude plugin eval`, which runs with-and-without evals in isolated sessions and exits non-zero below a threshold. Its format differs from `evals/evals.json`.
