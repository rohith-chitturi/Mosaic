# MOSAIC

## Historical Data Reconstruction & Lineage Inference Engine

Enterprise data ecosystems evolve over years. Databases migrate. Schemas change. Columns are renamed. Transformations change. Kafka topics appear. Spark jobs replace legacy processing. SQL scripts become obsolete. Datasets are copied across storage systems. Documentation becomes incomplete.

MOSAIC reconstructs this historical evolution using observable evidence and deterministic inference.

---

## Why MOSAIC Exists

Consider a concrete example of a standard data evolution:

```text
2018
MySQL
    ↓
customer_id
phone
amount_cents

2020
PostgreSQL
    ↓
customer_id
phone_number
amount

2022
Kafka
    ↓
customer.events

2024
Spark
    ↓
customer_features

2026
Warehouse
    ↓
lifetime_value
```

An enterprise engineer looking at the 2026 warehouse might not know how `lifetime_value` relates to the 2018 `MySQL` tables. Documentation is lost, pipelines were rewritten, and knowledge evaporated. 

MOSAIC attempts to reconstruct that history automatically.

---

## Data Archaeology

> MOSAIC treats an enterprise's accumulated data artifacts as an archaeological record and reconstructs relationships, transformations, schema evolution, and lineage from evidence.

MOSAIC distinguishes between facts and probabilistic deductions:
- **Observation:** A strict fact extracted from an environment (e.g., "SQL file references `customer_id`").
- **Candidate:** A plausible relationship found via cheap heuristics.
- **Inference:** A probabilistic deduction backed by an algorithm.
- **Evidence:** Structural or statistical signals backing (or contradicting) an inference.
- **Confidence:** A deterministic score.
- **Contradiction:** Conflicting evidence that flags a relationship for human review.
- **Lineage Assertion:** A confirmed relationship added to the graph.
- **Human Confirmation:** Manual override/approval generating an audit event.

---

## Explain This Column

The flagship feature of MOSAIC is the ability to explain the full lineage of any column.

Example query: `customer.lifetime_value`

MOSAIC discovers:
```text
orders.amount
      ↓
currency_normalization()
      ↓
customer_transaction_total
      ↓
rolling_sum()
      ↓
customer.lifetime_value
```

MOSAIC provides the historical versions, evidence, deterministic confidence, transformations, upstream dependencies, and downstream consumers.

---

## Key Capabilities

- **Dataset Discovery:** Scans PostgreSQL, MySQL, CSV, JSON, Parquet, Kafka, SQL, and Spark artifacts.
- **Data Profiling:** Calculates structural, statistical, and semantic metadata.
- **Column Fingerprinting:** Generates signatures for cross-version identity detection.
- **Schema Archaeology:** Detects schema evolution, type changes, and timeline drift.
- **Rename Detection:** Identifies probable column renames using lexical/semantic inference.
- **Transformation Inference:** Infers logic from source/target behavior and artifact parsers.
- **SQL Archaeology:** Extracts lineage and dependencies from raw SQL.
- **Spark Archaeology:** Extracts dependencies from PySpark code.
- **Candidate Generation:** Blocking strategy to avoid O(N²) cross-column comparisons.
- **Evidence Engine:** Gathers statistical, schema, and artifact signals.
- **Confidence & Consistency:** Deterministic scoring and explicit contradiction detection.
- **Lineage Graph:** A version-aware directed lineage graph (with cycle detection).
- **Impact Analysis:** Upstream and downstream traversals.
- **Human Review:** UI for engineers to confirm or reject relationships.
- **Replayability:** Deterministic, versioned inference runs allowing full reproducibility.

---

## Architecture

![Architecture](docs/architecture/ARCHITECTURE.md) (See full documentation in `docs/architecture/`)

### Architecture Principles

- **Clean Architecture & SOLID:** Layered decoupling ensuring testing and maintainability.
- **Domain-driven design:** Explicit modeling of Datasets, Lineage, Evidence, and Assertions.
- **Event-Driven Architecture:** Kafka serves as the immutable event backbone, decoupling heavy processing from rapid metadata discovery.
- **Immutable Event Envelopes:** Every event has a rigid schema, ensuring causation/correlation traceability.
- **Deterministic Inference:** Replayable algorithms generating inferences bound to an `inference_run_id`.
- **Version-Aware Lineage:** Connections map precise Dataset/Column *versions*.
- **Idempotent Processing:** Consumers handle at-least-once delivery safely.
- **Fault tolerance & Observability:** Strict DLQs and audit trails for distributed debugging.

### Data Flow

```text
Sources
 ↓
Discovery
 ↓
Observations
 ↓
Candidate Generation
 ↓
Inference
 ↓
Evidence
 ↓
Confidence / Consistency
 ↓
Supported / Conflicted / Rejected
 ↓
Lineage Assertions
 ↓
Investigation API
 ↓
Investigation UI
```

---

## Technology Stack

| Layer          | Technology              | Purpose                               |
| -------------- | ----------------------- | ------------------------------------- |
| Backend        | Python                  | Core services and inference           |
| API            | FastAPI                 | Investigation API                     |
| Metadata       | PostgreSQL              | Metadata and lineage graph            |
| Source DB      | MySQL                   | Legacy source simulation              |
| Events         | Kafka                   | Immutable asynchronous event backbone |
| Processing     | Spark / PySpark         | Large-scale profiling & overlap       |
| Historical     | Hive-compatible storage | Legacy data simulation                |
| Object storage | S3 / MinIO              | Dataset artifacts                     |
| Frontend       | Next.js / TypeScript    | Investigation interface               |
| Containers     | Docker                  | Reproducible development              |
| Cloud          | AWS                     | Production deployment target          |
| CI             | GitHub Actions          | Automated validation                  |

### Why these technologies?

- **Why Kafka?** Immutable event history, decoupling, replay, correlation IDs, and asynchronous processing. It orchestrates without the need for Airflow.
- **Why Spark?** Large-scale statistical and cross-dataset workloads. Applied selectively only after candidate generation.
- **Why PostgreSQL?** Transactional metadata, versioned entities, recursive lineage queries (CTEs), JSONB, indexing.
- **Why MySQL/Hive?** To faithfully simulate legacy enterprise systems undergoing migration.
- **Why MinIO?** Local S3-compatible development.
- **Why AWS?** Production deployment target.
- **Why Python?** Standardized ecosystem for deep data engineering and probabilistic inference logic.

---

## Inference Engine

The pipeline processes candidates through deterministic evaluation:
```text
Candidate
 ↓
Lexical similarity
 ↓
Semantic compatibility
 ↓
Value overlap
 ↓
Distribution compatibility
 ↓
Temporal alignment
 ↓
Artifact evidence
 ↓
Key relationship
 ↓
Negative evidence
 ↓
Confidence
 ↓
Consistency evaluation
```
Every inference is deterministic and versioned by `algorithm_version` and `inference_run_id`.

---

## Evidence Model

Positive and negative evidence are first-class citizens. MOSAIC avoids blindly trusting single signals.
```text
VALUE_OVERLAP       +0.91
SCHEMA_SIMILARITY   +0.94
SQL_REFERENCE       +1.00
TYPE_CONFLICT       -0.90
```
If evidence heavily contradicts (e.g. strong value overlap but strict type incompatibility), the inference is routed to Human Review.

---

## Observation vs Inference

- **OBSERVATION:** Fact. (e.g., "SQL script references `customer_id`.")
- **INFERENCE:** Hypothesis. (e.g., "`cust_id` and `customer_id` probably represent the same field.")
- **CONFIRMATION:** Fact. (e.g., "Engineer confirms the relationship.")

---

## Kafka Design

Core topics:
- `mosaic.discovery.events`
- `mosaic.profile.events`
- `mosaic.artifact.events`
- `mosaic.inference.events`
- `mosaic.lineage.events`
- `mosaic.inference.dlq`

All events follow a strict envelope including `event_id`, `correlation_id`, `causation_id`, and `aggregate_type`.
[Read Kafka Design](docs/architecture/KAFKA_DESIGN.md)

---

## Spark Design

Spark is used strictly for heavy distributed tasks (e.g., large-scale value overlap). MOSAIC implements partition-aware processing, predicate pushdown, column pruning, broadcast joins, shuffle minimization, AQE, and selective caching. Spark is NOT used for every workload.
[Read Spark Design](docs/architecture/SPARK_DESIGN.md)

---

## Lineage Model

Lineage is a **directed version-aware graph with cycle detection**. It maps explicit `DatasetVersion` and `ColumnVersion` entities, forming `LineageAssertion` edges.

---

## Security

MOSAIC utilizes JWT, RBAC (ADMIN, DATA_ENGINEER, ANALYST, VIEWER), and data masking. Raw data is never persisted; only statistical profiles and fingerprints are kept.
[Read Security](docs/architecture/SECURITY.md)

---

## AWS Architecture

```text
ALB
 ↓
ECS/Fargate
 ↓
FastAPI / Workers
 ↓
MSK
 ↓
Spark/EMR
 ↓
S3

RDS PostgreSQL
```
*(Production Architecture. Local dev utilizes Docker Compose with Postgres/Kafka/MinIO).*

---

## Repository Structure

```text
mosaic/
├── docs/                     # Documentation and ADRs (Implemented)
├── .brain/                   # Project memory and state (Implemented)
├── apps/                     # Next.js and FastAPI apps (Planned)
├── services/                 # Backend inference/discovery services (Planned)
├── packages/                 # Shared domain/core models (Planned)
├── infrastructure/           # Docker/Terraform configs (Planned)
├── data/                     # Synthetic data generators (Planned)
├── tests/                    # Testing suite (Planned)
├── docker-compose.yml        # (Planned)
├── Makefile                  # (Planned)
└── README.md                 # (Implemented)
```

---

## Project Brain

MOSAIC is built across long-running asynchronous AI/engineering sessions. The `.brain/` directory acts as an explicit memory system.
It stores the current phase, architectural decisions, and next actions. Every session begins with a recovery protocol reading `.brain/` to restore full context, ensuring deterministic project continuation.

---

## GitHub Engineering Workflow

```text
Issue → Branch → Implementation → Tests → PR → Self Review → CI → Code Review → Fixes → Merge → Brain Update
```

GitHub is our core engineering system. We utilize Issues, Milestones, Labels, PRs, Code Reviews, GitHub Actions (CI), conventional commits, and release tags.

---

## Development Roadmap

- **Phase 0 — Architecture Foundation** (`COMPLETE`)
- **Phase 1 — Data Universe** (`NEXT`)
- **Phase 2 — Discovery** (`PLANNED`)
- **Phase 3 — Profiling** (`PLANNED`)
- **Phase 4 — Schema Archaeology** (`PLANNED`)
- **Phase 5 — Inference Engine** (`PLANNED`)
- **Phase 6 — Artifact Archaeology** (`PLANNED`)
- **Phase 7 — Kafka** (`PLANNED`)
- **Phase 8 — Spark** (`PLANNED`)
- **Phase 9 — Lineage** (`PLANNED`)
- **Phase 10 — API** (`PLANNED`)
- **Phase 11 — UI** (`PLANNED`)
- **Phase 12 — Reliability** (`PLANNED`)
- **Phase 13 — Performance** (`PLANNED`)
- **Phase 14 — Cloud** (`PLANNED`)
- **Phase 15 — Production Hardening** (`PLANNED`)

## Current Status

```text
Phase 0 — COMPLETE
Phase 1 — NOT STARTED
```

---

## Local Setup

*(Coming in Phase 1 / Phase 2)*

```bash
git clone <repository>
cd mosaic
docker compose up -d
make setup
```

## Development Commands

*(Planned)*
- `make install`
- `make test`
- `make lint`
- `make demo`

---

## Demo

*(Coming in later phases)*
Executing `make demo` will eventually orchestrate the full synthetic Meridian Commerce environment, run discovery, profiling, and inference, and expose the UI for lineage investigation.

## Example Investigation

If investigating `customer.phone`:
```text
2018: phone
2020: phone_number
2023: phone_hash
```

MOSAIC traces this:
```text
phone
 ↓
phone_number
 ↓
SHA256(phone_number)
 ↓
phone_hash
```
Exposing structural evidence and calculated confidence.

---

## Testing Philosophy

MOSAIC mandates comprehensive unit, integration, and E2E testing alongside an explicit failure laboratory injecting bad schemas, missing partitions, and duplicates to validate resilience.

## Performance

*(Planned)*
Benchmarks will validate pipelines against 100K, 1M, 10M, and 50M row scales.

---

## Design Decisions (ADRs)

- [ADR-001 — Project Brain Architecture](docs/architecture/ADRs/ADR-001-project-brain.md)
- [ADR-002 — Event-Driven Core using Kafka](docs/architecture/ADRs/ADR-002-event-driven-architecture.md)
- [ADR-003 — Targeted Spark Processing](docs/architecture/ADRs/ADR-003-spark-optimization.md)

## Documentation Map

```text
docs/
├── architecture/
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_MODEL.md
│   ├── EVENT_MODEL.md
│   ├── INFERENCE_MODEL.md
│   ├── DATA_MODEL.md
│   ├── KAFKA_DESIGN.md
│   ├── SPARK_DESIGN.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   └── ADRs/
```

---

## Project Differentiation

**Typical Pipeline:**
```text
source → ETL → warehouse → dashboard
```

**MOSAIC Pipeline:**
```text
unknown historical ecosystem → discover evidence → profile artifacts → generate candidates → infer relationships → evaluate evidence → detect contradictions → reconstruct lineage → explain historical evolution
```

---

## Limitations

MOSAIC relies on probabilistic inference. Limitations exist around:
- Insufficient historical data
- Ambiguous/opaque transformations (e.g. encrypted fields)
- Missing legacy artifacts
- Unresolvable contradictions (which flag for human review)

MOSAIC surfaces uncertainty rather than hiding it.

---

## Future Directions
- Adapters for Snowflake, BigQuery, Redshift, Azure.
- Richer SQL dialect support.
- Graph database adapter.

*(These features will not be implemented until their respective architectural phase arrives).*

---

## Contributing
Follow the GitHub Workflow. Strict adherence to Conventional Commits and formatting checks.

## License
*(Pending)*
