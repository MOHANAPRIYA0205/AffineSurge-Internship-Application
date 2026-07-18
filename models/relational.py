import uuid
from typing import List, Optional
from datetime import datetime
import enum

from sqlalchemy import String, ForeignKey, Integer, JSON, Enum, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditableMixin, ImmutableMixin

class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class NodeType(str, enum.Enum):
    title = "title"
    heading = "heading"
    paragraph = "paragraph"
    list = "list"
    table = "table"
    figure = "figure"
    caption = "caption"
    footnote = "footnote"

class GenerationStatus(str, enum.Enum):
    success = "success"
    validation_failed = "validation_failed"
    provider_error = "provider_error"

class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Document(Base, AuditableMixin):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False)

class DocumentVersion(Base, AuditableMixin):
    __tablename__ = "document_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(nullable=False)
    source_file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False)

    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_doc_version"),
    )

class LogicalNode(Base, AuditableMixin):
    __tablename__ = "logical_nodes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)

class PhysicalNode(Base, AuditableMixin):
    __tablename__ = "physical_nodes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    logical_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("logical_nodes.id"), nullable=False)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_versions.id"), nullable=False)
    parent_physical_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("physical_nodes.id"), nullable=True)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    heading_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    heading_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    bounding_box: Mapped[dict] = mapped_column(JSON, nullable=False)
    reading_order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_hash: Mapped[str] = mapped_column(String, nullable=False)
    normalized_hash: Mapped[str] = mapped_column(String, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False) # metadata is a reserved attribute on Base

    __table_args__ = (
        Index("ix_physical_nodes_version_reading_order", "version_id", "reading_order_index"),
        Index("ix_physical_nodes_logical_node_id", "logical_node_id"),
    )

class Selection(Base, ImmutableMixin):
    __tablename__ = "selections"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    logical_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("logical_nodes.id"), nullable=False)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_versions.id"), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_selections_logical_node_version", "logical_node_id", "version_id"),
    )

class SelectionNode(Base):
    __tablename__ = "selection_nodes"
    selection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("selections.id"), primary_key=True)
    physical_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("physical_nodes.id"), primary_key=True)

class Generation(Base, AuditableMixin):
    __tablename__ = "generations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    selection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("selections.id"), nullable=False)
    status: Mapped[GenerationStatus] = mapped_column(Enum(GenerationStatus), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String, nullable=False)
    llm_model: Mapped[str] = mapped_column(String, nullable=False)
    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class GenerationTestCase(Base, ImmutableMixin):
    __tablename__ = "generation_test_cases"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), nullable=False)
    requirement_reference: Mapped[str] = mapped_column(String, nullable=False)

    selection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("selections.id"), nullable=False)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_versions.id"), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String, nullable=False)
    llm_model: Mapped[str] = mapped_column(String, nullable=False)

class GenerationHash(Base, ImmutableMixin):
    __tablename__ = "generation_hashes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generations.id"), nullable=False)
    physical_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("physical_nodes.id"), nullable=False)
    normalized_hash_at_generation_time: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("generation_id", "physical_node_id", name="uq_gen_hash_node"),
    )
