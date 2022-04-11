FROM python:3.9-slim

WORKDIR /app
ENV PORT=8000

RUN apt update && apt-get install -y cron
COPY clean-old.sh /
RUN crontab -l | { cat; echo "*/5 * * * * bash /clean-old.sh"; } | crontab -

RUN adduser flask
RUN chown --recursive flask:flask /app
USER flask

RUN python3 -m venv .venv && ./.venv/bin/python3 -m pip install pip==22

COPY --chown=flask pyproject.toml setup.cfg *.md .
COPY --chown=flask src ./src

RUN ./.venv/bin/python3 -m pip install .

# Must use sh format for env expansion
# https://docs.docker.com/engine/reference/builder/#cmd
CMD [ "sh", "-c", "./.venv/bin/gunicorn --chdir=./src --bind=\":$PORT\" icw:app" ]
