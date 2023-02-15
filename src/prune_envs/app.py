from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer


class EnvironmentsList(ListView):

    BINDINGS = [("d", "toggle_deletion", "Delete/Undelete")]

    def action_toggle_deletion(self):
        self.highlighted_child.toggle_class("delete")
        print(self.highlighted_child.classes)


class ListViewExample(App):

    CSS_PATH = "app.css"

    def compose(self) -> ComposeResult:
        yield EnvironmentsList(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()

    def on_mount(self):
        self.screen.focus_next()


if __name__ == "__main__":
    app = ListViewExample()
    app.run()
