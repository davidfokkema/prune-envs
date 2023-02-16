import pathlib
import subprocess
import threading
import time

from rich.progress import BarColumn, Progress, TextColumn
from textual.app import App, ComposeResult, Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static


class EnvironmentsList(ListView):

    BINDINGS = [("d", "mark_deletion", "Delete")]

    async def on_list_view_highlighted(self, highlighted: ListView.Highlighted) -> None:
        highlighted.item.parent.parent.scroll_to_widget(highlighted.item, animate=False)

    def action_mark_deletion(self) -> None:
        self.highlighted_child.delete()


class EnvironmentItem(ListItem):

    delete_thread = None

    def __init__(self, env: tuple) -> None:
        super().__init__()
        self.env_name, self.env_ctime = env

    def compose(self) -> ComposeResult:
        yield Label(self.env_name, id="env_name")
        yield Label(
            time.strftime("%b %d, %Y", time.localtime(self.env_ctime)), id="env_ctime"
        )
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


class InitScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Looking for conda environments...", id="init_message")


class QuitScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Waiting on running cleanups...", id="quit_message")


class PruneEnvironments(App):

    CSS_PATH = "app.css"

    BINDINGS = [("q", "quit", "Quit")]

    async def on_compose(self):
        await self.push_screen(InitScreen())
        self.envs = self.get_environments()
        self.pop_screen()

    def compose(self) -> ComposeResult:
        yield EnvironmentsList(
            *[EnvironmentItem(env) for env in self.envs],
        )
        yield Footer()

    def on_mount(self) -> None:
        self.screen.focus_next()

    async def action_quit(self) -> None:
        await self.push_screen(QuitScreen())
        self.query_one("EnvironmentsList").remove()
        return await super().action_quit()

    def get_environments(self) -> list[tuple]:
        process = subprocess.run("conda env list", shell=True, capture_output=True)
        envs = []
        for line in process.stdout.decode().splitlines():
            if line and line[0] != "#":
                env_name, *_, env_path = line.split()
                if env_name != "base":
                    ctime = pathlib.Path(env_path).stat().st_ctime
                    envs.append((env_name, ctime))
        return envs


if __name__ == "__main__":
    app = PruneEnvironments()
    app.run()
