---
doc: prd
status: approved
---

# BuildTrace — Product Requirements

BuildTrace is a local developer-console GUI for vibe coders and developers who want to visibly generate, inspect, and verify one small Python project from a request.

Source: `scope.md > The Unique Kernel`, `Who It's For`, and `The POC Boundary`.

## The Core Journey

Source: `scope.md > The Core Loop` and `What "Working" Looks Like`.

1. The user opens BuildTrace and sees a ready-to-build developer console with the fixed SQLite Python Task Manager demo selected.
2. They review or edit the visible demo prompt, then select **Build & Verify Project**.
3. BuildTrace visibly advances through generation of `database.py`, `main.py`, and `README.md`, then confirms that all files were written to the local working directory.
4. As each file becomes available, it appears in the code inspector for the user to examine.
5. When file writing succeeds, BuildTrace automatically initializes the generated task manager in the embedded terminal.
6. The user runs an add command for “Submit Devpost Video,” sees task ID 1 created, then runs the list command and sees the saved task in a formatted terminal table.
7. The completed green progress tracker, visible files, and working terminal output prove that BuildTrace created a real, runnable local project.

## Screens and Layout

Source: `scope.md > The POC Boundary`.

BuildTrace is one three-panel dashboard intended to make the whole proof visible at once.

- **Header bar** — displays the BuildTrace brand and the current LLM readiness status.
- **Left input-control panel** — contains the `Demo: SQLite Python Task Manager` preset, an editable prompt box, and the primary **Build & Verify Project** action.
- **Upper-right progress and code-inspector panel** — shows the step tracker and a tabbed file viewer for `main.py`, `database.py`, and `README.md` as they are written.
- **Lower-right embedded terminal panel** — shows automatic initialization and lets the user enter task-manager commands for the demo.

## Look and Feel

BuildTrace should feel like a focused, high-contrast modern developer console: transparent and technical, without a “magic AI” presentation.

- Slate-dark background `#111216` with `#181A20` card surfaces and `#2D313E` crisp one-pixel panel borders.
- Electric indigo `#6366F1` for primary actions and active highlights.
- Emerald `#10B981` for verified work, amber `#F59E0B` for active work, and red/amber for failures and unavailable readiness.
- Dark obsidian `#0B0C0E` terminal container.
- System sans-serif for interface text; a monospace face for code and terminal output.
- Six-pixel card corners and subtle pulse animation while generation is active.

## Features and Behavior

### Build request and readiness

Source: `scope.md > The Core Loop`.

- The input panel starts with the SQLite Python Task Manager demo preset and its target prompt.
- The prompt is editable before a build begins.
- A green header badge communicates that the LLM is ready.
- When no usable LLM key is detected, the badge shows **LLM Unreachable** in red or amber, the primary build action is disabled and relabeled **Fix Settings to Build**, and an inline banner explains the connection or key status. The banner also offers a distinct **Use Offline Template** action so the user can deliberately run the local fallback demo without live generation.

### Transparent project generation

Source: `scope.md > The Unique Kernel` and `What "Working" Looks Like`.

- Selecting **Build & Verify Project** starts a visible, ordered build sequence:
  1. Generate `database.py` for the SQLite schema setup.
  2. Generate `main.py` for task add, list, and complete behavior.
  3. Generate `README.md` with usage instructions.
  4. Confirm the generated files were saved to the working directory.
  5. Automatically execute the generated app for verification.
- The active step uses amber styling; successfully completed steps use green styling.
- The file inspector exposes each generated file in its own tab as it is written, so the user can inspect the real output rather than only reading progress messages.
- If disk writing fails, the affected step stops in red, an inline error identifies the target-path failure, and the primary action becomes **Retry Build**.

### Local execution and proof

Source: `scope.md > What "Working" Looks Like`.

- Following successful file generation, the terminal automatically runs `python main.py init`.
- The user can then enter `python main.py add "Submit Devpost Video"` and sees confirmation that task ID 1 was created.
- The user can enter `python main.py list` and sees a formatted table containing the stored task.
- If automatic execution fails, the completed generation and disk-write steps remain green while **Auto-Execution** is marked red. The terminal displays the raw Python traceback in red, **Regenerate & Repair** becomes available, and the code inspector focuses the affected file.

## States and Boundaries

- **First ready state** — The task-manager preset and editable prompt are present; the LLM readiness badge is green and the build action is enabled.
- **Building state** — The current generation step is amber, earlier verified steps are green, and the code viewer progressively receives files.
- **Verified state** — All build steps are green; the terminal shows initialization plus the demonstrated task creation and list result.
- **LLM unavailable state** — The header badge, disabled primary action, and inline explanation make it clear that live generation cannot start until readiness is restored; a separate **Use Offline Template** action offers the local fallback demo.
- **Disk-write failure state** — Generation stops at the failed write, the target-path issue is visible, and retrying is the offered recovery action.
- **Execution failure state** — The terminal shows the raw failure, the failed auto-execution step is visibly distinct from successful generation, and repair focuses on the relevant file.

## Product Decisions

- BuildTrace is a single-window, three-panel GUI — this lets a one-minute demo show input, transparent work, generated output, and verification together.
- The PoC uses the preset SQLite Python Task Manager scenario — one real, testable path keeps the proof focused.
- Generated files must be real local files and must be run locally — visible proof matters more than a simulated agent workflow.
- The terminal automatically initializes the app, then the user demonstrates adding and listing a task — this makes persistence observable in the demo.
- The product uses a modern dark developer-console identity — the UI should communicate technical transparency and keep code, progress, and terminal output legible.

## What We're Building

- One BuildTrace dashboard with the defined header, input panel, progress/file-inspection panel, and embedded terminal.
- An editable task-manager demo prompt and a build action.
- A visibly ordered generation and local-write experience for `database.py`, `main.py`, and `README.md`.
- A tabbed file inspector for those generated files.
- Automatic initialization plus user-entered add and list task-manager verification commands.
- The LLM-unavailable, disk-write-failure, and execution-failure states described above.

## Deferred From the POC

- Other project prompts, Python tools, and desktop scripts — this proof demonstrates only one fixed task-manager outcome.
- PHP, HTML/CSS/JavaScript web applications and web servers — they do not strengthen this focused Python demonstration.
- PostgreSQL and MySQL — SQLite is sufficient to prove persistence without setup overhead.
- Streaming graphical desktop windows — the PoC verifies a CLI workflow in the embedded terminal.
- Model-provider switching — one primary LLM keeps the build flow simple and testable.
- Long-running cloud work — the product proves immediate local generation and verification.

## Possible Later Enhancements

- Add prompt-driven Python project templates, including automation and desktop-tool projects.
- Add web-application generation, other database engines, and broader project customization.
- Add downloadable project archives, richer file editing, and selectable LLM providers.

## Non-Goals

- This is not a general-purpose autonomous application builder; it proves one transparent, working project-generation loop.
- This is not a browser or web-server development environment; its scope is local Python CLI generation and verification.
- This does not hide failed work behind a generic completion message; failures must stay visible and distinguishable from successful steps.

## Open Questions

- None that block the proof-of-concept product definition.
