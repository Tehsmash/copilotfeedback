"""Git diff parser."""

import re
import subprocess

from .models import Diff, DiffFile, DiffLine


def get_git_diff() -> str:
    """Execute git diff HEAD and return output."""
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def parse_diff(diff_text: str) -> Diff:
    """Parse git diff output into structured data."""
    diff = Diff()
    current_file: DiffFile | None = None
    current_hunk = ""
    old_line_no = 0
    new_line_no = 0

    lines = diff_text.split("\n")

    for line in lines:
        # File header
        if line.startswith("diff --git"):
            if current_file:
                diff.files.append(current_file)
            current_file = None

        # File path (--- and +++)
        elif line.startswith("+++"):
            path = line[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            current_file = DiffFile(path=path)

        # Hunk header
        elif line.startswith("@@"):
            match = re.match(r"@@ -(\d+),?\d* \+(\d+),?\d* @@.*", line)
            if match:
                old_line_no = int(match.group(1))
                new_line_no = int(match.group(2))
                current_hunk = line.split("@@")[1].strip() if "@@" in line else line
            if current_file:
                diff_line = DiffLine(
                    line_type="@",
                    content=line,
                    old_line_no=None,
                    new_line_no=None,
                    file_path=current_file.path,
                    hunk_header=line,
                )
                current_file.lines.append(diff_line)

        # Diff content
        elif current_file and line:
            if line.startswith("+"):
                diff_line = DiffLine(
                    line_type="+",
                    content=line[1:],
                    old_line_no=None,
                    new_line_no=new_line_no,
                    file_path=current_file.path,
                    hunk_header=current_hunk,
                )
                current_file.lines.append(diff_line)
                new_line_no += 1
            elif line.startswith("-"):
                diff_line = DiffLine(
                    line_type="-",
                    content=line[1:],
                    old_line_no=old_line_no,
                    new_line_no=None,
                    file_path=current_file.path,
                    hunk_header=current_hunk,
                )
                current_file.lines.append(diff_line)
                old_line_no += 1
            elif line.startswith(" "):
                diff_line = DiffLine(
                    line_type=" ",
                    content=line[1:],
                    old_line_no=old_line_no,
                    new_line_no=new_line_no,
                    file_path=current_file.path,
                    hunk_header=current_hunk,
                )
                current_file.lines.append(diff_line)
                old_line_no += 1
                new_line_no += 1

    if current_file:
        diff.files.append(current_file)

    return diff
