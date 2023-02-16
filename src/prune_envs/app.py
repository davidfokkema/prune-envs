import subprocess
import threading
import time

from rich.spinner import Spinner
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.widgets import Footer, Label, ListItem, ListView, Static

from prune_envs import conda


class EnvironmentsList(ListView):

    BINDINGS = [("d", "mark_deletion", "Delete")]

    async def on_list_view_highlighted(self, highlighted: ListView.Highlighted) -> None:
        highlighted.item.scroll_visible()

    def action_mark_deletion(self) -> None:
        self.highlighted_child.delete()


class EnvironmentItem(ListItem):

    delete_thread = None
    _spinner = Spinner(name="simpleDots")

    def __init__(self, env: tuple) -> None:
        super().__init__()
        self.env_name, self.env_ctime = env

    def compose(self) -> ComposeResult:
        yield Label(self.env_name, id="env_name")
        yield Label(
            time.strftime("%b %d, %Y", time.localtime(self.env_ctime)), id="env_ctime"
        )
        yield Horizontal(Static(id="status_msg"), Static(id="spinner"), id="status")

    def delete(self) -> None:
        if not "delete" in self.classes:
            self.add_class("delete")
            self.query_one("#status_msg").update("Deleting")

            self.delete_thread = threading.Thread(
                target=conda.remove_environment,
                args=(self.env_name,),
            )
            self.delete_thread.start()
            self.timer = self.set_interval(1 / 60, self.update_progress)

    def update_progress(self) -> None:
        try:
            self.query_one("#spinner").update(self._spinner)
            if not self.delete_thread.is_alive():
                self.query_one("#spinner").update()
                self.query_one("#status_msg").update("Deleted")
                self.timer.stop_no_wait()
        except NoMatches:
            # during app shutdown, this method may still fire when child widgets are already destroyed
            pass

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
        self.envs = conda.get_environments()
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


if __name__ == "__main__":
    app = PruneEnvironments()
    app.run()
