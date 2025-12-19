"""Data models for diff parsing and comments."""

from dataclasses import dataclass, field


@dataclass
class DiffLine:
    """Represents a single line in a diff."""

    line_type: str  # ' ', '+', '-', '@'
    content: str
    old_line_no: int | None
    new_line_no: int | None
    file_path: str
    hunk_header: str


@dataclass
class Comment:
    """Represents a comment on a diff line."""

    file: str
    line_no: int | None
    hunk: str
    content: str
    context: str


@dataclass
class DiffFile:
    """Represents a file in the diff."""

    path: str
    lines: list[DiffLine] = field(default_factory=list)
    comments: dict[int, Comment] = field(default_factory=dict)


@dataclass
class Diff:
    """Represents the entire diff."""

    files: list[DiffFile] = field(default_factory=list)
