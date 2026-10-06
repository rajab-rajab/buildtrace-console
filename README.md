# BuildTrace

BuildTrace is a local CustomTkinter developer console that makes one AI-assisted build visible: it generates a SQLite-backed Python CLI task manager, writes the files to disk, lets you inspect them, and runs the result in an embedded terminal.

## License

This project is available under the [MIT License](LICENSE).

## Run locally

Use Python 3.11 or newer. From the repository root:

```powershell
& 'C:\Users\RAJAB BAIG\AppData\Local\Programs\Python\Python311\python.exe' -m pip install -r requirements.txt
& 'C:\Users\RAJAB BAIG\AppData\Local\Programs\Python\Python311\python.exe' app.py
```

The interface has two safe paths:

- **Build & Verify Project** uses `OPENAI_API_KEY` when it is available through the process environment or a local ignored `.env` file.
- **Use Offline Template** writes the same three-file task-manager project locally without a network call, so the demo remains reliable.

Never commit a key. `.env` and `.env.*` are ignored by this repository.

## One-minute demo

1. Launch BuildTrace and select **Use Offline Template** (or **Build & Verify Project** when the green LLM badge is ready).
2. Watch the five progress steps complete and inspect `main.py`, `database.py`, and `README.md` in the file tabs.
3. Wait for the terminal to initialize the generated SQLite database.
4. Run these commands in the terminal command bar:

   ```text
   python main.py add "Submit Devpost Video"
   python main.py list
   ```

5. The formatted task row proves the generated project wrote and read local SQLite data.

Generated project files stay isolated in `output/buildtrace_app/` and are not tracked by Git.

## Verify

```powershell
& 'C:\Users\RAJAB BAIG\AppData\Local\Programs\Python\Python311\python.exe' -W error::ResourceWarning -m unittest discover -s tests -v
```
