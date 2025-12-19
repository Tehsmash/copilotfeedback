"""Textual TUI application for reviewing diffs."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from .models import Comment, Diff, DiffLine
from .output import generate_feedback


class DiffLineWidget(Static, can_focus=True):
    """Widget to display a single diff line."""

    def __init__(self, diff_line: DiffLine, index: int) -> None:
        super().__init__()
        self.diff_line = diff_line
        self.index = index
        # Only allow focus on actual code lines, not hunk headers
        self.can_focus = diff_line.line_type != "@"

    def render(self) -> str:
        """Render the diff line."""
        line = self.diff_line
        prefix = ""

        if line.line_type == "@":
            prefix = "  "
        elif line.line_type == "+":
            prefix = "+ "
        elif line.line_type == "-":
            prefix = "- "
        else:
            prefix = "  "

        # Add focus indicator
        focus_marker = "▶ " if self.has_focus else "  "
        return f"{focus_marker}{prefix}{line.content}"

    def on_mount(self) -> None:
        """Set styles when mounted."""
        if self.diff_line.line_type == "@":
            self.styles.background = "blue"
            self.styles.color = "white"
        elif self.diff_line.line_type == "+":
            self.styles.background = "green"
            self.styles.color = "white"
        elif self.diff_line.line_type == "-":
            self.styles.background = "red"
            self.styles.color = "white"

    def on_focus(self) -> None:
        """Handle focus event."""
        self.refresh()

    def on_blur(self) -> None:
        """Handle blur event."""
        self.refresh()


class CommentWidget(Static):
    """Widget to display a comment."""

    def __init__(self, comment: Comment) -> None:
        super().__init__()
        self.comment = comment

    def render(self) -> str:
        """Render the comment."""
        return f"    → [Comment] {self.comment.content}"

    def on_mount(self) -> None:
        """Set styles when mounted."""
        self.styles.background = "yellow"
        self.styles.color = "black"
        self.styles.padding = (0, 2)


class DiffReviewApp(App[None]):
    """Textual app for reviewing git diffs."""

    CSS = """
    Screen {
        background: $surface;
    }

    DiffLineWidget {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    CommentWidget {
        width: 100%;
        height: auto;
    }

    Input {
        dock: bottom;
        width: 100%;
        border: solid $accent;
    }

    #diff-container {
        height: 100%;
    }

    .file-header {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("c", "create_comment", "Create comment"),
        Binding("e", "edit_comment", "Edit comment"),
        Binding("d", "delete_comment", "Delete comment"),
        Binding("q", "quit_app", "Quit and save"),
        Binding("escape", "cancel_edit", "Cancel edit", show=False),
        Binding("up", "focus_previous", "↑ Move up", show=False),
        Binding("down", "focus_next", "↓ Move down", show=False),
        Binding("tab", "focus_next", show=False, priority=True),
        Binding("shift+tab", "focus_previous", show=False, priority=True),
    ]

    # Disable screenshot command
    ENABLE_COMMAND_PALETTE = False

    def __init__(self, diff: Diff) -> None:
        super().__init__()
        self.title = "Copilot Feedback"
        self.sub_title = "Navigate: ↑/↓/Tab/Shift+Tab  |  Comment: c  |  Quit: q"
        self.diff = diff
        self.current_line_idx = 0
        self.editing = False
        self.edit_line_idx: int | None = None
        self.all_lines: list[DiffLine] = []
        self.line_to_file: dict[int, int] = {}

        # Flatten all lines for easy navigation
        for file_idx, file in enumerate(diff.files):
            for line in file.lines:
                self.line_to_file[len(self.all_lines)] = file_idx
                self.all_lines.append(line)

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header(show_clock=False)
        yield VerticalScroll(id="diff-container")
        yield Footer()

    def on_mount(self) -> None:
        """Build the diff view on mount."""
        container = self.query_one("#diff-container", VerticalScroll)

        line_idx = 0
        for file in self.diff.files:
            # Add file header
            header = Static(f"─── File: {file.path} {'─' * 50}")
            header.add_class("file-header")
            container.mount(header)

            # Add diff lines
            for file_line_idx, line in enumerate(file.lines):
                diff_widget = DiffLineWidget(line, line_idx)
                container.mount(diff_widget)

                # Check if there's a comment for this line
                if file_line_idx in file.comments:
                    comment_widget = CommentWidget(file.comments[file_line_idx])
                    container.mount(comment_widget)

                line_idx += 1

        # Focus first non-header line
        if self.all_lines:
            widgets = container.query(DiffLineWidget)
            for widget in widgets:
                # Skip hunk headers, focus first actual code line
                if widget.diff_line.line_type != "@":
                    widget.focus()
                    widget.scroll_visible()
                    break

    def action_create_comment(self) -> None:
        """Create a new comment on the current line."""
        if self.editing:
            return

        # Get currently focused widget
        focused = self.focused
        if not isinstance(focused, DiffLineWidget):
            self.notify("Please select a diff line first", severity="warning")
            return

        widget = focused
        self.edit_line_idx = widget.index
        self.editing = True

        # Show input widget
        input_widget = Input(placeholder="Enter comment (Esc to cancel)")
        self.mount(input_widget)
        input_widget.focus()

    def action_edit_comment(self) -> None:
        """Edit an existing comment."""
        if self.editing:
            return

        # Get currently focused widget
        focused = self.focused
        if not isinstance(focused, DiffLineWidget):
            self.notify("Please select a diff line first", severity="warning")
            return

        widget = focused
        file_idx = self.line_to_file[widget.index]
        file = self.diff.files[file_idx]

        # Find the line index within the file
        file_line_idx = 0
        for i, line in enumerate(file.lines):
            if line == widget.diff_line:
                file_line_idx = i
                break

        if file_line_idx not in file.comments:
            self.notify("No comment to edit on this line", severity="warning")
            return

        self.edit_line_idx = widget.index
        self.editing = True

        # Show input widget with existing comment
        existing_comment = file.comments[file_line_idx].content
        input_widget = Input(value=existing_comment, placeholder="Edit comment (Esc to cancel)")
        self.mount(input_widget)
        input_widget.focus()

    def action_delete_comment(self) -> None:
        """Delete comment on current line."""
        if self.editing:
            return

        # Get currently focused widget
        focused = self.focused
        if not isinstance(focused, DiffLineWidget):
            self.notify("Please select a diff line first", severity="warning")
            return

        widget = focused
        file_idx = self.line_to_file[widget.index]
        file = self.diff.files[file_idx]

        # Find the line index within the file
        file_line_idx = 0
        for i, line in enumerate(file.lines):
            if line == widget.diff_line:
                file_line_idx = i
                break

        if file_line_idx in file.comments:
            del file.comments[file_line_idx]
            self.notify("Comment deleted")
            self.rebuild_view()
        else:
            self.notify("No comment to delete on this line", severity="warning")

    def action_cancel_edit(self) -> None:
        """Cancel editing a comment."""
        if self.editing:
            self.editing = False
            self.edit_line_idx = None
            # Remove input widget
            input_widgets = self.query(Input)
            if input_widgets:
                input_widgets.first().remove()
            # Refocus diff view
            container = self.query_one("#diff-container", VerticalScroll)
            widgets = container.query(DiffLineWidget)
            if widgets:
                widgets.first().focus()

    def action_quit_app(self) -> None:
        """Quit and save feedback."""
        generate_feedback(self.diff)
        self.notify("Feedback saved to feedback.json")
        self.exit()

    def action_focus_previous(self) -> None:
        """Move focus to previous line."""
        if self.editing:
            return
        self.screen.focus_previous()

    def action_focus_next(self) -> None:
        """Move focus to next line."""
        if self.editing:
            return
        self.screen.focus_next()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle comment input submission."""
        if not self.editing or self.edit_line_idx is None:
            return

        comment_text = event.value.strip()
        if not comment_text:
            self.action_cancel_edit()
            return

        # Find the file and line
        file_idx = self.line_to_file[self.edit_line_idx]
        file = self.diff.files[file_idx]
        line = self.all_lines[self.edit_line_idx]

        # Find the line index within the file
        file_line_idx = 0
        for i, file_line in enumerate(file.lines):
            if file_line == line:
                file_line_idx = i
                break

        # Create comment
        comment = Comment(
            file=file.path,
            line_no=line.new_line_no or line.old_line_no,
            hunk=line.hunk_header,
            content=comment_text,
            context=line.content,
        )

        file.comments[file_line_idx] = comment
        self.editing = False
        self.edit_line_idx = None

        # Remove input widget and rebuild view
        event.input.remove()
        self.rebuild_view()
        self.notify("Comment saved")

    def rebuild_view(self) -> None:
        """Rebuild the diff view."""
        container = self.query_one("#diff-container", VerticalScroll)
        container.remove_children()

        line_idx = 0
        for file in self.diff.files:
            # Add file header
            header = Static(f"─── File: {file.path} {'─' * 50}")
            header.add_class("file-header")
            container.mount(header)

            # Add diff lines
            for file_line_idx, line in enumerate(file.lines):
                diff_widget = DiffLineWidget(line, line_idx)
                container.mount(diff_widget)

                # Check if there's a comment for this line
                if file_line_idx in file.comments:
                    comment_widget = CommentWidget(file.comments[file_line_idx])
                    container.mount(comment_widget)

                line_idx += 1

        # Refocus first non-header line
        widgets = container.query(DiffLineWidget)
        for widget in widgets:
            if widget.diff_line.line_type != "@":
                widget.focus()
                widget.scroll_visible()
                break
