"""
API routes package.

Responsibility:
- Validate input via Pydantic schemas.
- Route HTTP requests to the appropriate service methods.
- Map service layer results and exceptions to HTTP responses.

Allowed Imports:
- `app.services`
- `app.schemas` (Pydantic models)
- `app.core.dependencies`

Strictly Forbidden Imports:
- `app.models` (SQLAlchemy/MongoDB directly)
- `app.repositories` (Database queries)
- `app.domain` (Domain logic)
"""
