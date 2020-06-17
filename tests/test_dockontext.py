import asyncio
import random
import string
from contextlib import asynccontextmanager

import pytest  # type: ignore

from dockontext.dockontext import (
    Container,
    CreationFailed,
    Result,
    _run,
    container_generator_from_image,
)


@pytest.mark.asyncio
async def test_run():
    assert await _run("echo hello", 0.1) == Result(0, "hello", "")


@pytest.mark.asyncio
async def test_run_timeout():
    from dockontext.dockontext import _run

    with pytest.raises(asyncio.TimeoutError):
        assert await _run("sleep 0.2", 0.1)

    assert await _run("sleep 0.1", 0.2)


@pytest.mark.asyncio
async def test_container_generator_from_image():

    context = asynccontextmanager(container_generator_from_image)

    async with context(_random_string(), "alpine", 300.0, 60.0) as container:
        assert await container.execute("echo hello", 5.0) == Result(
            0, "hello", ""
        )


@pytest.mark.asyncio
async def test_container_generator_from_image_creation_failure():

    context = asynccontextmanager(container_generator_from_image)

    with pytest.raises(CreationFailed) as e:
        async with context(_random_string(), "invalid_image", 300.0, 60.0):
            pass
    assert str(e.value).startswith("dockercontext failed to create container")


@pytest.mark.asyncio
async def test_container_close():

    name = _random_string()
    container = Container(name)

    created = await _run(
        f"docker run -d --name {container.name} alpine " "tail -f /dev/null",
        300.0,
    )

    async def exist():
        res = await _run(f"docker container inspect {container.name}", 300.0)
        return res.returncode == 0

    assert created.returncode == 0 and await exist()

    await container.close(60.0)

    assert not await exist()


@pytest.mark.asyncio
async def test_container_ip():

    context = asynccontextmanager(container_generator_from_image)

    async with context(_random_string(), "alpine", 300.0, 60.0) as container:
        ip = await container.ip(60.0)
        assert len(ip.split(".")) == 4


def _random_string():
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=30)
    )
