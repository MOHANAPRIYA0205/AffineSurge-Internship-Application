from sqlalchemy.orm import Session
from app.models.relational import Document

class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_document(self, document_id: str) -> Document | None:
        return self.session.query(Document).filter(Document.id == document_id).first()
