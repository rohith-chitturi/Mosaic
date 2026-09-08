from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from services.discovery.domain.dataset import Schema

class ScanResult(BaseModel):
    """
    The raw output of a scanner. Scanners only describe what exists in the source.
    They do not make persistence decisions.
    """
    source_id: str = Field(..., description="The ID of the source scanned")
    dataset_name: str = Field(..., description="The name or path of the discovered dataset")
    format: str = Field(..., description="The format of the dataset")
    schema_def: Schema = Field(..., description="The extracted schema")
    partitions: Optional[List[str]] = Field(default=None, description="Partition keys if present")
    file_count: Optional[int] = Field(default=None, description="File count for object storage datasets")
    total_bytes: Optional[int] = Field(default=None, description="Total size in bytes if known")
    scanned_at: datetime = Field(default_factory=datetime.utcnow, description="When the scan occurred")
