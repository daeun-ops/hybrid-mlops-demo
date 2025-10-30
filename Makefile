.PHONY: up down infer health gpu logs restart clean ps

up:
	docker compose up -d --build ray-inference
	@echo "⏳ Waiting for health..."; \
	for i in {1..45}; do s=$$(docker inspect -f '{{.State.Health.Status}}' ray-inference 2>/dev/null || echo unknown); \
	  if [ "$$s" = "healthy" ]; then echo "✅ Container is healthy."; break; fi; sleep 2; done
	@$(MAKE) infer

down:
	docker compose down --remove-orphans || true

health:
	@echo -n "Health: "; curl -s http://127.0.0.1:8000/inference/healthz; echo

infer:
	@echo -n "Infer : "; curl -s -X POST http://127.0.0.1:8000/inference/ \
	  -H 'Content-Type: application/json' -d '{"input":[10,20,30,40]}'; echo

gpu:
	@docker exec -i ray-inference python3 - <<'PY'
import torch, os
print("cuda_available:", torch.cuda.is_available())
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
if torch.cuda.is_available():
    print("device_name:", torch.cuda.get_device_name(0))
PY
	@docker exec -it ray-inference bash -lc "ray status" || true

logs:
	docker logs -n 200 -f ray-inference

restart:
	docker compose restart ray-inference

clean:
	docker builder prune -f || true

ps:
	docker compose ps
