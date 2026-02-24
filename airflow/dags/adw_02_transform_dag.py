"""
AdventureWorks Data Pipeline - Transform DAG

This DAG runs dbt transforms to create staging and marts layer
from the raw schemas in the data warehouse.
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
    "adw_02_transform",
    default_args=default_args,
    description="Transform raw data using dbt",
    schedule_interval="@daily",
    catchup=False,
    tags=["transform", "dbt", "adventureworks"],
)

# Task 1: dbt deps (install packages)
dbt_deps = DockerOperator(
    task_id="dbt_deps",
    image="ghcr.io/dbt-labs/dbt-postgres:latest",
    command="dbt deps",
    auto_remove=True,
    docker_conn_id="docker_default",
    network_mode="data-engineering-adventureworks-tutorial_default",
    mount_tmp_dir=False,
    working_dir="/usr/app",
    environment={
        "DBT_PROFILES_DIR": "/usr/app",
        "DBT_TARGET_PATH": "/usr/app/target",
    },
    volumes={
        "/home/kasm-user/projects/data-engineering-adventureworks-tutorial/dbt": {
            "bind": "/usr/app",
            "mode": "rw"
        }
    },
    dag=dag,
)

# Task 2: dbt run (execute models)
dbt_run = DockerOperator(
    task_id="dbt_run",
    image="ghcr.io/dbt-labs/dbt-postgres:latest",
    command="dbt run",
    auto_remove=True,
    docker_conn_id="docker_default",
    network_mode="data-engineering-adventureworks-tutorial_default",
    mount_tmp_dir=False,
    working_dir="/usr/app",
    environment={
        "DBT_PROFILES_DIR": "/usr/app",
        "DBT_TARGET_PATH": "/usr/app/target",
    },
    volumes={
        "/home/kasm-user/projects/data-engineering-adventureworks-tutorial/dbt": {
            "bind": "/usr/app",
            "mode": "rw"
        }
    },
    dag=dag,
)

# Task 3: dbt test (run data quality tests)
dbt_test = DockerOperator(
    task_id="dbt_test",
    image="ghcr.io/dbt-labs/dbt-postgres:latest",
    command="dbt test",
    auto_remove=True,
    docker_conn_id="docker_default",
    network_mode="data-engineering-adventureworks-tutorial_default",
    mount_tmp_dir=False,
    working_dir="/usr/app",
    environment={
        "DBT_PROFILES_DIR": "/usr/app",
        "DBT_TARGET_PATH": "/usr/app/target",
    },
    volumes={
        "/home/kasm-user/projects/data-engineering-adventureworks-tutorial/dbt": {
            "bind": "/usr/app",
            "mode": "rw"
        }
    },
    dag=dag,
)

# Define task dependencies
dbt_deps >> dbt_run >> dbt_test
