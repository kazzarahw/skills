#!/usr/bin/env python3
# Modified from anthropics/skills skill-creator (Apache-2.0): added the agent-neutral
# "command" runner (--runner command --agent-cmd ... --skills-dir ...), so trigger
# evals work with any agent CLI that loads skills from a folder, not only claude -p;
# each query now runs in its own folder so parallel workers can't see each other's copies.
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes an agent to trigger (read the skill)
for a set of queries. Outputs results as JSON.

Runners:
  claude   (default) installs the candidate as a temporary Claude Code command file and
           watches `claude -p` stream-json output for the Skill/Read call.
  command  installs the candidate as a temporary skill folder in --skills-dir (default
           .agents/skills, the cross-agent convention) and runs --agent-cmd, a shell
           template with {query} (shell-quoted) and optionally {model}. The query counts
           as triggered when the agent's output mentions the temporary skill's unique
           name, so use the agent's JSON or verbose output mode. Example:
             --agent-cmd 'codex exec --json --sandbox read-only --skip-git-repo-check {query}'
"""

import argparse
import json
import os
import select
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


RUNS_DIR = ".skill-eval-runs"


def find_project_root(runner: str = "claude") -> Path:
    """Return the folder that holds per-query run folders: the current directory.

    Every query runs in its own <cwd>/.skill-eval-runs/<id>/ folder containing only its
    temporary skill, so parallel runs can't load each other's copies (the original
    version shared one .claude/commands/ folder across workers, and walked up to
    ~/.claude/ when run from inside the home directory).
    """
    return Path.cwd()


INSTALLED_SKILL_DIRS = [
    ".agents/skills", ".claude/skills", "~/.agents/skills", "~/.config/agents/skills", "~/.claude/skills",
    "~/.codex/skills", "~/.cursor/skills", "~/.copilot/skills", "~/.gemini/skills", "~/.config/opencode/skills",
]


def warn_installed_copies(skill_name: str) -> None:
    """Warn when a skill with the same name is installed where agents will also see it.

    Agents often load the installed copy instead of the temporary test copy, which
    counts as "not triggered" and makes a good description look bad.
    """
    found = [d for d in INSTALLED_SKILL_DIRS if (Path(d).expanduser() / skill_name / "SKILL.md").exists()]
    if found:
        print(f"Warning: '{skill_name}' is already installed in {', '.join(found)}. Agents that read those "
              "folders may load the installed copy instead of the test copy, which scores as a miss. "
              "Move it aside for the duration of the eval for accurate results.", file=sys.stderr)


def run_single_query_command(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    agent_cmd: str,
    skills_dir: str,
    model: str | None = None,
    trigger_regex: str | None = None,
) -> bool:
    """Run one query through an arbitrary agent CLI and report whether it used the skill.

    Triggered means the output matches trigger_regex ({name} = the temporary skill's
    name, regex-escaped) or, without one, simply mentions that name.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    # Each query gets its own folder, so concurrent runs never see each other's copies
    run_root = Path(project_root) / RUNS_DIR / unique_id
    skill_dir = run_root / skills_dir / clean_name
    indented_desc = "\n  ".join(skill_description.split("\n"))
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {clean_name}\ndescription: |\n  {indented_desc}\n---\n\n"
        f"# {skill_name}\n\nThis skill handles: {skill_description}\n"
    )
    import re
    pattern = re.compile(trigger_regex.replace("{name}", re.escape(clean_name)) if trigger_regex else re.escape(clean_name))
    cmd = agent_cmd.replace("{query}", shlex.quote(query)).replace("{model}", shlex.quote(model or ""))
    process = subprocess.Popen(
        ["bash", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        cwd=run_root,
        start_new_session=True,  # so the whole agent process tree can be killed
    )
    out = process.stdout
    assert out is not None
    seen = ""
    try:
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([out], [], [], 1.0)
            if ready:
                chunk = os.read(out.fileno(), 8192)
                if not chunk:
                    break
                # keep a tail long enough to catch a name split across reads
                seen = (seen + chunk.decode("utf-8", errors="replace"))[-8192:]
                if pattern.search(seen):
                    return True
            elif process.poll() is not None:
                break
        rest = out.read() if process.poll() is not None else b""
        return bool(pattern.search(seen + (rest or b"").decode("utf-8", errors="replace")))
    finally:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        shutil.rmtree(run_root, ignore_errors=True)


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    # Each query gets its own folder, so concurrent runs never see each other's copies
    run_root = Path(project_root) / RUNS_DIR / unique_id
    project_commands_dir = run_root / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=run_root,
            env=env,
        )

        triggered = False
        start_time = time.time()
        buffer = ""
        # Track state for stream event detection
        pending_tool_name = None
        accumulated_json = ""

        try:
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        buffer += remaining.decode("utf-8", errors="replace")
                    break

                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue

                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Early detection via stream events
                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                else:
                                    return False

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if clean_name in accumulated_json:
                                    return True

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                return clean_name in accumulated_json
                            if se_type == "message_stop":
                                return False

                    # Fallback: full assistant message
                    elif event.get("type") == "assistant":
                        message = event.get("message", {})
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                                triggered = True
                            elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                                triggered = True
                            return triggered

                    elif event.get("type") == "result":
                        return triggered
        finally:
            # Clean up process on any exit path (return, exception, timeout)
            if process.poll() is None:
                process.kill()
                process.wait()

        return triggered
    finally:
        shutil.rmtree(run_root, ignore_errors=True)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    runner: str = "claude",
    agent_cmd: str | None = None,
    skills_dir: str = ".agents/skills",
    trigger_regex: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    if runner == "command" and not agent_cmd:
        raise ValueError("--runner command needs --agent-cmd (a shell template containing {query})")
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                if runner == "command":
                    future = executor.submit(
                        run_single_query_command,
                        item["query"], skill_name, description, timeout, str(project_root),
                        agent_cmd, skills_dir, model, trigger_regex,
                    )
                else:
                    future = executor.submit(
                        run_single_query,
                        item["query"],
                        skill_name,
                        description,
                        timeout,
                        str(project_root),
                        model,
                    )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model for the agent (claude runner: passed to claude -p; command runner: substituted for {model})")
    parser.add_argument("--runner", choices=["claude", "command"], default="claude",
                        help="claude: Claude Code's claude -p; command: any agent CLI via --agent-cmd")
    parser.add_argument("--agent-cmd", default=None,
                        help="Shell template for the command runner, with {query} and optional {model}")
    parser.add_argument("--skills-dir", default=".agents/skills",
                        help="Where the command runner installs the temporary skill, relative to cwd")
    parser.add_argument("--trigger-regex", default=None,
                        help="Command runner: regex that marks a trigger, with {name} for the temporary skill's name "
                             "(default: any mention of the name)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()
    if args.runner == "command" and not args.agent_cmd:
        parser.error("--runner command requires --agent-cmd")

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root(args.runner)
    warn_installed_copies(name)

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        runner=args.runner,
        agent_cmd=args.agent_cmd,
        skills_dir=args.skills_dir,
        trigger_regex=args.trigger_regex,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
