# Kafka Design

- **Role:** Asynchronous event backbone linking Discovery, Profiling, Inference, and Storage.
- **Topics:**
  - `mosaic.discovery.events`
  - `mosaic.profile.events`
  - `mosaic.artifact.events`
  - `mosaic.inference.events`
  - `mosaic.lineage.events`
  - `mosaic.dlq`
- **Guarantees:** At-least-once processing, relying on idempotent consumers that check `event_id` against PostgreSQL before applying changes.
