# MOSAIC Architecture

## Overall System Architecture

```mermaid
graph TD
    subgraph Enterprise Sources
        PG[(PostgreSQL)]
        MY[(MySQL)]
        S3[(Object Storage
Parquet/CSV)]
        CODE[Code Artifacts
SQL/Spark]
    end

    subgraph Discovery
        DE[Discovery Engine]
    end

    subgraph Event Backbone
        KAFKA[[Apache Kafka
Immutable Event Envelope]]
    end

    subgraph Inference & Graph Pipeline
        OBS[(Observations)]
        CE[Candidate Engine
Blocking & Filtering]
        IE[Inference Engine]
        EE[Evidence Engine]
        CC[Confidence & Consistency]
    end

    subgraph Processing Layer
        SPARK[Apache Spark
Job Dispatcher]
    end

    subgraph Storage & Presentation
        LG[(PostgreSQL
Version-Aware
Lineage Graph)]
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
