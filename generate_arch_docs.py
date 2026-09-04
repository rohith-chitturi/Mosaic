import os

docs = {
    "docs/architecture/ARCHITECTURE.md": """# MOSAIC Architecture

## Overall System Architecture

```mermaid
graph TD
    subgraph Enterprise Sources
        PG[(PostgreSQL)]
        MY[(MySQL)]
        S3[(Object Storage\nParquet/CSV)]
        CODE[Code Artifacts\nSQL/Spark]
    end

    subgraph Discovery
        DE[Discovery Engine]
    end

    subgraph Event Backbone
        KAFKA[[Apache Kafka\nImmutable Event Envelope]]
    end

    subgraph Inference & Graph Pipeline
        OBS[(Observations)]
        CE[Candidate Engine\nBlocking & Filtering]
        IE[Inference Engine]
        EE[Evidence Engine]
        CC[Confidence & Consistency]
    end

    subgraph Processing Layer
        SPARK[Apache Spark\nJob Dispatcher]
    end

    subgraph Storage & Presentation
        LG[(PostgreSQL\nVersion-Aware\nLineage Graph)]
        RQ[(Review Queue)]
        API[FastAPI Layer]
        UI[Next.js UI]
    end

    PG --> DE
    MY --> DE
    S3 --> DE
    CODE --> DE
    
    DE --> KAFKA
    
    KAFKA --> OBS
    OBS --> CE
    CE --> IE
    IE --> EE
    EE --> CC
    
    CC -->|SUPPORTED| LG
    CC -->|CONFLICTED| RQ
    
    LG --> API
    RQ --> API
    API --> UI
```

## Inference Pipeline Lifecycle

1. **OBSERVED:** Raw facts are extracted from data sources or artifact parsers.
2. **CANDIDATE:** Plausible relationships are identified using cheap heuristics (Blocking/Indexing).
3. **EVALUATED:** Expensive inference algorithms test the candidate.
4. **INFERRED:** The algorithm produces a hypothesis and confidence score.
5. **SUPPORTED / CONFLICTED / REJECTED:** Consistency checks apply evidence thresholds and contradiction rules. Conflicted relationships enter the Review Queue.
6. **PROMOTION POLICY (LINEAGE ASSERTION):** Supported relationships meeting strict policy thresholds are promoted to full Lineage Assertions in the graph.
7. **HUMAN REVIEW:** Engineers can CONFIRM, REJECT, or OVERRIDE inferences, generating audit events.

## Why Kafka?
MOSAIC treats discovery, profiling, artifact analysis, and inference as asynchronous event-driven operations. Kafka provides immutable event history, decoupled consumers, replayability, correlation IDs, and failure recovery.

## Why Spark?
The expensive part of reconstruction is cross-dataset statistical comparison and value analysis. Once the candidate set is generated, Spark allows those workloads to scale without forcing the entire system into Spark.
""",

    "docs/architecture/DOMAIN_MODEL.md": """# Domain Model

```mermaid
erDiagram
    DatasetVersion ||--o{ Observation : generates
    ColumnVersion ||--o{ Observation : generates
    
    Observation ||--o{ CandidateRelationship : triggers
    CandidateRelationship ||--o{ InferenceRun : evaluated_in
    InferenceRun ||--o{ Inference : produces
    
    Inference ||--o{ Evidence : supported_by
    Inference ||--o{ Contradiction : flagged_by
    
    Inference ||--o{ LineageAssertion : becomes
    
    DatasetVersion ||--o{ LineageAssertion : connects_source
    DatasetVersion ||--o{ LineageAssertion : connects_target
    ColumnVersion ||--o{ LineageAssertion : connects_source
    ColumnVersion ||--o{ LineageAssertion : connects_target
```

## Key Entities
- **DatasetVersion / ColumnVersion:** Lineage explicitly links versions, not generic tables/columns.
- **Observation:** A hard fact extracted from an environment (e.g. "Script X selects Y").
- **CandidateRelationship:** A pair identified through cheap blocking heuristics.
- **InferenceRun:** The deterministic execution context (algorithm version, timestamp, configuration hash).
- **Inference:** The calculated hypothesis.
- **Evidence / Contradiction:** Positive and negative statistical or structural signals backing an inference.
- **LineageAssertion:** A confirmed relationship integrated into the directed lineage graph.
""",

    "docs/architecture/EVENT_MODEL.md": """# Event Model (Kafka)

Every Kafka message in MOSAIC must adhere to an immutable envelope. Arbitrary JSON payloads are rejected.

## MosaicEvent Envelope

```json
{
  "event_id": "evt_8f921-1234-abcd",
  "event_type": "SCHEMA_OBSERVED",
  "event_version": "1.0",
  "occurred_at": "2026-09-03T22:45:00Z",
  "producer": "discovery-engine-pg",
  "correlation_id": "run_92821",
  "causation_id": "evt_prev-9876",
  "aggregate_type": "DATASET_VERSION",
  "aggregate_id": "dv_8f921",
  "payload": {
     // Specific schema payload
  }
}
```

This ensures global traceability, idempotency, and robust distributed debugging.
""",

    "docs/architecture/INFERENCE_MODEL.md": """# Inference Model

## Blocking & Candidate Generation
To avoid O(N²) comparisons across 100,000+ columns, inference occurs in stages:
1. **Blocking:** Cheap signaling (trigram indices, data types, basic cardinality).
2. **Result:** Reduces 10 billion combinations to ~2,000 plausible candidates.
3. **Evaluation:** Expensive deterministic algorithms (e.g., Spark value overlap) process the remaining candidates.

## Inference Versioning
Every inference generated stores exactly how it was produced.

**InferenceRun**
- `run_id`
- `algorithm_name` (e.g., rename-detector)
- `algorithm_version` (e.g., v1.2)
- `configuration_hash`
- `started_at`, `completed_at`
- `status`

**Inference**
- `inference_id`
- `run_id`
- `candidate_id`
- `result`
- `confidence`
- `created_at`

## Evidence Types
Both positive and negative evidence are first-class concepts.
- `VALUE_OVERLAP` (+0.91)
- `SCHEMA_SIMILARITY` (+0.94)
- `TYPE_CONFLICT` (-0.90)

Contradictory evidence routes the inference to the Review Queue.
""",

    "docs/architecture/DATA_MODEL.md": """# Data Model (PostgreSQL)

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
""",

    "docs/architecture/KAFKA_DESIGN.md": """# Kafka Design

- **Role:** Asynchronous event backbone linking Discovery, Profiling, Inference, and Storage.
- **Topics:**
  - `mosaic.discovery.events`
  - `mosaic.profile.events`
  - `mosaic.artifact.events`
  - `mosaic.inference.events`
  - `mosaic.lineage.events`
  - `mosaic.dlq`
- **Guarantees:** At-least-once processing, relying on idempotent consumers that check `event_id` against PostgreSQL before applying changes.
""",

    "docs/architecture/SPARK_DESIGN.md": """# Spark Optimization Strategy

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
""",

    "docs/architecture/SECURITY.md": """# Security Architecture

- **Authentication:** JWT via FastAPI.
- **RBAC:** Roles for ADMIN, DATA_ENGINEER, ANALYST, VIEWER.
- **Data Protection:** The system profiles metadata and statistical aggregates. Raw data is never stored locally beyond ephemeral Spark processing tasks.
- **Audit:** Human boundary overrides generate `INFERENCE_CONFIRMED_BY_ENGINEER` or `INFERENCE_REJECTED_BY_ENGINEER` audit events.
""",

    "docs/architecture/DEPLOYMENT.md": """# Deployment Architecture

AWS-first containerized architecture:

- **Compute:** ECS Fargate for API, UI, and Event Dispatchers. EMR Serverless/Clusters for Spark processing.
- **Storage:** Amazon S3 for object storage and historical file archives. Amazon RDS for PostgreSQL metadata and lineage graph.
- **Streaming:** Amazon MSK for Kafka.
- **Networking:** Application Load Balancer routes traffic to the UI and API.
""",

    "docs/architecture/ADRs/ADR-001-project-brain.md": """# ADR-001: Project Brain Architecture

**Date:** 2026-09-03
**Status:** Accepted

## Context
MOSAIC requires long-term memory across multiple disparate engineering sessions (or AI autonomous agent sessions). Standard contextual memory evaporates between sessions.

## Decision
Establish `.brain/` within the repository itself as the definitive source of truth for Project State, Architecture State, Decisions, and Phase progression. The `.brain/` is a first-class component of the engineering workflow.

## Consequences
- Requires strict updates before merging any PR.
- Ensures absolute context recovery regardless of the executing agent or engineer.
""",

    "docs/architecture/ADRs/ADR-002-event-driven-architecture.md": """# ADR-002: Event-Driven Core using Kafka

**Date:** 2026-09-03
**Status:** Accepted

## Context
Data discovery and inference happen at vastly different speeds. Direct API calls between services lead to timeouts and cascading failures.

## Decision
Use Apache Kafka as the immutable event backbone. All inter-domain communication uses strict typed `MosaicEvent` envelopes. No orchestration tool (like Airflow) is used; Kafka drives dispatching.

## Consequences
- Guarantees replayability and decoupling.
- Requires all consumers to handle idempotency explicitly.
""",

    "docs/architecture/ADRs/ADR-003-spark-optimization.md": """# ADR-003: Targeted Spark Processing

**Date:** 2026-09-03
**Status:** Accepted

## Context
Profiling every column against every column is an O(N²) problem. Pure Spark jobs over the entire enterprise data lake fail to scale.

## Decision
Utilize a two-tier Candidate Engine. Cheap Python/SQL blocking heuristics reduce candidates. Spark is invoked only on plausible candidates, utilizing aggressive optimization strategies (AQE, broadcast joins, column pruning, skew detection) rather than naive caching.

## Consequences
- Reduces computational overhead drastically.
- Requires maintaining dual implementations for simple filtering vs deep Spark comparison.
"""
}

for filepath, content in docs.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Generated all architecture documents.")
