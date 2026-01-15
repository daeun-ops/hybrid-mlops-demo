# Architecture Overview

This document explains the structure and reasoning behind the Hybrid MLOps Demo.  
The goal is not to build a large-scale production system but to simulate **how hybrid data and inference pipelines can work**, even in a minimal local setup.

---

## 1. Background

The project started as a simple **Docker Compose environment** to test local inference using Ray Serve.  
However, several gaps became clear:

| Issue | Description |
|--------|-------------|
| Limited scope | Everything ran locally; no way to test hybrid or remote flows. |
| Fragile when GPU is missing | If CUDA was not available, the whole service failed. |
| Static orchestration | Airflow DAGs were fixed to one endpoint. |
| Weak visibility | Only manual logs, no real monitoring layer. |

---

## 2. Design Goals

This iteration focuses on educational and structural clarity:

1. **Hybrid-ready design** — keep the same logic for both local and cloud runs.  
2. **Single DAG orchestration** — Airflow controls the entire data and inference flow.  
3. **CPU fallback** — if GPU is absent, inference gracefully switches mode.  
4. **Light observability** — add Prometheus and Grafana for end-to-end visibility.  
5. **Developer accessibility** — use simple Make targets and safe environment setup.

---

## 3. Logical Flow
Camera / Mock Image → MinIO (S3 folder)

→ Airflow FileSensor or S3KeySensor detects change

→ Ray Serve inference API

→ Prometheus scrapes /metrics

→ Grafana visualizes latency, count, errors


- The data flow is continuous and event-driven.
- All components are local by default, but the same DAG can target a remote endpoint (e.g., EKS ingress).
- The design is modular enough to extend into hybrid or cost-aware scenarios later.

---

## 4. Key Components

| Layer | Description |
|--------|-------------|
| Ray Serve | Inference API; runs on CPU or GPU automatically |
| Airflow | Orchestrates tasks and triggers inference jobs |
| MinIO | Lightweight S3-compatible storage |
| Prometheus | Collects system metrics |
| Grafana | Displays latency, request rate, and GPU/CPU activity |
| Terraform / Helm (optional) | Used when extending to EKS-based setups |

---

## 5. Typical Commands

| Purpose | Command |
|----------|----------|
| Start local stack | `make e2e-local` |
| Run observability stack | `make obs-up` |
| Test inference manually | `make infer` |
| Check container health | `make health` |

---

## 6. Next Steps

- Optional migration to AWS EKS for hybrid demo.  
- Add simple FinOps dashboard (mock GPU cost).  
- Expand Airflow DAG to trigger multi-endpoint inference.

---


# Hybrid MLOps Architecture (Lightweight Version)

This project demonstrates a hybrid inference and observability workflow:

1. **Local Sensor Simulation (MinIO)**
   - Camera images are uploaded to a local S3 bucket.
   - Airflow detects file events using `S3KeySensor`.

2. **Orchestration (Airflow)**
   - DAG triggers Ray Serve inference API.
   - Same DAG can be reused for EKS endpoints.

3. **Inference (Ray Serve)**
   - Lightweight FastAPI-based Ray Serve deployment.
   - Switchable between GPU/CPU.

4. **Observability**
   - Prometheus scrapes metrics from Ray Serve.
   - Grafana visualizes latency, requests, and custom GPU activity.

5. **Scalability (Future Extension)**
   - Optional EKS setup with Terraform + Helm for distributed inference.

> Local and Cloud share the same logical flow — only endpoints differ.

