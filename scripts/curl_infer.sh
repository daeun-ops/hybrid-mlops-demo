#!/usr/bin/env bash
set -euo pipefail
echo -n "Health: "
curl -s http://127.0.0.1:8000/inference/healthz && echo
echo -n "Infer : "
curl -s -X POST http://127.0.0.1:8000/inference/ \
  -H 'Content-Type: application/json' \
  -d '{"input":[10,20,30,40]}' && echo
