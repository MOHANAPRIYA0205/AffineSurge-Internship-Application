"""
MongoDB Collection Documentation

This module documents the structure of the MongoDB collections used for
storing large/semi-structured artifacts that don't fit the relational schema.

Collections:

1. `ocr_layouts`
----------------
Purpose: Stores raw PP-Structure layout output per page.
Example Document:
{
    "_id": ObjectId("..."),
    "document_id": UUID("..."),
    "version_id": UUID("..."),
    "page_number": 1,
    "layout_regions": [
        {
            "type": "figure",
            "bbox": [10.0, 20.5, 300.0, 400.0],
            "confidence": 0.98
        },
        ...
    ],
    "created_at": ISODate("2024-05-01T10:00:00Z")
}

2. `ocr_blocks`
---------------
Purpose: Stores raw PaddleOCR block recognition output.
Example Document:
{
    "_id": ObjectId("..."),
    "document_id": UUID("..."),
    "version_id": UUID("..."),
    "page_number": 1,
    "blocks": [
        {
            "bbox": [[10, 20], [100, 20], [100, 40], [10, 40]],
            "text": "Introduction",
            "confidence": 0.99
        },
        ...
    ],
    "created_at": ISODate("2024-05-01T10:00:05Z")
}

3. `search_documents`
---------------------
Purpose: Denormalized full-text search document per `document_version` used
by the search index (used by Step 7).
Example Document:
{
    "_id": ObjectId("..."),
    "document_id": UUID("..."),
    "version_id": UUID("..."),
    "version_number": 2,
    "logical_node_id": UUID("..."),
    "node_type": "paragraph",
    "heading_text": "1.0 Introduction",
    "body_text": "This is the system manual...",
    "page_number": 1,
    "created_at": ISODate("2024-05-01T10:05:00Z")
}
"""
