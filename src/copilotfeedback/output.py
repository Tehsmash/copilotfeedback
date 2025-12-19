"""Output generator for feedback."""

import json
from datetime import UTC, datetime

from .models import Diff


def generate_feedback(diff: Diff, output_path: str = "feedback.json") -> None:
    """Generate feedback JSON file from diff with comments."""
    comments = []

    for file in diff.files:
        for line_idx, comment in file.comments.items():
            comments.append({
                "file": comment.file,
                "line": comment.line_no,
                "hunk": comment.hunk,
                "content": comment.content,
                "context": comment.context,
            })

    feedback = {
        "timestamp": datetime.now(UTC).isoformat(),
        "diff_command": "git diff HEAD",
        "comments": comments,
    }

    with open(output_path, "w") as f:
        json.dump(feedback, f, indent=2)
