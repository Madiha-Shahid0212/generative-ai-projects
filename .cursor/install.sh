#!/usr/bin/env bash
#
# Idempotent development-environment setup for the generative-ai-projects repo.
#
# Installs Python dependencies (into a shared virtualenv at repo root) for the
# three Python projects plus the resume PDF builder, and installs the Node
# dependencies for the "explain-like-im-a-bot" React frontend.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="$REPO_ROOT/.venv"

# The default image ships Python 3.12 but not the venv module; install it if
# creating a virtualenv fails. Guarded so reruns stay fast and non-interactive.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "==> Installing python3-venv"
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3-venv python3-pip
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "==> Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Upgrading pip"
python -m pip install --upgrade pip -q

echo "==> Installing Python dependencies"
pip install -q \
  -r cot-persona-reasoning/requirements.txt \
  -r resume-interview-generator/requirements.txt \
  -r explain-like-im-a-bot/requirements.txt \
  reportlab   # used by resume/build_resume.py (no requirements.txt of its own)

echo "==> Installing frontend (npm) dependencies"
cd "$REPO_ROOT/explain-like-im-a-bot/frontend"
npm install --no-fund --no-audit

echo "==> Setup complete"
