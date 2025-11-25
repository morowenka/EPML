.PHONY: uv-sync format lint typecheck download-data clean help

UV := uv

help:
	@echo "Available targets:"
	@echo "  uv-sync        Install project dependencies using uv"
	@echo "  format         Format Python files with ruff"
	@echo "  lint           Run ruff linting"
	@echo "  typecheck      Run mypy type checks"
	@echo "  download-data  Download the Kaggle dataset"
	@echo "  clean          Remove cache artifacts"

uv-sync:
	$(UV) sync

format:
	$(UV) run ruff format

lint:
	$(UV) run ruff check --force-exclude

typecheck:
	$(UV) run mypy .

download-data:
	bash data/download_dataset.sh

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .mypy_cache/ .ruff_cache/
