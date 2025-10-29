# ray_inference/Dockerfile
FROM nvidia/cuda:11.6.2-base-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAY_memory_monitor_refresh_ms=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-distutils curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

# PyTorch(CUDA 11.6)
RUN pip install --no-cache-dir \
    torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 \
    --extra-index-url https://download.pytorch.org/whl/cu116

# ✅ Ray Serve와 호환되는 FastAPI/uvicorn 버전 고정
RUN pip install --no-cache-dir \
    "ray[serve]==2.9.3" \
    fastapi==0.108.0 \
    uvicorn==0.23.2

WORKDIR /app
COPY serve_app.py /app/serve_app.py

EXPOSE 8000
CMD ["python3", "serve_app.py"]

