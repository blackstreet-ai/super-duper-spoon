# agents-proj-15

A minimal starter project using the OpenAI Agents SDK with Python 3.11+.

## Prerequisites
- Python 3.11 or newer
- An OpenAI API key available as `OPENAI_API_KEY`

## Quickstart

1) Create and activate a virtual environment (already created by the workflow under `.venv/`).

2) Install dependencies (already installed by the workflow):
```
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install openai-agents
```

3) Environment setup
- Copy `.env.example` to `.env` and set your real API key:
```
cp .env.example .env
# then edit .env to set: OPENAI_API_KEY=sk-...
```

4) Run the hello agent
```
.venv/bin/python src/main.py
```
You should see a haiku printed to your terminal. If you don’t, double-check that your API key is set and that you’re using the project’s `.venv`.

## Using Makefile

You can run everything with one command:
```
make run
```
This will:
- create `.venv` if it doesn't exist
- upgrade `pip`
- install project dependencies
- run the app

To remove the virtual environment (cleanup):
```
make clean
```

## Project layout
```
src/
  __init__.py
  main.py
```

## Python version policy
This repository requires Python 3.11+. See `pyproject.toml` for the `requires-python` setting.
