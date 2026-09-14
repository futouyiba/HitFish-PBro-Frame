#!/usr/bin/env python3
"""Feishu whiteboard raw export -> Layer A (pframe-source-normalized.json).

Graphic migration only: format unification, zero semantic interpretation.
Every text is preserved byte-for-byte; geometry preserved as-is.
"""
import argparse
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def join_paragraphs(rich_text):
    """Feishu rich_text paragraphs -> plain multiline string (byte-faithful).

    Each paragraph becomes one line (multi-element runs concatenated in order,
    empty paragraphs become empty lines)."""
    lines = []
    for para in rich_text.get("paragraphs", []):
        parts = []
        for el in para.get("elements", []):
            te = el.get("text_element")
            if te and te.get("text"):
                parts.append(te["text"])
        lines.append("".join(parts))
    return "\n".join(lines), len(rich_text.get("paragraphs", []))


def norm_text(text_obj):
    """Common text extraction for shapes / connectors / mind_map nodes."""
    if not text_obj:
        return None
    t = {
        "value": text_obj.get("text", ""),
        "fontSize": text_obj.get("font_size"),
        "fontWeight": text_obj.get("font_weight"),
        "color": text_obj.get("text_color"),
        "textAlign": text_obj.get("horizontal_align"),
        "verticalAlign": text_obj.get("vertical_align"),
        "italic": text_obj.get("italic", False),
    }
    if "rich_text" in text_obj and text_obj["rich_text"]:
        value, para_count = join_paragraphs(text_obj["rich_text"])
        t["value"] = value
        t["paragraphCount"] = para_count
    return t


def norm_connector_end(end_obj, arrow_style):
    if not end_obj:
        return None
    return {
        "targetId": end_obj.get("id"),
        "fx": end_obj.get("position", {}).get("x"),
        "fy": end_obj.get("position", {}).get("y"),
        "snap": end_obj.get("snap_to"),
        "arrowStyle": arrow_style,
    }


def normalize_node(node, index):
    ntype = node["type"]
    el = {
        "normalizedElementId": f"src_{index:03d}",
        "sourceId": node["id"],
        "x": node["x"],
        "y": node["y"],
        "width": node["width"],
        "height": node["height"],
        "angle": node.get("angle", 0),
        "zIndex": node.get("z_index"),
        "parentId": node.get("parent_id"),
        "lockedInSource": node.get("locked"),
    }

    if ntype == "composite_shape":
        el["type"] = "shape"
        el["subtype"] = node["composite_shape"].get("type")
        el["text"] = norm_text(node.get("text"))
        style = node.get("style") or {}
        el["style"] = {
            "fill": style.get("fill_color"),
            "fillOpacity": style.get("fill_opacity"),
            "borderStyle": style.get("border_style"),
            "borderColor": style.get("border_color"),
            "borderWidth": style.get("border_width"),
        }
    elif ntype == "connector":
        conn = node["connector"]
        el["type"] = "connector"
        el["subtype"] = conn.get("shape")  # polyline
        el["connector"] = {
            "start": norm_connector_end(
                conn.get("start_object"), conn.get("start", {}).get("arrow_style")),
            "end": norm_connector_end(
                conn.get("end_object"), conn.get("end", {}).get("arrow_style")),
            "turningPoints": [[p["x"], p["y"]] for p in conn.get("turning_points", [])],
            "specifiedCoordinate": conn.get("specified_coordinate"),
        }
        caps = conn.get("captions", {}).get("data", [])
        if caps:
            el["connector"]["caption"] = {
                "text": norm_text(caps[0]),
                "position": conn.get("caption_position"),
                "positionType": conn.get("caption_position_type"),
            }
        style = node.get("style") or {}
        el["style"] = {
            "borderStyle": style.get("border_style"),
            "borderColor": style.get("border_color"),
            "borderWidth": style.get("border_width"),
        }
    elif ntype == "text_shape":
        el["type"] = "text"
        el["subtype"] = "text_shape"
        el["text"] = norm_text(node.get("text"))
        el["style"] = {}
    elif ntype == "mind_map":
        el["type"] = "mindmap_root" if "mind_map_root" in node else "mindmap_node"
        el["subtype"] = (node.get("mind_map_node") or {}).get("type")
        el["mindMap"] = {
            "parentId": node.get("mind_map", {}).get("parent_id"),
            "collapsed": (node.get("mind_map_node") or {}).get("collapsed"),
        }
        el["text"] = norm_text(node.get("text"))
        style = node.get("style") or {}
        el["style"] = {
            "fill": style.get("fill_color"),
            "borderStyle": style.get("border_style"),
            "borderColor": style.get("border_color"),
            "borderWidth": style.get("border_width"),
        }
    elif ntype == "group":
        el["type"] = "group"
        el["group"] = {"children": list(node.get("children", []))}
    else:
        el["type"] = f"UNSUPPORTED:{ntype}"
    return el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.join(ROOT, "source", "feishu-original.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "normalized", "pframe-source-normalized.json"))
    args = ap.parse_args()

    with open(args.source, encoding="utf-8") as f:
        raw = json.load(f)

    elements = [normalize_node(n, i + 1) for i, n in enumerate(raw["nodes"])]

    doc = {
        "source": "feishu",
        "sourceDocumentId": "ES2Sd89jeoCsiVxqY3WcHbV4n4c",
        "sourceDiagramId": "DfFRwiueTh2QbdbzS1scoNomnkj",
        "capturedAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "sourceNodeCount": len(raw["nodes"]),
        "notes": "Graphic migration intermediate representation. No FCF semantics. "
                 "Connector turningPoints are relative to the connector bbox origin (x,y).",
        "elements": elements,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    # sanity summary
    from collections import Counter
    print("normalized elements:", len(elements))
    print(Counter(e["type"] for e in elements))


if __name__ == "__main__":
    main()
