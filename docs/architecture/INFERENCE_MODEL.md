# Inference Model

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
