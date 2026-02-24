# AdventureWorks Data Engineering Tutorial

End-to-End Local Data Engineering Pipeline: AdventureWorks OLTP → Lakehouse DWH

## Tech Stack

**Docker Compose · Meltano · Airflow · dbt · Spark · Apache Polaris · Iceberg · Superset · Jupyter**

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION                                │
│  Airflow (CeleryExecutor) + Redis + Airflow-Postgres                   │
│  [Webserver] [Scheduler] [Worker x2] [Flower]                          │
└───────────────────┬────────────────────────────────────────────────────┘
                    │ triggers
   ┌────────────────▼────────────────────────────────────────────────┐
   │  INGESTION          TRANSFORM              LAKEHOUSE            │
   │  Meltano         →  dbt (Postgres)    →  Spark + Iceberg        │
   │  tap-postgres       Bronze/Silver         Gold Layer            │
   │  target-postgres    (star schema)         Apache Polaris        │
   │                                           (REST catalog)        │
   └────────────────────────────────────────────────────────────────-┘
         ↑                                           ↓
  source-db (OLTP)                         warehouse-db (DWH)
  AdventureWorks                           Postgres + Iceberg
         ↓                                           ↓
   ┌─────────────────────────────────────────────────┐
   │           ANALYSIS LAYER                        │
   │   Superset (Dashboards)   Jupyter (Notebooks)   │
   └─────────────────────────────────────────────────┘
```

## Medallion Architecture

| Layer | Description | Schema | Format |
|-------|-------------|---------|--------|
| Bronze | Raw data from OLTP | raw_sales, raw_production, raw_person | CSV-like |
| Silver | Cleaned, standardized | staging | Views |
| Gold | Analytics-ready (Star Schema) | marts | Tables |

## Quick Start

```bash
# Clone and setup
git clone https://github.com/josecw/data-engineering-adventureworks-tutorial.git
cd data-engineering-adventureworks-tutorial

# Start all services
make up

# Wait for services to be ready (~2-3 minutes)
make logs

# Run full pipeline
# 1. Ingest data (Meltano)
make meltano-run

# 2. Transform data (dbt)
make dbt-run

# 3. Test data quality
make dbt-test

# 4. Publish to Iceberg (Spark)
make spark-submit-gold
```

## Access Services

| Service | URL | Credentials |
|----------|-----|-------------|
| Airflow | http://localhost:8080 | admin/admin |
| Airflow Flower | http://localhost:5555 | - |
| Superset | http://localhost:8088 | admin/admin |
| Jupyter | http://localhost:8888 | - |
| Polaris | http://localhost:8181 | adw_client/adw_secret_1234 |
| Spark UI | http://localhost:8090 | - |

## Project Structure

```
adventureworks-pipeline/
├── .env                          # Environment variables
├── docker-compose.yml              # Full stack services (15 containers)
├── Makefile                       # Convenience commands
├── README.md                      # This file
│
├── infra/
│   ├── polaris/
│   │   ├── polaris-bootstrap.sh    # Create catalog/namespace/roles
│   │   └── polaris-config.yml     # Polaris configuration
│   └── superset/
│       └── superset_config.py      # Superset configuration
│
├── meltano/
│   └── meltano.yml               # Meltano ELT configuration
│
├── dbt/
│   ├── dbt_project.yml            # dbt project config
│   ├── profiles.yml                # dbt connection profiles
│   ├── packages.yml               # dbt packages
│   ├── models/
│   │   ├── sources/                # Bronze layer declaration
│   │   │   └── schema.yml
│   │   ├── staging/                # Silver layer (cleaned views)
│   │   │   ├── schema.yml
│   │   │   ├── stg_sales__orders.sql
│   │   │   ├── stg_sales__order_detail.sql
│   │   │   ├── stg_person__customer.sql
│   │   │   └── stg_production__product.sql
│   │   └── marts/                  # Gold layer (Star Schema)
│   │       ├── schema.yml
│   │       ├── dim_customer.sql
│   │       ├── dim_product.sql
│   │       ├── dim_date.sql
│   │       ├── dim_territory.sql
│   │       └── fct_sales.sql
│   └── macros/
│       └── generate_surrogate_key.sql
│
├── spark/
│   ├── Dockerfile                  # Spark + Iceberg jars
│   ├── conf/
│   │   └── spark-defaults.conf    # Iceberg + Polaris config
│   └── jobs/
│       ├── publish_gold_to_iceberg.py
│       └── validate_iceberg_tables.py
│
├── airflow/
│   ├── Dockerfile                  # Airflow + Python dependencies
│   ├── requirements.txt
│   └── dags/
│       ├── adw_01_ingestion_dag.py    # Meltano EL
│       ├── adw_02_transform_dag.py    # dbt transformations
│       ├── adw_03_publish_dag.py      # Spark to Iceberg
│       └── adw_master_dag.py         # Orchestrate all
│
└── notebooks/
    └── 01_adventureworks_analysis.ipynb
```

## Tutorial Parts

### Part 0 — Environment Setup
- `.env` - All service credentials and configuration

### Part 1 — Docker Compose (Full Stack)
- 15 services in Docker Compose
- Airflow with CeleryExecutor
- Spark Master/Worker
- Apache Polaris catalog
- Superset BI
- Jupyter Notebook

### Part 2 — Airflow Dockerfile
- Base image: `apache/airflow:2.9.0`
- Includes: Java 17, meltano, dbt, Spark providers

### Part 3 — Meltano (Ingestion)
- `tap-postgres` - Extract from AdventureWorks OLTP
- `target-postgres` - Load to warehouse raw schemas
- Schemas: `raw_sales`, `raw_production`, `raw_person`, `raw_humanresources`

### Part 4 — dbt (Transformation)
**4.1 Project Config**
- `dbt_project.yml` - Project configuration
- `profiles.yml` - Connection to warehouse-db
- `packages.yml` - dbt_utils, dbt_date

**4.2 Sources (Bronze layer)**
- Declare raw schemas as dbt sources
- Add basic tests (unique, not_null)

**4.3 Staging Models (Silver layer)**
- Clean and rename columns
- Type casting and null handling
- Data quality tests

**4.4 Mart Models (Gold layer - Star Schema)**
- Dimensions: `dim_customer`, `dim_product`, `dim_date`, `dim_territory`
- Fact: `fct_sales` (join all dimensions)
- Surrogate keys using `dbt_utils.generate_surrogate_key`

### Part 5 — Spark + Polaris + Iceberg (Lakehouse)
**5.1 Spark Dockerfile**
- Base: `bitnami/spark:3.5`
- Includes: Iceberg runtime, PostgreSQL JDBC

**5.2 Polaris Bootstrap**
- Create catalog: `adw_catalog`
- Create namespace: `adw`
- Create principal: `adw_client`
- Grant catalog roles

**5.3 Spark Jobs**
- `publish_gold_to_iceberg.py` - Publish marts to Iceberg tables
- `validate_iceberg_tables.py` - Validate Iceberg tables

### Part 6 — Airflow DAGs (Full Orchestration)
- **adw_01_ingestion_dag**: Meltano EL (1 AM daily)
- **adw_02_transform_dag**: dbt transformations (3 AM daily)
- **adw_03_publish_dag**: Spark to Iceberg (5 AM daily)
- **adw_master_dag**: Orchestrate all DAGs with dependencies

## Data Flow

1. **Source DB** (AdventureWorks OLTP)
   - Tables: `sales.salesorderheader`, `sales.salesorderdetail`, `production.product`, `person.person`

2. **Meltano EL** (tap-postgres → target-postgres)
   - Loads to: `raw_sales`, `raw_production`, `raw_person`
   - Adds metadata: `_sdc_received_at`, `_sdc_sequence`

3. **dbt Transform** (staging → marts)
   - **Staging**: Clean views with renamed columns
   - **Marts**: Star schema with surrogate keys
   - **fct_sales**: Join order details + dimensions

4. **Spark Publish** (Postgres → Iceberg)
   - Read from: `marts.*` (Postgres)
   - Write to: `polaris.adw.*` (Iceberg)
   - Partition `fct_sales` by year + month

5. **Analysis Layer**
   - **Superset**: Connect to warehouse-db for BI dashboards
   - **Jupyter**: Connect to Iceberg via Spark for analysis

## Star Schema

**Dimensions:**
- `dim_customer`: Customer attributes + surrogate key
- `dim_product`: Product attributes + gross margin
- `dim_date`: Date spine (2011-2025)
- `dim_territory`: Sales territory attributes

**Fact:**
- `fct_sales`: One row per order line item
  - Foreign keys: `customer_key`, `product_key`, `territory_key`, `order_date_key`
  - Measures: `order_qty`, `unit_price`, `line_total`, `tax_amount`, `freight`

## Checkpoints

### Checkpoint 1: Ingestion Complete
```bash
make meltano-run
```
Verify tables in `warehouse` database:
- `raw_sales.salesorderheader`
- `raw_production.product`
- `raw_person.person`

### Checkpoint 2: Transformation Complete
```bash
make dbt-run && make dbt-test
```
Verify Star Schema in `warehouse.marts`:
- `dim_customer`, `dim_product`, `dim_date`, `dim_territory`
- `fct_sales`

### Checkpoint 3: Lakehouse Published
```bash
make spark-submit-gold
```
Verify Iceberg tables in Polaris catalog:
- `polaris.adw.fct_sales` (partitioned)
- `polaris.adw.dim_customer`
- `polaris.adw.dim_product`
- `polaris.adw.dim_territory`
- `polaris.adw.dim_date`

## Airflow Schedules

| DAG | Schedule | Description |
|-----|----------|-------------|
| adw_01_ingestion | 1 AM daily | Meltano EL |
| adw_02_transform | 3 AM daily | dbt transformations |
| adw_03_publish | 5 AM daily | Spark to Iceberg |

## Services & Ports

| Service | Port | Purpose |
|---------|------|---------|
| source-db | 5432 | AdventureWorks OLTP |
| warehouse-db | 5433 | Data Warehouse (Postgres) |
| airflow-db | 5432 | Airflow metadata |
| airflow-webserver | 8080 | Airflow UI |
| airflow-flower | 5555 | Celery monitor |
| polaris | 8181 | Iceberg REST catalog |
| spark-master | 7077, 8090 | Spark UI |
| superset | 8088 | BI dashboards |
| jupyter | 8888 | Notebook server |

## Learning Outcomes

By completing this tutorial, you will:
- ✅ Build end-to-end data pipeline locally
- ✅ Ingest data with Meltano (ELT)
- ✅ Transform data with dbt (Medallion architecture)
- ✅ Publish to Apache Iceberg with Spark
- ✅ Use Apache Polaris as REST catalog
- ✅ Orchestrate with Airflow (CeleryExecutor)
- ✅ Analyze with Superset + Jupyter

## Troubleshooting

**Services not starting:**
```bash
# Check logs
make logs

# Restart specific service
docker-compose restart <service-name>
```

**Meltano errors:**
```bash
# Reinstall Meltano plugins
docker-compose exec airflow-worker-1 bash -c "cd /opt/meltano && meltano install"
```

**dbt errors:**
```bash
# Test connection
docker-compose exec airflow-worker-1 bash -c "cd /opt/dbt && dbt debug --profiles-dir ."
```

**Spark errors:**
```bash
# Check Spark logs
docker-compose logs spark-master
docker-compose logs spark-worker
```

## Resources

- [AdventureWorks Database](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure)
- [Meltano Docs](https://docs.meltano.com/)
- [dbt Docs](https://docs.getdbt.com/)
- [Apache Airflow](https://airflow.apache.org/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [Apache Polaris](https://polaris.apache.org/)
- [Apache Superset](https://superset.apache.org/)

## License

MIT License - feel free to use for learning and educational purposes.

---

**Built with ❤️ for the data engineering community**
