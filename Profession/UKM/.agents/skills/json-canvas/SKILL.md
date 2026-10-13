---
name: json-canvas
description: Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.
---

# JSON Canvas Skill

This skill enables skills-compatible agents to create and edit valid JSON Canvas files (`.canvas`) used in Obsidian and other applications.

## Overview

JSON Canvas is an open file format for infinite canvas data. Canvas files use the `.canvas` extension and contain valid JSON following the [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/).

### Utilities
This skill includes helper scripts in `scripts/`:
*   `canvas_analyzer.py`: Validates structure and Group containment.
*   `canvas_to_md.py`: Converts a Canvas into a linear Markdown document (useful for LLM context).
*   `canvas_to_blocks.py`: Extracts blocks from canvas nodes.
*   `canvas_editor.py`: CLI tool to programmatically add nodes and edges (edit capability). Supports **batch operations** for efficiency.

## Specification Reference
For detailed JSON Canvas schema documentation (Node structures, Edges, Colors, complete examples, layout guidelines, and validation rules), please read `references/spec.md`.

### canvas_editor.py (Editing & Batching)

**Best for**: Adding content (nodes/edges) to a canvas.

**Usage**:
```bash
python3 .agent/skills/json-canvas/scripts/canvas_editor.py --file "path/to/file.canvas" --action [add_node|add_edge|update_node|delete_node|batch] --payload 'JSON_STRING'
```

#### Batch Mode (Recommended)
Use `--action batch` to perform multiple operations in a single tool call. This is **highly recommended** for agents to improve token efficiency and reliability.

**Payload Format**: A JSON List of operation objects. Each object MUST have an `action` field.

```json
[
  {
    "action": "add_node",
    "id": "node1", 
    "type": "text", 
    "text": "First Node",
    "x": 0, "y": 0, "width": 200, "height": 100
  },
  {
    "action": "add_node",
    "id": "node2",
    "type": "text",
    "text": "Second Node",
    "x": 300, "y": 0, "width": 200, "height": 100
  },
  {
    "action": "add_edge",
    "fromNode": "node1",
    "toNode": "node2"
  }
]
```

**Note**: If an ID is not provided for `add_node` or `add_edge`, one will be auto-generated.
