# syntax=docker/dockerfile:1.4
FROM python:3.10 as builder

WORKDIR /tmp/wheels
COPY pyproject.toml .

# Prebuild dependencies as wheels
RUN <<'EOFDOCKER'
apt update
apt-get install -y python3-toml
rm -rf /var/lib/apt/lists/*

/usr/bin/python3 <<'EOF'
from pathlib import Path

import toml

pyproject = toml.loads(Path("pyproject.toml").read_text())
proj = pyproject["project"]

deps = {
    "wheel",
    *pyproject["build-system"]["requires"],
    *proj["dependencies"],
    *proj["optional-dependencies"]["test"],
    *proj["optional-dependencies"]["dev"],
}
Path("requirements.txt").write_text("\n".join(deps))
EOF

python3 -m pip wheel -r requirements.txt
EOFDOCKER

FROM python:3.10-slim as runner

COPY --from=builder /tmp/wheels/*.whl /tmp/wheels/

RUN \
    apt update \
    && apt-get install -y cron \
    && rm -rf /var/lib/apt/lists/*

COPY clean-old.sh /
RUN crontab -l | { cat; echo "*/5 * * * * bash /clean-old.sh"; } | crontab -

WORKDIR /app
COPY pyproject.toml *.md /app/
COPY src ./src/
COPY tests ./tests/

RUN \
    adduser docker-user \
    && chown --recursive docker-user:docker-user /app
USER docker-user

RUN \
    python3 -m venv --system-site-packages .venv \
    && ./.venv/bin/python3 -m pip install pip==22

RUN \
    ./.venv/bin/python3 -m pip install --no-index --find-links=/tmp/wheels /app[test,dev] \
    && ./.venv/bin/python3 -m pytest tests

CMD [ "./.venv/bin/gunicorn", "--bind=0.0.0.0", "--workers=4", "icw:app" ]
