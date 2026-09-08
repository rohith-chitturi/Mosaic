from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class MosaicEvent(BaseModel):
    """
    The immutable envelope required for all events in MOSAIC.
    Adheres strictly to the EVENT_MODEL.md specification.
    """
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event Type (e.g., DATASET_DISCOVERED, DISCOVERY_RUN_STARTED)")
    event_version: str = Field(default="1.0")
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    producer: str = Field(default="discovery-engine")
    correlation_id: str = Field(..., description="Ties events together, typically the run ID")
    causation_id: Optional[str] = Field(default=None, description="The event ID that triggered this one")
    aggregate_type: str = Field(..., description="The entity type (e.g., DATASET, SCHEMA, RUN)")
    aggregate_id: str = Field(..., description="The entity ID")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data payload")
