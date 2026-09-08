from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Source(BaseModel):
    """
    Represents a physical or logical source system in the enterprise.
    Examples: 'SOURCE:mysql:meridian-legacy', 'SOURCE:postgres:meridian-core', 'SOURCE:minio:meridian-lake'
    """
    source_id: str = Field(..., description="Unique identifier for the source, e.g., SOURCE:mysql:meridian-legacy")
    source_type: str = Field(..., description="Type of the source (e.g., mysql, postgres, minio)")
    name: str = Field(..., description="Human-readable name of the source")
    location: str = Field(..., description="Connection string or URI of the source")
    configuration_reference: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary configuration metadata")
