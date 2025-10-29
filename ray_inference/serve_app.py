# ray_inference/serve_app.py
from fastapi import FastAPI
from ray import serve
import torch

# Ray HTTP 서버 명시적으로 시작 (단일 노드)
serve.start(
    detached=True,
    http_options={"host": "0.0.0.0", "port": 8000},
    dedicated_cpu=False,
)

@serve.deployment(
    ray_actor_options={"num_cpus": 0.25}  # 로컬/WSL 경량화
)
class InferenceService:
    def __init__(self):
        # 직렬화 안전: FastAPI를 인스턴스 내부에서 생성
        app = FastAPI(title="Hybrid MLOps Demo - Ray Serve")

        # GPU/CPU 자동감지
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            self.device = "cpu"

        # 간단한 데모 모델
        self.model = torch.nn.Linear(4, 2).to(self.device)
        self.model.eval()

        @app.get("/inference/healthz")
        def healthz():
            return {"ok": True, "device": self.device}

        @app.post("/inference/")
        def infer(payload: dict):
            x = payload.get("input", [1.0, 2.0, 3.0, 4.0])
            x = torch.tensor(x, dtype=torch.float32, device=self.device)
            with torch.no_grad():
                y = self.model(x)
            return {"device": self.device, "output": y.tolist()}

        self._app = app

    # Ray Serve가 호출할 ASGI 엔드포인트
    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)

# 배포
if __name__ == "__main__":  # 컨테이너 시작시 실행
    InferenceService.deploy()
else:
    InferenceService.deploy()
