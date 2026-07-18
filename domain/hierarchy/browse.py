from typing import List, Dict, Any, Optional

def get_node_with_children(target_id: str, all_nodes: List[Any]) -> Optional[Dict[str, Any]]:
    """
    Given a target logical_node_id and a list of nodes, returns the node and its immediate children.
    """
    target_node = None
    children = []
    
    for node in all_nodes:
        node_id = getattr(node, "logical_node_id", getattr(node, "id", None))
        parent_id = getattr(node, "parent_id", None)
        
        if node_id == target_id:
            target_node = node
            
        # If node has children attribute already populated (e.g. HierarchyNode)
        if hasattr(node, "children") and node_id == target_id:
            return {
                "node": target_node,
                "children": getattr(node, "children")
            }
            
        if parent_id == target_id:
            children.append(node)
            
    if not target_node:
        return None
        
    return {
        "node": target_node,
        "children": children
    }
