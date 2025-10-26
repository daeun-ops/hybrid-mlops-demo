from fastapi import FastAPI
import time

app = FastAPI()

@app.post("/inference")
def infer(payload: dict):
    time.sleep(0.2)
    return {"prediction": "vehicle", "confidence": 0.973}
