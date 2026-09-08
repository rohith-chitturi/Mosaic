import uuid
import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from services.discovery.app.dependencies import get_db, get_metadata_repo, get_event_publisher, generate_correlation_id
from services.discovery.app.config import settings
from services.discovery.persistence.metadata_repo import MetadataRepository
from services.discovery.persistence.models import Base, SourceModel
from services.discovery.events.publisher import EventPublisher
from services.discovery.events.envelope import MosaicEvent
from services.discovery.domain.source import Source
from services.discovery.domain.observation import ObservationBuilder
from services.discovery.scanners.object_storage_scanner import ObjectStorageScanner
from services.discovery.app.dependencies import engine

# Create tables for Phase 2 if Alembic isn't configured/run yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MOSAIC Discovery API")

@app.post("/sources")
def register_source(source: Source, repo: MetadataRepository = Depends(lambda: get_metadata_repo(next(get_db())))):
    repo.save_source(source)
    return {"status": "registered", "source_id": source.source_id}

@app.post("/scans/{source_id}")
def trigger_scan(
    source_id: str, 
    db: Session = Depends(get_db), 
    repo: MetadataRepository = Depends(get_metadata_repo),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    correlation_id = generate_correlation_id()
    
    # 1. Fetch Source
    source_model = db.query(SourceModel).filter(SourceModel.source_id == source_id).first()
    if not source_model:
        raise HTTPException(status_code=404, detail="Source not found")
        
    source = Source(
        source_id=source_model.source_id,
        source_type=source_model.source_type,
        name=source_model.name,
        location=source_model.location,
        configuration_reference=source_model.configuration
    )
    
    # 2. Publish DISCOVERY_RUN_STARTED
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    publisher.publish("mosaic.discovery.events", MosaicEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="DISCOVERY_RUN_STARTED",
        correlation_id=correlation_id,
        aggregate_type="DISCOVERY_RUN",
        aggregate_id=run_id,
        payload={"source_id": source_id}
    ))
    
    try:
        # 3. Initialize appropriate scanner
        if source.source_type == "minio":
            # In Phase 2 Foundation, we simulate scanning the generated data lake directory
            # For testing without a real MinIO connection, we assume location is a local path
            base_dir = os.path.abspath(source.location)
            scanner = ObjectStorageScanner(source, base_dir=base_dir)
        else:
            raise NotImplementedError(f"Scanner for {source.source_type} not implemented")
            
        # 4. Execute Scan
        scan_results = scanner.scan()
        
        # 5. Process Results (Observation Builder -> Persistence -> Events)
        observations_count = 0
        for res in scan_results:
            dataset, version, observation = ObservationBuilder.build_from_scan(res)
            
            # Persist to PostgreSQL
            repo.save_observation(dataset, version, observation)
            
            # Publish Kafka Events
            publisher.publish("mosaic.discovery.events", MosaicEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type="DATASET_DISCOVERED",
                correlation_id=correlation_id,
                causation_id=run_id,
                aggregate_type="DATASET",
                aggregate_id=dataset.dataset_id,
                payload={"name": dataset.name, "format": dataset.format}
            ))
            
            publisher.publish("mosaic.discovery.events", MosaicEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type="SCHEMA_DISCOVERED",
                correlation_id=correlation_id,
                causation_id=run_id,
                aggregate_type="DATASET_VERSION",
                aggregate_id=version.version_id,
                payload={"schema_fingerprint": version.schema_def.fingerprint(), "dataset_id": dataset.dataset_id}
            ))
            observations_count += 1
            
        # 6. Publish DISCOVERY_RUN_COMPLETED
        publisher.publish("mosaic.discovery.events", MosaicEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="DISCOVERY_RUN_COMPLETED",
            correlation_id=correlation_id,
            aggregate_type="DISCOVERY_RUN",
            aggregate_id=run_id,
            payload={"source_id": source_id, "observations_count": observations_count}
        ))
        
        publisher.flush()
        return {"status": "completed", "run_id": run_id, "observations_count": observations_count}
        
    except Exception as e:
        # Publish DISCOVERY_RUN_FAILED
        publisher.publish("mosaic.discovery.events", MosaicEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="DISCOVERY_RUN_FAILED",
            correlation_id=correlation_id,
            aggregate_type="DISCOVERY_RUN",
            aggregate_id=run_id,
            payload={"source_id": source_id, "error": str(e)}
        ))
        publisher.flush()
        raise HTTPException(status_code=500, detail=str(e))
