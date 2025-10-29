from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from ray import serve
import torch, time

serve.start(
    detached=True,
    http_options={"host": "0.0.0.0", "port": 8000},
    dedicated_cpu=False
)

@serve.deployment(
    route_prefix="/inference",
    ray_actor_options={"num_cpus": 0.25}
)
class InferenceService:
    def __init__(self):
        app = FastAPI()

        self.req_total = Counter("inference_requests_total", "Total inference requests")
        self.req_lat   = Histogram("inference_request_latency_seconds", "Inference latency (s)")
        self.device_g  = Gauge("inference_device_is_cuda", "1=cuda, 0=cpu")

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception as e:
            print(f"[WARN] CUDA check failed: {e}; fallback=cpu")
            self.device = "cpu"

        self.device_g.set(1 if self.device == "cuda" else 0)
        print(f"[INFO] Using device: {self.device}")

        self.model = torch.nn.Linear(4, 2).to(self.device)
        self.model.eval()

        @app.get("/healthz")
        def _healthz():
            return {"ok": True}

        @app.get("/metrics")
        def _metrics():
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

        @app.post("/")
        def _infer(payload: dict):
            self.req_total.inc()
            t0 = time.time()
            x = payload.get("input", [1.0, 2.0, 3.0, 4.0])
            x = torch.tensor(x, dtype=torch.float32, device=self.device)
            with torch.no_grad():
                y = self.model(x)
            self.req_lat.observe(time.time() - t0)
            return {"device": self.device, "output": y.tolist()}

        self._app = app

    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)

InferenceService.deploy()
