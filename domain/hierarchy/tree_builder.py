from typing import List, Optional
from app.domain.parser.models import ParsedBlock
from app.models.relational import NodeType
from app.domain.hierarchy.models import HierarchyNode
from app.domain.hierarchy.normalizer import normalize_text, compute_hash

def build_tree(blocks: List[ParsedBlock]) -> List[HierarchyNode]:
    """
    Converts a flat ordered block stream into a parent/child tree.
    """
    root_nodes: List[HierarchyNode] = []
    open_headings: List[HierarchyNode] = []
    last_figure_or_table: Optional[HierarchyNode] = None

    for block in blocks:
        normalized = normalize_text(block.text)
        original_hash = compute_hash(block.text)
        normalized_hash = compute_hash(normalized)
        
        node = HierarchyNode(
            node_type=block.node_type,
            heading_level=block.heading_level,
            text=block.text,
            original_hash=original_hash,
            normalized_hash=normalized_hash,
            page_number=block.page_number,
            bounding_box=block.bbox.model_dump(),
            reading_order_index=block.reading_order_index
        )
        
        if node.node_type == NodeType.caption:
            if last_figure_or_table:
                node.parent_id = last_figure_or_table.id
                last_figure_or_table.children.append(node)
            else:
                _attach_to_nearest_heading(node, open_headings, root_nodes)
        elif node.node_type == NodeType.heading:
            level = node.heading_level or 1
            while open_headings and (open_headings[-1].heading_level or 1) >= level:
                open_headings.pop()
            
            if open_headings:
                parent = open_headings[-1]
                node.parent_id = parent.id
                parent.children.append(node)
            else:
                root_nodes.append(node)
                
            open_headings.append(node)
        else:
            _attach_to_nearest_heading(node, open_headings, root_nodes)
            
            if node.node_type in [NodeType.figure, NodeType.table]:
                last_figure_or_table = node
                
    return root_nodes

def _attach_to_nearest_heading(node: HierarchyNode, open_headings: List[HierarchyNode], root_nodes: List[HierarchyNode]):
    if open_headings:
        parent = open_headings[-1]
        node.parent_id = parent.id
        parent.children.append(node)
    else:
        root_nodes.append(node)
