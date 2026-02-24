"""
AdventureWorks Data Pipeline - Ingestion DAG

This DAG runs Meltano EL to extract data from AdventureWorks OLTP
and load into the data warehouse raw schemas.
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
    "adw_01_ingestion",
    default_args=default_args,
    description="Extract and load AdventureWorks data using Meltano",
    schedule_interval="@daily",
    catchup=False,
    tags=["ingestion", "meltano", "adventureworks"],
)

# Task 1: Run Meltano EL
run_meltano_el = DockerOperator(
    task_id="run_meltano_el",
    image="meltano/meltano:latest",
    command="meltano el tap-postgres target-postgres",
    auto_remove=True,
    docker_conn_id="docker_default",
    network_mode="data-engineering-adventureworks-tutorial_default",
    mount_tmp_dir=False,
    environment={
        "MELTANO_DATABASE_HOST": "source-db",
        "MELTANO_DATABASE_PORT": "5432",
        "MELTANO_DATABASE_USER": "postgres",
        "MELTANO_DATABASE_PASSWORD": "password",
        "MELTANO_DATABASE_DBNAME": "Adventureworks",
    },
    dag=dag,
)

# Task 2: Verify data loaded
verify_data = BashOperator(
    task_id="verify_data_loaded",
    bash_command="""
        docker exec warehouse-db psql -U dwh_user -d warehouse -c "
            SELECT
                'raw_sales' as schema_name,
                COUNT(*) as table_count
            FROM information_schema.tables
            WHERE table_schema = 'raw_sales'
            UNION ALL
            SELECT 'raw_production', COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw_production'
            UNION ALL
            SELECT 'raw_person', COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw_person';
        "
    """,
    dag=dag,
)

# Define task dependencies
run_meltano_el >> verify_data
