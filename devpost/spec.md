---
doc: spec
status: approved
---

# BuildTrace — Technical Spec

## How This Works, In Plain Language

BuildTrace is a local desktop window. The left panel holds the task-manager request; clicking **Build & Verify Project** asks one OpenAI model to return the three project files as JSON. If that call cannot be used, BuildTrace uses a checked-in copy of the same three files instead, so the demo stays runnable. The app validates the response, writes each file into its own output folder, displays its contents, and runs the generated task manager while showing its output in the lower-right terminal.

The output project owns its own SQLite database; BuildTrace itself only holds temporary interface information, such as the current step, selected file, build messages, and process output. Keeping the host app, generated code, and generated database in separate places makes it easy to show what the agent created and avoids accidentally overwriting BuildTrace source files.

This implements `prd.md > The Core Journey`, `Features and Behavior > Transparent project generation`, and `Features and Behavior > Local execution and proof`.

## The Core Journey Through the System

PRD ref: `prd.md > The Core Journey`.

1. The local CustomTkinter app starts, reads the fixed demo preset, checks the process environment and a root `.env` file for `OPENAI_API_KEY`, and updates the header badge.
2. The user edits or accepts the prompt and selects **Build & Verify Project**.
3. The build controller resets the UI, begins the progress sequence, and asks the generation service for a JSON object containing `database.py`, `main.py`, and `README.md`.
4. If the user started a live build and its response is unavailable within 10 seconds or returns an authentication, quota, or network failure, the controller loads `templates/task_manager_fallback.json` instead and records that fallback was used in the progress log. If no key was found at startup, the disabled primary button is paired with a separate **Use Offline Template** action that starts this same fallback path deliberately.
5. The response validator requires exactly the three expected non-empty text files before the file writer creates `output/buildtrace_app/` and writes them there.
6. Each successful write updates its progress entry and inserts the file into the tabbed inspector.
7. After the disk-write check, the terminal runner executes `python main.py init` with `output/buildtrace_app/` as its working directory. Its output is streamed safely to the terminal widget.
8. The user enters task-manager commands in the terminal command field. Each allowed command is run as a separate subprocess in the same output directory, and its output is appended to the terminal pane.
9. A successful add and list command proves that the generated application has persisted a task to its SQLite database.

## Stack

- **Python 3.11+** — single-language local host and generated CLI runtime. Version should be verified on the target demo machine at build start.
- **CustomTkinter** — learner-selected desktop GUI framework; provides the dark, modern panel layout without a web server or port conflicts. [CustomTkinter documentation](https://customtkinter.tomschimansky.com/).
- **Python standard library** (`subprocess`, `threading`, `queue`, `json`, `pathlib`, `shlex`, `sqlite3`) — supplies process execution, background work, validation, file writing, safe command parsing, and the generated app's persistence without extra services.
- **OpenAI Python SDK** — calls the learner-selected OpenAI Chat Completions API using `gpt-4o-mini` for the PoC. `gpt-4o` is a later manual upgrade option, not automatic fallback. [Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat/create) and [OpenAI model documentation](https://platform.openai.com/docs/models).
- **`python-dotenv`** — optional local-development loading of `OPENAI_API_KEY` from an ignored environment file; the application must never display the key.

`gpt-4o-mini` is selected because this is a fixed, small generation task. The model name and access must be verified early in the build against the connected OpenAI project. The API request uses the learner-selected `response_format={"type": "json_object"}`. JSON mode guarantees parseable JSON, not the exact expected keys, so `GenerationService` must enforce the required filenames and reject malformed or incomplete content before any disk write. Official OpenAI documentation describes JSON object mode as valid JSON output and recommends structured JSON schemas where supported; the PoC deliberately retains the learner's JSON-object choice while adding local validation. [OpenAI API reference](https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal?lang=python).

## Where It Runs and How Someone Tries It

BuildTrace runs locally on a desktop with Python 3.11+; it is recorded locally for the required demo video. No website, web server, or deployment is part of this PoC.

1. Install the dependencies from `requirements.txt`.
2. Set `OPENAI_API_KEY` in a local ignored environment file or environment variable if live generation is desired. Without it, the fallback project is used for a reliable demo.
3. Start the host app with `python app.py` from the repository root.
4. In BuildTrace, keep the SQLite task-manager preset selected, then choose **Build & Verify Project**.
5. Confirm the three visible generated files and the successful `init` output.
6. Enter `python main.py add "Submit Devpost Video"`, then `python main.py list`, and record the resulting terminal output.

The submission still requires a short demo video and public GitHub repository; local recording is sufficient for the proof. Deployment is intentionally not planned.

## Look and Feel

Implements `prd.md > Look and Feel` and `Screens and Layout`.

- Apply `#111216` as the app background and `#181A20` to cards/panels; divide the three work areas with one-pixel `#2D313E` borders and six-pixel rounded corners.
- Use `#6366F1` for the main build action and active selections, `#F59E0B` for an active generation step, `#10B981` for verified steps, and red for failed/unreachable states.
- Use the platform system sans-serif for general interface copy and a configured monospaced font (prefer JetBrains Mono or Fira Code when installed) for file content and terminal text.
- Style the `CTkTextbox` terminal with `#0B0C0E`, high-contrast text, and red traceback tags. Apply a small scheduled pulse to the active progress row only while a build is running.

CustomTkinter can reproduce the palette, spacing, panel hierarchy, and status treatments; a full CSS-like animation system is not required for the PoC.

## Components

### AppShell

Owns the CustomTkinter root window, three-panel layout, shared theme, and safe handoff of background-thread updates to the UI thread.

PRD ref: `prd.md > Screens and Layout` and `Look and Feel`.

### HeaderStatus

Displays the BuildTrace name and LLM readiness badge. It checks the process environment first and then a root `.env` file through `python-dotenv`; a non-empty key enables the live-build action and shows **LLM Ready** in green. With no key, it shows **LLM Unreachable** in amber/red, disables the primary action, and exposes the offline-template option. A key only permits a live request attempt; a timeout, authentication, quota, or connection failure changes the status to unreachable.

PRD ref: `prd.md > Features and Behavior > Build request and readiness`.

### BuildInputPanel

Shows the fixed `Demo: SQLite Python Task Manager` preset, editable prompt field, status banner, and primary action. In the unavailable state, it disables and relabels the primary action **Fix Settings to Build**, then offers a distinct **Use Offline Template** action. It starts a live build in the ready state and exposes **Retry Build** after a write failure.

PRD ref: `prd.md > Features and Behavior > Build request and readiness`.

### BuildController

Coordinates one build at a time: clears prior output, emits ordered status events, calls `GenerationService`, validates payloads, invokes `ProjectWriter`, and then starts `TerminalRunner`. It maps errors into the product states rather than letting a background exception terminate the GUI.

PRD ref: `prd.md > Features and Behavior > Transparent project generation` and `States and Boundaries`.

### ProgressTracker

Renders five ordered steps: generate `database.py`, generate `main.py`, generate `README.md`, disk-write check, and auto-execution. Steps may be pending, active (amber), verified (green), or failed (red). The tracker records fallback use in its visible log while still showing the actual generated files and execution result.

PRD ref: `prd.md > Features and Behavior > Transparent project generation`.

### GenerationService

Builds a narrowly scoped OpenAI Chat Completions request that instructs the model to return JSON with `database.py`, `main.py`, and `README.md` only. It sends the user-visible demo prompt alongside a system instruction that fixes the JSON shape and requires a SQLite CLI task manager with add, list, complete, and init commands. It enforces a 10-second request timeout and routes missing key, timeout, connection, quota, authentication, and malformed responses to `FallbackProvider`.

PRD ref: `prd.md > Features and Behavior > Transparent project generation`.

### FallbackProvider

Reads the checked-in `templates/task_manager_fallback.json` and returns the same three-file JSON shape as the live generator. It is a transparent resilience feature, not simulated verification: the fallback files are still written locally and actually executed.

PRD ref: `prd.md > Features and Behavior > Transparent project generation` and `Local execution and proof`.

### PayloadValidator and ProjectWriter

`PayloadValidator` accepts only the expected filenames, rejects absolute or traversal paths, requires string contents, and reports the offending field without writing partial output. `ProjectWriter` creates and writes only within `output/buildtrace_app/`, overwriting prior generated artifacts for this fixed demo after validation succeeds. It returns the written paths for the inspector and disk-write progress step.

PRD ref: `prd.md > Features and Behavior > Transparent project generation`.

### FileInspector

Maintains tabs for `main.py`, `database.py`, and `README.md`; each tab shows the content read from the exact file written to the output directory. On a generated-code execution failure, it selects the named affected file when available.

PRD ref: `prd.md > Features and Behavior > Transparent project generation` and `Local execution and proof`.

### TerminalRunner

Uses `subprocess.Popen` with `output/buildtrace_app/` as the working directory. Reader threads place stdout and stderr lines into a queue; the CustomTkinter main loop periodically drains that queue into the dark `CTkTextbox`, so the UI never blocks. The initial command is `python main.py init`. A separate one-line command field parses and permits only the demo's `python main.py init`, `add`, `list`, and `complete` invocations, then launches each command with the current Python interpreter rather than passing arbitrary text to a shell.

PRD ref: `prd.md > Features and Behavior > Local execution and proof`.

### Generated Task Manager

The generated `database.py` owns schema initialization and task storage. The generated `main.py` exposes `init`, `add`, `list`, and `complete` commands and prints observable CLI results. The generated `README.md` documents those commands. This generated app is not part of BuildTrace's host implementation, but it is the artifact the demo must prove is real and runnable.

PRD ref: `prd.md > What We're Building` and `Features and Behavior > Local execution and proof`.

## Data Model

### Host interface data

The host app keeps the selected preset, editable prompt, step statuses, currently selected file, build log, and terminal output in memory only. Closing BuildTrace clears this interface data; the next run returns to the fixed demo preset.

### Generated project files

The validated model or fallback payload originates from the generation service and is persisted as `output/buildtrace_app/main.py`, `database.py`, and `README.md`. A later build replaces those three files only after a complete payload validates successfully. The inspector always reads from these written files.

### Generated task data

The generated task manager creates `output/buildtrace_app/tasks.db`. Its single `tasks` table stores `id`, `title`, `completed`, and `created_at`; `add` inserts a task, `list` reads it, and `complete` updates it. It persists between task-manager commands and between BuildTrace restarts until the user starts a fresh generated build or deletes the output folder.

## File Structure

```
appforge-agent/
├── app.py                              # CustomTkinter application entry point
├── requirements.txt                    # Host-app dependencies
├── README.md                           # Host setup and demo instructions
├── src/
│   ├── __init__.py
│   ├── app_shell.py                    # Window layout, UI event scheduling
│   ├── theme.py                        # Colors, fonts, and shared UI styling
│   ├── build_controller.py             # Orchestrates the build-to-run sequence
│   ├── generation_service.py           # OpenAI Chat Completions request and timeout handling
│   ├── fallback_provider.py            # Loads deterministic fallback payload
│   ├── payload_validator.py            # Validates safe expected file payloads
│   ├── project_writer.py               # Writes validated files inside output root
│   ├── terminal_runner.py              # Popen execution and streamed-output queue
│   └── ui/
│       ├── header_status.py             # Brand and API readiness badge
│       ├── build_input_panel.py         # Preset, prompt, action, and banners
│       ├── progress_tracker.py          # Ordered visual build steps
│       ├── file_inspector.py            # Generated-file tabs
│       └── terminal_panel.py            # CTkTextbox and command entry
├── templates/
│   └── task_manager_fallback.json       # Validated three-file local fallback
├── output/
│   └── buildtrace_app/                  # Runtime-generated project; ignored by Git
│       ├── main.py
│       ├── database.py
│       ├── README.md
│       └── tasks.db
├── tests/
│   ├── test_payload_validator.py
│   ├── test_project_writer.py
│   ├── test_fallback_provider.py
│   ├── test_generated_task_manager.py
│   └── test_build_controller.py
└── devpost/                             # Approved planning documents
```

## External Services and Dependencies

### OpenAI Chat Completions API

- **Endpoint:** `POST https://api.openai.com/v1/chat/completions`.
- **Authentication:** `Authorization: Bearer $OPENAI_API_KEY`; the key stays in a local ignored environment source or process environment and is never shown in the GUI, logs, repository, or generated files.
- **Request shape:** `model: "gpt-4o-mini"`, a system message defining the three-file response contract, the user demo prompt, and `response_format: {"type": "json_object"}`.
- **Expected response:** an assistant content string that parses to an object with string values for `database.py`, `main.py`, and `README.md`; local validation is the final authority.
- **Timeout and fallback:** stop waiting after 10 seconds and load the local fallback for unavailable key, timeout, network, authentication, or quota failures.
- **Documentation:** [Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create), [API error codes](https://platform.openai.com/docs/guides/error-codes), and [API data controls](https://platform.openai.com/docs/guides/your-data).
- **Cost and limits:** model availability, pricing, and rate limits depend on the selected OpenAI project and must be checked in the Platform dashboard before relying on live generation. The fallback means those constraints do not prevent the demo.

### Local SQLite

SQLite is bundled with standard Python for this use. It has no API key, network endpoint, or hosted-service cost. The generated task manager opens only its local `tasks.db` inside the generated output directory.

## Important Failure Modes

- **No usable API key** → Header changes to **LLM Unreachable**, the primary build action becomes **Fix Settings to Build**, and an inline banner identifies the missing-key issue while offering **Use Offline Template**. Selecting that option runs the validated local fallback.
- **Live API failure after a build begins** → The controller records the timeout, connection, authentication, or quota problem and continues using the validated local fallback so an in-progress demo can finish.
- **Generation payload is malformed or unsafe** → No generated file is written; the progress log identifies validation failure and offers retry. Fallback is used for a malformed live response when its local payload validates.
- **Disk write or permission failure** → The disk-write step turns red, the target-path error appears in the inline log, and the primary action becomes **Retry Build**.
- **Generated script fails** → The first four steps remain green, auto-execution turns red, the terminal displays the captured traceback in red, and **Regenerate & Repair** is offered while the inspector selects the affected generated file where identifiable.
- **Terminal command is not part of the demo CLI** → The runner does not invoke a shell; it shows a concise local message limiting input to `init`, `add`, `list`, and `complete` task-manager commands.

## What Was Simplified and Why

- **One `gpt-4o-mini` request plus local fallback** instead of multi-model routing — it demonstrates transparent generation while keeping cost, latency, and configuration small. Multi-model switching would add provider selection and more failure paths without strengthening the demo.
- **A controlled terminal command field** instead of a full unrestricted shell emulator — it proves the generated CLI works while avoiding arbitrary-shell execution in the desktop app.
- **One fixed task-manager contract** instead of arbitrary project generation — it keeps validation, files, and the demo outcome predictable while still proving the visible build-and-verify kernel.
- **Local execution and recording** instead of deployment — it avoids hosting and port management while meeting the video-and-repository submission requirements.

## Decisions and Open Issues

- **Learner decision: CustomTkinter host app** — chosen for a modern dark local GUI with no web-server or port-conflict overhead; the accepted tradeoff is desktop-only distribution for this PoC.
- **Learner decision: `output/buildtrace_app/` output root** — keeps generated application files separate from host source; previous demo output is replaced only after full validation.
- **Learner decision: OpenAI Chat Completions with `gpt-4o-mini` and JSON object mode** — uses one primary provider and parseable JSON; the accepted tradeoff is that a local validator must enforce the three-file contract. `gpt-4o` remains a manual later upgrade, not an automatic runtime switch.
- **Learner decision: deterministic local fallback** — protects the demo from absent credentials, timeout, quota, or network failure while preserving actual local file writing and execution.
- **Learner decision: asynchronous `subprocess.Popen` terminal runner** — preserves a responsive GUI while showing line-by-line command output; the accepted safety boundary is a command allowlist rather than a general shell.
- **Useful clarification: JSON object mode versus file-contract correctness** — JSON mode produces valid JSON but does not alone ensure the expected filenames and content. The blueprint resolves this by validating exact safe filenames and non-empty string content before every write; this will be covered by `tests/test_payload_validator.py`.
- **Open issue to verify at build start:** Confirm that the selected OpenAI project has access to `gpt-4o-mini` and that the local Python environment meets the chosen dependency versions. This does not block the fallback-backed demo but determines whether live generation is enabled.
