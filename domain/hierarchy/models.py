from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uuid
from app.models.relational import NodeType

class HierarchyNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    logical_node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    node_type: NodeType
    heading_level: Optional[int] = None
    text: str
    original_hash: str
    normalized_hash: str
    children: List['HierarchyNode'] = Field(default_factory=list)

    page_number: int
    bounding_box: dict
    reading_order_index: int
