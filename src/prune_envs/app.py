import asyncio
import time

from rich.spinner import Spinner
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

from prune_envs import conda


class EnvironmentsList(ListView):
    """A widget showing a list of conda environments."""

    BINDINGS = [("d", "mark_deletion", "Delete")]

    async def on_list_view_highlighted(self, highlighted: ListView.Highlighted) -> None:
        """Make sure the hightlighed item does not scroll out of view."""
        highlighted.item.scroll_visible()

    def action_mark_deletion(self) -> None:
        """Delete the highlighted conda environment."""
        self.highlighted_child.delete()


class EnvironmentItem(ListItem):
    """A widget showing an individual conda environment."""

    app: "PruneEnvironments"

    delete_worker = None
    _spinner = Spinner(name="simpleDots")

    def __init__(self, env: tuple[str, int]) -> None:
        """Initialize the class.

        Args:
            env (tuple[str, int]): the name and creation timestamp of the
                environment.
        """
        super().__init__()
        self.env_name, self.env_ctime = env
        self.update_timer = self.set_interval(1 / 60, self.update_progress, pause=True)

    def compose(self) -> ComposeResult:
        """Compose the user interface showing the name and creation time."""
        yield Label(self.env_name, id="env_name")
        yield Label(
            time.strftime("%b %d, %Y", time.localtime(self.env_ctime)), id="env_ctime"
        )
        with Horizontal(id="status"):
            yield Static(id="status_msg")
            yield Static(id="spinner")

    def delete(self) -> None:
        """Start deleting the conda environment."""
        if "delete" not in self.classes:
            self.add_class("delete")
            self.delete_worker = self.remove_environment()

    @work
    async def remove_environment(self) -> None:
        """Remove the conda environment.

        This worker asynchronously updates the user interface to indicate that the environment is currently being removed, starts the removal process and awaits its completion. Finally, the user interface is updated to indicate that the removal process is finished.
        """
        self.query_one("#status_msg").update("Deleting")
        self.update_timer.resume()

        await conda.remove_environment(self.env_name, lock=self.app.conda_lock)

        self.update_timer.stop()
        # update the spinner widget to an empty value
        self.query_one("#spinner").update()
        self.query_one("#status_msg").update("Deleted")

    def update_progress(self) -> None:
        """Update the progress spinner."""
        self.query_one("#spinner").update(self._spinner)

    async def wait_on_worker(self) -> None:
        """Wait for the worker to finish before shutdown."""
        if self.delete_worker:
            await self.delete_worker.wait()


class WaitScreen(ModalScreen):
    """A modal wait screen displaying a message."""

    def __init__(self, msg: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.msg = msg

    def compose(self) -> ComposeResult:
        """Compose the user interface displaying a main message."""
        with Vertical(id="modal_wait"):
            with Center():
                yield Label(self.msg, id="msg")
            yield LoadingIndicator()


class MainScreen(Screen):
    """The main screen of the app."""

    class ShutdownComplete(Message): ...

    AUTO_FOCUS = EnvironmentsList

    def compose(self) -> ComposeResult:
        """Compose the main user interface showing a list of environments."""
        yield Header()
        yield Footer()
        yield Label(
            "Please select an environment and press 'd' to delete",
            id="instructions",
        )
        with VerticalScroll():
            yield EnvironmentsList(
                *[EnvironmentItem(env) for env in self.app.envs],
            )

    @work
    async def shutdown(self):
        for environment_item in self.query(EnvironmentItem):
            await environment_item.wait_on_worker()
        self.post_message(self.ShutdownComplete())


class PruneEnvironments(App[None]):
    """The main app class."""

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    CSS_PATH = "app.tcss"

    conda_lock = asyncio.Lock()

    async def on_mount(self) -> None:
        """Compose the wait screen and load environments."""
        await self.push_screen(WaitScreen("Looking for conda environments..."))
        self.envs = conda.get_environments()
        self.pop_screen()
        self.push_screen(MainScreen())

    async def action_quit(self) -> None:
        """Run cleanup procedure on quitting the app."""
        self.query_one(MainScreen).shutdown()
        await self.push_screen(WaitScreen("Waiting on running cleanups..."))

    @on(MainScreen.ShutdownComplete)
    async def run_quit(self):
        await super().action_quit()


app = PruneEnvironments()


def main():
    """Main app entry point."""
    app.run()


if __name__ == "__main__":
    main()
