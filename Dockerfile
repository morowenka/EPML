FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/root/.cache/uv

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl ca-certificates git unzip && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

CMD ["uv", "run", "python"]

