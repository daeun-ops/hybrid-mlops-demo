from fastapi import FastAPI, Body
from fastapi.responses import PlainTextResponse
import torch
import time

from ray import serve

api = FastAPI(title="Hybrid Ray Inference")

@serve.deployment
@serve.ingress(api)
class InferenceService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @api.get("/healthz")
    async def healthz(self):
        return {"ok": True, "device": self.device}

    @api.post("/")
    async def infer(self, payload: dict = Body(...)):
        xs = payload.get("input", [])
        if not isinstance(xs, list):
            return {"error": "input must be a list"}
        try:
            out = [float(x) * 2 for x in xs]
        except Exception:
            return {"error": "input must be a list of numbers"}
        return {"device": self.device, "output": out}

    @api.get("/metrics")
    async def metrics(self):
        return PlainTextResponse(
            "# HELP inference_requests_total Total inference requests\n"
            "# TYPE inference_requests_total counter\n"
            "inference_requests_total{service=\"ray-inference\"} 0\n"
        )

# 신규 Serve API
app = InferenceService.bind()
serve.run(app, route_prefix="/inference")

# ✅ 컨테이너 프로세스 유지 (중요!)
print("[serve_app] Ray Serve app is up. Sleeping forever to keep process alive...")
while True:
    time.sleep(3600)

