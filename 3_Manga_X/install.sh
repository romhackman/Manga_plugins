#!/bin/bash
cd "$(dirname "$0")"

VENV_PYTHON="../../../.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo ".venv introuvable"
    exit 1
fi

"$VENV_PYTHON" -m pip install -r requirements.txt
