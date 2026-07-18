from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
from app.models.relational import NodeType

class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

class ParsedBlock(BaseModel):
    text: str
    bbox: BoundingBox
    page_number: int
    node_type: NodeType = NodeType.paragraph
    heading_level: Optional[int] = None
    confidence: float = 1.0
    reading_order_index: int = -1
    is_native_text: bool = True
    font_size: Optional[float] = None

class DocumentPayload(BaseModel):
    blocks: List[ParsedBlock]
    raw_layouts: List[dict] = Field(default_factory=list)
    raw_ocr: List[dict] = Field(default_factory=list)
