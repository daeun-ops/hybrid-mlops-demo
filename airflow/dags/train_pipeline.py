from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow, os, time, random

def train_model():
    mlflow.set_tracking_uri("http://host.docker.internal:5000")
    mlflow.set_experiment("hybrid-demo")
    with mlflow.start_run(run_name="mock-train"):
        time.sleep(1)
        acc = round(0.90 + random.random()*0.05, 4)
        mlflow.log_param("epochs", 3)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_artifact(__file__)

with DAG(
    "train_pipeline",
    start_date=datetime(2025,1,1),
    schedule_interval=None,
    catchup=False,
    tags=["demo","mlflow"],
) as dag:
    PythonOperator(task_id="train", python_callable=train_model)
