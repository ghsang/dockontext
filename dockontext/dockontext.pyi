# isort:skip_file

from typing import AsyncGenerator, Optional, Protocol

class Result(Protocol):
    returncode: Optional[int]
    stdout: str
    stderr: str

class Container(Protocol):
    def __init__(self, name: str): ...
    async def close(self, timeo: float) -> None: ...
    async def execute(self, cmd: str, timeo: float) -> Result: ...
    async def ip(self, timeo: float) -> str: ...

async def container_generator_from_image(
    name: str,
    image: str,
    init_timeo: float,
    stop_timeo: float,
    args: str = ...,
) -> AsyncGenerator[Container, None]: ...

class CreationFailed(Exception):
    def __init__(self, res: Result): ...
    def __str__(self) -> str: ...

async def _run(cmd: str, timeo: float) -> Result: ...