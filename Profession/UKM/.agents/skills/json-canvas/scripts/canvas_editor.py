import argparse
import json
import os
import sys
import uuid
import secrets

def generate_id():
    """Generates a 16-character hex ID similar to Obsidian's."""
    return secrets.token_hex(8)

def load_canvas(file_path):
    if not os.path.exists(file_path):
        # Initialize empty canvas if not exists
        return {"nodes": [], "edges": []}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Ensure basic structure
            if 'nodes' not in data: data['nodes'] = []
            if 'edges' not in data: data['edges'] = []
            return data
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)

def save_canvas(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Success: Updated {file_path}")

def add_node(data, payload):
    # Validate payload
    required_fields = ['type', 'x', 'y', 'width', 'height']
    for field in required_fields:
        if field not in payload:
            print(f"Error: Missing required field '{field}' in payload")
            sys.exit(1)
            
    # Auto-generate ID if missing
    if 'id' not in payload:
        payload['id'] = generate_id()
    
    # Check ID uniqueness
    existing_ids = {n['id'] for n in data['nodes']}
    if payload['id'] in existing_ids:
        print(f"Error: Node ID '{payload['id']}' already exists")
        sys.exit(1)

    data['nodes'].append(payload)
    print(f"Added node: {payload['id']} ({payload['type']})")

def add_edge(data, payload):
    # Validate payload
    required_fields = ['fromNode', 'toNode']
    for field in required_fields:
        if field not in payload:
            print(f"Error: Missing required field '{field}' in payload")
            sys.exit(1)
            
    # Auto-generate ID if missing
    if 'id' not in payload:
        payload['id'] = generate_id()

    # Check existence of source/target nodes
    node_ids = {n['id'] for n in data['nodes']}
    if payload['fromNode'] not in node_ids:
        print(f"Error: fromNode '{payload['fromNode']}' does not exist")
        sys.exit(1)
    if payload['toNode'] not in node_ids:
        print(f"Error: toNode '{payload['toNode']}' does not exist")
        sys.exit(1)

    data['edges'].append(payload)
    print(f"Added edge: {payload['fromNode']} -> {payload['toNode']}")

def update_node(data, payload):
    # Payload must have 'id'
    if 'id' not in payload:
        print("Error: Payload must contain 'id' for update")
        sys.exit(1)
        
    target_id = payload['id']
    found = False
    for node in data['nodes']:
        if node['id'] == target_id:
            # Update fields
            for k, v in payload.items():
                if k != 'id': # Don't update ID
                    node[k] = v
            found = True
            print(f"Updated node: {target_id}")
            break
            
    if not found:
        print(f"Error: Node ID '{target_id}' not found")
        sys.exit(1)

def update_edge(data, payload):
    # Payload must have 'id'
    if 'id' not in payload:
        print("Error: Payload must contain 'id' for update")
        sys.exit(1)
        
    target_id = payload['id']
    found = False
    for edge in data['edges']:
        if edge['id'] == target_id:
            # Update fields
            for k, v in payload.items():
                if k != 'id': # Don't update ID
                    edge[k] = v
            found = True
            print(f"Updated edge: {target_id}")
            break
            
    if not found:
        print(f"Error: Edge ID '{target_id}' not found")
        sys.exit(1)

def delete_node(data, payload):
    if 'id' not in payload:
        print("Error: Payload must contain 'id' for delete")
        sys.exit(1)
        
    target_id = payload['id']
    initial_count = len(data['nodes'])
    data['nodes'] = [n for n in data['nodes'] if n['id'] != target_id]
    
    if len(data['nodes']) < initial_count:
        # Also remove connected edges
        data['edges'] = [e for e in data['edges'] if e['fromNode'] != target_id and e['toNode'] != target_id]
        print(f"Deleted node: {target_id}")
    else:
        print(f"Error: Node ID '{target_id}' not found")
        sys.exit(1)


def execute_action(action, data, payload):
    if action == 'add_node':
        add_node(data, payload)
    elif action == 'add_edge':
        add_edge(data, payload)
    elif action == 'update_node':
        update_node(data, payload)
    elif action == 'update_edge':
        update_edge(data, payload)
    elif action == 'delete_node':
        delete_node(data, payload)
    else:
        print(f"Error: Unknown action '{action}'")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Edit JSON Canvas files via CLI.")
    parser.add_argument('--file', required=True, help="Path to the .canvas file")
    parser.add_argument('--action', required=True, choices=['add_node', 'add_edge', 'update_node', 'update_edge', 'delete_node', 'batch'], help="Action to perform")
    parser.add_argument('--payload', required=True, help="JSON string representing the node or edge object (or list of objects for batch)")

    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError:
        print("Error: Payload argument is not valid JSON")
        sys.exit(1)

    data = load_canvas(args.file)

    if args.action == 'batch':
        if not isinstance(payload, list):
            print("Error: Payload for 'batch' action must be a JSON list")
            sys.exit(1)
        
        print(f"Processing batch ({len(payload)} operations)...")
        for i, op in enumerate(payload):
            if 'action' not in op:
                print(f"Error: Batch operation #{i} missing 'action' field")
                sys.exit(1)
            
            action = op['action']
            op_payload = op.copy()
            op_payload.pop('action', None)
            
            print(f"--- Op {i+1}: {action} ---")
            execute_action(action, data, op_payload)
    else:
        execute_action(args.action, data, payload)

    save_canvas(args.file, data)

if __name__ == "__main__":
    main()
