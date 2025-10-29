# ray_inference/Dockerfile
FROM nvidia/cuda:11.6.2-base-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# base deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-distutils curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

# ✅ PyTorch CUDA 11.6 (공식 권장 방식)
RUN pip install --no-cache-dir \
    torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 \
    --extra-index-url https://download.pytorch.org/whl/cu116

# app deps
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn==0.30.6 \
    prometheus_client==0.20.0

WORKDIR /app
COPY serve_app.py /app/serve_app.py

EXPOSE 8000
# ✅ Ray 없이 Uvicorn으로 먼저 안정 구동
CMD ["uvicorn", "serve_app:app", "--host", "0.0.0.0", "--port", "8000"]
