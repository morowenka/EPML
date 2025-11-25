#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Export Kaggle credentials from .env if it exists
if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

KAGGLE_USERNAME="${KAGGLE_USERNAME:-}"
KAGGLE_TOKEN="${KAGGLE_TOKEN:-}"

if [[ -z "${KAGGLE_USERNAME}" || -z "${KAGGLE_TOKEN}" ]]; then
  echo "Missing Kaggle credentials. Please set KAGGLE_USERNAME and KAGGLE_TOKEN in .env." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed or not on PATH. Install uv before downloading the dataset." >&2
  exit 1
fi

if ! command -v unzip >/dev/null 2>&1; then
  echo "unzip command not found. Please install unzip to extract the dataset archive." >&2
  exit 1
fi

RAW_DIR="${REPO_ROOT}/data/raw"
EXTERNAL_DIR="${REPO_ROOT}/data/external"
INTERIM_DIR="${REPO_ROOT}/data/interim"
PROCESSED_DIR="${REPO_ROOT}/data/processed"

mkdir -p "${RAW_DIR}" "${EXTERNAL_DIR}" "${INTERIM_DIR}" "${PROCESSED_DIR}"

KAGGLE_DIR="${HOME}/.kaggle"
mkdir -p "${KAGGLE_DIR}"
chmod 700 "${KAGGLE_DIR}"

KAGGLE_JSON="${KAGGLE_DIR}/kaggle.json"
cat > "${KAGGLE_JSON}" <<EOF
{
  "username": "${KAGGLE_USERNAME}",
  "key": "${KAGGLE_TOKEN}"
}
EOF
chmod 600 "${KAGGLE_JSON}"

DATASET="yasserh/wine-quality-dataset"
DOWNLOAD_CMD=(uv run kaggle datasets download "${DATASET}" -p "${RAW_DIR}" --force)

echo "Downloading ${DATASET} into ${RAW_DIR}..."
"${DOWNLOAD_CMD[@]}"

shopt -s nullglob
for archive in "${RAW_DIR}"/*.zip; do
  echo "Extracting ${archive}..."
  unzip -o "${archive}" -d "${RAW_DIR}" >/dev/null
  rm -f "${archive}"
done
shopt -u nullglob

echo "Dataset is ready in ${RAW_DIR}."

