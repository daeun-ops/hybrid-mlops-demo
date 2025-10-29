# ray_inference/serve_app.py
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import torch, time

app = FastAPI(title="Hybrid MLOps Demo - Inference")

# Prometheus metrics
REQ_TOTAL = Counter("inference_requests_total", "Total inference requests")
REQ_LAT   = Histogram("inference_request_latency_seconds", "Inference latency (s)")
DEVICE_G  = Gauge("inference_device_is_cuda", "1=cuda, 0=cpu")

# --- model init ---
try:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception as e:
    print(f"[WARN] CUDA check failed: {e}; fallback=cpu")
    DEVICE = "cpu"

DEVICE_G.set(1 if DEVICE == "cuda" else 0)
print(f"[INFO] Using device: {DEVICE}")

MODEL = torch.nn.Linear(4, 2).to(DEVICE)
MODEL.eval()

# --- routes under /inference ---
@app.get("/inference/healthz")
def healthz():
    return {"ok": True}

@app.get("/inference/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/inference/")
def infer(payload: dict):
    REQ_TOTAL.inc()
    t0 = time.time()
    x = payload.get("input", [1.0, 2.0, 3.0, 4.0])
    x = torch.tensor(x, dtype=torch.float32, device=DEVICE)
    with torch.no_grad():
        y = MODEL(x)
    REQ_LAT.observe(time.time() - t0)
    return {"device": DEVICE, "output": y.tolist()}
