"""
Domain logic package.

Responsibility:
- Pure business logic (parser, OCR, hierarchy, versioning, selection, generation, staleness, search).
- Persistence-ignorant functions.
- Use plain dataclasses or Pydantic DTOs.

Allowed Imports:
- Built-in Python modules.
- `app.schemas` (Pydantic models)
- Third-party libraries like `rapidfuzz`, `fitz`, etc.

Strictly Forbidden Imports:
- `app.models` (ORMs/database)
- `app.repositories`
- `app.api`
- `app.services`
"""
