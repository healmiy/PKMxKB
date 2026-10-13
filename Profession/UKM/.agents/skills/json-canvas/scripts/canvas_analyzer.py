#!/usr/bin/env python3
"""
Canvas analyzer for Obsidian .canvas files
- Lists group frames and classifies nodes as strictly contained vs touching
- Normalizes Obsidian wiki links to display text after the pipe

Usage:
  python3 .agents/skills/json-canvas/scripts/canvas_analyzer.py "path/to/file.canvas"
  python3 .agents/skills/json-canvas/scripts/canvas_analyzer.py --format json "path/to/file.canvas"
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

WIKI_RX = re.compile(r"\[\[(?:[^\]|#]+(?:#[^\]|]+)?)(?:\|([^\]]+))?\]\]")


def normalize_wikilinks(text: str) -> str:
    """Replace wiki links with their display text when present.
    [[target]] -> target (without anchors)
    [[target|Display]] -> Display
    """
    def repl(m: re.Match[str]) -> str:
        disp = m.group(1)
        if disp:
            return disp
        inner = m.group(0)[2:-2]  # strip [[ ]]
        # remove any anchor and keep the target label
        return inner.split("|", 1)[0].split("#", 1)[0]

    return WIKI_RX.sub(repl, text)


def bounds(n: Dict[str, Any]) -> Tuple[float, float, float, float]:
    return (float(n["x"]), float(n["y"]), float(n["x"]) + float(n["width"]), float(n["y"]) + float(n["height"]))


def strictly_contains(frame: Dict[str, Any], node: Dict[str, Any]) -> bool:
    fx, fy, frx, fry = bounds(frame)
    nx, ny, nrx, nry = bounds(node)
    return fx < nx and fy < ny and nrx < frx and nry < fry


def load_canvas(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def analyze_frames(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in data.get("nodes", [])}
    groups = [n for n in nodes.values() if n.get("type") == "group"]
    results = []
    for g in groups:
        inside = []
        touching = []
        for n in nodes.values():
            if n["id"] == g["id"] or "width" not in n or "height" not in n:
                continue
            if strictly_contains(g, n):
                label = n.get("text")
                if n.get("type") == "text" and label:
                    label = normalize_wikilinks(label).strip()
                elif n.get("type") == "file":
                    label = n.get("file", "")
                else:
                    label = label or ""
                inside.append({"id": n["id"], "label": label})
            else:
                # touching/overlap heuristic (edge contact or overlap)
                fx, fy, frx, fry = bounds(g)
                nx, ny, nrx, nry = bounds(n)
                # Treat edge equality as touching (edge contact counts)
                overlap = not (nrx < fx or frx < nx or nry < fy or fry < ny)
                if overlap and not strictly_contains(g, n):
                    label = n.get("text")
                    if n.get("type") == "text" and label:
                        label = normalize_wikilinks(label).strip()
                    elif n.get("type") == "file":
                        label = n.get("file", "")
                    else:
                        label = label or ""
                    touching.append({"id": n["id"], "label": label})
        results.append({
            "group_id": g["id"],
            "group_label": g.get("label", ""),
            "contained": inside,
            "touching": touching,
        })
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="Path to .canvas file")
    ap.add_argument("--format", choices=["plain", "json"], default="plain")
    args = ap.parse_args()

    data = load_canvas(Path(args.path))
    frames = analyze_frames(data)

    if args.format == "json":
        print(json.dumps(frames, ensure_ascii=False, indent=2))
    else:
        for f in frames:
            print(f"Frame: {f['group_label']} ({f['group_id']})")
            print("  Contained:")
            for item in f["contained"]:
                print(f"   - {item['id']} {item['label']}")
            print("  Touching:")
            for item in f["touching"]:
                print(f"   - {item['id']} {item['label']}")


if __name__ == "__main__":
    main()
