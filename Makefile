.DEFAULT_GOAL := all
sources = src tests

.PHONY: install
install:
	poetry install
	pre-commit install

.PHONY: format
format:
	ruff format $(sources)

.PHONY: lint
lint:
	ruff $(sources) --fix --exit-zero

.PHONY: test
test:
	pytest

.PHONY: all
all: lint test

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -rf `find . -name .pytest_cache`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build

.PHONY: docker-test
docker-test:
	docker-compose down --rmi local
	docker-compose up --build --force-recreate