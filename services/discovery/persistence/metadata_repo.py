from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from services.discovery.persistence.models import (
    DatasetModel, DatasetVersionModel, SchemaModel, ColumnModel, ObservationModel, SourceModel
)
from services.discovery.domain.dataset import Dataset, DatasetVersion, Schema
from services.discovery.domain.observation import Observation
from services.discovery.domain.source import Source

class MetadataRepository:
    def __init__(self, session: Session):
        self.session = session
        
    def save_source(self, source: Source):
        stmt = insert(SourceModel).values(
            source_id=source.source_id,
            source_type=source.source_type,
            name=source.name,
            location=source.location,
            configuration=source.configuration_reference
        ).on_conflict_do_nothing(index_elements=['source_id'])
        self.session.execute(stmt)
        
    def save_observation(self, dataset: Dataset, version: DatasetVersion, observation: Observation):
        # 1. Idempotent save for Dataset
        stmt_ds = insert(DatasetModel).values(
            dataset_id=dataset.dataset_id,
            source_id=dataset.source_id,
            name=dataset.name,
            format=dataset.format
        ).on_conflict_do_nothing(index_elements=['dataset_id'])
        self.session.execute(stmt_ds)
        
        # 2. Idempotent save for Schema and Columns
        schema_fp = version.schema_def.fingerprint()
        stmt_sc = insert(SchemaModel).values(
            schema_fingerprint=schema_fp
        ).on_conflict_do_nothing(index_elements=['schema_fingerprint'])
        res = self.session.execute(stmt_sc)
        
        # Only insert columns if the schema was newly inserted to avoid constraint errors or duplicate attempts
        if res.rowcount > 0:
            for col in version.schema_def.columns:
                stmt_col = insert(ColumnModel).values(
                    schema_fingerprint=schema_fp,
                    name=col.name,
                    physical_type=col.physical_type,
                    nullable=col.nullable,
                    ordinal_position=col.ordinal_position
                )
                self.session.execute(stmt_col)
                
        # 3. Idempotent save for Version
        stmt_ver = insert(DatasetVersionModel).values(
            version_id=version.version_id,
            dataset_id=dataset.dataset_id,
            observed_at=version.observed_at,
            partitions=version.partitions,
            file_count=version.file_count,
            total_bytes=version.total_bytes
        ).on_conflict_do_nothing(index_elements=['version_id'])
        self.session.execute(stmt_ver)
        
        # 4. Save Observation Fact (Observations are immutable and unique per run)
        stmt_obs = insert(ObservationModel).values(
            observation_id=observation.observation_id,
            observed_at=observation.observed_at,
            source_id=observation.source_id,
            dataset_id=observation.dataset_id,
            version_id=observation.version_id,
            schema_fingerprint=observation.schema_fingerprint
        )
        self.session.execute(stmt_obs)
        self.session.commit()
