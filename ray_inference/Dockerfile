FROM nvidia/cuda:11.6.2-base-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ca-certificates curl && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    pip3 install --no-cache-dir --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir "ray[serve]==2.9.3" fastapi uvicorn prometheus-client \
 && pip3 install --no-cache-dir torch==1.13.1+cu116 -f https://download.pytorch.org/whl/torch_stable.html

WORKDIR /app
COPY serve_app.py /app/serve_app.py

EXPOSE 8000
CMD ["python", "serve_app.py"]

