"""Terminal tutorial for the AAMAD crew workflow.

``aamad tutorial`` teaches the methodology. It does not run personas or
write project artifacts.
"""

from __future__ import annotations

import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TextIO

import questionary
import yaml

from .validator import (
    BUILD_ARTIFACTS,
    DELIVER_ARTIFACTS,
    REVIEW_ARTIFACTS,
    SAD_DECISION_HEADINGS,
    SECURITY_MD,
)

WIDTH = 76


def _protect_commands(text: str) -> str:
    """Keep text inside backticks on one line when the paragraph wraps."""

    def repl(match: re.Match[str]) -> str:
        return match.group(0).replace(" ", "\u00a0")

    return re.sub(r"`[^`]+`", repl, text)


def _fill(text: str, *, subsequent_indent: str = "") -> str:
    filled = textwrap.fill(
        _protect_commands(text),
        width=WIDTH,
        break_on_hyphens=False,
        break_long_words=False,
        subsequent_indent=subsequent_indent,
    )
    return filled.replace("\u00a0", " ")

PRD_PATH = "project-context/1.define/prd.md"
SAD_PATH = "project-context/1.define/sad.md"


class TutorialCancelled(Exception):
    """Raised when the operator quits an interactive tutorial prompt."""


class Prompter(Protocol):
    def choose(self, message: str, options: list[tuple[str, str]]) -> str | None:
        """Return the selected option value, or None when the prompt is cancelled."""


@dataclass(frozen=True)
class Choice:
    value: str
    label: str
    correct: bool
    feedback: str


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    body: str
    prompt: str
    choices: tuple[Choice, ...]

    def correct(self) -> Choice:
        for choice in self.choices:
            if choice.correct:
                return choice
        raise RuntimeError(f"lesson {self.id} has no correct choice")


LESSONS: tuple[Lesson, ...] = (
    Lesson(
        id="what-aamad-is",
        title="What AAMAD is",
        body=(
            "AAMAD is a context-engineering framework for building multi-agent "
            "applications. The stable part is the development crew: personas, "
            "rules, templates, and markdown artifacts under project-context/. "
            "You drive that crew from Cursor, Claude Code, VS Code with GitHub "
            "Copilot, or Kiro.\n\n"
            "The CLI does not run Define, Build, and Deliver for you. "
            "`aamad init` copies the crew into the repo and prints which persona "
            "to open. You invoke one persona at a time, in a fresh chat per module.\n\n"
            "Runtime adapters (CrewAI, Claude Agent SDK, Cursor SDK) choose the "
            "runtime of the application you generate in Build. They do not change "
            "the crew's phase order. `crew.autonomy` in aamad.config.yml governs "
            "how far the development crew proceeds on its own. It does not pick "
            "the application pattern, and it does not raise tool privilege."
        ),
        prompt="What does `aamad init` do?",
        choices=(
            Choice(
                "installs",
                "Copies the crew into the project and names the persona to open next",
                True,
                "Init installs files and prints next steps. Personas run in the IDE.",
            ),
            Choice(
                "writes-prd",
                "Runs the Product Manager and writes the PRD",
                False,
                "The PRD is written by @product-mgr in the IDE, after init.",
            ),
            Choice(
                "runs-phases",
                "Starts the selected runtime and executes every phase",
                False,
                "No runtime executes AAMAD's own phases. You invoke each persona.",
            ),
        ),
    ),
    Lesson(
        id="install-and-init",
        title="Install and initialize",
        body=(
            "Requires Python 3.9+. From any shell:\n\n"
            "  pip install aamad\n"
            "  cd your-project\n"
            "  aamad init\n\n"
            "On a terminal, init asks three questions, in order. First, the "
            "development environment. Second, greenfield (a new product) or "
            "brownfield (a repo that already has a project). Third, only for "
            "greenfield, the runtime adapter: crewai, claude-agent-sdk, "
            "cursor-sdk, or choose this later. Later leaves CrewAI as the "
            "default until you set AAMAD_TARGET_RUNTIME.\n\n"
            "Skip the prompts with flags:\n\n"
            "  aamad init --ide cursor --mode greenfield --runtime crewai\n"
            "  aamad init --ide cursor --mode brownfield\n\n"
            "Without a TTY you must pass `--ide`. Init writes `project.mode` "
            "into aamad.config.yml. A chosen runtime is stored as "
            "AAMAD_TARGET_RUNTIME. Brownfield init also creates "
            "project-context/0.review/ and leaves an existing README in place "
            "unless you pass `--overwrite`."
        ),
        prompt="When does init ask which runtime adapter to use?",
        choices=(
            Choice(
                "greenfield",
                "On greenfield only. Brownfield skips that question",
                True,
                "Runtime is a Build-target choice for a new product. Brownfield init does not ask.",
            ),
            Choice(
                "always",
                "On every init, greenfield and brownfield",
                False,
                "Brownfield skips the runtime prompt. Set AAMAD_TARGET_RUNTIME later if you need it.",
            ),
            Choice(
                "overwrite",
                "Only when you pass --overwrite",
                False,
                "--overwrite replaces generated files. It does not control the runtime question.",
            ),
        ),
    ),
    Lesson(
        id="two-spines",
        title="Greenfield and brownfield",
        body=(
            "Greenfield starts at Phase 1. Open @product-mgr and run "
            "`*elicit-requirements` (must do / must not / must cost / must prove), "
            "then `*create-prd` and `*create-stories`. Hand off to @system.arch "
            "for the architecture decisions and sad.md. When a UI is in scope, "
            "@ux.designer writes ux.md and you approve it before material "
            "frontend work. Then Build, then Deliver.\n\n"
            "Brownfield starts at Phase 0. @system.arch `*review-codebase` writes "
            "current-state.md, documentation.md, and architecture-backlog.md "
            "under project-context/0.review/. `*create-sad` writes an as-is SAD "
            "plus Proposed Enhancements and an Operator Decision that starts as "
            "pending. You set that decision to approved, approved-with-changes, "
            "or rejected.\n\n"
            "Phase 1 on a brownfield repo is constrained: the PRD and stories "
            "cover the approved enhancements only, and only after the decision "
            "is approved or approved-with-changes. Do not scaffold a replacement "
            "app. Do not overwrite the existing README. Backlog items are "
            "structural, not bug fixes."
        ),
        prompt="When can Phase 1 start on a brownfield repo?",
        choices=(
            Choice(
                "after-decision",
                "After Operator Decision is approved or approved-with-changes",
                True,
                "Rejected stays in Review. Revise the backlog and SAD before any PRD.",
            ),
            Choice(
                "after-init",
                "Immediately after aamad init",
                False,
                "Init only creates the Review folder. Evidence and the Operator Decision come first.",
            ),
            Choice(
                "after-qa",
                "After qa.md exists",
                False,
                "QA is Phase 2. Brownfield Define cannot start before the Operator Decision.",
            ),
        ),
    ),
    Lesson(
        id="artifacts",
        title="Artifacts and quality gates",
        body=(
            "Decisions live in files, not in chat memory. Artifacts end with "
            "Sources, Assumptions, Open Questions, and Audit.\n\n"
            "  project-context/0.review/    brownfield evidence\n"
            "  project-context/1.define/    system description, optional MRD,\n"
            "                               PRD, stories, SAD, ux.md\n"
            "  project-context/2.build/     setup, frontend, backend, integration,\n"
            "                               qa, evals, security, ux-review\n"
            "  project-context/3.deliver/   deploy.md and user-guide.md\n\n"
            "CHECKLIST.md is the step list. AGENTS.md says where personas live "
            "for your IDE. aamad.config.yml holds shared preferences.\n\n"
            "Check a gate when the files exist:\n\n"
            "  aamad validate --phase review\n"
            "  aamad validate --phase define\n"
            "  aamad validate --phase build\n"
            "  aamad validate --phase deliver\n\n"
            "`--phase auto` picks from the files it finds. Validate reports "
            "gaps. It does not fill them in."
        ),
        prompt="Where does the PRD go?",
        choices=(
            Choice(
                "define",
                "project-context/1.define/prd.md",
                True,
                "Define artifacts live under project-context/1.define/.",
            ),
            Choice(
                "build",
                "project-context/2.build/prd.md",
                False,
                "Phase 2 holds implementation notes (setup, frontend, backend, qa), not the PRD.",
            ),
            Choice(
                "readme",
                "The repository README",
                False,
                "The README is not the requirements artifact. Brownfield init leaves it alone.",
            ),
        ),
    ),
    Lesson(
        id="personas",
        title="Personas and commands",
        body=(
            "Open a fresh chat for each module. Invoke the persona, then a "
            "star command. Cursor uses @product-mgr in chat. Claude Code uses "
            "the agent name, or /phase-0-review and /phase-1-define. VS Code "
            "uses the agent dropdown or @name. Kiro uses the agent picker.\n\n"
            "@product-mgr runs `*elicit-requirements`, `*create-prd`, and "
            "`*create-stories`. It does not choose the application pattern.\n\n"
            "@system.arch runs `*review-codebase` on brownfield, and "
            "`*decompose-work`, `*select-pattern`, `*define-controls`, "
            "`*create-sad`, and `*define-eval-criteria`.\n\n"
            "@ux.designer runs `*design-ux`. You approve ux.md before material "
            "frontend work. Brownfield UX is only for an approved enhancement "
            "that adds a surface, flow, or interaction.\n\n"
            "Build is @project.mgr `*setup-project`, @frontend.eng `*develop-fe`, "
            "@backend.eng `*develop-be`, and @integration.eng `*integrate-api`. "
            "@qa.eng runs tests, `*verify-change`, and `*run-evals`. "
            "@security.eng runs `*assess-security`. @devops.eng prepares the "
            "release and writes deploy.md.\n\n"
            "After a code, config, or deploy change, that persona runs "
            "`*sync-docs` and waits for your approval. Sync does not rewrite "
            "the PRD, the SAD, or Review artifacts."
        ),
        prompt="Who records the application pattern?",
        choices=(
            Choice(
                "architect",
                "@system.arch, in the SAD Pattern Decision",
                True,
                "The product manager elicits constraints. The architect records the pattern.",
            ),
            Choice(
                "product",
                "@product-mgr, during elicitation",
                False,
                "Elicitation captures must-do, must-not, must-cost, and must-prove. It does not select a pattern.",
            ),
            Choice(
                "runtime",
                "The runtime adapter chosen at init",
                False,
                "The adapter is the generated app's runtime. The pattern is augmented call, workflow, or agent.",
            ),
        ),
    ),
    Lesson(
        id="five-decisions",
        title="Five decisions before Build",
        body=(
            "Before implementation, sad.md records five decisions. @system.arch "
            "writes them. Build personas implement them.\n\n"
            "1. Work Ownership. Each user-visible step belongs to the model, "
            "an existing system, or a human.\n"
            "2. Pattern Decision. One primary shape: augmented call, workflow, "
            "or agent. There is no fourth option named multi-agent. An "
            "augmented call is a single model call wrapped by your application. "
            "A workflow is a sequence the code decides. An agent is a model "
            "that chooses the next role.\n"
            "3. Reference Architecture. The closest proven shape, and its known "
            "failure. Retrieval is not the source of live state.\n"
            "4. Model and Context Strategy. Start on the balanced default model. "
            "A model or prompt change is a release: an eval gate and a rollback "
            "criterion before the swap.\n"
            "5. Control Register. Input screening, output screening, and "
            "tool-call authorization. Side effects fail closed.\n\n"
            "`*define-eval-criteria` fills the evaluation table (dimension, "
            "metric, threshold, grading method, source) after a PRD exists. "
            "`aamad validate --phase define` expects the five headings."
        ),
        prompt="Code chooses the next step. A model may be one of those steps. Which pattern is that?",
        choices=(
            Choice(
                "workflow",
                "workflow",
                True,
                "A sequence written in code is a workflow, even when a step calls a model.",
            ),
            Choice(
                "agent",
                "agent",
                False,
                "An agent is a model that chooses the next role. Fixed code is not an agent.",
            ),
            Choice(
                "crew",
                "multi-agent, because several personas exist in AAMAD",
                False,
                "The development crew is AAMAD's method. The product pattern has three shapes, and multi-agent is not one of them.",
            ),
        ),
    ),
    Lesson(
        id="build-deliver",
        title="Build, evals, security, deliver",
        body=(
            "After the SAD, and after ux.md is approved when a UI is in scope, "
            "Phase 2 proceeds in order: setup, frontend, backend, integration, "
            "QA, evals when the pattern includes a model call, security, then "
            "Deliver.\n\n"
            "@frontend.eng implements the approved ux.md and writes ux-review.md. "
            "A matching visual snapshot is not proof the design is good.\n\n"
            "@backend.eng implements the recorded pattern for "
            "AAMAD_TARGET_RUNTIME. It does not add an agent loop, live-state "
            "retrieval, or a side-effecting tool the SAD did not allow.\n\n"
            "@qa.eng writes qa.md. When the pattern includes a model call, "
            "`*run-evals` writes evals.md from a golden dataset. @security.eng "
            "checks the Control Register against the code and writes "
            "security.md. That assessment is required under the default config.\n\n"
            "@devops.eng then writes project-context/3.deliver/deploy.md, "
            "including a live control register and an outcome document, plus "
            "CI config and a user guide. Generating that config does not deploy "
            "the app. Operator chat stays short. The artifact is the long form."
        ),
        prompt="What must exist before Deliver under the default config?",
        choices=(
            Choice(
                "gates",
                "qa.md, security.md, and evals.md when the pattern calls a model",
                True,
                "Deliver reads those gates. evals.md is required when the Pattern Decision includes a model call.",
            ),
            Choice(
                "tests-only",
                "A green local test run is enough",
                False,
                "Tests land in qa.md. Deliver also waits on security.md, and on evals.md when a model is in the pattern.",
            ),
            Choice(
                "guide-only",
                "user-guide.md only",
                False,
                "The user guide is written during Deliver. It is not the entry gate.",
            ),
        ),
    ),
    Lesson(
        id="practice",
        title="What you run, and what you don't",
        body=(
            "New product, Cursor, CrewAI:\n\n"
            "  aamad init --ide cursor --mode greenfield --runtime crewai\n\n"
            "In Cursor, open @product-mgr and run `*elicit-requirements`, then "
            "`*create-prd` and `*create-stories`. In a new chat, open "
            "@system.arch and run `*decompose-work`, `*select-pattern`, "
            "`*define-controls`, and `*create-sad`. Then:\n\n"
            "  aamad validate --phase define\n\n"
            "Existing repo:\n\n"
            "  aamad init --ide cursor --mode brownfield\n\n"
            "Open @system.arch, run `*review-codebase`, then `*create-sad`, and "
            "record the Operator Decision before any PRD.\n\n"
            "When a file is missing, `aamad validate` names the gate. When docs "
            "drift after a code change, run `*sync-docs` in a fresh chat. "
            "Replay a lesson with `aamad tutorial --lesson <id>`, or print the "
            "study sheet with `aamad tutorial --print`."
        ),
        prompt="Which shell command writes the PRD?",
        choices=(
            Choice(
                "none",
                "None. @product-mgr writes it in the IDE after init",
                True,
                "The shell installs, validates, and teaches. Personas write the artifacts.",
            ),
            Choice(
                "aamad-prd",
                "aamad prd",
                False,
                "There is no prd subcommand. The command in chat is *create-prd, on @product-mgr.",
            ),
            Choice(
                "validate",
                "aamad validate --phase define",
                False,
                "Validate checks that prd.md and sad.md already exist. It does not author them.",
            ),
        ),
    ),
)


def lesson_by_id(lesson_id: str) -> Lesson:
    for lesson in LESSONS:
        if lesson.id == lesson_id:
            return lesson
    known = ", ".join(lesson.id for lesson in LESSONS)
    raise KeyError(f"Unknown lesson {lesson_id!r}. Known lessons: {known}")


def format_lesson_list() -> str:
    width = max(len(lesson.id) for lesson in LESSONS)
    lines = [f"{lesson.id.ljust(width)}  {lesson.title}" for lesson in LESSONS]
    return "\n".join(lines)


def _is_preserved_line(line: str) -> bool:
    """Keep command indents and numbered decision lines on their own rows."""
    if not line.strip() or line.startswith(" "):
        return True
    head, _, _rest = line.partition(". ")
    return head.isdigit()


def _wrap_paragraph(paragraph: str) -> str:
    lines = paragraph.split("\n")
    if all(_is_preserved_line(line) for line in lines):
        wrapped: list[str] = []
        for line in lines:
            if line.startswith("  ") or len(line) <= WIDTH:
                wrapped.append(line.rstrip())
            else:
                wrapped.append(_fill(line, subsequent_indent="   "))
        return "\n".join(wrapped)
    return _fill(" ".join(line.strip() for line in lines))


def _wrap_body(body: str) -> str:
    return "\n\n".join(_wrap_paragraph(part) for part in body.strip().split("\n\n"))


def format_lesson(lesson: Lesson, *, index: int, total: int) -> str:
    rule = "-" * WIDTH
    answer = lesson.correct()
    check = _fill(lesson.prompt)
    remember = _fill(f"Answer: {answer.label}. {answer.feedback}")
    return "\n".join(
        [
            f"Lesson {index} of {total} — {lesson.title}",
            rule,
            _wrap_body(lesson.body),
            "",
            "Check",
            check,
            remember,
        ]
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_mode(dest: Path) -> str | None:
    path = dest / "aamad.config.yml"
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(_read_text(path))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    mode = project.get("mode")
    if mode in ("greenfield", "brownfield"):
        return mode
    return None


def _is_project(dest: Path) -> bool:
    return (dest / "aamad.config.yml").is_file() or (dest / "project-context").is_dir()


def format_folder_hint(dest: Path) -> str:
    """Return the next crew action for ``dest``, based on which artifacts exist."""
    header = f"Where this folder stands\n{dest.resolve()}"
    if not dest.is_dir() or not _is_project(dest):
        body = (
            "This folder is not an AAMAD project yet. From the project root, "
            "run `aamad init`, then open the persona printed at the end."
        )
        return f"{header}\n\n{_fill(body)}"

    mode = _read_mode(dest)
    if mode is None and (dest / "aamad.config.yml").is_file():
        mode_line = "project.mode is missing or unreadable in aamad.config.yml. Treating the spine as greenfield until you set it."
    elif mode is None:
        mode_line = "No aamad.config.yml. project-context/ is present, so this hint follows the greenfield spine."
        mode = "greenfield"
    else:
        mode_line = f"project.mode is {mode}."

    def missing(relative: str) -> bool:
        return not (dest / relative).is_file()

    if mode == "brownfield" and any(missing(path) for path in REVIEW_ARTIFACTS):
        nxt = (
            "Next: open @system.arch and run *review-codebase, then *create-sad. "
            "Record the Operator Decision on project-context/1.define/sad.md "
            "before any PRD."
        )
    elif missing(PRD_PATH):
        if mode == "brownfield":
            nxt = (
                "Next: open @product-mgr for a constrained PRD and stories, "
                "and only after Operator Decision is approved or "
                "approved-with-changes. Run *create-prd and *create-stories."
            )
        else:
            nxt = (
                "Next: open @product-mgr. Run *elicit-requirements, then "
                "*create-prd and *create-stories."
            )
    elif missing(SAD_PATH):
        nxt = (
            "Next: open @system.arch and run *decompose-work, *select-pattern, "
            "*define-controls, and *create-sad."
        )
    else:
        sad_text = _read_text(dest / SAD_PATH)
        absent = [heading for heading in SAD_DECISION_HEADINGS if heading not in sad_text]
        if absent:
            joined = ", ".join(absent)
            nxt = (
                "Next: sad.md is missing decision headings "
                f"({joined}). Open @system.arch and finish *decompose-work, "
                "*select-pattern, and *define-controls before Build."
            )
        else:
            pending = [relative for relative in BUILD_ARTIFACTS if missing(relative)]
            if pending:
                first = pending[0]
                if first.endswith("setup.md"):
                    nxt = (
                        "Next: when a UI is in scope, open @ux.designer and run "
                        "*design-ux, then approve ux.md. Open @project.mgr and "
                        "run *setup-project."
                    )
                else:
                    nxt = (
                        f"Next: Phase 2 still needs {first}. Follow CHECKLIST.md "
                        "in a fresh chat for that persona."
                    )
            elif missing(SECURITY_MD):
                nxt = (
                    "Next: open @qa.eng and run *run-evals when the pattern "
                    "includes a model call, then open @security.eng and run "
                    "*assess-security."
                )
            elif any(missing(path) for path in DELIVER_ARTIFACTS):
                nxt = (
                    "Next: open @devops.eng and run *prepare-release. Deliver "
                    "reads qa.md, security.md, and evals.md when a model is in "
                    "the pattern."
                )
            else:
                nxt = (
                    "The phase artifacts are present. Run `aamad validate` for "
                    "the phase you are in. After a code change, run *sync-docs "
                    "in a fresh chat."
                )
    return f"{header}\n\n{_fill(mode_line)}\n\n{_fill(nxt)}"


def format_tutorial(dest: Path, lessons: tuple[Lesson, ...] | None = None) -> str:
    selected = lessons if lessons is not None else LESSONS
    total = len(selected)
    parts = [
        "AAMAD tutorial",
        _wrap_body(
            "The crew lives in your IDE. This is the map: what to install, "
            "which persona to open, and which file should exist before you "
            "move on.\n\n"
            "  aamad tutorial --list\n"
            "  aamad tutorial --lesson <id>\n"
            "  aamad tutorial --print"
        ),
        "",
    ]
    for index, lesson in enumerate(selected, start=1):
        parts.append(format_lesson(lesson, index=index, total=total))
        parts.append("")
    parts.append(format_folder_hint(dest))
    return "\n".join(parts).rstrip() + "\n"


class QuestionaryPrompter:
    def choose(self, message: str, options: list[tuple[str, str]]) -> str | None:
        choices = [questionary.Choice(title=label, value=value) for value, label in options]
        return questionary.select(message, choices=choices).ask()


def _choose(prompter: Prompter, message: str, options: list[tuple[str, str]]) -> str:
    selected = prompter.choose(message, options)
    if selected is None:
        raise TutorialCancelled("Tutorial stopped.")
    return selected


def _run_lesson(
    lesson: Lesson,
    *,
    index: int,
    total: int,
    prompter: Prompter,
    out: TextIO,
    last: bool,
) -> None:
    rule = "-" * WIDTH
    print(f"Lesson {index} of {total} — {lesson.title}", file=out)
    print(rule, file=out)
    print(_wrap_body(lesson.body), file=out)
    print(file=out)
    selected = _choose(
        prompter,
        lesson.prompt,
        [(choice.value, choice.label) for choice in lesson.choices],
    )
    chosen = next(choice for choice in lesson.choices if choice.value == selected)
    answer = lesson.correct()
    if chosen.correct:
        print(_fill(chosen.feedback), file=out)
    else:
        print(_fill(f"Not quite. {chosen.feedback}"), file=out)
        print(file=out)
        print(_fill(f"Answer: {answer.label}. {answer.feedback}"), file=out)
    print(file=out)
    if last:
        _choose(prompter, "End of the tutorial.", [("done", "Show where this folder stands")])
        return
    step = _choose(
        prompter,
        "Continue?",
        [("next", "Next lesson"), ("quit", "Stop here")],
    )
    if step == "quit":
        raise TutorialCancelled("Tutorial stopped.")


def _run_interactive(
    dest: Path,
    lessons: tuple[Lesson, ...],
    *,
    prompter: Prompter,
    out: TextIO,
    skip_menu: bool,
) -> int:
    print("AAMAD tutorial", file=out)
    if skip_menu and len(lessons) == 1:
        intro = "One lesson from the crew workflow. The check has one answer."
    else:
        count = len(LESSONS)
        intro = (
            f"{count} short lessons on the crew workflow. The check at the end "
            "of each one has one answer. Stopping early is fine."
        )
    print(_wrap_body(intro), file=out)
    print(file=out)
    selected = lessons
    start = 0
    if not skip_menu:
        options = [("all", "Start from the beginning")]
        options.extend((lesson.id, lesson.title) for lesson in LESSONS)
        options.append(("quit", "Quit"))
        picked = _choose(prompter, "How do you want to start?", options)
        if picked == "quit":
            print("Tutorial stopped.", file=out)
            return 0
        if picked != "all":
            start = next(index for index, lesson in enumerate(LESSONS) if lesson.id == picked)
            selected = LESSONS[start:]
    total = len(LESSONS) if not skip_menu else len(selected)
    try:
        for offset, lesson in enumerate(selected):
            index = start + offset + 1 if not skip_menu else offset + 1
            _run_lesson(
                lesson,
                index=index,
                total=total,
                prompter=prompter,
                out=out,
                last=offset == len(selected) - 1,
            )
            print(file=out)
    except TutorialCancelled as exc:
        print(str(exc), file=out)
        return 0
    print(format_folder_hint(dest), file=out)
    print(file=out)
    return 0


def run_tutorial(
    dest: Path,
    *,
    lesson_id: str | None = None,
    list_only: bool = False,
    interactive: bool = False,
    prompter: Prompter | None = None,
    out: TextIO | None = None,
) -> int:
    """Print or walk the tutorial. Returns a process exit code."""
    stream = sys.stdout if out is None else out
    if list_only:
        print(format_lesson_list(), file=stream)
        return 0
    try:
        selected = (lesson_by_id(lesson_id),) if lesson_id else LESSONS
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if interactive:
        walker = prompter if prompter is not None else QuestionaryPrompter()
        return _run_interactive(
            dest,
            selected,
            prompter=walker,
            out=stream,
            skip_menu=lesson_id is not None,
        )
    print(format_tutorial(dest, selected), file=stream, end="")
    return 0
