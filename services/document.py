from app.repositories.document import DocumentRepository

class DocumentService:
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo

    def fetch_document(self, document_id: str):
        return self.document_repo.get_document(document_id)
