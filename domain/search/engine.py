import re
from typing import List, Dict, Any

class SearchResult:
    def __init__(self, node_id: str, score: float, snippet: str):
        self.node_id = node_id
        self.score = score
        self.snippet = snippet

def generate_snippet(text: str, query: str, context_len: int = 30) -> str:
    """Generates a snippet with <mark> tags for the first match."""
    if not text:
        return ""
        
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(text)
    
    if not match:
        return text[:context_len * 2] + "..." if len(text) > context_len * 2 else text
        
    start_idx = max(0, match.start() - context_len)
    end_idx = min(len(text), match.end() + context_len)
    
    snippet = text[start_idx:end_idx]
    
    # Add ellipsis if truncated
    if start_idx > 0:
        snippet = "..." + snippet
    if end_idx < len(text):
        snippet = snippet + "..."
        
    # Highlight
    highlighted = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", snippet)
    return highlighted

def search_nodes(query: str, nodes: List[Any], scope: str = "both") -> List[SearchResult]:
    """
    Case-insensitive partial match search.
    Scope: 'heading', 'body', 'both'.
    Ranking: Simple term frequency of the exact query string (case-insensitive).
    """
    if not query.strip():
        return []
        
    query_lower = query.lower()
    results = []
    
    for node in nodes:
        score = 0
        snippet = ""
        
        # We assume node has 'text' and 'node_type' or 'heading_text'/'body_text'
        # The prompt says denormalized search doc has heading_text and body_text.
        # We'll support both direct text and body/heading attributes for flexibility
        
        heading_text = getattr(node, "heading_text", "")
        body_text = getattr(node, "body_text", "")
        
        # Fallback if using HierarchyNode directly
        if not heading_text and not body_text:
            if getattr(node, "node_type", None) == "heading" or getattr(node, "node_type", None) == "title":
                heading_text = getattr(node, "text", "")
            else:
                body_text = getattr(node, "text", "")
        
        if scope in ["heading", "both"] and heading_text:
            matches = heading_text.lower().count(query_lower)
            if matches > 0:
                score += matches * 2 # Headings weigh more
                if not snippet:
                    snippet = generate_snippet(heading_text, query)
                    
        if scope in ["body", "both"] and body_text:
            matches = body_text.lower().count(query_lower)
            if matches > 0:
                score += matches
                if not snippet:
                    snippet = generate_snippet(body_text, query)
                    
        if score > 0:
            node_id = getattr(node, "logical_node_id", getattr(node, "id", None))
            results.append(SearchResult(node_id=node_id, score=score, snippet=snippet))
            
    # Rank descending by score
    results.sort(key=lambda x: x.score, reverse=True)
    return results
