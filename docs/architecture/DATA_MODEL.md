# Data Model (PostgreSQL)

The primary data store for the Lineage Graph is PostgreSQL.

The graph is modeled as a **directed lineage graph with cycle detection**. It explicitly supports cycles (unlike a strict DAG) because enterprise data architectures frequently involve recursive data flows.

## Core Tables

- `dataset_versions`
- `column_versions`
- `observations`
- `candidate_relationships`
- `inference_runs`
- `inferences`
- `evidence`
- `lineage_assertions` (The Graph Edges)
- `human_audit_events` (INFERENCE_CONFIRMED_BY_ENGINEER, etc.)
