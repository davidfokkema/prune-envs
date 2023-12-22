import asyncio
import pathlib
import subprocess


def get_environments() -> list[tuple]:
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


async def remove_environment(name, lock):
    async with lock:
        process = await asyncio.create_subprocess_shell(
            f"conda env remove -n {name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await process.wait()
