FROM python:3.9-slim

WORKDIR /app
EXPOSE 8000

RUN adduser flask
RUN chown --recursive flask:flask /app
USER flask

RUN python3 -m venv .venv && ./.venv/bin/python3 -m pip install pip==22

COPY --chown=flask pyproject.toml setup.cfg *.md .
COPY --chown=flask src ./src
RUN ./.venv/bin/python3 -m pip install .

CMD [ "./.venv/bin/gunicorn", "--chdir=./src", "--bind=0.0.0.0", "icw:app" ]
