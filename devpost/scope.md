---
doc: scope
status: approved
---

# BuildTrace

A local GUI that transparently creates and verifies a small Python application from a plain-language request.

## The Unique Kernel

Instead of presenting code generation as a black box, BuildTrace makes the agent's work visible: the user sees a live, understandable build sequence, the files it creates, and the result running—all in one place.

## Who It's For

Vibe coders and early-career developers who want to turn an app request into a working starting point, while experienced developers can use it to inspect an agent's process rather than blindly accepting generated code. For this proof, the user needs a reliable way to see whether a requested Python project was really created and works.

## The Core Loop

The user enters a request for a Python CLI task manager with SQLite support. The app shows each generation step as it happens, writes the generated files to local disk, lets the user inspect them, then runs the project in an embedded terminal so the user can add and list tasks.

## Inspiration & Identity

The experience should feel like a transparent build console: clear, practical, and confidence-building rather than magical or opaque. The GUI foregrounds current work, completed steps, and verifiable output.

## Why This Matters to the Learner

This is a focused way to practice guiding an AI coding agent from a clear specification while retaining control of project structure, testing, and quality.

## What "Working" Looks Like

In a one-minute demo, a user asks for: "Build a Python CLI Task Manager app with SQLite support that can add, list, and complete tasks." BuildTrace visibly completes its progress log, creates `main.py`, `database.py`, and `README.md` on local disk, displays them in a file tree/viewer, and runs `main.py` in its embedded terminal. The terminal demonstrates adding and listing tasks against SQLite.

## The POC Boundary

- One fixed, end-to-end Python CLI task-manager scenario with SQLite.
- A local GUI with a live progress stream, generated-file inspection, and an embedded terminal runner.
- Generation of three real local files: `main.py`, `database.py`, and `README.md`.
- Actual local execution and verification of the generated application.
- One primary LLM API for the proof of concept.

## Later

- Prompt-driven support for other Python CLI, automation, and desktop-tool projects.
- Configurable generation for web applications using Python, PHP, HTML, CSS, and JavaScript.
- More database engines, project types, and model providers.
- Downloadable project archives and richer code editing features.

## Explicitly Cut

- PHP, HTML/CSS/JavaScript web applications and web-server generation, because the demo only needs one verified Python path.
- PostgreSQL and MySQL, because SQLite proves persistence without adding setup and configuration work.
- Live streaming of graphical Tkinter windows over VNC, because the PoC only needs to execute a CLI app.
- External multi-model API switching, because a single primary LLM keeps the proof focused and testable.
- Long-running cloud daemons, because generation and local verification are the entire demonstrated loop.
