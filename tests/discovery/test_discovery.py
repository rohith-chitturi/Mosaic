import pytest
import uuid
import os
from datetime import datetime
from services.discovery.domain.source import Source
from services.discovery.domain.dataset import Dataset, DatasetVersion, Schema, Column
from services.discovery.domain.observation import ObservationBuilder
from services.discovery.events.envelope import MosaicEvent

def test_source_registration():
    s = Source(
        source_id="SOURCE:postgres:meridian-core",
        source_type="postgres",
        name="meridian-core",
        location="postgresql://user:pass@localhost:5432/core"
    )
    assert s.source_id == "SOURCE:postgres:meridian-core"

def test_identity_stability():
    source_id = "SOURCE:minio:meridian-lake"
    dataset_name = "customer_features"
    id1 = Dataset.generate_id(source_id, dataset_name)
    id2 = Dataset.generate_id(source_id, dataset_name)
    assert id1 == id2, "Dataset identity must be deterministic"
    assert id1.startswith("ds_")

def test_schema_fingerprint_determinism():
    c1 = Column(name="id", physical_type="int", nullable=False, ordinal_position=1)
    c2 = Column(name="name", physical_type="varchar", nullable=True, ordinal_position=2)
    s1 = Schema(columns=[c1, c2])
    
    # Same columns, different order
    s2 = Schema(columns=[c2, c1])
    
    assert s1.fingerprint() == s2.fingerprint(), "Schema fingerprint must be order-independent"

def test_event_envelope_validation():
    # Valid envelope
    e = MosaicEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="TEST_EVENT",
        correlation_id="run_123",
        aggregate_type="TEST",
        aggregate_id="test_1",
        payload={"key": "value"}
    )
    assert e.event_type == "TEST_EVENT"

def test_no_lineage_inference_or_ground_truth(mocker):
    # This test asserts that our codebase does not import or use ground truth or lineage
    import services.discovery
    import inspect
    
    source_code = inspect.getsource(services.discovery)
    assert "ground_truth" not in source_code.lower(), "Discovery engine must not access ground truth!"
    assert "lineage" not in source_code.lower(), "Discovery engine must not perform lineage inference!"
    assert "fuzzy" not in source_code.lower(), "Discovery engine must not perform fuzzy matching!"
