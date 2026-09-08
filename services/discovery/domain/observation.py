from typing import List
from datetime import datetime
from services.discovery.domain.scan_result import ScanResult
from services.discovery.domain.dataset import Dataset, DatasetVersion, Schema, Column
from pydantic import BaseModel, Field

class Observation(BaseModel):
    """
    Represents an immutable observation of a fact in the enterprise.
    """
    observation_id: str = Field(..., description="Unique ID for this observation")
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    source_id: str
    dataset_id: str
    version_id: str
    schema_fingerprint: str

class ObservationBuilder:
    """
    Translates raw ScanResults into strict Observation models and Dataset/Version entities.
    """
    @staticmethod
    def build_from_scan(scan_result: ScanResult) -> tuple[Dataset, DatasetVersion, Observation]:
        dataset_id = Dataset.generate_id(scan_result.source_id, scan_result.dataset_name)
        schema_fingerprint = scan_result.schema_def.fingerprint()
        
        import hashlib
        version_id = "dv_" + hashlib.sha256(f"{dataset_id}::{schema_fingerprint}".encode()).hexdigest()[:16]
        
        version = DatasetVersion(
            version_id=version_id,
            schema_def=scan_result.schema_def,
            partitions=scan_result.partitions,
            file_count=scan_result.file_count,
            total_bytes=scan_result.total_bytes,
            observed_at=scan_result.scanned_at
        )
        
        dataset = Dataset(
            dataset_id=dataset_id,
            source_id=scan_result.source_id,
            name=scan_result.dataset_name,
            format=scan_result.format,
            versions=[version]
        )
        
        import uuid
        observation = Observation(
            observation_id="obs_" + uuid.uuid4().hex[:16],
            observed_at=scan_result.scanned_at,
            source_id=scan_result.source_id,
            dataset_id=dataset_id,
            version_id=version_id,
            schema_fingerprint=schema_fingerprint
        )
        
        return dataset, version, observation
