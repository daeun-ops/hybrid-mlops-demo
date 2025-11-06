# Changelog

All major updates and architectural changes are summarized below.

---

## [v2.0.0] – November 2025
### Shift to Hybrid-Ready Architecture
- Reorganized local Compose setup into hybrid-capable structure.
- Added Airflow → Ray Serve orchestration with MinIO as bridge storage.
- Introduced Prometheus + Grafana integration.
- Added CPU fallback mode when GPU is unavailable.
- Implemented `.env` / `.env.example` and pre-commit secret guard.

---

## [v1.2.0] – October 2025
### Observability Added
- Exposed Ray Serve `/metrics` endpoint.
- Added Prometheus and Grafana configuration for basic metric collection.
- Included request count, latency, and error panels.

---

## [v1.1.0] – September 2025
### Airflow Integration
- Added `s3_camera_to_infer.py` DAG (image detection → inference trigger).
- Integrated Airflow Compose setup for local testing.
- Configured MinIO and health checks.

---

## [v1.0.0] – August 2025
### Initial Local Demo
- Basic Ray Serve inference with FastAPI.
- Manual testing through curl.
- No orchestration or metrics layer yet.
