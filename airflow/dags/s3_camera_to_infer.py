from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

RAY_ENDPOINT = "http://ray-inference:8000/inference/"

with DAG(
    dag_id="s3_camera_to_infer",
    start_date=datetime(2025, 10, 31),
    schedule_interval="@once",
    catchup=False,
    default_args={"owner": "sophie"},
) as dag:

    wait_image = S3KeySensor(
        task_id="wait_image",
        bucket_name="camera",
        bucket_key="latest.jpg",
        aws_conn_id="minio_s3",
        poke_interval=5,
        timeout=60*10,
        soft_fail=False,
    )

    call_infer = BashOperator(
        task_id="call_infer",
        bash_command=(
            "curl -s -X POST {{ params.endpoint }} "
            "-H 'Content-Type: application/json' "
            "--data '{\"input\":[10,20,30,40]}'"
        ),
        params={"endpoint": RAY_ENDPOINT}
    )

    wait_image >> call_infer
