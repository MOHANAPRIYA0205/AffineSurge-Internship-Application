from typing import Dict, List, Any
import uuid

class ImmutableSelectionError(Exception):
    pass

class SelectionManager:
    """
    Manages user selections of nodes. 
    Selections are strictly immutable and permanently pinned to the version_id they were created against.
    """
    
    def create_selection(self, logical_node_id: str, version_id: str, created_by: str = None, label: str = None) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "logical_node_id": logical_node_id,
            "version_id": version_id,
            "created_by": created_by,
            "label": label
        }
        
    def update_selection(self, selection_id: str, **kwargs):
        """
        Attempting to update a selection will raise an exception to strictly enforce immutability.
        """
        raise ImmutableSelectionError("Selections are immutable after creation and cannot be updated.")
        
    def resolve_selection(self, selection: dict, all_versions_nodes: Dict[str, List[Any]]) -> Any:
        """
        Resolves the selection to the exact physical node from the pinned version.
        
        Args:
            selection: The selection dict returned by create_selection.
            all_versions_nodes: A mapping of version_id to a list of physical nodes available in the DB.
        """
        version_nodes = all_versions_nodes.get(selection["version_id"], [])
        
        for node in version_nodes:
            node_logical_id = getattr(node, "logical_node_id", getattr(node, "id", None))
            if node_logical_id == selection["logical_node_id"]:
                return node
                
        return None
