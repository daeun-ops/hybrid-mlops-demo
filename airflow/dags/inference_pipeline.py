from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="inference_pipeline_stub",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["stub","inference"],
) as dag:
    ping = BashOperator(
        task_id="curl_infer",
        bash_command="bash scripts/curl_infer.sh",
        cwd="{{ var.value.get('repo_root', '.') }}"
    )
