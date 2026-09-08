import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from services.discovery.app.config import settings
from services.discovery.events.publisher import EventPublisher
from services.discovery.persistence.metadata_repo import MetadataRepository

engine = create_engine(settings.postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_metadata_repo(db: Session) -> MetadataRepository:
    return MetadataRepository(db)

# Singleton publisher
_publisher = EventPublisher(brokers=settings.kafka_brokers)

def get_event_publisher() -> EventPublisher:
    return _publisher

def generate_correlation_id() -> str:
    return f"run_{uuid.uuid4().hex[:12]}"
