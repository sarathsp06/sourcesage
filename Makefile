.PHONY: init test lint fix format clean run build install venv

# Python interpreter to use
PYTHON := python3
# Test file
TEST_FILE := test_storage.py
# Package name
PACKAGE := sourcesage
# Virtual environment directory
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Create a virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

# Initialize the project
init: venv
	@echo "Installing dependencies..."
	$(VENV_PIP) install -e .
	$(VENV_PIP) install ruff build
	@echo "Dependencies installed successfully."

# Run tests
test: venv
	@echo "Running tests..."
	$(VENV_PYTHON) $(TEST_FILE)
	@echo "Tests completed."

# Run linting
lint: venv
	@echo "Running linters..."
	$(VENV_BIN)/ruff check $(PACKAGE)
	@echo "Linting completed."

# Fix linting issues
fix: venv
	@echo "Fixing linting issues..."
	$(VENV_BIN)/ruff check --fix $(PACKAGE)
	@echo "Linting fixes completed."

# Format code
format: venv
	@echo "Formatting code..."
	$(VENV_BIN)/ruff format $(PACKAGE)
	@echo "Formatting completed."

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ .ruff_cache/ $(VENV_DIR)/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	@echo "Cleanup completed."

# Run the MCP server
run: venv
	@echo "Starting SourceSage MCP server..."
	$(VENV_PYTHON) -m sourcesage.mcp_server

# Build the package
build: venv
	@echo "Building package..."
	$(VENV_PYTHON) -m build
	@echo "Build completed."

# Install the package locally
install: venv
	@echo "Installing package locally..."
	$(VENV_PIP) install -e .
	@echo "Installation completed."

# Show help
help:
	@echo "Available targets:"
	@echo "  venv     - Create a virtual environment"
	@echo "  init     - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linters"
	@echo "  fix      - Fix linting issues"
	@echo "  format   - Format code"
	@echo "  clean    - Clean up temporary files"
	@echo "  run      - Run the MCP server"
	@echo "  build    - Build the package"
	@echo "  install  - Install the package locally"
	@echo "  help     - Show this help message"
