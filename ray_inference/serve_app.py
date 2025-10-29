from fastapi import FastAPI, Body
from fastapi.responses import PlainTextResponse
import torch
import time

from ray import serve

api = FastAPI(title="Hybrid Ray Inference")

@serve.deployment(ray_actor_options={"num_gpus": 1})(ray_actor_options={"num_gpus": 1})
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

if __name__ == "__main__":
    # ✅ HTTP 서버는 여기서 '딱 한 번' 명시적으로 시작
    serve.start(http_options={"host": "0.0.0.0", "port": 8000})
    # ✅ 애플리케이션은 host/port 없이 run
    app = InferenceService.bind()
    serve.run(app, route_prefix="/inference")

    print("[serve_app] Ray Serve up on 0.0.0.0:8000 /inference — holding process…")
    while True:
        time.sleep(3600)
