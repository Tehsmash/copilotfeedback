# Copilot Feedback

A Terminal UI (TUI) tool for reviewing git diffs and providing structured feedback to coding agents.

## Overview

Instead of manually reviewing `git diff` output and copy-pasting feedback into a chat window, this tool provides a GitHub PR-style review interface directly in your terminal. Navigate through changes, add comments on specific lines, and export structured feedback that coding agents can consume.

## Features

- 📝 Review `git diff HEAD` changes in a unified diff view
- 💬 Add, edit, and delete comments on specific lines
- ⌨️  Keyboard-driven navigation (arrow keys, Page Up/Down)
- 📤 Export feedback as JSON for coding agent consumption
- 🎨 Syntax-highlighted diff view (additions, deletions, context)

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Usage

```bash
# Run in a git repository with uncommitted changes
copilotfeedback
```

### Keyboard Controls

- **↑/↓ Arrow Keys**: Navigate through diff lines
- **Page Up/Down**: Quick navigation through large diffs
- **c**: Create new comment on current line
- **e**: Edit existing comment on current line
- **d**: Delete comment on current line
- **Esc**: Cancel comment editing
- **q**: Quit and save feedback to `feedback.json`

## Output Format

The tool generates a `feedback.json` file with the following structure:

```json
{
  "timestamp": "2025-12-19T10:48:00Z",
  "diff_command": "git diff HEAD",
  "comments": [
    {
      "file": "src/example.py",
      "line": 13,
      "hunk": "@@ -10,5 +10,7 @@",
      "content": "Consider adding error handling here",
      "context": "    return result"
    }
  ]
}
```

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run linter
uv run ruff check src/

# Run type checker
uv run mypy src/

# Format code
uv run ruff format src/
```

## Tech Stack

- **Python 3.13+**
- **Textual**: Terminal UI framework
- **Ruff**: Linter and formatter
- **Mypy**: Type checker
- **uv**: Package manager

## License

MIT
