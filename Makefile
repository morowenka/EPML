.PHONY: uv-sync format lint typecheck download-data clean help parallel-pipeline parallel-stages prepare-data train-model compute-stats

UV := uv

help:
	@echo "Available targets:"
	@echo "  uv-sync           Install project dependencies using uv"
	@echo "  format            Format Python files with ruff"
	@echo "  lint              Run ruff linting"
	@echo "  typecheck         Run mypy type checks"
	@echo "  download-data     Download the Kaggle dataset"
	@echo "  clean             Remove cache artifacts"
	@echo ""
	@echo "Pipeline targets:"
	@echo "  parallel-pipeline Run full pipeline with parallel stages"
	@echo "  parallel-stages   Run train_model and compute_statistics in parallel"
	@echo "  prepare-data      Run data preparation stage"
	@echo "  train-model       Run model training stage"
	@echo "  compute-stats     Run statistics computation stage"

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

# Pipeline targets
prepare-data:
	@echo "[prepare-data] Starting at $$(date +%H:%M:%S)"
	PYTHONPATH=. $(UV) run python src/data/make_dataset.py
	@echo "[prepare-data] Finished at $$(date +%H:%M:%S)"

train-model:
	@echo "[train-model] Starting at $$(date +%H:%M:%S)"
	PYTHONPATH=. $(UV) run python src/models/train_model.py
	@echo "[train-model] Finished at $$(date +%H:%M:%S)"

compute-stats:
	@echo "[compute-stats] Starting at $$(date +%H:%M:%S)"
	PYTHONPATH=. $(UV) run python src/data/compute_statistics.py
	@echo "[compute-stats] Finished at $$(date +%H:%M:%S)"

# Dependencies only - run with: make -j2 parallel-stages
parallel-stages: train-model compute-stats

# Sequential prepare-data, then parallel stages
parallel-pipeline:
	@echo "Step 1: Running prepare-data..."
	@$(MAKE) prepare-data
	@echo "Step 2: Running parallel stages..."
	@$(MAKE) -j2 parallel-stages
