
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
