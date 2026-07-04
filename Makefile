# --- CONFIGURATION ---
VENV_NAME = .venv
UV = uv
export UV_SYSTEM_CERTS = 1

# Forces native 'uv sync' to target your custom directory name
export UV_PROJECT_ENVIRONMENT = $(VENV_NAME)

ifeq ($(OS),Windows_NT)
    VENV_BIN = $(VENV_NAME)/Scripts
else
    VENV_BIN = $(VENV_NAME)/bin
endif

PYTHON = $(VENV_BIN)/python

.PHONY: help install test lint clean uninstall

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(VENV_NAME): 
	@echo "Creating custom virtual environment '$(VENV_NAME)'..."
	$(UV) venv $(VENV_NAME)

install: $(VENV_NAME) ## Sync dependencies perfectly using native 'uv sync'
	@echo "Syncing environment with pyproject.toml / uv.lock..."
	$(UV) sync
	
	@# If you have local wheels that aren't declared in your pyproject.toml, 
	@# we install them right after using '--inexact' so uv doesn't delete them.
	@if [ "$$(ls *.whl 2>/dev/null)" ]; then \
		echo "Syncing local wheel files..."; \
		$(UV) pip install *.whl --python $(PYTHON); \
	fi

test: ## Run unit tests using pytest via uv
	$(UV) run --python $(PYTHON) pytest tests/

lint: ## Run code checks and formatting via uv
	$(UV) run --python $(PYTHON) ruff check .
	$(UV) run --python $(PYTHON) ruff format .

clean: ## Remove caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .uv build dist *.egg-info

uninstall: ## Remove virtual environment
	rm -rf $(VENV_NAME)
