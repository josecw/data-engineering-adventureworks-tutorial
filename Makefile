up:
	docker-compose up -d --build

down:
	docker-compose down -v

logs:
	docker-compose logs -f

meltano-run:
	docker-compose exec airflow-worker-1 \
	  bash -c "cd /opt/meltano && meltano run tap-postgres target-postgres"

dbt-run:
	docker-compose exec airflow-worker-1 \
	  bash -c "cd /opt/dbt && dbt run --profiles-dir ."

dbt-test:
	docker-compose exec airflow-worker-1 \
	  bash -c "cd /opt/dbt && dbt test --profiles-dir ."

spark-submit-gold:
	docker-compose exec spark-master \
	  /opt/bitnami/spark/bin/spark-submit \
	  --master spark://spark-master:7077 \
	  /opt/spark-jobs/publish_gold_to_iceberg.py
