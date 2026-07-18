from pydantic import BaseModel, Field
from typing import List, Optional, Any

class DocumentResponse(BaseModel):
    document_id: str
    version_id: str

class VersionResponse(BaseModel):
    version_id: str
    created_at: str
    
class NodeResponse(BaseModel):
    id: str
    logical_node_id: str
    text: str
    children: List['NodeResponse'] = []
    
class SearchResponse(BaseModel):
    results: List[dict]

class SelectionCreate(BaseModel):
    logical_node_id: str
    version_id: str
    label: Optional[str] = None

class SelectionResponse(BaseModel):
    id: str
    status: str
    diff: Optional[str] = None
    
class GenerationTriggerResponse(BaseModel):
    generation_id: str

class GenerationStatusResponse(BaseModel):
    status: str
    result: Optional[dict] = None
