from fastapi import FastAPI, Body
from fastapi.responses import PlainTextResponse
import torch, time
from ray import serve

app = FastAPI(title="Hybrid Ray Inference")

@serve.deployment(ray_actor_options={"num_gpus": 1})
@serve.ingress(app)
class InferenceService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.total_requests = 0
        self.total_latency = 0.0

    @app.get("/healthz")
    async def healthz(self):
        return {"ok": True, "device": self.device}

    @app.post("/")
    async def infer(self, payload: dict = Body(...)):
        start = time.time()
        xs = payload.get("input", [])
        if not isinstance(xs, list):
            return {"error": "input must be a list"}
        try:
            out = [float(x) * 2 for x in xs]
        except Exception:
            return {"error": "input must be a list of numbers"}
        latency = time.time() - start
        self.total_requests += 1
        self.total_latency += latency
        return {"device": self.device, "output": out, "latency_sec": round(latency, 6)}

    @app.get("/metrics")
    async def metrics(self):
        avg_latency = (self.total_latency / self.total_requests) if self.total_requests else 0.0
        metrics_text = (
            "# HELP inference_requests_total Total inference requests\n"
            "# TYPE inference_requests_total counter\n"
            f"inference_requests_total{{service=\"ray-inference\"}} {self.total_requests}\n"
            "# HELP inference_avg_latency_seconds Average inference latency\n"
            "# TYPE inference_avg_latency_seconds gauge\n"
            f"inference_avg_latency_seconds{{service=\"ray-inference\"}} {avg_latency:.6f}\n"
        )
        return PlainTextResponse(metrics_text)

serve.start(http_options={"host": "0.0.0.0", "port": 8000})
serve.run(InferenceService.bind(), route_prefix="/inference")

print("[serve_app] Ray Serve app (with metrics) is running…")
while True:
    time.sleep(3600)
