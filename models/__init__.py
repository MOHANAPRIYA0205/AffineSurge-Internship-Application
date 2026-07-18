"""
Database models package.

Responsibility:
- Define SQLAlchemy (relational) models.
- Define MongoDB document shapes.

Allowed Imports:
- Third-party database libraries (`sqlalchemy`, `pymongo`).

Strictly Forbidden Imports:
- `app.api`
- `app.services`
- `app.domain` (avoid circular dependencies; models shouldn't know about domain logic)
"""

from app.models.base import Base
from app.models.relational import (
    Document, DocumentVersion, LogicalNode, PhysicalNode,
    Selection, SelectionNode, Generation, GenerationTestCase, GenerationHash
)

__all__ = [
    "Base", "Document", "DocumentVersion", "LogicalNode", "PhysicalNode",
    "Selection", "SelectionNode", "Generation", "GenerationTestCase", "GenerationHash"
]
