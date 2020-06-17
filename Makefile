.PHONY: add-poetry install

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
        match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
        if match:
                target, help = match.groups()
                print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

add-poetry:
	if [ -s requirements.in ]; then poetry add $(shell $(cat requirements.in)); fi
	poetry add --dev $(shell cat requirements_dev.in)

install:
	poetry install
