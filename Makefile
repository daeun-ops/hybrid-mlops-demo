# Makefile
# -------------------------------

SHELL := /bin/bash
ENV_FILE := .env

include $(ENV_FILE)

.PHONY: e2e-local obs-up clean

e2e-local:
	@echo "Running local MLOps pipeline..."
	docker compose up -d airflow redis postgres ray-inference minio
	@echo " Waiting for health checks..."
	sleep 15
	curl -X GET http://localhost:8000/ || echo "Ray inference starting..."
	@echo " Local MLOps pipeline started successfully!"

obs-up:
	@echo "🔭 Starting Observability stack..."
	docker compose up -d prometheus grafana
	sleep 10
	@echo " Prometheus (9090) and Grafana (3000) ready."

clean:
	docker compose down -v
	rm -rf airflow/logs logs
