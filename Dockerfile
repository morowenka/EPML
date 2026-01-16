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

# Примечание: dvc repro должен выполняться ВНУТРИ контейнера после dvc pull
# Согласно отчету hw2 (раздел Docker), правильный workflow:
# 1. docker build -t wine-hw2 .
# 2. docker run ... wine-hw2 bash
# 3. Внутри контейнера: uv sync --frozen && dvc pull --remote localremote && dvc repro
# dvc repro не выполняется во время build, так как:
# - DVC remote недоступен во время build (только через volume mount при запуске)
# - MLflow создает mlruns/ во время train_model, что должно происходить в runtime

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["bash"]

