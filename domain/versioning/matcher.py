from typing import List, Dict, Tuple, Optional
from rapidfuzz import fuzz
from app.domain.hierarchy.models import HierarchyNode

class VersionMatcher:
    """
    Matches new physical nodes to existing logical nodes from a prior version.
    
    The confidence formula used is exactly:
    confidence = (
        0.35 * heading_similarity      # RapidFuzz token_sort_ratio on heading text
      + 0.30 * body_similarity         # RapidFuzz on normalized body text
      + 0.15 * parent_similarity       # 1.0 if matched parent logical node, else 0.0
      + 0.10 * position_similarity     # 1 - normalized distance in reading order
      + 0.10 * path_similarity         # RapidFuzz on heading-path string
    )
    """
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold

    def _get_path(self, node: HierarchyNode, node_map: Dict[str, HierarchyNode]) -> str:
        """Helper to get full path string (e.g. '1.0 Intro > 1.1 Context')"""
        path_parts = []
        curr = node
        while curr:
            if curr.text:
                path_parts.append(curr.text)
            if curr.parent_id and curr.parent_id in node_map:
                curr = node_map[curr.parent_id]
            else:
                break
        return " > ".join(reversed(path_parts))

    def match_versions(self, v1_nodes: List[HierarchyNode], v2_nodes: List[HierarchyNode]) -> List[HierarchyNode]:
        """
        Matches v2 nodes against v1 nodes and updates logical_node_ids of v2 nodes.
        Unmatched v2 nodes retain their randomly generated new logical_node_id.
        Unmatched v1 nodes are effectively 'removed' from the new version.
        """
        v1_map = {n.id: n for n in v1_nodes}
        v2_map = {n.id: n for n in v2_nodes}
        
        # Flatten v1 to list for comparison
        v1_list = v1_nodes
        
        # Keep track of which v1 nodes have been matched to prevent double-matching
        matched_v1 = set()
        
        for n2 in v2_nodes:
            best_score = 0.0
            best_match: Optional[HierarchyNode] = None
            
            n2_path = self._get_path(n2, v2_map)
            
            for n1 in v1_list:
                if n1.id in matched_v1:
                    continue
                    
                # 1. heading_similarity (only relevant if it is a heading, else compare text)
                h_sim = fuzz.token_sort_ratio(n1.text, n2.text) / 100.0
                
                # 2. body_similarity
                b_sim = fuzz.token_sort_ratio(n1.normalized_hash, n2.normalized_hash) / 100.0
                if n1.normalized_hash == n2.normalized_hash:
                    b_sim = 1.0 # Exact match override
                
                # 3. parent_similarity
                p_sim = 0.0
                if n1.parent_id and n2.parent_id:
                    n1_parent = v1_map.get(n1.parent_id)
                    n2_parent = v2_map.get(n2.parent_id)
                    # If the newly assigned logical_node_id of the parent matches the old parent's logical ID
                    if n1_parent and n2_parent and n1_parent.logical_node_id == n2_parent.logical_node_id:
                        p_sim = 1.0
                elif not n1.parent_id and not n2.parent_id:
                    p_sim = 1.0 # Both roots
                
                # 4. position_similarity
                max_pos = max(len(v1_nodes), len(v2_nodes))
                pos_dist = abs(n1.reading_order_index - n2.reading_order_index)
                pos_sim = 1.0 - (pos_dist / max_pos if max_pos > 0 else 0)
                
                # 5. path_similarity
                n1_path = self._get_path(n1, v1_map)
                path_sim = fuzz.token_sort_ratio(n1_path, n2_path) / 100.0
                
                confidence = (
                    0.35 * h_sim +
                    0.30 * b_sim +
                    0.15 * p_sim +
                    0.10 * pos_sim +
                    0.10 * path_sim
                )
                
                if confidence > best_score:
                    best_score = confidence
                    best_match = n1
            
            if best_score >= self.threshold and best_match:
                n2.logical_node_id = best_match.logical_node_id
                matched_v1.add(best_match.id)
                
        return v2_nodes
