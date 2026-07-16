# Development Setup

## Windows

Use Windows for GitHub Desktop and source editing. Run and test the Linux
runtime in one of these environments:

- WSL2 with Ubuntu
- A Linux virtual machine
- The Raspberry Pi Zero 2 W
- A Debian/Ubuntu development machine

USB printing should ultimately be tested on the Pi.

## Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
ruff check .
mypy
```

## Run the local development server

```bash
barprep-edge
```

Open:

```text
http://localhost:8787
```
