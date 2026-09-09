import os
from typing import List
from datetime import datetime
from services.discovery.domain.source import Source
from services.discovery.domain.scan_result import ScanResult
from services.discovery.domain.dataset import Schema, Column
from services.discovery.scanners.base import Scanner

class ObjectStorageScanner(Scanner):
    """
    Scans an Object Storage path using MinIO client looking for Parquet datasets.
    Extracts deterministic schemas from Parquet metadata using PyArrow via S3 URI
    without reading row data.
    """
    def __init__(self, source: Source, endpoint: str, access_key: str, secret_key: str):
        super().__init__(source)
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def scan(self) -> List[ScanResult]:
        results = []
        try:
            from minio import Minio
            import pyarrow.parquet as pq
            from pyarrow.fs import S3FileSystem
        except ImportError:
            print("WARNING: minio or pyarrow not installed. ObjectStorageScanner cannot run.")
            return results

        # Configure S3 FileSystem for PyArrow
        s3_fs = S3FileSystem(
            endpoint_override=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            scheme="http",
            allow_bucket_creation=True
        )

        client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )

        # Assuming location is the bucket name for MinIO sources
        bucket_name = self.source.location
        if not client.bucket_exists(bucket_name):
            print(f"WARNING: Bucket {bucket_name} does not exist.")
            return results

        objects = client.list_objects(bucket_name, recursive=True)
        
        # Group files by logical dataset based on common prefix (simplistic heuristic)
        # e.g., customer_features/year=2022/month=01/part-0000.parquet -> dataset: customer_features
        dataset_paths = {}
        for obj in objects:
            if obj.object_name.endswith('.parquet'):
                parts = obj.object_name.split('/')
                # Find root before partitions (folders with '=')
                ds_parts = []
                for p in parts:
                    if '=' in p:
                        break
                    ds_parts.append(p)
                
                # If the file itself is at root, or we found the root
                if ds_parts:
                    # if the last part is the parquet file itself, remove it to get the prefix
                    if ds_parts[-1].endswith('.parquet'):
                        ds_parts.pop()
                        
                ds_name = "/".join(ds_parts) if ds_parts else "root_dataset"
                if ds_name not in dataset_paths:
                    dataset_paths[ds_name] = []
                dataset_paths[ds_name].append(obj.object_name)

        # For each dataset prefix, read metadata from the first parquet file found
        for ds_name, files in dataset_paths.items():
            if not files:
                continue
                
            sample_file = files[0]
            s3_uri = f"{bucket_name}/{sample_file}"
            
            try:
                # Read metadata explicitly without full file scan
                metadata = pq.read_metadata(s3_uri, filesystem=s3_fs)
                arrow_schema = metadata.schema.to_arrow_schema()
                
                columns = []
                for idx, field in enumerate(arrow_schema):
                    columns.append(Column(
                        name=field.name,
                        physical_type=str(field.type),
                        nullable=field.nullable,
                        ordinal_position=idx + 1
                    ))
                
                schema_def = Schema(columns=columns)
                
                # Estimate partitions from all file paths
                partitions = set()
                for f in files:
                    parts = f.split('/')
                    for p in parts:
                        if "=" in p:
                            partitions.add(p.split("=")[0])
                            
                # Calculate total bytes
                total_bytes = 0
                for f in files:
                    stat = client.stat_object(bucket_name, f)
                    total_bytes += stat.size

                results.append(ScanResult(
                    source_id=self.source.source_id,
                    dataset_name=ds_name,
                    format="parquet",
                    schema_def=schema_def,
                    partitions=list(partitions) if partitions else None,
                    file_count=len(files),
                    total_bytes=total_bytes,
                    scanned_at=datetime.utcnow()
                ))
            except Exception as e:
                print(f"Failed to scan {s3_uri}: {str(e)}")
                
        return results
