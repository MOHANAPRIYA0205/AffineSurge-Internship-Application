from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from app.api.schemas import (
    DocumentResponse, VersionResponse, NodeResponse, SearchResponse,
    SelectionCreate, SelectionResponse, GenerationTriggerResponse, GenerationStatusResponse
)
from typing import List

router = APIRouter()

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Must be a PDF file")
    # Mock return for testing API contract
    return {"document_id": "doc_123", "version_id": "v1"}

@router.get("/documents/{document_id}/versions", response_model=List[VersionResponse])
def list_versions(document_id: str):
    return [{"version_id": "v1", "created_at": "2024-01-01T00:00:00Z"}]

@router.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: str):
    return {"id": "phy_1", "logical_node_id": node_id, "text": "Mock Node Text", "children": []}

@router.get("/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=1), scope: str = Query("both", pattern="^(heading|body|both)$")):
    return {"results": [{"node_id": "n1", "score": 1.0, "snippet": f"<mark>{q}</mark>"}]}

@router.post("/selections", response_model=SelectionResponse)
def create_selection(sel: SelectionCreate):
    return {"id": "sel_1", "status": "current"}

@router.get("/selections/{selection_id}", response_model=SelectionResponse)
def get_selection(selection_id: str):
    return {"id": selection_id, "status": "current"}

@router.post("/selections/{selection_id}/generate", response_model=GenerationTriggerResponse, status_code=202)
def trigger_generation(selection_id: str, background_tasks: BackgroundTasks):
    return {"generation_id": "gen_1"}

@router.get("/generations/{generation_id}", response_model=GenerationStatusResponse)
def get_generation_status(generation_id: str):
    return {"status": "success", "result": {"test_cases": []}}
