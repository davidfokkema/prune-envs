import subprocess
import threading

from rich.progress import BarColumn, Progress, TextColumn
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView, Static


class EnvironmentsList(ListView):

    BINDINGS = [("d", "mark_deletion", "Toggle Delete/Undelete")]

    def action_mark_deletion(self) -> None:
        self.highlighted_child.delete()


class Environment(ListItem):
    def __init__(self, env_name: str) -> None:
        super().__init__()
        self.env_name = env_name

    def compose(self) -> ComposeResult:
        yield Label(self.env_name, id="env_name")
        yield Static(id="status")

    def delete(self) -> None:
        if not "delete" in self.classes:
            self.add_class("delete")
            self._progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
            )
            self._progress.add_task("Deleting...", total=None)

            self.delete_thread = threading.Thread(
                target=subprocess.run, kwargs=dict(args=["sleep", "15"])
            )
            self.delete_thread.start()

            self.timer = self.set_interval(1 / 60, self.update_progress)

    def update_progress(self) -> None:
        self.query_one("#status").update(self._progress)
        if not self.delete_thread.is_alive():
            self.query_one("#status").update("Deleted.")
            self.timer.stop_no_wait()


class ListViewExample(App):

    CSS_PATH = "app.css"

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield EnvironmentsList(
            Environment("One"),
            Environment("Two"),
            Environment("Three"),
        )
        yield Footer()

    def on_mount(self):
        self.screen.focus_next()


if __name__ == "__main__":
    app = ListViewExample()
    app.run()
