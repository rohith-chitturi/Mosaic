# Spark Optimization Strategy

Spark is leveraged strictly for heavy cross-dataset comparisons. Airflow is intentionally omitted; Kafka serves as the job dispatcher.

## Optimization Principles

1. **Partition-aware processing:** Align workloads with existing storage partitions.
2. **Predicate pushdown:** Filter at the storage layer.
3. **Column pruning:** Load only the columns being compared.
4. **Broadcast joins:** Used exclusively for genuinely small candidate sets joined against massive tables.
5. **Shuffle minimization:** Group transformations to avoid wide network shuffles.
6. **Skew detection:** Salt keys or handle skew logically when comparing non-uniform cardinality datasets.
7. **Adaptive Query Execution (AQE):** Enabled by default to dynamically optimize shuffle partitions and join strategies.
8. **Cache only when reused:** Avoid aggressive caching. Memory is only allocated if iterative algorithms reuse the dataset heavily.
9. **Incremental profiling:** Use temporal high-water marks.
10. **Avoid full dataset scans:** Pre-computed statistical fingerprints are used whenever sufficient.
