#!/usr/bin/env bash
set -euo pipefail
minikube start --driver=docker --cpus=4 --memory=6144
kubectl get nodes
