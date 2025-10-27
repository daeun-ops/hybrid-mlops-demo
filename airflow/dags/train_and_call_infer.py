from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import random, time

MLFLOW_URI = "http://host.docker.internal:5000"
INFER_URL  = "http://host.docker.internal:8001/inference"  # 8001로 통일

def train():
    import mlflow  # 지연 import: 파싱 시점 에러 방지
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("hybrid-demo")
    acc = round(0.90 + random.random()*0.05, 4)
    with mlflow.start_run(run_name="mock-train"):
        mlflow.log_param("epochs", 3)
        mlflow.log_metric("accuracy", acc)
        mlflow.set_tag("phase", "onprem-build")
        time.sleep(1)

def call_infer():
    import requests  # 지연 import
    payload = {"input":[10,20,30,40]}
    r = requests.post(INFER_URL, json=payload, timeout=10)
    r.raise_for_status()
    print("inference:", r.json())

with DAG(
    dag_id="hybrid_train_and_infer",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["hybrid","demo"]
) as dag:
    t1 = PythonOperator(task_id="train_onprem", python_callable=train)
    t2 = PythonOperator(task_id="cloud_infer", python_callable=call_infer)
    t1 >> t2
