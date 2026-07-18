"""
Repositories package.

Responsibility:
- Provide an abstraction layer for data persistence.
- Execute database queries (SQLAlchemy and MongoDB).
- Implement interfaces defined by the service layer.

Allowed Imports:
- `app.models` (SQLAlchemy and MongoDB models)
- `app.domain` (to map models to domain objects if necessary)
- `app.schemas`

Strictly Forbidden Imports:
- `app.api`
- `app.services`
"""
