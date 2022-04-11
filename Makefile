PORT=8000

.PHONY: help
help:
	@awk '/^.PHONY:/ { next } /^[^ \t]*:/ { gsub(":.*", ""); print }' Makefile

.PHONY: debug
debug:
	./run.py

.PHONY: build-heroku
build-heroku:
	DOCKER_DEFAULT_PLATFORM=linux/amd64 heroku container:push web

.PHONY: release-heroku
release-heroku: build-heroku
	heroku container:release web

.PHONY: build
build:
	docker build -t icw .

.PHONY: serve
serve: build
	docker run -it -p "${PORT}:${PORT}" -e PORT="${PORT}" icw
