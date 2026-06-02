FROM python:3.11-slim-bookworm@sha256:8dca233de9f3d9bb410665f00a4da6dd06f331083137e0e98ccf227236fcc438

ARG QUARTO_VERSION=1.9.38
ARG TARGETARCH

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHON=python \
    NBA_PREDICT=nba-predict

WORKDIR /app

RUN set -eux; \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        make \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    docker_arch="${TARGETARCH:-$(dpkg --print-architecture)}" \
    && case "${docker_arch}" in \
        amd64) quarto_arch="amd64" ;; \
        arm64) quarto_arch="arm64" ;; \
        *) echo "Unsupported Docker architecture: ${docker_arch}" >&2; exit 1 ;; \
    esac \
    && quarto_asset="quarto-${QUARTO_VERSION}-linux-${quarto_arch}.deb" \
    && curl -fsSL \
        "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/${quarto_asset}" \
        -o "/tmp/${quarto_asset}" \
    && apt-get update \
    && apt-get install -y --no-install-recommends "/tmp/${quarto_asset}" \
    && rm -f "/tmp/${quarto_asset}" \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-lock.txt pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-lock.txt \
    && python -m pip install -e . --no-deps

COPY . .

CMD ["make", "reproduce"]
