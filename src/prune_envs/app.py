from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer, Static
import threading


class EnvironmentsList(ListView):

    BINDINGS = [("q", "quit", "Quit"), ("d", "mark_deletion", "Toggle Delete/Undelete")]

    def action_mark_deletion(self):
        self.highlighted_child.delete()


class Environment(ListItem):
    def __init__(self, env_name: str) -> None:
        super().__init__()
        self.env_name = env_name

    def compose(self) -> ComposeResult:
        yield Label(self.env_name)
        yield Static(id="status")

    def delete(self):
        self.add_class("delete")


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
