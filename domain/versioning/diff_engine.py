import difflib
from typing import Optional, Any

def generate_diff(old_text: str, new_text: str) -> str:
    """Generates a unified diff using difflib."""
    # Ensure lines end with newlines for unified_diff
    old_lines = [line + '\n' for line in old_text.splitlines()]
    new_lines = [line + '\n' for line in new_text.splitlines()]
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile='v_pinned',
        tofile='v_latest',
        lineterm='\n'
    )
    return "".join(diff)

class StalenessDetector:
    def check_staleness(self, pinned_node: Any, latest_node: Optional[Any]) -> tuple[str, Optional[str]]:
        """
        Determines the state of a selection relative to the latest document version.
        Returns:
            Tuple containing (status: str, diff_text: Optional[str])
            Status can be 'current', 'stale', or 'removed'.
        """
        if latest_node is None:
            return "removed", None
            
        if pinned_node.normalized_hash != latest_node.normalized_hash:
            diff = generate_diff(getattr(pinned_node, "text", ""), getattr(latest_node, "text", ""))
            return "stale", diff
            
        return "current", None
