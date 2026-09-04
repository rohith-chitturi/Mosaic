
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
