import asyncio
import atexit
from dataclasses import dataclass
from shlex import quote
from typing import AsyncGenerator, Optional


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
        self._close_atexit = lambda: asyncio.run(self.close(999.0))
        atexit.register(self._close_atexit)

    async def close(self, timeo: float) -> None:
        await _run(f"docker stop {quote(self.name)}", timeo)
        await _run(f"docker rm {quote(self.name)}", timeo)
        atexit.unregister(self._close_atexit)

    async def execute(self, cmd: str, timeo: float) -> Result:
        return await _run(f"docker exec {quote(self.name)} {cmd}", timeo)

    async def ip(self, timeo: float) -> str:
        cmd = "docker inspect -f "
        cmd += "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "
        cmd += quote(self.name)
        result = await _run(cmd, timeo)
        assert result.returncode == 0, "Querying ip failed"
        return result.stdout


async def container_generator_from_image(
    name: str, image: str, init_timeo: float, stop_timeo: float, args: str = ""
) -> AsyncGenerator[Container, None]:
    container = Container(name)
    cmd = f"docker run -d --name {container.name} "

    if args:
        cmd += args

    cmd += f" {quote(image)} tail -f /dev/null"
    print(cmd)

    created = await _run(cmd, init_timeo)

    if created.returncode != 0:
        raise CreationFailed(created)

    yield container
    await container.close(stop_timeo)


async def _run(cmd: str, timeo: float) -> Result:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeo)
    return Result(proc.returncode, stdout.decode().rstrip(), stderr.decode())
