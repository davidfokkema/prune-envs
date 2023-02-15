import subprocess
import threading

from rich.progress import BarColumn, Progress, TextColumn
from textual.app import App, ComposeResult, Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static


class EnvironmentsList(ListView):

    BINDINGS = [("d", "mark_deletion", "Toggle Delete/Undelete")]

    def action_mark_deletion(self) -> None:
        self.highlighted_child.delete()


class Environment(ListItem):

    delete_thread = None

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
                target=subprocess.run, kwargs=dict(args=["sleep", "5"])
            )
            self.delete_thread.start()

            self.timer = self.set_interval(1 / 60, self.update_progress)

    def update_progress(self) -> None:
        self.query_one("#status").update(self._progress)
        if not self.delete_thread.is_alive():
            self.query_one("#status").update("Deleted.")
            self.timer.stop_no_wait()

    def on_unmount(self):
        if self.delete_thread:
            self.delete_thread.join()


class QuitScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Waiting on running cleanups...", id="quit_dialog")


class ListViewExample(App):

    CSS_PATH = "app.css"

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        envs = self.get_environments()
        yield EnvironmentsList(
            *[Environment(env) for env in envs],
        )
        yield Footer()

    def on_mount(self) -> None:
        self.screen.focus_next()

    async def action_quit(self) -> None:
        await self.push_screen(QuitScreen())
        self.query_one("EnvironmentsList").remove()
        return await super().action_quit()

    def get_environments(self) -> list[str]:
        process = subprocess.run("conda env list", shell=True, capture_output=True)
        lines = process.stdout.decode().splitlines()
        envs = [line.split()[0] for line in lines if line and line[0] != "#"]
        envs.remove("base")
        return envs


if __name__ == "__main__":
    app = ListViewExample()
    app.run()
