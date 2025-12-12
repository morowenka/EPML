FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    PATH="/root/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl ca-certificates git unzip \
        build-essential cmake \
        && \
    rm -rf /var/lib/apt/lists/*

# Примечание: Apache Arrow для сборки pyarrow
# В большинстве случаев pyarrow установится через предкомпилированные wheel-пакеты
# Если требуется сборка из исходников, установите Arrow:
# RUN apt-get update && apt-get install -y libarrow-dev libparquet-dev && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

RUN uv tool install dvc==3.59.0
RUN dvc repro

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["bash"]

