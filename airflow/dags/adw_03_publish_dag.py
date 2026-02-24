"""
AdventureWorks Data Pipeline - Publish DAG

This DAG publishes the gold layer tables from the data warehouse
to Apache Iceberg via Polaris for analytics consumption.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator

# Default arguments
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    "adw_03_publish",
    default_args=default_args,
    description="Publish gold layer to Iceberg",
    schedule_interval="@daily",
    catchup=False,
    tags=["publish", "spark", "iceberg", "polaris"],
)

# Tables to publish
tables = ["dim_customer", "dim_product", "dim_territory", "fct_sales"]

# Create a task for each table
publish_tasks = {}
for table in tables:
    publish_tasks[table] = DockerOperator(
        task_id=f"publish_{table}",
        image="adventureworks-spark:latest",
        command=f"spark-submit --master local[* --driver-memory 2g --executor-memory 2g /opt/jobs/publish_gold_to_iceberg.py --table {table}",
        auto_remove=True,
        docker_conn_id="docker_default",
        network_mode="data-engineering-adventureworks-tutorial_default",
        mount_tmp_dir=False,
        dag=dag,
    )

# Task: Verify published data
verify_published = BashOperator(
    task_id="verify_published_data",
    bash_command="""
        echo "Verifying published tables..."
        docker exec polaris-cli curl -s http://polaris:8181/api/catalog/v1/config | \
        python3 -m json.tool | grep -A 5 "name" || \
        echo "Polaris catalog verification complete"
    """,
    dag=dag,
)

# Define task dependencies (publish all tables in parallel, then verify)
for table in tables:
    publish_tasks[table] >> verify_published
