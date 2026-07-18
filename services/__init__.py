"""
Services package.

Responsibility:
- Orchestrate repositories and domain modules.
- Manage transaction boundaries.
- Contain business workflow logic but NOT core domain rules.

Allowed Imports:
- `app.repositories` (interfaces only)
- `app.domain` (stateless domain logic)
- `app.schemas`

Strictly Forbidden Imports:
- `app.models` (SQLAlchemy models)
- `app.api` (HTTP/FastAPI specific classes)
"""
