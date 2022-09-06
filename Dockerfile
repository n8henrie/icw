# FROM python:3.9 as builder
#
# RUN apt install gcc
# RUN python3 -m pip wheel 'typed-ast<1.1'
# RUN find / -name '*.whl' -ls; false

FROM python:3.9-slim as runner

COPY --from=builder /root/.pip/ /root/.pip/

ENV PORT=8000

RUN \
    apt update \
    && apt-get install -y cron \
    && rm -rf /var/lib/apt/lists/*
    # && apt-get install -y gcc \
    # && pip install 'typed-ast<1.1.0' \
    # && apt-get purge -y --auto-remove gcc

COPY clean-old.sh /
RUN crontab -l | { cat; echo "*/5 * * * * bash /clean-old.sh"; } | crontab -

WORKDIR /app
COPY pyproject.toml setup.cfg *.md .
COPY src ./src
COPY tests ./tests

RUN adduser flask
RUN chown --recursive flask:flask /app
USER flask

RUN \
    python3 -m venv --system-site-packages .venv \
    && ./.venv/bin/python3 -m pip install pip==22 \
    && ./.venv/bin/python3 -m pip install --prefer-binary .[test,dev] \
    && ./.venv/bin/python3 -m pytest tests

# Must use sh format for env expansion
# https://docs.docker.com/engine/reference/builder/#cmd
CMD [ "sh", "-c", "./.venv/bin/gunicorn --chdir=./src --bind=\":$PORT\" --workers=4 icw:app" ]
