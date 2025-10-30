.PHONY: up down infer health gpu logs restart clean ps

# 컨테이너 빌드+기동 → 헬스대기 → 샘플 추론까지 한 번에
up:
	docker compose up -d --build ray-inference
	@echo "⏳ Waiting for health..."; \
	for i in {1..45}; do s=$$(docker inspect -f '{{.State.Health.Status}}' ray-inference 2>/dev/null || echo unknown); \
	  if [ "$$s" = "healthy" ]; then echo "✅ Container is healthy."; break; fi; sleep 2; done
	@$(MAKE) infer

# 정지/정리
down:
	docker compose down --remove-orphans || true

# 헬스체크만
health:
	@echo -n "Health: "; curl -s http://127.0.0.1:8000/inference/healthz; echo

# 샘플 추론 호출
infer:
	@echo -n "Infer : "; curl -s -X POST http://127.0.0.1:8000/inference/ \
	  -H 'Content-Type: application/json' -d '{"input":[10,20,30,40]}'; echo

# GPU/리소스 상태 (컨테이너 내부)
gpu:
	@docker exec -i ray-inference python3 - <<'PY'
import torch, os
print("cuda_available:", torch.cuda.is_available())
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
if torch.cuda.is_available():
    print("device_name:", torch.cuda.get_device_name(0))
PY
	@docker exec -it ray-inference bash -lc "ray status" || true

# 로그 tail
logs:
	docker logs -n 200 -f ray-inference

# 빠른 재시작
restart:
	docker compose restart ray-inference

# 빌드 캐시/죽은 리소스 청소
clean:
	docker builder prune -f || true

# 상태
ps:
	docker compose ps
