.DEFAULT_GOAL := run

PYTHON := python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Create venv and upgrade pip
venv:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(PY) -m pip install --upgrade pip

# Install project dependencies
install: venv
	@$(PIP) install openai-agents python-dotenv

# Run the hello agent
run: install
	@$(PY) src/main.py

# Remove the virtual environment (careful!)
clean:
	rm -rf $(VENV)
