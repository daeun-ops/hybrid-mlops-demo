from datetime import datetime
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.bash import BashOperator

BUCKET = "camera"
KEY = "latest.jpg"
AWS_CONN_ID = "minio_s3"
RAY_ENDPOINT = "http://ray-inference:8000/inference/"

with DAG(
    dag_id="s3_camera_to_infer",
    start_date=datetime(2025, 10, 31),
    schedule_interval="@once",
    catchup=False,
    default_args={"owner": "sophie"},
    tags=["s3", "minio", "ray"],
) as dag:

    wait_s3 = S3KeySensor(
        task_id="wait_s3_latest_jpg",
        bucket_key=KEY,
        bucket_name=BUCKET,
        aws_conn_id=AWS_CONN_ID,
        poke_interval=5,
        timeout=600,
        mode="poke",
    )

    call_infer = BashOperator(
        task_id="call_ray_infer",
        bash_command=(
            "curl -s -X POST {{ params.endpoint }} "
            "-H 'Content-Type: application/json' "
            "--data '{\"input\":[10,20,30,40]}'"
        ),
        params={"endpoint": RAY_ENDPOINT},
    )

    wait_s3 >> call_infer
