import atexit
import subprocess
from dataclasses import dataclass
from shlex import quote
from typing import Callable, Generator, Optional


@dataclass
class Result:
    returncode: Optional[int]
    stdout: str
    stderr: str


class CreationFailed(Exception):
    def __init__(self, res: Result):
        self.res = res
        self.message = f"dockercontext failed to create container: {self.res}"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class Container:
    def __init__(self, name: str):
        self.name = "dockontext-" + name
        self._close_atexit = lambda: self.close()
        atexit.register(self._close_atexit)

    def close(self, timeo: float = 60.0) -> None:
        _run(f"docker stop {quote(self.name)}", timeo)
        _run(f"docker rm {quote(self.name)}", timeo)
        atexit.unregister(self._close_atexit)

    def execute(self, cmd: str, timeo: float) -> Result:
        return _run(f"docker exec {quote(self.name)} {cmd}", timeo)

    def ip(self, timeo: float = 10.0) -> str:
        cmd = "docker inspect -f "
        cmd += "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "
        cmd += quote(self.name)
        result = _run(cmd, timeo)
        assert result.returncode == 0, "Querying ip failed"
        return result.stdout


@dataclass
class Config:
    name: str
    image: str
    init_timeo: float = 300.0
    stop_timeo: float = 60.0
    args: str = ""
    entry_cmd: str = ""


ContainerFactory = Generator[Callable[[Config], Container], None, None]


def container_generator_from_image() -> ContainerFactory:
    _container = []
    _stop_timeo = []

    def inner(cfg: Config):
        container = Container(cfg.name)

        _container.append(container)
        _stop_timeo.append(cfg.stop_timeo)

        cmds = [f"docker run -d --name {container.name}"]

        if cfg.args:
            cmds.append(cfg.args)

        cmds.append(quote(cfg.image))

        if cfg.entry_cmd:
            cmds.append(cfg.entry_cmd)

        cmd = " ".join(cmds)

        created = _run(cmd, cfg.init_timeo)

        if created.returncode != 0:
            raise CreationFailed(created)

        return container

    yield inner

    _container[0].close(_stop_timeo[0])


def _run(cmd: str, timeo: float) -> Result:
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = proc.communicate(timeout=timeo)
    return Result(proc.returncode, stdout.decode().rstrip(), stderr.decode())
