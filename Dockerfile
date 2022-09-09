FROM python:3.10 as builder

COPY pyproject.toml *.md /app/
COPY src /app/src/
WORKDIR /tmp/wheels
RUN \
    python3 -m pip install build \
    && python3 -m build /app \
    && python3 -m pip wheel /app[test,dev]

FROM python:3.10-slim as runner

COPY --from=builder /tmp/wheels/*.whl /tmp/wheels/

ENV PORT=8000

RUN \
    apt update \
    && apt-get install -y cron \
    && rm -rf /var/lib/apt/lists/*

COPY clean-old.sh /
RUN crontab -l | { cat; echo "*/5 * * * * bash /clean-old.sh"; } | crontab -

WORKDIR /app
COPY tests ./tests/

RUN adduser docker-user
RUN chown --recursive docker-user:docker-user /app
USER docker-user

RUN \
    python3 -m venv --system-site-packages .venv \
    && ./.venv/bin/python3 -m pip install pip==22 \
    && ./.venv/bin/python3 -m pip install --no-index --find-links=/tmp/wheels icw[test,dev] \
    && ./.venv/bin/python3 -m pytest tests

CMD [ "./.venv/bin/gunicorn", "--bind=:8000", "--workers=4", "icw:app" ]
