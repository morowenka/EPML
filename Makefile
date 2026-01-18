.PHONY: uv-sync format lint typecheck download-data clean help clearml-start clearml-stop clearml-logs clearml-setup docs docs-clean docs-serve

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
	@echo "  docs           Build documentation"
	@echo "  docs-clean     Clean documentation build"
	@echo "  docs-serve     Build and serve documentation locally"

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

docs:
	cd docs && $(UV) run sphinx-build -b html . _build/html

docs-clean:
	rm -rf docs/_build

docs-serve: docs
	@echo "Starting documentation server on http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@cd docs/_build/html && $(UV) run python -m http.server 8000
