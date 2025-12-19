# Git Diff Review CLI Tool - Design Document

## Overview
A CLI tool that facilitates reviewing git diffs and leaving line-specific comments to provide structured feedback to coding agents.

## Core Concept
Enable developers to:
1. View git diffs in an interactive manner
2. Comment on specific lines or changes
3. Export feedback in a structured format that coding agents can consume

## Use Cases
- Reviewing changes made by AI coding assistants
- Providing detailed feedback on specific code modifications
- Creating a feedback loop between human reviewers and coding agents
- Documenting review comments for later reference

## Key Features (To Define)

### 1. Diff Viewing
- [ ] Display git diff in an readable format
- [ ] Support different diff views (unified, split, etc.)
- [ ] Highlight additions/deletions/modifications
- [ ] Navigate between files and hunks

### 2. Comment System
- [ ] Add comments to specific lines
- [ ] Support different comment types (suggestion, question, issue, approval)
- [ ] Allow multi-line comments
- [ ] Reference line numbers or line ranges

### 3. Output Format
- [ ] JSON format for programmatic consumption
- [ ] Human-readable format for documentation
- [ ] Integration with existing tools (GitHub comments, etc.)

## Technical Considerations

### Input
- Git diff output (staged changes, commits, branches)
- Working directory changes
- Comparison between commits/branches

### Storage
- Temporary storage during review session
- Persistent storage for feedback history
- Format: JSON, YAML, or custom format?

### User Interface
- Interactive TUI (Terminal UI) vs command-based
- Vim-like navigation?
- Mouse support?

## Design Decisions

### 1. Git Diff Scope
**Decision:** Review working directory changes before committing (`git diff HEAD`)
- Focuses on pre-commit review workflow
- Reviews changes that haven't been committed yet
- Simple, single-purpose scope

### 2. Comment Structure
**Decision:** Comments linked to specific lines + diff hunks with plain text content
- Each comment references:
  - File path
  - Line number (in the diff context)
  - Diff hunk information
  - Plain text comment content
- No special formatting, just text feedback

### 3. Tool Integration
**Decision:** No integration with existing code review tools
- Standalone tool for local review workflow
- Replaces manual `git diff` → copy feedback → paste into chat
- Provides structured PR-style review locally

### 4. Interactivity Level
**Decision:** Full TUI with GitHub-style unified diff view
- Visual diff display (unified format)
- Inline comment entry and display
- Keyboard-driven navigation and actions

### 5. Feedback Persistence
**Decision:** No versioning/tracking - session-based only
- Operates on diff at command start time
- Outputs single feedback file at end of session
- Simple, stateless operation

### 6. Large Diff Handling
**Decision:** Same handling as small diffs with page navigation
- Scrollable view with arrow key navigation
- Page up/down for quick movement
- No special treatment needed

## User Experience Design

### TUI Layout
```
┌─ File: src/example.js ────────────────────────────────────┐
│ @@ -10,5 +10,7 @@                                         │
│   function example() {                                     │
│ -   console.log("old");                                    │
│ +   console.log("new");                                    │
│ +   return true;                                           │
│     → [Comment] Consider adding error handling here       │
│   }                                                         │
└────────────────────────────────────────────────────────────┘
```

### Navigation & Controls
- **Arrow Keys (↑/↓):** Navigate through diff lines
- **Page Up/Down:** Quick navigation through large diffs
- **c:** Create new comment on current line
- **e:** Edit existing comment on current line
- **d:** Delete comment on current line
- **Esc:** Exit comment editing, return to navigation
- **q:** Quit and save feedback
- Current line is highlighted

### Comment Display
- Comments displayed inline with diff
- Indented to distinguish from code
- Prefixed with marker (e.g., "→ [Comment]")
- Multi-line comments supported in edit mode

### Workflow
1. Run command: `copilotfeedback` (or similar)
2. Tool captures `git diff HEAD`
3. TUI opens with unified diff view
4. User navigates and adds comments
5. User quits (q)
6. Tool outputs feedback file

## Output Format

### Feedback File Structure (JSON)
```json
{
  "timestamp": "2025-12-19T10:40:16.776Z",
  "diff_command": "git diff HEAD",
  "comments": [
    {
      "file": "src/example.js",
      "line": 13,
      "hunk": "@@ -10,5 +10,7 @@",
      "content": "Consider adding error handling here",
      "context": "+   return true;"
    }
  ]
}
```

## Similar Tools & Inspiration
- `git add -p` (interactive staging)
- GitHub PR review interface (unified view)
- Code review tools (Gerrit, ReviewBoard)
- `tig` (text-mode interface for git)

## Implementation Considerations

### Technology Stack
- Language: Go, Python, or Rust (TUI library availability)
- TUI Libraries:
  - Go: bubbletea, tview
  - Python: textual, urwid
  - Rust: ratatui
- Git integration: execute `git diff HEAD` and parse output

### Core Components
1. **Diff Parser:** Parse git diff output into structured data
2. **TUI Engine:** Render diff and handle user input
3. **Comment Manager:** Store and manage comments during session
4. **Output Generator:** Export comments to JSON file

## Next Steps
1. ✅ Define user experience and workflow
2. ✅ Choose output format (JSON)
3. ✅ Choose implementation language and TUI library (Python + Textual)
4. ✅ Build diff parser
5. ✅ Create basic TUI prototype
6. ✅ Implement comment management
7. ✅ Add output generation

## Status
**Prototype Complete!** The basic implementation is working with all core features.
