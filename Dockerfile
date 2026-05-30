FROM python:3.11-slim

ARG QUARTO_VERSION=1.7.32
ARG TARGETARCH

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        make \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
        amd64) quarto_arch="amd64" ;; \
        arm64) quarto_arch="arm64" ;; \
        *) echo "Unsupported Docker architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL \
        "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${quarto_arch}.deb" \
        -o /tmp/quarto.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/quarto.deb \
    && rm -f /tmp/quarto.deb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-lock.txt pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-lock.txt \
    && python -m pip install -e . --no-deps

COPY . .

CMD ["make", "reproduce"]
