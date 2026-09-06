import os

def generate_2022_spark_artifacts(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    script = """
# 2022 Spark Enrichment Pipeline
# Joins Postgres customers with Postgres orders to calculate transaction totals

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, col

spark = SparkSession.builder.appName("CustomerEnrichment").getOrCreate()

# Read postgres extracts
customers_df = spark.read.json("s3://meridian-lake/2018_postgres/customers.json")
orders_df = spark.read.json("s3://meridian-lake/2018_postgres/orders.json")

# Calculate transaction total
transaction_totals = orders_df.groupBy("customer_id").agg(
    _sum("amount").alias("customer_transaction_total")
)

# Join and enrich
enriched_df = customers_df.join(transaction_totals, "customer_id", "left")

# Write to Data Lake
enriched_df.write.partitionBy("year", "month").parquet("s3://meridian-lake/2022_lake/customer_features/")
"""
    with open(os.path.join(output_dir, "customer_enrichment.py"), "w", encoding='utf-8') as f:
        f.write(script)

def generate_2024_spark_artifacts(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    script = """
# 2024 Historical Backfill Script
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr

spark = SparkSession.builder.appName("HistoricalBackfill").getOrCreate()

events_df = spark.read.json("s3://meridian-kafka/2020_kafka/order_events_v2.json")

# Some undocumented timezone shifts were applied manually during this run
backfill_df = events_df.select(
    col("schema_version"),
    col("order_id"),
    col("customer_id"),
    col("amount").cast("int").alias("amount"), # Undocumented truncation
    col("currency"),
    col("event_timestamp") # Some rows had timezone shifts
)

backfill_df.write.parquet("s3://meridian-lake/2024_lake/backfills/historical_order_backfill/")
"""
    with open(os.path.join(output_dir, "historical_backfill_2024.py"), "w", encoding='utf-8') as f:
        f.write(script)
