# ADR-002: Event-Driven Core using Kafka

**Date:** 2026-09-03
**Status:** Accepted

## Context
Data discovery and inference happen at vastly different speeds. Direct API calls between services lead to timeouts and cascading failures.

## Decision
Use Apache Kafka as the immutable event backbone. All inter-domain communication uses strict typed `MosaicEvent` envelopes. No orchestration tool (like Airflow) is used; Kafka drives dispatching.

## Consequences
- Guarantees replayability and decoupling.
- Requires all consumers to handle idempotency explicitly.
