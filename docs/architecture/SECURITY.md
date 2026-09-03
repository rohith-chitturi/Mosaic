# Security Architecture

- **Authentication:** JWT via FastAPI.
- **RBAC:** Roles for ADMIN, DATA_ENGINEER, ANALYST, VIEWER.
- **Data Protection:** The system profiles metadata and statistical aggregates. Raw data is never stored locally beyond ephemeral Spark processing tasks.
- **Audit:** Human boundary overrides generate `INFERENCE_CONFIRMED_BY_ENGINEER` or `INFERENCE_REJECTED_BY_ENGINEER` audit events.
