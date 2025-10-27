from fastapi import FastAPI, Response
from ray import serve
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import torch, time

app = FastAPI()
serve.start(detached=True)

REQ_TOTAL = Counter("inference_requests_total", "Total inference requests")
REQ_LAT   = Histogram("inference_request_latency_seconds", "Inference latency (s)")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@serve.deployment(route_prefix="/inference")
@serve.ingress(app)
class InferenceService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Using device: {self.device}")
        self.model = torch.nn.Linear(4, 2).to(self.device)
        self.model.eval()

    @app.post("/")
    def infer(self, payload: dict):
        REQ_TOTAL.inc()
        start = time.time()
        x = payload.get("input", [1.0, 2.0, 3.0, 4.0])
        x = torch.tensor(x, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            y = self.model(x)
        REQ_LAT.observe(time.time() - start)
        return {"device": self.device, "output": y.tolist()}

# 간단 헬스체크
@app.get("/healthz")
def healthz():
    return {"ok": True}

InferenceService.deploy()

