serve:
	./run.py

build-docker:
	heroku container:push web

deploy:
	heroku container:release web
