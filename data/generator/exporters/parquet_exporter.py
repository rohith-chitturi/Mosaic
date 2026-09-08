import os
import sys

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("FATAL ERROR: pyarrow is required for parquet export but could not be imported.", file=sys.stderr)
    print("Please install it with 'pip install pyarrow'.", file=sys.stderr)
    sys.exit(1)

def export_to_parquet(data: list[dict], filepath: str, schema: pa.Schema = None, compression: str = 'snappy'):
    """
    Exports a list of dictionaries to an Apache Parquet file using pyarrow.
    
    Args:
        data: List of dictionaries representing rows.
        filepath: Destination file path (must end in .parquet).
        schema: Optional pyarrow Schema for explicit typing. If None, it's inferred.
        compression: Compression algorithm (e.g., 'snappy', 'gzip', 'brotli', 'none').
    """
    if not filepath.endswith(".parquet"):
        raise ValueError(f"Filepath must end with .parquet, got: {filepath}")
        
    if not data:
        print(f"Warning: Empty data provided for {filepath}. Skipping parquet generation.")
        return
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Sort dictionaries by key to ensure deterministic column ordering if schema is inferred
    # For rows, we preserve the input ordering as that's up to the caller to make deterministic
    deterministic_data = [{k: row[k] for k in sorted(row.keys())} for row in data]
    
    # Create Arrow Table
    table = pa.Table.from_pylist(deterministic_data, schema=schema)
    
    # Write Parquet
    pq.write_table(table, filepath, compression=compression)
    
    # Validate after writing
    try:
        read_table = pq.read_table(filepath)
        if read_table.num_rows != len(data):
            raise RuntimeError(f"Validation failed: Wrote {len(data)} rows but read {read_table.num_rows} rows from {filepath}")
    except Exception as e:
        raise RuntimeError(f"Failed to validate written parquet file at {filepath}: {str(e)}")
