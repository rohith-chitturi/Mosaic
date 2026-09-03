# MOSAIC

> MOSAIC is a historical data reconstruction engine that discovers undocumented relationships and evolution across enterprise datasets, schemas, SQL artifacts, Spark jobs, Kafka streams, and cloud storage.

MOSAIC is an enterprise-grade data archaeology and reconstruction platform. It reconstructs how an enterprise's data evolved by scanning legacy SQL scripts, tracking schema drift, parsing Spark jobs, tracking Kafka streaming artifacts, and piecing together a probabilistic lineage graph.

It answers complex questions about enterprise data history:
* Where did this dataset originate?
* Was this column renamed?
* What transformation produced it?
* Which historical dataset is the predecessor?
* Which pipeline created this table?
* Which systems consume this data?
* What downstream systems are affected by a change?
* What evidence proves a suspected lineage relationship?

## Core Product Concept

Organizations often evolve their data ecosystem over many years (e.g., MySQL → PostgreSQL → Kafka → Spark → object storage data lake). During these migrations, documentation is often lost, schemas drift, pipelines are rewritten, and artifacts are orphaned.

MOSAIC takes all artifacts and systems in an enterprise (PostgreSQL, MySQL, Parquet/JSON/CSV data, Spark code, Kafka topics, SQL artifacts) and builds a **Historical Data Reconstruction & Lineage Inference Engine**. 

MOSAIC operates probabilistically: the system does not take lineage as absolute truth unless directly observed and parsed (e.g. from a SQL query). Instead, it classifies lineage as `HYPOTHESIS`, `SUPPORTED`, `CONFIRMED`, or `REJECTED`, complete with confidence scores driven by overlapping values, structural schemas, statistical profiling, and temporal evidence.

## Key Features

### "Explain This Column"
The flagship feature of MOSAIC allows engineers to select any column, e.g., `customer.lifetime_value`, and MOSAIC reconstructs its complete history:
* Historical Origin and Evolution (e.g., `INTEGER` → `DECIMAL(12,2)`)
* Transformation lineage (e.g., `rolling_sum()`)
* Downstream Consumers (Kafka topics, ML feature tables)
* Confidence of the inference and statistical Evidence (e.g., "12.8M correlated records").

### Discovery & Profiling Engine
Scans and fingerprints data sources (PostgreSQL, MySQL, CSV, JSON, Parquet, Kafka topics) to calculate structural, statistical, and semantic metadata. Data profiles are stored as reusable fingerprints.

### Artifact Archaeology (SQL & Spark)
Parses SQL scripts and PySpark code structurally to extract read sources, transformations, aliases, aggregations, and target datasets, constructing observed relationships from actual data engineering code.

### Transformation & Rename Inference
Detects renamed columns, combined columns (e.g., `first_name + last_name -> full_name`), and structural transformations using lexical similarity, semantic compatibility, temporal proximity, and statistical distribution matching.

### Deterministic Confidence Engine
A deterministic scoring algorithm calculates confidence based on schema similarity, value overlap, artifact evidence, and temporal alignment. Every inference exposes its underlying evidence.

### Impact Analysis
Allows developers to query a column/table and instantly retrieve all downstream dependency chains across databases, object storage, ML features, and Kafka streams.

### Failure Laboratory
A controlled environment to inject real-world enterprise imperfections (duplicate records, missing partitions, partial migrations, schema type changes) and prove MOSAIC can detect and explain these scenarios.

## High-Level Architecture

```
                 MERIDIAN COMMERCE (Enterprise Data Ecosystem)
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
      PostgreSQL       MySQL        File Artifacts
          │              │          CSV/JSON/Parquet
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                DISCOVERY ENGINE
                         │
                         ▼
                PROFILING ENGINE
                         │
                         ▼
                  KAFKA EVENT BUS
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
    Schema Engine   Fingerprinting   Artifact Parser
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                 INFERENCE ENGINE
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Relationship   Transformation   Temporal
       Inference       Inference       Inference
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                   EVIDENCE ENGINE
                         │
                         ▼
                   LINEAGE GRAPH
                         │
                         ▼
                  PostgreSQL
                         │
                         ▼
                  FastAPI
                         │
                         ▼
                   Next.js UI
```

## Technology Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic, SQLAlchemy, Alembic, asyncio
- **Databases:** PostgreSQL (Lineage Metadata & Graph), MySQL
- **Data Processing:** Apache Spark, PySpark (Distributed profiling, large value-overlap analysis)
- **Event Infrastructure:** Apache Kafka (Event backbone for discovery, schema, profiling, and inference)
- **Object Storage:** S3-compatible (MinIO for local dev, AWS S3 for production)
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Code Quality:** Ruff, Mypy, Pytest, Pre-commit
- **Containers:** Docker, Docker Compose
- **Cloud:** AWS-first architecture (RDS, S3, MSK, ECS)

## Project Memory (Project Brain)

MOSAIC utilizes an internal, persistent project memory system located in the `.brain/` directory. This allows asynchronous autonomous agents and engineers to maintain state.

The `.brain/` directory contains current architecture states, phase progressions, decisions, known issues, completed work, and session logs, ensuring context is never lost across engineering sessions.

## Quick Start (Local Demo)

A one-command local demo allows developers to spin up the entire system.

```bash
make demo
```

The demo spins up Docker Compose services (Postgres, MySQL, Kafka, MinIO, Spark, API, Workers, UI), generates a realistic historical data ecosystem (Meridian Commerce), and executes discovery, profiling, inference, and graph generation automatically.

## API Usage

MOSAIC exposes versioned REST APIs. Some core endpoints:

```text
GET /api/v1/datasets/{id}/timeline
GET /api/v1/columns/{id}/history
GET /api/v1/lineage/upstream/{id}
GET /api/v1/lineage/downstream/{id}
POST /api/v1/inferences/{id}/confirm
POST /api/v1/replay
GET /api/v1/impact-analysis
```

## Security

MOSAIC implements authentication, JWT, RBAC (ADMIN, DATA_ENGINEER, ANALYST, VIEWER), secret separation, and data masking capabilities.

## Observability

Structured logging, trace IDs, correlation IDs, and metrics for Kafka consumer lag, processing latency, and failure rates are integrated throughout the system.

## Project Roadmap

The development of MOSAIC is structured into sequential phases:

* **PHASE 0:** Architecture (Domain Model, ADRs, Diagram, Project Brain)
* **PHASE 1:** Meridian Commerce Data Universe Generator
* **PHASE 2:** Discovery Engine (PostgreSQL, MySQL, CSV/JSON/Parquet, Kafka)
* **PHASE 3:** Profiling Engine (Structural, Statistical, Semantic, Fingerprinting)
* **PHASE 4:** Schema Archaeology (Diff, Rename Detection, Timeline)
* **PHASE 5:** Inference Engine (Relationship, Transformation, Confidence, Evidence)
* **PHASE 6:** Artifact Archaeology (SQL Parser, Spark Parser)
* **PHASE 7:** Kafka (Events, DLQ, Replay)
* **PHASE 8:** Spark (Distributed Profiling, Overlap Analysis)
* **PHASE 9:** Lineage (Graph model, Recursive Traversal, Impact Analysis)
* **PHASE 10:** REST APIs
* **PHASE 11:** Investigation UI (Next.js)
* **PHASE 12:** Reliability (Failure Laboratory, Observability)
* **PHASE 13:** Performance Optimization (Benchmarking)
* **PHASE 14:** Cloud Deployment (AWS)
* **PHASE 15:** Production Hardening (Security, CI/CD, Documentation)
