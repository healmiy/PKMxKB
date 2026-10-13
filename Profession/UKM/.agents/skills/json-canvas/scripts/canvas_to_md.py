import json
import os
import sys

def get_node_content(node):
    """Returns the formatted markdown content for a node."""
    node_type = node.get('type')
    content = ""
    
    if node_type == 'text':
        text = node.get('text', '').strip()
        if text:
            content = f"{text}\n"
            
    elif node_type == 'file':
        file_path = node.get('file')
        if file_path:
            # Check for image extensions
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                return ""
            content = f"**File Reference**: [[{file_path}]]\n"
            
    elif node_type == 'group':
        label = node.get('label')
        if label:
            content = f"\n## {label}\n"
            
    elif node_type == 'link':
        url = node.get('url')
        if url:
            content = f"**Link**: {url}\n"
            
    return content

def convert_canvas_to_md(canvas_path):
    try:
        with open(canvas_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading canvas file: {e}")
        return

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    if not nodes:
        print("No nodes found in canvas.")
        return

    # 1. Build the Graph and Identify Groups
    node_map = {node['id']: node for node in nodes}
    adj = {node['id']: [] for node in nodes} 
    in_degree = {node['id']: 0 for node in nodes}
    
    # Identify Groups and Containment
    groups = [n for n in nodes if n.get('type') == 'group']
    node_to_group = {} # node_id -> group_id
    
    def get_bounds(n):
        return (n.get('x', 0), n.get('y', 0), n.get('x', 0) + n.get('width', 0), n.get('y', 0) + n.get('height', 0))

    def is_contained(inner_node, outer_group):
        if 'width' not in inner_node or 'height' not in inner_node: return False
        ix, iy, ix2, iy2 = get_bounds(inner_node)
        gx, gy, gx2, gy2 = get_bounds(outer_group)
        return gx <= ix and gy <= iy and gx2 >= ix2 and gy2 >= iy2

    for node in nodes:
        if node.get('type') == 'group': continue
        # Find if this node is inside any group
        # If overlapping multiple, take the smallest one? Or just the first one found.
        # Canvas usually doesn't have overlapping groups, simple check is fine.
        for g in groups:
            if is_contained(node, g):
                node_to_group[node['id']] = g['id']
                break

    for edge in edges:
        from_node = edge.get('fromNode')
        to_node = edge.get('toNode')
        label = edge.get('label', '')
        
        if from_node in node_map and to_node in node_map:
            adj[from_node].append({'to': to_node, 'label': label})
            in_degree[to_node] += 1

    # 2. Sort children
    for store_id in adj:
        adj[store_id].sort(key=lambda x: (node_map[x['to']].get('y', 0), node_map[x['to']].get('x', 0)))

    visited = set()
    output_lines = []
    
    basename = os.path.basename(canvas_path)
    title = os.path.splitext(basename)[0]
    output_lines.append(f"# {title}\n")

    def traverse(node_id, current_group_id):
        if node_id in visited:
            return
        
        # If we are strictly processing a group, don't jump out of it
        # Unless the node has no group, then maybe it's fine? 
        # But 'current_group_id' implies the section we are in.
        node_group = node_to_group.get(node_id)
        
        if current_group_id is not None and node_group != current_group_id:
            # We hit a boundary. Link to it instead of printing.
            target_group = node_map.get(node_group) if node_group else None
            group_name = target_group.get('label', 'General') if target_group else "Ungrouped"
            output_lines.append(f"> *↪️ Continues in section: [{group_name}]*\n\n")
            return

        visited.add(node_id)
        node = node_map[node_id]
        
        # Add Node Content
        content = get_node_content(node)
        if content:
            output_lines.append(content)
            if node.get('type') != 'group':
                output_lines.append("\n---\n")

        # Traverse Children
        children = adj[node_id]
        for child_info in children:
            child_id = child_info['to']
            edge_label = child_info['label']
            
            # Check containment before recursing to avoid printing "continues in..." if it's already visited
            if child_id not in visited:
                child_group = node_to_group.get(child_id)
                
                # Add Edge Label if present
                if edge_label:
                    output_lines.append(f"> *➡️ {edge_label}*\n\n")
                
                traverse(child_id, current_group_id)

    # 3. Process by Sections (Groups)
    # Sort groups by Y, X
    groups.sort(key=lambda g: (g['y'], g['x']))
    
    for g in groups:
        group_id = g['id']
        label = g.get('label', 'Untitled Group')
        output_lines.append(f"\n## {label}\n\n")
        
        # Find nodes in this group
        group_nodes = [n for n in nodes if node_to_group.get(n['id']) == group_id]
        if not group_nodes:
            continue
            
        # Sort by Y, X
        group_nodes.sort(key=lambda n: (n['y'], n['x']))
        
        # Find local roots (nodes in group with no incoming edges from INSIDE the group)
        # Or just iterate all unvisited nodes in the group
        for node in group_nodes:
            if node['id'] not in visited:
                traverse(node['id'], group_id)

    # 4. Process Ungrouped Nodes
    ungrouped_nodes = [n for n in nodes if n['id'] not in node_to_group and n.get('type') != 'group']
    if ungrouped_nodes:
        output_lines.append(f"\n## Ungrouped\n\n")
        ungrouped_nodes.sort(key=lambda n: (n.get('y', 0), n.get('x', 0)))
        
        for node in ungrouped_nodes:
            if node['id'] not in visited:
                 traverse(node['id'], None)

    # Write to file
    output_path = os.path.splitext(canvas_path)[0] + ".md"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))
        print(f"Successfully converted '{canvas_path}' to '{output_path}'")
    except Exception as e:
        print(f"Error writing markdown file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 canvas_to_md.py <path_to_canvas_file>")
    else:
        convert_canvas_to_md(sys.argv[1])
