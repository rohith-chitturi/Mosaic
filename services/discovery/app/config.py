from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_url: str = "postgresql://mosaic:mosaic_password@localhost:5432/mosaic_discovery"
    kafka_brokers: str = "localhost:9094"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    
    class Config:
        env_file = ".env"

settings = Settings()
