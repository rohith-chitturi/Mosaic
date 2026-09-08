import sys
import os
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.generator.domains.universe import DataUniverse
from data.generator.eras.era_2022 import Era2022
from data.generator.exporters.parquet_exporter import export_to_parquet

try:
    import pyarrow.parquet as pq
    import pyarrow as pa
except ImportError:
    # Pyarrow is strictly required for this test, fail loudly.
    print("FATAL ERROR: pyarrow is required for testing parquet generation.")
    sys.exit(1)

def test_parquet_generation():
    print("Running Parquet generation validation...")
    
    # 1. Setup deterministic universe
    u = DataUniverse(seed=42, scale="small")
    u.generate_canonical_only()
    
    # Clean output dir
    output_dir = os.path.join("data", "generated")
    test_lake_dir = os.path.join(output_dir, "2022_lake")
    if os.path.exists(test_lake_dir):
        shutil.rmtree(test_lake_dir)
        
    # 2. Generate 2022 dataset
    era_2022 = Era2022(u, output_dir)
    era_2022.generate()
    
    parquet_path = os.path.join(test_lake_dir, "customer_features", "year=2022", "month=01", "part-0000.parquet")
    
    assert os.path.exists(parquet_path), "Parquet file was not generated at expected path."
    
    # 3. Read generated Parquet
    table = pq.read_table(parquet_path)
    
    # 4. Compare row counts
    expected_count = len(u.customers)
    assert table.num_rows == expected_count, f"Row count mismatch: expected {expected_count}, got {table.num_rows}"
    
    # 5. Compare schemas
    schema = table.schema
    expected_columns = ["customer_id", "customer_transaction_total", "first_name", "is_active", "last_name"]
    # Depending on how pyarrow reads, it might inject partition columns since the path is hive-partitioned.
    # We verify that our logical columns are present.
    assert set(expected_columns).issubset(set(schema.names)), f"Schema columns mismatch: {schema.names} does not contain {expected_columns}"
    
    # Verify deterministic regeneration
    # Generate again into a different folder to compare logical content
    second_output_dir = os.path.join("data", "generated_second")
    second_lake_dir = os.path.join(second_output_dir, "2022_lake")
    if os.path.exists(second_lake_dir):
        shutil.rmtree(second_lake_dir)
        
    u2 = DataUniverse(seed=42, scale="small")
    u2.generate_canonical_only()
    era_2022_second = Era2022(u2, second_output_dir)
    era_2022_second.generate()
    
    second_parquet_path = os.path.join(second_lake_dir, "customer_features", "year=2022", "month=01", "part-0000.parquet")
    table2 = pq.read_table(second_parquet_path)
    
    # 6. Verify deterministic logical records
    # Arrow tables implement __eq__ which does a deep comparison of schemas and columns
    assert table.equals(table2), "Determinism failed! Identical logical data produced different Arrow Tables."
    
    print("Parquet validation tests passed.")
    
if __name__ == "__main__":
    test_parquet_generation()
