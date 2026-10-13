#!/usr/bin/env python3
"""
canvas_to_blocks.py - Extract clean text blocks from .canvas files for RAG embedding

This mimics Smart Connections' block embedding format but for canvas files.
It extracts only the meaningful TEXT content from nodes, ignoring JSON structure.

Output format matches SmartBlock pattern:
  - breadcrumbs + "\n" + content
  - breadcrumbs = "path > canvasfile > NodeTitle/Preview"

Usage:
  python3 canvas_to_blocks.py "path/to/file.canvas"
  python3 canvas_to_blocks.py "path/to/file.canvas" --output json
  python3 canvas_to_blocks.py "path/to/file.canvas" --output md
"""

import json
import os
import sys
import re
import argparse
from typing import List, Dict, Any, Optional

def get_node_title(node: Dict[str, Any], max_length: int = 50) -> str:
    """
    Extract a title/preview from a node's content.
    Similar to how SmartBlock creates breadcrumbs from headings.
    """
    node_type = node.get('type', '')
    
    if node_type == 'text':
        text = node.get('text', '').strip()
        if not text:
            return f"TextNode_{node['id'][:8]}"
        
        # Try to extract first heading
        heading_match = re.match(r'^#{1,6}\s+(.+)$', text, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()[:max_length]
        
        # Otherwise use first line as preview
        first_line = text.split('\n')[0].strip()
        # Remove markdown formatting
        first_line = re.sub(r'[*_`#\[\]]', '', first_line)
        if len(first_line) > max_length:
            return first_line[:max_length-3] + "..."
        return first_line if first_line else f"TextNode_{node['id'][:8]}"
    
    elif node_type == 'file':
        file_path = node.get('file', '')
        if file_path:
            return os.path.basename(file_path)
        return f"FileNode_{node['id'][:8]}"
    
    elif node_type == 'group':
        return node.get('label', f"Group_{node['id'][:8]}")
    
    elif node_type == 'link':
        url = node.get('url', '')
        return url[:max_length] if url else f"LinkNode_{node['id'][:8]}"
    
    return f"Node_{node['id'][:8]}"

def get_node_content(node: Dict[str, Any]) -> str:
    """
    Extract the clean text content from a node.
    This is what gets embedded.
    """
    node_type = node.get('type', '')
    
    if node_type == 'text':
        return node.get('text', '').strip()
    
    elif node_type == 'file':
        file_path = node.get('file', '')
        if file_path:
            # Skip images - they don't have meaningful text
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp']:
                return ""
            return f"Reference to: {file_path}"
        return ""
    
    elif node_type == 'group':
        label = node.get('label', '')
        return f"Group: {label}" if label else ""
    
    elif node_type == 'link':
        url = node.get('url', '')
        return f"External link: {url}" if url else ""
    
    return ""

def parse_canvas_blocks(canvas_path: str) -> List[Dict[str, Any]]:
    """
    Parse a canvas file and extract blocks similar to Smart Connections' format.
    
    Returns list of blocks with:
    - key: "canvasfile.canvas#node_id"
    - breadcrumbs: "folder > filename > NodeTitle"
    - content: clean text content
    - embed_input: breadcrumbs + "\n" + content (ready for embedding)
    - lines: [start, end] (simulated as node index)
    """
    try:
        with open(canvas_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading canvas file: {e}", file=sys.stderr)
        return []
    
    nodes = data.get('nodes', [])
    if not nodes:
        return []
    
    # Build breadcrumb prefix from path
    canvas_name = os.path.basename(canvas_path)
    canvas_dir = os.path.dirname(canvas_path)
    folder_name = os.path.basename(canvas_dir) if canvas_dir else ""
    
    # Similar to SmartBlock.breadcrumbs format
    base_breadcrumb = f"{folder_name} > {canvas_name}".lstrip(" >")
    
    blocks = []
    
    # Sort nodes by position (top-to-bottom, left-to-right)
    nodes_sorted = sorted(nodes, key=lambda n: (n.get('y', 0), n.get('x', 0)))
    
    for idx, node in enumerate(nodes_sorted):
        node_id = node.get('id', f'node_{idx}')
        content = get_node_content(node)
        
        # Skip empty content (images, empty nodes)
        if not content:
            continue
        
        node_title = get_node_title(node)
        
        # Build key like SmartBlock: "file#heading"
        key = f"{canvas_name}#{node_id}"
        
        # Build breadcrumbs like SmartBlock
        breadcrumbs = f"{base_breadcrumb} > {node_title}"
        
        # The embed_input is what gets sent to the embedding model
        embed_input = f"{breadcrumbs}\n{content}"
        
        block = {
            'key': key,
            'node_id': node_id,
            'type': node.get('type'),
            'breadcrumbs': breadcrumbs,
            'content': content,
            'embed_input': embed_input,
            'lines': [idx, idx + 1],  # Simulated line range
            'position': {
                'x': node.get('x', 0),
                'y': node.get('y', 0)
            }
        }
        blocks.append(block)
    
    return blocks

def output_as_markdown(blocks: List[Dict[str, Any]], canvas_path: str) -> str:
    """
    Output blocks as markdown suitable for embedding or review.
    """
    canvas_name = os.path.splitext(os.path.basename(canvas_path))[0]
    lines = [f"# {canvas_name} - Blocks for Embedding\n"]
    
    for block in blocks:
        lines.append(f"## {block['breadcrumbs']}")
        lines.append(f"<!-- key: {block['key']} -->")
        lines.append("")
        lines.append(block['content'])
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)

def output_as_json(blocks: List[Dict[str, Any]]) -> str:
    """
    Output blocks as JSON (for programmatic use).
    """
    return json.dumps(blocks, indent=2, ensure_ascii=False)

def output_as_embed_inputs(blocks: List[Dict[str, Any]]) -> str:
    """
    Output just the embed_input strings (what would be sent to embedding model).
    """
    lines = []
    for block in blocks:
        lines.append(f"=== BLOCK: {block['key']} ===")
        lines.append(block['embed_input'])
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description='Extract clean text blocks from .canvas files for RAG embedding'
    )
    parser.add_argument('canvas_path', help='Path to the .canvas file')
    parser.add_argument(
        '--output', '-o',
        choices=['json', 'md', 'embed', 'summary'],
        default='summary',
        help='Output format: json, md (markdown), embed (raw embed inputs), summary (default)'
    )
    parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='Save output to file instead of stdout'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.canvas_path):
        print(f"Error: File not found: {args.canvas_path}", file=sys.stderr)
        sys.exit(1)
    
    blocks = parse_canvas_blocks(args.canvas_path)
    
    if not blocks:
        print("No embeddable blocks found in canvas.", file=sys.stderr)
        sys.exit(1)
    
    if args.output == 'json':
        output = output_as_json(blocks)
        ext = '.blocks.json'
    elif args.output == 'md':
        output = output_as_markdown(blocks, args.canvas_path)
        ext = '.blocks.md'
    elif args.output == 'embed':
        output = output_as_embed_inputs(blocks)
        ext = '.embed.txt'
    else:  # summary
        print(f"Canvas: {args.canvas_path}")
        print(f"Total nodes: {len(blocks)}")
        print("")
        print("Blocks (ready for embedding):")
        print("-" * 60)
        for block in blocks:
            content_preview = block['content'][:80].replace('\n', ' ')
            if len(block['content']) > 80:
                content_preview += "..."
            print(f"  [{block['type']}] {block['breadcrumbs']}")
            print(f"       → {content_preview}")
            print()
        return
    
    if args.save:
        output_path = os.path.splitext(args.canvas_path)[0] + ext
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to: {output_path}", file=sys.stderr)
    else:
        print(output)

if __name__ == "__main__":
    main()
