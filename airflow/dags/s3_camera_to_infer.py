# airflow/dags/s3_camera_to_infer.py
# -------------------------------
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.http_operator import SimpleHttpOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "sophie",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "s3_camera_to_infer",
    default_args=default_args,
    start_date=datetime(2025, 11, 1),
    schedule_interval="@once",
    catchup=False,
    description="Detect new image in MinIO and trigger Ray Serve inference",
) as dag:

    wait_for_image = S3KeySensor(
        task_id="wait_s3_latest_jpg",
        bucket_key="camera/*.jpg",
        bucket_name="camera",
        aws_conn_id="minio_s3",
        poke_interval=30,
    )

    trigger_inference = SimpleHttpOperator(
        task_id="call_ray_infer",
        http_conn_id="ray_inference",
        endpoint="/inference",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"trigger": "s3_camera_event"}',
    )

    wait_for_image >> trigger_inference
