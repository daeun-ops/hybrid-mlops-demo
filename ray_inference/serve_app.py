from ray import serve
from fastapi import FastAPI
import time

app = FastAPI()

@serve.deployment
@serve.ingress(app)
class InferenceService:
    def __init__(self):
        time.sleep(0.3)

    @app.post("/")
    def infer(self, payload: dict):
        time.sleep(0.5)
        return {"prediction": "vehicle", "confidence": 0.973}

if __name__ == "__main__":
    serve.start(http_options={"host": "127.0.0.1", "port": 8002})
    serve.run(InferenceService.bind(), route_prefix="/inference")
