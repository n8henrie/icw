.PHONY: help
help:
	@awk '/^.PHONY:/ { next } /^[^ \t]*:/ { gsub(":.*", ""); print }' Makefile

.PHONY: serve
serve:
	./run.py

.PHONY: build-heroku
build-heroku:
	heroku container:push web

.PHONY: release-heroku
release-heroku:
	heroku container:release web
