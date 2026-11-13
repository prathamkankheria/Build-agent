# Build Agent

A CLI coding agent that can list, read, edit and write files, and run Python
programs in a selected project directory.

Set `OPENROUTER_API_KEY` in your environment or a `.env` file, then run:

```sh
uv run main.py "Explain this project"
uv run main.py --working-directory ./calculator --verbose "Fix the bug in main.py"
```

The working directory defaults to `./calculator`. Use `--working-directory` to
choose another existing project. `--verbose` shows tool arguments and results.
The agent can replace an exact, uniquely matching piece of text in a file, or
write an entire file when needed.

**Use only with trusted projects and prompts.** The agent can overwrite files
and execute Python without asking for confirmation. Python programs have the
same permissions and environment as the user running the agent: the working
directory checks are not a sandbox and do not restrict what a program can do.
Tool results, including file contents, are sent to OpenRouter and its model
providers. Avoid using the agent with secrets or sensitive files. Review
changes before relying on them.