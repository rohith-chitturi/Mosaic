import os
from typing import List
from datetime import datetime
from services.discovery.domain.source import Source
from services.discovery.domain.scan_result import ScanResult
from services.discovery.domain.dataset import Schema, Column
from services.discovery.scanners.base import Scanner

class ObjectStorageScanner(Scanner):
    """
    Scans an Object Storage path (MinIO/S3 or Local for testing) looking for Parquet datasets.
    Extracts deterministic schemas from Parquet metadata using PyArrow without reading row data.
    """
    def __init__(self, source: Source, base_dir: str):
        super().__init__(source)
        # Using base_dir for local filesystem simulation of object storage
        self.base_dir = base_dir

    def scan(self) -> List[ScanResult]:
        results = []
        
        try:
            import pyarrow.parquet as pq
            import pyarrow.dataset as ds
        except ImportError:
            print("WARNING: pyarrow not installed. ObjectStorageScanner cannot run.")
            return results

        # In Phase 2, we simulate scanning the data lake directory
        if not os.path.exists(self.base_dir):
            return results

        # Simplistic discovery: any folder containing .parquet files is a dataset
        for root, dirs, files in os.walk(self.base_dir):
            parquet_files = [f for f in files if f.endswith('.parquet')]
            
            if parquet_files:
                # Discovered a dataset partition or root!
                # To keep it simple, we use pyarrow dataset API to infer the overall dataset
                try:
                    dataset = ds.dataset(root, format="parquet")
                    
                    columns = []
                    for idx, field in enumerate(dataset.schema):
                        columns.append(Column(
                            name=field.name,
                            physical_type=str(field.type),
                            nullable=field.nullable,
                            ordinal_position=idx + 1
                        ))
                    
                    schema_def = Schema(columns=columns)
                    
                    # Estimate partitions if the path has '='
                    partitions = []
                    parts = root.replace(self.base_dir, "").split(os.sep)
                    for p in parts:
                        if "=" in p:
                            partitions.append(p.split("=")[0])
                            
                    # Clean up dataset name by removing partition paths
                    ds_name_parts = []
                    for p in parts:
                        if "=" not in p and p:
                            ds_name_parts.append(p)
                    dataset_name = "/".join(ds_name_parts)
                    if not dataset_name:
                        dataset_name = "root_dataset"

                    results.append(ScanResult(
                        source_id=self.source.source_id,
                        dataset_name=dataset_name,
                        format="parquet",
                        schema_def=schema_def,
                        partitions=list(set(partitions)) if partitions else None,
                        file_count=len(dataset.files),
                        total_bytes=sum(os.path.getsize(f) for f in dataset.files) if dataset.files else None,
                        scanned_at=datetime.utcnow()
                    ))
                    
                    # We clear dirs to avoid walking into sub-partitions once we recognize the root
                    # Note: PyArrow dataset reads recursively anyway
                    dirs.clear()
                except Exception as e:
                    print(f"Failed to scan {root}: {str(e)}")
                    
        return results
