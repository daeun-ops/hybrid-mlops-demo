#!/usr/bin/env bash
set -euo pipefail
pip3 install --user mlflow >/dev/null 2>&1 || true
~/.local/bin/mlflow ui --host 0.0.0.0 --port 5000

