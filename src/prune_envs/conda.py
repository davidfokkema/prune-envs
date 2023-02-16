import pathlib
import subprocess


def get_environments() -> list[tuple]:
    process = subprocess.run("conda env list", shell=True, capture_output=True)
    envs = []
    for line in process.stdout.decode().splitlines():
        if line and line[0] != "#":
            env_name, *_, env_path = line.split()
            if env_name != "base":
                ctime = pathlib.Path(env_path).stat().st_ctime
                envs.append((env_name, ctime))
    return envs


def remove_environment(name):
    subprocess.run(
        f"conda env remove -n {name} --dry-run",
        shell=True,
        capture_output=True,
    )
