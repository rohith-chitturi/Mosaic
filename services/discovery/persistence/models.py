from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass

class SourceModel(Base):
    __tablename__ = "sources"
    source_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    
class DatasetModel(Base):
    __tablename__ = "datasets"
    dataset_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)

class DatasetVersionModel(Base):
    __tablename__ = "dataset_versions"
    version_id: Mapped[str] = mapped_column(String, primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.dataset_id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    partitions: Mapped[list] = mapped_column(JSON, nullable=True)
    file_count: Mapped[int] = mapped_column(Integer, nullable=True)
    total_bytes: Mapped[int] = mapped_column(Integer, nullable=True)

class SchemaModel(Base):
    __tablename__ = "schemas"
    schema_fingerprint: Mapped[str] = mapped_column(String, primary_key=True)

class ColumnModel(Base):
    __tablename__ = "columns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schema_fingerprint: Mapped[str] = mapped_column(ForeignKey("schemas.schema_fingerprint"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    physical_type: Mapped[str] = mapped_column(String, nullable=False)
    nullable: Mapped[bool] = mapped_column(Boolean, default=True)
    ordinal_position: Mapped[int] = mapped_column(Integer, nullable=False)

class ObservationModel(Base):
    __tablename__ = "observations"
    observation_id: Mapped[str] = mapped_column(String, primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[str] = mapped_column(String, nullable=False)
    version_id: Mapped[str] = mapped_column(String, nullable=False)
    schema_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
