import os
import time
import subprocess
import requests
import psycopg2
from minio import Minio

# Configuration
API_URL = "http://127.0.0.1:8000"
DB_URL = "postgresql://mosaic:mosaic_password@127.0.0.1:5432/mosaic_discovery"
MINIO_URL = "127.0.0.1:9000"
BUCKET_NAME = "meridian-lake"

def wait_for_api():
    print("Waiting for FastAPI to be healthy...")
    for _ in range(30):
        try:
            requests.get(f"{API_URL}/docs")
            print("API is up!")
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    raise RuntimeError("API failed to start")

def setup_infrastructure():
    print("Starting docker-compose infrastructure...")
    subprocess.run(["docker", "compose", "-f", "infrastructure/docker-compose.yml", "up", "-d"], check=True)
    time.sleep(10) # Wait for init

def setup_minio_data():
    print("Setting up MinIO bucket and uploading test data...")
    client = Minio(MINIO_URL, access_key="minioadmin", secret_key="minioadmin", secure=False)
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
    
    # Upload representative parquet
    local_file = "data/generated/2022_lake/customer_features/year=2022/month=01/part-0000.parquet"
    if os.path.exists(local_file):
        client.fput_object(BUCKET_NAME, "customer_features/year=2022/month=01/part-0000.parquet", local_file)
    else:
        print(f"WARNING: Test data not found at {local_file}. Please ensure Phase 1 data is generated.")

def verify_database_state(expected_datasets: int):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM datasets;")
    datasets = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM dataset_versions;")
    versions = cur.fetchone()[0]
    
    conn.close()
    
    print(f"Database contains {datasets} datasets and {versions} versions.")
    if expected_datasets > 0:
        assert datasets == expected_datasets, f"Expected {expected_datasets} datasets, got {datasets}"

def test_discovery_flow():
    # Register source
    resp = requests.post(f"{API_URL}/sources", json={
        "source_id": f"SOURCE:minio:{BUCKET_NAME}",
        "source_type": "minio",
        "name": BUCKET_NAME,
        "location": BUCKET_NAME
    })
    resp.raise_for_status()
    print("Source registered.")

    # DISCOVERY RUN 1
    print("Triggering Discovery Run #1...")
    resp = requests.post(f"{API_URL}/scans/SOURCE:minio:{BUCKET_NAME}")
    resp.raise_for_status()
    print("Run #1 Completed:", resp.json())
    
    verify_database_state(expected_datasets=1)

    # DISCOVERY RUN 2 (Idempotency)
    print("Triggering Discovery Run #2 (Idempotency Check)...")
    resp = requests.post(f"{API_URL}/scans/SOURCE:minio:{BUCKET_NAME}")
    resp.raise_for_status()
    print("Run #2 Completed:", resp.json())
    
    print("Verifying Idempotency...")
    verify_database_state(expected_datasets=1) # Should still be 1

    # STOP KAFKA
    print("Stopping Kafka to test failure invariants...")
    subprocess.run(["docker", "compose", "-f", "infrastructure/docker-compose.yml", "stop", "kafka"], check=True)
    time.sleep(5)

    # DISCOVERY RUN 3 (Expect Failure)
    print("Triggering Discovery Run #3 (Expect Failure)...")
    resp = requests.post(f"{API_URL}/scans/SOURCE:minio:{BUCKET_NAME}")
    if resp.status_code == 500:
        print("Run #3 Failed successfully with 500 as expected.")
    else:
        raise RuntimeError(f"Expected 500 Failure, got {resp.status_code}")

    # RESTART KAFKA (Recovery)
    print("Restarting Kafka to test recovery...")
    subprocess.run(["docker", "compose", "-f", "infrastructure/docker-compose.yml", "start", "kafka"], check=True)
    time.sleep(10)

    # DISCOVERY RUN 4 (Recovery check)
    print("Triggering Discovery Run #4 (Expect Recovery)...")
    resp = requests.post(f"{API_URL}/scans/SOURCE:minio:{BUCKET_NAME}")
    resp.raise_for_status()
    print("Run #4 Completed successfully, recovery confirmed!")

if __name__ == "__main__":
    try:
        setup_infrastructure()
        setup_minio_data()
        
        # Start API server in background
        print("Starting FastAPI server in background...")
        api_proc = subprocess.Popen(["uvicorn", "services.discovery.app.main:app", "--host", "127.0.0.1", "--port", "8000"])
        
        wait_for_api()
        test_discovery_flow()
        print("INTEGRATION VERIFICATION: ALL CHECKS PASSED ✅")
    finally:
        print("Cleaning up...")
        if 'api_proc' in locals():
            api_proc.terminate()
        subprocess.run(["docker", "compose", "-f", "infrastructure/docker-compose.yml", "down"])
