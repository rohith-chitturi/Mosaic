# Deployment Architecture

AWS-first containerized architecture:

- **Compute:** ECS Fargate for API, UI, and Event Dispatchers. EMR Serverless/Clusters for Spark processing.
- **Storage:** Amazon S3 for object storage and historical file archives. Amazon RDS for PostgreSQL metadata and lineage graph.
- **Streaming:** Amazon MSK for Kafka.
- **Networking:** Application Load Balancer routes traffic to the UI and API.
