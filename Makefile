SHELL := /bin/bash
PYTHON = /usr/bin/env python3
PORT=8000

.PHONY: help
help:
	@awk '/^.PHONY:/ { next } /^[^ \t]*:/ { gsub(":.*", ""); print }' Makefile

.PHONY: debug
debug:
	./run.py

.PHONY: build-heroku
build-heroku:
	heroku container:login
	DOCKER_DEFAULT_PLATFORM=linux/amd64 heroku container:push web

.PHONY: release-heroku
release-heroku: build-heroku
	heroku container:login
	heroku container:release web

.PHONY: build
build:
	docker build -t icw .

.PHONY: serve
serve: build
	docker run -it --rm -p "${PORT}:${PORT}" -e PORT="${PORT}" icw

.PHONY: clean-docs
clean-docs:
	rm -rf docs/icw*.rst docs/modules.rst docs/_build

.PHONY: docs
docs: clean-docs .venv
	source .venv/bin/activate \
		&& python -m pip install -e .[dev] \
		&& sphinx-apidoc -o docs/ src/icw \
		&& $(MAKE) -C docs clean \
		&& $(MAKE) -C docs html
	-open docs/_build/html/index.html

.venv:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e .

.PHONY: test
test: .venv
	.venv/bin/python -m pip install -e .[test]
	py.test tests

.PHONY: test-all
test-all:
	tox
