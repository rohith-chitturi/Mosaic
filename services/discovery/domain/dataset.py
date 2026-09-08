from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Column(BaseModel):
    name: str = Field(..., description="Name of the column")
    physical_type: str = Field(..., description="Physical type of the column in the source system (e.g., VARCHAR(255), int64)")
    nullable: bool = Field(..., description="Whether the column can contain null values")
    ordinal_position: int = Field(..., description="The position of the column in the schema (1-indexed)")

class Schema(BaseModel):
    columns: List[Column] = Field(default_factory=list, description="List of columns in the schema")
    
    def fingerprint(self) -> str:
        """
        Calculates a deterministic identity for the schema based on its columns.
        This is useful for detecting schema drift across versions.
        """
        import hashlib
        # We sort by ordinal position to ensure consistent hashing
        sorted_cols = sorted(self.columns, key=lambda c: c.ordinal_position)
        col_strings = [f"{c.name}:{c.physical_type}:{c.nullable}:{c.ordinal_position}" for c in sorted_cols]
        joined = "|".join(col_strings)
        return hashlib.sha256(joined.encode()).hexdigest()

class DatasetVersion(BaseModel):
    version_id: str = Field(..., description="Unique deterministic identifier for this version of the dataset")
    schema_def: Schema = Field(..., description="The schema structure observed in this version")
    partitions: Optional[List[str]] = Field(default=None, description="List of partition keys if applicable")
    file_count: Optional[int] = Field(default=None, description="Number of files (for object storage)")
    total_bytes: Optional[int] = Field(default=None, description="Total size in bytes (if determinable)")
    observed_at: datetime = Field(..., description="When this version was observed")

class Dataset(BaseModel):
    dataset_id: str = Field(..., description="Globally unique identifier, e.g., hash(source_id + dataset_name)")
    source_id: str = Field(..., description="Reference to the Source this dataset belongs to")
    name: str = Field(..., description="The name or path of the dataset (e.g., 'customer_features' or 'public.users')")
    format: str = Field(..., description="The physical format (e.g., 'parquet', 'table', 'csv')")
    versions: List[DatasetVersion] = Field(default_factory=list, description="Observed versions of this dataset")
    
    @staticmethod
    def generate_id(source_id: str, name: str) -> str:
        import hashlib
        return "ds_" + hashlib.sha256(f"{source_id}::{name}".encode()).hexdigest()[:16]
