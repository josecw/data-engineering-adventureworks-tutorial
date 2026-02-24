# AdventureWorks Data Engineering Tutorial

A comprehensive data engineering tutorial using the AdventureWorks OLTP database. This project demonstrates building a modern data lakehouse architecture with PostgreSQL, Apache Iceberg, dbt, Apache Spark, Airflow, and Superset.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Source System                              │
│                    AdventureWorks OLTP (PostgreSQL)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Meltano (tap-postgres → target-postgres)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Warehouse Layer                              │
│                         PostgreSQL                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Raw Layer       │ Staging Layer   │ Marts Layer             │   │
│  │ - raw_sales     │ staging.*       │ marts.*                 │   │
│  │ - raw_product   │                 │ - dim_customer          │   │
│  │ - raw_person    │                 │ - dim_product           │   │
│  │                 │                 │ - dim_territory         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                         ↑              ↑                             │
│                      dbt transforms  dbt tests                      │
└──────────────────────────┴──────────────┴───────────────────────────┘
                               │
                               │ Spark publish
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Data Lakehouse Layer                             │
│                    Apache Iceberg (via Polaris)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Gold Layer                                                   │   │
│  │ - gold.dim_customer                                          │   │
│  │ - gold.dim_product                                           │   │
│  │ - gold.dim_territory                                         │   │
│  │ - gold.fct_sales                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Query via Trino/Presto
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Analytics Layer                                  │
│                          Apache Superset                              │
│                       (Dashboards & BI)                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
data-engineering-adventureworks-tutorial/
├── airflow/
│   ├── Dockerfile                      # Airflow image
│   └── dags/
│       ├── adw_01_ingestion_dag.py     # Meltano EL pipeline
│       ├── adw_02_transform_dag.py      # dbt transform pipeline
│       └── adw_03_publish_dag.py        # Spark publish to Iceberg
│
├── dbt/
│   ├── dbt_project.yml                 # dbt project configuration
│   ├── profiles.yml                     # dbt database profiles
│   ├── packages.yml                     # dbt packages (dbt_utils, dbt_date)
│   ├── macros/
│   │   └── generate_surrogate_key.sql  # Surrogate key generation macro
│   └── models/
│       ├── sources/
│       │   └── schema.yml              # Source definitions
│       ├── staging/
│       │   ├── stg_sales__order_detail.sql
│       │   ├── stg_person__customer.sql
│       │   ├── stg_production__product.sql
│       │   └── schema.yml
│       └── marts/
│           ├── dim_customer.sql
│           ├── dim_product.sql
│           ├── dim_date.sql
│           ├── dim_territory.sql
│           ├── fct_sales.sql
│           └── schema.yml
│
├── infra/
│   ├── polaris/
│   │   ├── polaris-config.yml          # Polaris catalog configuration
│   │   └── polaris-bootstrap.sh        # Bootstrap script
│   └── superset/
│       └── superset_config.py         # Superset configuration
│
├── meltano/
│   └── meltano.yml                     # Meltano EL configuration
│
├── spark/
│   ├── Dockerfile                      # Spark with Iceberg support
│   ├── conf/
│   │   └── spark-defaults.conf         # Spark + Iceberg config
│   └── jobs/
│       └── publish_gold_to_iceberg.py  # Publish job
│
├── docker-compose.yml                  # Orchestrates all services
├── Makefile                           # Convenience commands
└── .env                               # Environment variables
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available for Docker
- (Optional) Git for version control

### 1. Clone and Setup

```bash
# Navigate to project directory
cd /home/kasm-user/projects/data-engineering-adventureworks-tutorial

# Copy environment file (edit as needed)
cp .env.example .env

# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Initialize the Data Pipeline

```bash
# Wait for services to be ready (30-60 seconds)

# Run Meltano EL to extract data from source
make ingest

# Run dbt transformations
make transform

# Publish to Iceberg
make publish
```

### 3. Verify Data

```bash
# Check raw schemas in warehouse
make verify-raw

# Check marts tables
make verify-marts

# Check Iceberg tables
make verify-iceberg
```

### 4. Access Services

- **Airflow**: http://localhost:8080 (admin/admin)
- **Superset**: http://localhost:8088 (admin/admin)
- **Polaris API**: http://localhost:8181/api/catalog
- **Grafana** (if enabled): http://localhost:3000

## Pipeline Orchestration

The data pipeline consists of three Airflow DAGs:

### DAG 1: adw_01_ingestion

- **Purpose**: Extract data from AdventureWorks OLTP and load into raw schemas
- **Tool**: Meltano (tap-postgres → target-postgres)
- **Frequency**: Daily
- **Schemas Created**:
  - `raw_sales.*` - Sales tables
  - `raw_production.*` - Product tables
  - `raw_person.*` - Person tables
  - `raw_humanresources.*` - HR tables

### DAG 2: adw_02_transform

- **Purpose**: Transform raw data into staging and marts layers
- **Tool**: dbt
- **Frequency**: Daily (after ingestion)
- **Layers Created**:
  - `staging.*` - Cleaned, renamed source tables
  - `marts.*` - Dimension and fact tables

### DAG 3: adw_03_publish

- **Purpose**: Publish gold layer to Iceberg via Polaris
- **Tool**: Apache Spark
- **Frequency**: Daily (after transform)
- **Tables Published**:
  - `gold.dim_customer`
  - `gold.dim_product`
  - `gold.dim_territory`
  - `gold.fct_sales`

## Data Models

### Staging Layer

| Table | Description | Source |
|-------|-------------|--------|
| `stg_sales__orders` | Sales order headers | `raw_sales.salesorderheader` |
| `stg_sales__order_detail` | Sales order line items | `raw_sales.salesorderdetail` |
| `stg_person__customer` | Customer + Person join | `raw_sales.customer` + `raw_person.person` |
| `stg_production__product` | Product + Category hierarchy | `raw_production.product` + subcategory + category |

### Marts Layer

| Table | Type | Description | Grain |
|-------|------|-------------|-------|
| `dim_customer` | Dimension | Customer master data | One row per customer |
| `dim_product` | Dimension | Product master data | One row per product |
| `dim_date` | Dimension | Date dimension (generated) | One row per day |
| `dim_territory` | Dimension | Sales territory | One row per territory |
| `fct_sales` | Fact | Sales transactions | One row per order line item |

## Key Technologies

- **Meltano**: EL (Extract-Load) framework for data ingestion
- **dbt**: Data transformation tool for SQL-based modeling
- **Apache Spark**: Distributed data processing
- **Apache Iceberg**: Table format for data lakes
- **Polaris**: Iceberg catalog service
- **Airflow**: Workflow orchestration
- **Superset**: Business intelligence and visualization
- **PostgreSQL**: Source OLTP and warehouse database
- **Docker Compose**: Container orchestration

## Development Workflow

### Add a New Source Table

1. Add source definition in `dbt/models/sources/schema.yml`
2. Create staging model in `dbt/models/staging/`
3. Add tests in `dbt/models/staging/schema.yml`
4. Run `make transform` to verify

### Add a New Dimension or Fact Table

1. Create model in `dbt/models/marts/`
2. Add tests in `dbt/models/marts/schema.yml`
3. Add to publish job in `spark/jobs/publish_gold_to_iceberg.py`
4. Run `make transform && make publish`

### Debug Pipeline Issues

```bash
# Check Airflow logs
docker-compose logs airflow-scheduler | grep -i error

# Check dbt logs
make dbt-debug

# Check Spark job logs
docker-compose logs spark

# Inspect data in warehouse
docker exec -it warehouse-db psql -U dwh_user -d warehouse
```

## Testing

### dbt Tests

```bash
# Run all tests
make test

# Run specific test
cd dbt && dbt test --models dim_customer

# Run data freshness tests
cd dbt && dbt source snapshot-freshness
```

### Data Quality Checks

The project includes the following tests:
- **Uniqueness**: Primary keys across all dimensions
- **Not Null**: Critical fields (order dates, customer IDs, etc.)
- **Referential Integrity**: Foreign key relationships in fact table

## Scaling Considerations

### For Large Datasets

1. **Increase Spark resources**: Update `spark-defaults.conf`
2. **Partitioning**: Add partitioning strategy to Iceberg tables
3. **Incremental loads**: Implement CDC in Meltano instead of full loads
4. **Query optimization**: Add materialized views in warehouse

### Production Deployment

1. Move services to Kubernetes (e.g., using Helm charts)
2. Use managed services (AWS MSK, AWS Glue, Airflow on MWAA)
3. Add monitoring (Prometheus, Grafana)
4. Implement backup and disaster recovery
5. Add authentication and authorization (OIDC, LDAP)

## Troubleshooting

### Common Issues

**Issue**: Meltano fails to connect to source database
- **Solution**: Check `.env` variables for source-db credentials

**Issue**: dbt runs but tests fail
- **Solution**: Verify data in raw schemas: `make verify-raw`

**Issue**: Spark job fails with OutOfMemoryError
- **Solution**: Increase memory in `spark-defaults.conf`

**Issue**: Polaris catalog not accessible
- **Solution**: Check if Polaris container is running: `docker-compose ps polaris`

## Useful Commands

```bash
# Using Makefile
make up              # Start all services
make down            # Stop all services
make logs            # View all logs
make ingest         # Run Meltano EL
make transform       # Run dbt transformations
make publish         # Publish to Iceberg
make test            # Run dbt tests
make clean           # Remove containers and volumes
make rebuild         # Rebuild all images

# Docker Compose direct
docker-compose ps
docker-compose logs -f airflow
docker-compose exec warehouse-db psql -U dwh_user -d warehouse
docker-compose exec airflow airflow dags list
```

## Learning Path

This tutorial covers:

1. **Ingestion**: Extracting data from OLTP using Meltano
2. **Transformation**: Building data models with dbt
3. **Storage**: Managing a data warehouse with PostgreSQL
4. **Data Lake**: Publishing to Iceberg with Spark
5. **Orchestration**: Coordinating pipelines with Airflow
6. **Analytics**: Visualizing data with Superset

## Resources

- [Meltano Documentation](https://docs.meltano.com/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Superset Documentation](https://superset.apache.org/docs/)
- [AdventureWorks Sample Database](https://docs.microsoft.com/en-us/sql/samples/adventureworks-install-configure)

## Contributing

This is a learning project. Feel free to:
- Fork and experiment
- Submit issues or pull requests
- Share your learnings

## License

MIT License - See LICENSE file for details

---

**Happy Data Engineering! 🚀**
