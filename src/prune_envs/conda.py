import asyncio
import pathlib
import subprocess


def get_environments() -> list[tuple]:
    """Get a list of conda environments.

    Returns a list of conda environments where each item is a tuple consisting
    of the name of the environment and its creation timestamp.

    Returns:
        list[tuple]: the list of environments
    """
    process = subprocess.run("conda env list", shell=True, capture_output=True)
    envs = []
    for line in process.stdout.decode().splitlines():
        match line.split():
            case "#", *_:
                pass
            case env_name, *_, env_path if env_name != "base":
                ctime = pathlib.Path(env_path).stat().st_ctime
                envs.append((env_name, ctime))
            case _:
                pass
    return envs


async def remove_environment(name: str, lock: asyncio.Lock) -> None:
    """Remove a conda environment.

    Remove the named conda environment. The process is locked using the provided
    lock to ensure that the `conda env remove` command is not run concurrently
    which breaks the removal process.

    Args:
        name (str): the name of the environment to remove. lock (asyncio.Lock):
        the lock to guard the removal process.
    """
    async with lock:
        process = await asyncio.create_subprocess_shell(
            f"conda env remove -n {name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await process.wait()
