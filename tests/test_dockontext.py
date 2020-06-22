import random
import string
from subprocess import TimeoutExpired

import pytest  # type: ignore

from dockontext.dockontext import (
    Config,
    Container,
    CreationFailed,
    Result,
    _run,
    container_generator_from_image,
)

create_container = pytest.fixture(container_generator_from_image)


def test_run():
    assert _run("echo hello", 0.1) == Result(0, "hello", "")


def test_run_timeout():
    from dockontext.dockontext import _run

    with pytest.raises(TimeoutExpired):
        assert _run("sleep 0.2", 0.1)

    assert _run("sleep 0.1", 0.2)


def test_container_generator_from_image(create_container):
    container = create_container(_config())
    assert container.execute("echo hello", 5.0) == Result(0, "hello", "")


def test_container_generator_from_image_creation_failure(create_container):

    with pytest.raises(CreationFailed) as e:
        create_container(_config(image="invalid_image"))
    assert str(e.value).startswith("dockercontext failed to create container")


def test_container_close():

    name = _random_string()
    container = Container(name)

    created = _run(
        f"docker run -d --name {container.name} alpine " "tail -f /dev/null",
        300.0,
    )

    def exist():
        res = _run(f"docker container inspect {container.name}", 300.0)
        return res.returncode == 0

    assert created.returncode == 0 and exist()

    container.close()

    assert not exist()


def test_container_ip(create_container):
    container = create_container(_config())
    ip = container.ip()
    assert len(ip.split(".")) == 4


def _config(image="alpine"):
    return Config(
        name=_random_string(), image=image, entry_cmd="tail -f /dev/null"
    )


def _random_string():
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=30)
    )
