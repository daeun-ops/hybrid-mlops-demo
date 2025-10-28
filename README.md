## Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS%20EKS-FF9900?logo=amazon-aws&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white" />
  <img src="https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Ray-028CF0?logo=ray&logoColor=white" />
  <img src="https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apache-airflow&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=github-actions&logoColor=white" />
</p>




## Workflow

We build everything in feature branches and merge into `dev` through Pull Requests.  
`main` only contains stable code.

Each change has
- an Issue (what we want),
- a branch (where we build it),
- a PR (how it lands in `dev`).

Milestones group related Issues (example: `Inference Observability v0.1`).


## Current Flow

- MLflow: `./mlflow/run_mlflow.sh` → http://localhost:5000  
- Airflow: `docker compose up -d` in `airflow/` → http://localhost:8080  
- DAG `hybrid_train_and_infer`
  - trains,
  - logs to MLflow,
  - calls the inference service on port 8000.


## Upcoming Work

- `feature/metrics-exporter`  
  Expose GPU memory / utilization at `/metrics` using `pynvml`.

- `feat/prom-stack-minimal`  
  `observability/docker-compose.yml` with Prometheus + Grafana scraping `ray-inference:8000`.

- `feat/airflow-hardening`  
  Airflow retries, timeouts, logging, and webhook alert on failure.

- `chore/ci-docker-build`  
  GitHub Actions builds the Docker image on every PR and tags it `dev-<sha>`.

  
## Reference

For background and notes on Airflow + ML pipeline flow, seE
https://danykde0til.tistory.com/182
