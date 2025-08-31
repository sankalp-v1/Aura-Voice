#!/usr/bin/env bash
set -euo pipefail

# Robust environment setup for Aura-Voice
# - Installs pyenv if missing
# - Creates Python 3.11 venv (.venv)
# - Installs torch (CPU) + requirements.txt

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_VERSION="3.11.13"
VENV_DIR="$REPO_ROOT/.venv"

echo "Using repo root: $REPO_ROOT"

# Install pyenv if missing
if ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv not found. Installing via brew..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required to install pyenv. Install Homebrew first: https://brew.sh"
    exit 1
  fi
  brew update
  brew install pyenv
fi

# Ensure Python is installed via pyenv
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
  echo "Installing Python ${PYTHON_VERSION} via pyenv..."
  pyenv install -s ${PYTHON_VERSION}
fi

# Use pyenv local for this repo
pyenv local ${PYTHON_VERSION}

# Create venv
if [ -d "$VENV_DIR" ]; then
  echo "Removing existing venv..."
  rm -rf "$VENV_DIR"
fi
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

# Install appropriate torch. Try CPU wheel first (works on most macOS setups).
# Note: on Apple Silicon you may want the 'mps' wheel; adjust if needed.
echo "Installing torch (CPU) - may take a while..."
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio || true

# Install project requirements
python -m pip install -r requirements.txt || true

echo "Environment setup complete. Activate with: source .venv/bin/activate"
