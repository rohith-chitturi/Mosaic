# Event Model (Kafka)

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
