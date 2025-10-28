#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 50); do
  curl -s -X POST http://127.0.0.1:8000/inference \
    -H 'Content-Type: application/json' \
    -d '{"input":[1,2,3,4]}' >/dev/null &
done
wait
echo "done"

