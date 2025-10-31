.PHONY: up down health infer gpu logs restart clean ps

up:
	docker compose up -d --build ray-inference
	@echo "⏳ Waiting for health..."; \
	for i in {1..60}; do s=$$(docker inspect -f '{{.State.Health.Status}}' ray-inference 2>/dev/null || echo unknown); \
	  if [ "$$s" = "healthy" ]; then echo "✅ Container is healthy."; break; fi; sleep 2; done
	@$(MAKE) health
	@sleep 3
	@$(MAKE) infer

down:
	docker compose down --remove-orphans || true

health:
	@echo -n "Health: " && curl -sf http://127.0.0.1:8000/inference/healthz && echo || echo "❌ Health check failed"

infer:
	@echo -n "Infer : " && curl -sf -X POST http://127.0.0.1:8000/inference/ -H 'Content-Type: application/json' -d '{"input":[10,20,30,40]}' && echo || echo "❌ Inference failed"

gpu:
	@docker exec -i ray-inference python3 -c 'import torch,os;print("cuda_available:",torch.cuda.is_available());print("CUDA_VISIBLE_DEVICES:",os.environ.get("CUDA_VISIBLE_DEVICES"));print("device_name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")'
	@docker exec -it ray-inference bash -lc "ray status" || true

logs:
	docker logs -n 200 -f ray-inference

restart:
	docker compose restart ray-inference

clean:
	docker builder prune -f || true

ps:
	docker compose ps

.PHONY: obs-up obs-down obs-check obs-open

obs-up:
	@echo "🔭 Starting Prometheus + Grafana..."
	docker compose up -d prometheus grafana
	@echo "⏳ Waiting Prometheus..."
	@for i in $$(seq 1 40); do \
	  s=$$(docker inspect -f '{{.State.Health.Status}}' prometheus 2>/dev/null || echo unknown); \
	  if [ "$$s" = "healthy" ]; then echo "✅ Prometheus healthy"; break; fi; sleep 2; done
	@echo "⏳ Waiting Grafana..."
	@for i in $$(seq 1 60); do \
	  s=$$(docker inspect -f '{{.State.Health.Status}}' grafana 2>/dev/null || echo unknown); \
	  if [ "$$s" = "healthy" ]; then echo "✅ Grafana healthy"; break; fi; sleep 2; done

obs-check:
	@echo "🔎 Prometheus targets:" && \
	curl -s http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {scrapeUrl, health, lastScrape}' || true
	@echo "🔎 Sample metrics:" && curl -s http://127.0.0.1:9090/api/v1/query?query=inference_requests_total

obs-open:
	@echo "👉 Prometheus: http://localhost:9090"
	@echo "👉 Grafana   : http://localhost:3000 (admin/admin)"
	@echo "   Dashboard : Search for \"Ray Inference - Quick View\""

obs-down:
	docker compose rm -sfv prometheus grafana || true
