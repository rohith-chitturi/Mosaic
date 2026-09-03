# Domain Model

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
