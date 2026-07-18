import unicodedata
import hashlib
import re

def normalize_text(text: str) -> str:
    """
    Normalizes text for consistent hashing and version matching.
    
    Steps:
    1. Unicode normalization (NFKC).
    2. Convert line endings to single spaces.
    3. Collapse repeated spaces to a single space.
    4. Strip leading and trailing whitespace.
    """
    if not text:
        return ""
    # 1. NFKC
    nfkc_text = unicodedata.normalize('NFKC', text)
    # 2 & 3. Collapse whitespace (including newlines) into single space
    collapsed_text = re.sub(r'\s+', ' ', nfkc_text)
    # 4. Strip
    return collapsed_text.strip()

def compute_hash(text: str) -> str:
    """Computes SHA-256 hash of a given string."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
