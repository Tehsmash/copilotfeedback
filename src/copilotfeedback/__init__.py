"""Copilot Feedback - A TUI for reviewing git diffs and providing feedback."""

from .app import DiffReviewApp
from .parser import get_git_diff, parse_diff


def main() -> None:
    """Main entry point for the application."""
    try:
        # Get git diff
        diff_text = get_git_diff()

        if not diff_text.strip():
            print("No changes detected in git diff HEAD")
            return

        # Parse diff
        diff = parse_diff(diff_text)

        if not diff.files:
            print("No files to review")
            return

        # Run TUI app
        app = DiffReviewApp(diff)
        app.run()

    except Exception as e:
        print(f"Error: {e}")
        raise
