# KNOWN_ISSUES

None.

## Era 2022 Data Lake Format Limitation
The current development environment emits a JSON fallback representation for the 2022 partitioned dataset because valid Parquet generation is not yet available in this environment. Files ending in `.parquet.json` must not be interpreted as valid Apache Parquet files. Real Parquet output remains an open Phase 1 requirement.
