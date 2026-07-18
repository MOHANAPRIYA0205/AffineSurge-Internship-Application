from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.document import DocumentRepository
from app.services.document import DocumentService

def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(session=db)

def get_document_service(repo: DocumentRepository = Depends(get_document_repository)) -> DocumentService:
    return DocumentService(document_repo=repo)
