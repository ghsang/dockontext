# dockontext
[![pypi](https://img.shields.io/pypi/v/dockontext.svg)](https://pypi.python.org/pypi/dockontext)
[![Build Status](https://travis-ci.com/ghsang/dockontext.svg?branch=master)](https://travis-ci.com/ghsang/dockontext)
[![codecov](https://codecov.io/gh/ghsang/dockontext/branch/master/graph/badge.svg)](https://codecov.io/gh/ghsang/dockontext)


### context manager that runs and closes docker containers
* When integration or end-to-end test needs temporal docker container to fake remote systems, this package will help to create/close/remove the temporal docker container.

### Features
* Create docker container by giving image name. The container will be named as 'docontext={name}'
* Close and remove the container when exit.

### Example

#### pytest.fixture
```
import pytest
from dockontext import container_generator_from_image, Result, Config

create_container = pytest.fixture(container_generator_from_image)

def test_fixture(create_container):
     config = Config(name, "alpine:latest")
     container = create_container(config)
     result = container.execute("echo hello", timeout: float)
     assert result == Result(returncode=0, stdout="hello\n", stderr="")
```


### TODO
* Dockerfile
* docker-compose.yml
* container group context

### Free software: MIT License


### Credits

* This package was created with [Cookiecutter][1]
* Also was copied and modified from the [audreyr/cookiecutter-pypackage][2] project template.

[1]: https://github.com/cookiecutter/cookiecutter
[2]: https://github.com/audreyr/cookiecutter-pypackage
