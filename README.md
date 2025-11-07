# Hybrid MLOps Demo (Local + Cloud Simulation)

This repository demonstrates a **lightweight hybrid MLOps pipeline** designed for experimentation and learning.  
It focuses on connecting simple local components (Airflow, MinIO, Ray Serve) with a simulated or optional cloud backend (EKS).  
The goal is to understand how **data flow, orchestration, and observability** can work together across environments — even on a single developer laptop.

---
### Local Hardware Environment

All local workloads run on a developer laptop that simulates an **on-premise inference node** within a hybrid infrastructure.

| Component | Description |
| --- | --- |
| **CPU** | 6-core (1.0 vCPU used during Ray tasks) |
| **GPU** | NVIDIA GeForce RTX 2060 (CUDA 11.6 enabled) |
| **Memory** | ~4.8 GiB usage / 32 GiB total |
| **Inference Engine** | Ray Serve (`ray-inference:cu116`) |
| **Monitoring** | Prometheus / Grafana metrics (e.g. `inference_requests_total`) |
| **Health Checks** | `/inference/healthz`, `/inference/metrics` endpoints |

In this setup, the laptop acts as a **physical on-premise node**—handling real GPU inference and exposing unified observability endpoints—while the cloud (EKS) side represents scalable compute resources for production or distributed workloads.



---
## Project Overview

The original version of this project was built as a small **local inference demo** using Docker Compose.  
It worked for functional testing but had several limitations:

- Hard to test scenarios where GPU or services are unavailable.  
- Difficult to switch between local and cloud endpoints.  
- Observability limited to container logs only.  
- No cost or efficiency visibility when scaling between environments.

To improve this, the project was restructured into a **hybrid-style architecture** that keeps all core logic local but mirrors how a real multi-environment MLOps system would behave.

---

## Project Focus Areas

### Hybrid Flow
Connects **local components (MinIO, Airflow, Ray Serve)** and allows easy migration of the same logic to a **cloud environment** later on.

### Orchestration
A single **Airflow DAG** coordinates image detection, inference triggering, and metric collection.

### Fallback Logic
When GPU is unavailable or skipped, inference falls back to CPU mode automatically — preserving workflow continuity.

### Observability
**Prometheus + Grafana** visualize latency, throughput, and resource activity.  
Focus is on learning how metrics are exposed and visualized, not on production-scale performance.

### Developer Usability
Simple to run and modify:
- `make e2e-local` — full local pipeline test  
- `make obs-up` — start observability stack  
- Safe `.env` handling and pre-commit secret checks

---

## Technology Stack

| Category | Components |
|-----------|-------------|
| **Inference Service** | Ray Serve + FastAPI (CUDA optional, runs on CPU if not available) |
| **Scheduler** | Apache Airflow 2.9.x (FileSensor / S3KeySensor → BashOperator / HTTP call) |
| **Storage** | MinIO (S3 compatible local bucket) |
| **Observability** | Prometheus + Grafana (custom /metrics endpoint and dashboards) |
| **Automation** | Docker Compose, Makefile, .env / .env.example, pre-commit guard |
| **Cloud Extension** | AWS EKS, Terraform, Helm for scaling and FinOps demo |

---

## Project Board

All current progress and planned tasks are tracked on the public GitHub project board

**[View Project Dashboard → daeun-ops / Hybrid MLOps Project](https://github.com/users/daeun-ops/projects/4)**

The board records all small, granular tasks — reflecting day-to-day progress, experiments, and validation notes.


---

