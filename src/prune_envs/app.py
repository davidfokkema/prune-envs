from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer, Static
from rich.progress import Progress, TextColumn, BarColumn


class EnvironmentsList(ListView):

    BINDINGS = [("q", "quit", "Quit"), ("d", "mark_deletion", "Toggle Delete/Undelete")]

    def action_mark_deletion(self) -> None:
        self.highlighted_child.delete()


class Environment(ListItem):
    counts = 0

    def __init__(self, env_name: str) -> None:
        super().__init__()
        self.env_name = env_name

    def compose(self) -> ComposeResult:
        yield Label(self.env_name, id="env_name")
        yield Static(id="status")

    def delete(self) -> None:
        self.add_class("delete")
        self._progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
        )
        self._progress.add_task("Deleting...", total=None)
        self.timer = self.set_interval(1 / 60, self.update_progress)

    def update_progress(self) -> None:
        self.query_one("#status").update(self._progress)
        self.counts += 1
        if self.counts > 180:
            self.query_one("#status").update("Deleted.")
            self.timer.stop_no_wait()


class ListViewExample(App):

    CSS_PATH = "app.css"

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
