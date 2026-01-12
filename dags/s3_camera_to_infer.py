import json
import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

BUCKET = os.getenv("CAMERA_BUCKET", "camera")
KEY = os.getenv("CAMERA_KEY", "latest.jpg")
AWS_CONN_ID = os.getenv("MINIO_AWS_CONN_ID", "minio_s3")
RAY_ENDPOINT = os.getenv("RAY_INFERENCE_ENDPOINT", "http://ray-inference:8000/inference/")
S3_POKE_INTERVAL = int(os.getenv("S3_POKE_INTERVAL", "5"))
S3_TIMEOUT_SECONDS = int(os.getenv("S3_TIMEOUT_SECONDS", str(60 * 10)))
CURL_TIMEOUT_SECONDS = int(os.getenv("RAY_CURL_TIMEOUT_SECONDS", "30"))

OWNER = os.getenv("AIRFLOW_OWNER", "sophie")
RETRIES = int(os.getenv("AIRFLOW_RETRIES", "1"))
RETRY_DELAY_MINUTES = int(os.getenv("AIRFLOW_RETRY_DELAY_MINUTES", "1"))

PAYLOAD_JSON = json.dumps({"input": [10, 20, 30, 40]})

default_args = {
    "owner": OWNER,
    "retries": RETRIES,
    "retry_delay": timedelta(minutes=RETRY_DELAY_MINUTES),
}

with DAG(
    dag_id="s3_camera_to_infer",
    start_date=pendulum.datetime(2025, 10, 31, tz="UTC"),
    schedule="@once",
    catchup=False,
    default_args=default_args,
    tags=["s3", "minio", "ray"],
    max_active_runs=1,
) as dag:
    wait_s3 = S3KeySensor(
        task_id="wait_s3_latest_jpg",
        bucket_key=KEY,
        bucket_name=BUCKET,
        aws_conn_id=AWS_CONN_ID,
        poke_interval=S3_POKE_INTERVAL,
        timeout=S3_TIMEOUT_SECONDS,
        soft_fail=False,
        mode="reschedule",
    )

    call_infer = BashOperator(
        task_id="call_ray_infer",
        bash_command=(
            "set -euo pipefail\n"
            "curl -sS --fail --max-time {{ params.timeout }} "
            "-X POST \"{{ params.endpoint }}\" "
            "-H 'Content-Type: application/json' "
            "--data-raw '{{ params.payload }}'\n"
        ),
        params={
            "endpoint": RAY_ENDPOINT,
            "payload": PAYLOAD_JSON,
            "timeout": CURL_TIMEOUT_SECONDS,
        },
    )

    wait_s3 >> call_infer
