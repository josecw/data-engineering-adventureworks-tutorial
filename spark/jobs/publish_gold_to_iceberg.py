#!/usr/bin/env python3
"""
Publish gold layer data to Apache Iceberg via Polaris catalog.

This job reads transformed data from the warehouse and writes it
to Iceberg tables for analytics consumption.
"""

import sys
import argparse
from pyspark.sql import SparkSession


def main():
    parser = argparse.ArgumentParser(
        description="Publish gold layer data to Iceberg"
    )
    parser.add_argument(
        "--table",
        type=str,
        required=True,
        choices=["dim_customer", "dim_product", "dim_territory", "fct_sales"],
        help="Table to publish"
    )
    parser.add_argument(
        "--warehouse-url",
        type=str,
        default="jdbc:postgresql://warehouse-db:5432/warehouse",
        help="Warehouse database URL"
    )
    parser.add_argument(
        "--warehouse-user",
        type=str,
        default="dwh_user",
        help="Warehouse database user"
    )
    parser.add_argument(
        "--warehouse-password",
        type=str,
        default="dwh_password",
        help="Warehouse database password"
    )
    args = parser.parse_args()

    # Initialize Spark session with Iceberg support
    spark = (SparkSession.builder
        .appName(f"Publish_{args.table}_to_Iceberg")
        .config("spark.jars", "/opt/spark/jars/postgresql-42.7.2.jar")
        .getOrCreate())

    try:
        # Read from warehouse
        jdbc_props = {
            "user": args.warehouse_user,
            "password": args.warehouse_password,
            "driver": "org.postgresql.Driver"
        }

        print(f"Reading {args.table} from warehouse...")
        df = spark.read.jdbc(
            url=args.warehouse_url,
            table=f"marts.{args.table}",
            properties=jdbc_props
        )

        # Write to Iceberg
        iceberg_table = f"polaris.gold.{args.table}"
        print(f"Writing to {iceberg_table}...")

        df.writeTo(iceberg_table).using("iceberg").createOrReplace()

        print(f"Successfully published {args.table} to Iceberg!")

        # Show statistics
        print(f"\nTable statistics:")
        df.printSchema()
        print(f"Total rows: {df.count()}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
