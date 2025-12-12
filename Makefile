.PHONY: uv-sync format lint typecheck download-data clean help clearml-start clearml-stop clearml-logs clearml-setup

UV := uv

help:
	@echo "Available targets:"
	@echo "  uv-sync        Install project dependencies using uv"
	@echo "  format         Format Python files with ruff"
	@echo "  lint           Run ruff linting"
	@echo "  typecheck      Run mypy type checks"
	@echo "  download-data  Download the Kaggle dataset"
	@echo "  clean          Remove cache artifacts"
	@echo "  clearml-start  Start ClearML Server"
	@echo "  clearml-stop   Stop ClearML Server"
	@echo "  clearml-logs   View ClearML Server logs"
	@echo "  clearml-setup  Setup ClearML (start server and create project)"

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

clearml-start:
	docker-compose up -d
	@echo "ClearML Server starting. UI will be available at http://localhost:8080"

clearml-stop:
	docker-compose down

clearml-logs:
	docker-compose logs -f

clearml-setup: clearml-start
	@echo "Waiting for ClearML Server to be ready..."
	@sleep 10
	@echo "Run 'python scripts/create_clearml_project.py' after creating account in UI"
