#!/usr/bin/env python3
"""Generate pframe-working.excalidraw = pframe-base.excalidraw (locked, untouched)
+ overlay elements defined in overlay-spec.json.

Base is copied verbatim; only OVR_* elements are appended. Deterministic:
overlay element ids/seeds derive from spec item ids, updated pinned like base.

Primitive kinds:
  scaffold-check  badge + label + leader line + callout (mechanism check, TEST01)
  badge           small rect + bound text
  numberTag       badge with P/C/D-style number text
  semanticTag     number tag + adjacent card (EN contract name + CN line);
                  optional `leader` = anchor-relative polyline pointing at the node
  deltaSpan       optional `bracket` polyline spanning several nodes + tag + card
  highlightBox    translucent box around the anchored element
  callout         standalone text
"""
import argparse
import json
import os

import to_excalidraw as conv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DEFAULT_COLOR = "#b45309"
DEFAULT_FILL = "#fef3c7"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def resolve_anchor(spec, emap, base_by_id):
    stable = spec["anchor"]["stableId"]
    hint = spec["anchor"].get("elementHint", "rectangle")
    rec = next((r for r in emap["elements"] + emap["derivedElements"]
                if r["stableId"] == stable), None)
    if rec is None:
        raise SystemExit(f"overlay-spec: stableId {stable} not found in element-map")
    cands = [base_by_id[i] for i in rec["excalidrawElementIds"]
             if base_by_id[i]["type"] == hint]
    if not cands:
        cands = [base_by_id[i] for i in rec["excalidrawElementIds"]
                 if base_by_id[i]["type"] != "text"]
    return cands[0]


def badge_element(item, color, fill):
    off = item.get("offset", {})
    x, y = item["_anchor"]["x"] + off.get("dx", 0), item["_anchor"]["y"] + off.get("dy", 0)
    tag = f"OVR_{item['id']}"
    badge = conv.common_fields(f"{tag}_BADGE", "rectangle", x, y, 72, 30, color, [], False)
    badge.update({"backgroundColor": fill, "roundness": {"type": 3}, "opacity": 90,
                  "boundElements": [{"id": f"{tag}_LABEL", "type": "text"}]})
    label = conv.make_bound_text(
        f"{tag}_LABEL", badge,
        {"value": item.get("text", item["id"]), "fontSize": 14, "color": color,
         "textAlign": "center", "verticalAlign": "mid"}, [])
    label["locked"] = False
    return badge, label


def leader_element(item, color, from_el):
    tag = f"OVR_{item['id']}"
    a = (from_el["x"] + from_el["width"], from_el["y"] + from_el["height"] / 2)
    t = item["_anchor"]
    b = (t["x"], t["y"] + t["height"] / 2)
    lead = conv.common_fields(f"{tag}_LEAD", "arrow", a[0], a[1],
                              abs(b[0] - a[0]), abs(b[1] - a[1]), color, [], False)
    lead.update({"points": [[0.0, 0.0], [b[0] - a[0], b[1] - a[1]]],
                 "startArrowhead": None, "endArrowhead": "arrow",
                 "startBinding": None, "endBinding": None})
    return lead


def callout_element(item, color):
    off = item.get("offset", {})
    t = item["_anchor"]
    text = item.get("callout") or item.get("text", "")
    fs = 12
    w = conv.text_width(text, fs) or 120
    el = conv.common_fields(f"OVR_{item['id']}_CALLOUT", "text",
                            t["x"] + off.get("dx", 0) - 14, t["y"] + off.get("dy", 0) - 44,
                            w, fs * 1.25, color, [], False)
    el.update({"fontSize": fs, "fontFamily": conv.FONT_FAMILY_NORMAL, "text": text,
               "textAlign": "left", "verticalAlign": "top", "containerId": None,
               "originalText": text, "lineHeight": 1.25, "baseline": round(fs * 0.9)})
    return el


def highlight_element(item, color):
    t = item["_anchor"]
    off = item.get("offset", {})
    pad = 10
    el = conv.common_fields(f"OVR_{item['id']}_BOX", "rectangle",
                            t["x"] - pad + off.get("dx", 0), t["y"] - pad + off.get("dy", 0),
                            t["width"] + 2 * pad, t["height"] + 2 * pad, color, [], False)
    el.update({"backgroundColor": "transparent", "opacity": 60,
               "strokeStyle": "dashed", "strokeWidth": "thin", "roundness": None})
    return el


def polyline_element(item, color, pts, suffix, arrow_end=False):
    """anchor 相对折线；pts 为相对锚点左上角的 [x,y] 序列。"""
    ax, ay = item["_anchor"]["x"], item["_anchor"]["y"]
    ab = [(ax + p[0], ay + p[1]) for p in pts]
    ox, oy = ab[0]
    rel = [[round(p[0] - ox, 2), round(p[1] - oy, 2)] for p in ab]
    xs = [p[0] for p in rel]; ys = [p[1] for p in rel]
    el = conv.common_fields(f"OVR_{item['id']}_{suffix}", "arrow", ox, oy,
                            max(xs) - min(xs), max(ys) - min(ys), color, [], False)
    el.update({"points": rel,
               "startArrowhead": None,
               "endArrowhead": "arrow" if arrow_end else None,
               "startBinding": None, "endBinding": None,
               "strokeWidth": "thin"})
    return el


def semantic_tag_elements(item, color, fill):
    """小型编号标签 + 紧邻轻量语义卡片（EN Contract 名 + 中文一行）。"""
    tag = f"OVR_{item['id']}"
    off = item.get("offset", {})
    tx, ty = item["_anchor"]["x"] + off.get("dx", 0), item["_anchor"]["y"] + off.get("dy", 0)
    num_tag = conv.common_fields(f"{tag}_TAG", "rectangle", tx, ty, 44, 20, color, [], False)
    num_tag.update({"backgroundColor": fill, "roundness": {"type": 3}, "opacity": 100,
                    "strokeWidth": 2,
                    "boundElements": [{"id": f"{tag}_TAGTEXT", "type": "text"}]})
    num_text = conv.make_bound_text(
        f"{tag}_TAGTEXT", num_tag,
        {"value": item.get("text", item["id"]), "fontSize": 12, "color": color,
         "textAlign": "center", "verticalAlign": "mid"}, [])
    num_text["locked"] = False

    value = item["en"] + "\n" + item["cn"]
    fs = item.get("fontSize", 12)
    lines = value.split("\n")
    cw = max(conv.text_width(l, fs) for l in lines) + 18
    ch = len(lines) * fs * 1.3 + 10
    side = item.get("cardSide", "right")
    if side == "left":
        cx = tx - 6 - cw
    else:
        cx = tx + 44 + 6
    cy = ty - (ch - 20) / 2
    card = conv.common_fields(f"{tag}_CARD", "rectangle", cx, cy, cw, ch,
                              item.get("cardColor", color), [], False)
    card.update({"backgroundColor": item.get("cardFill", "#ffffff"),
                 "roundness": {"type": 3}, "opacity": 100, "strokeWidth": 2,
                 "boundElements": [{"id": f"{tag}_CARDTEXT", "type": "text"}]})
    card_text = conv.make_bound_text(
        f"{tag}_CARDTEXT", card,
        {"value": value, "fontSize": fs, "color": "#1f2329",
         "textAlign": "left", "verticalAlign": "mid"}, [])
    card_text["locked"] = False
    return [num_tag, num_text, card, card_text]


def render_item(item, emap, base_by_id):
    color = item.get("color", DEFAULT_COLOR)
    fill = item.get("fill", DEFAULT_FILL)
    item["_anchor"] = resolve_anchor(item, emap, base_by_id)
    kind = item["kind"]
    out = []
    if kind == "scaffold-check":
        badge, label = badge_element(item, color, fill)
        out.extend([leader_element(item, color, badge), badge, label,
                    callout_element(item, color)])
    elif kind == "semanticTag":
        out.extend(semantic_tag_elements(item, color, fill))
        if item.get("leader"):
            out.append(polyline_element(item, color, item["leader"], "LEAD", arrow_end=True))
    elif kind == "deltaSpan":
        if item.get("bracket"):
            out.append(polyline_element(item, color, item["bracket"], "SPAN"))
        out.extend(semantic_tag_elements(item, color, fill))
    elif kind in ("badge", "numberTag"):
        b, l = badge_element(item, color, fill)
        out.extend([b, l])
    elif kind == "highlightBox":
        out.append(highlight_element(item, color))
    elif kind == "callout":
        out.append(callout_element(item, color))
    else:
        raise SystemExit(f"overlay-spec: unknown kind {kind!r} on item {item['id']}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(ROOT, "pframe-base.excalidraw"))
    ap.add_argument("--spec", default=os.path.join(ROOT, "overlay-spec.json"))
    ap.add_argument("--map", default=os.path.join(ROOT, "element-map.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "pframe-working.excalidraw"))
    args = ap.parse_args()

    base = load(args.base)
    spec = load(args.spec)
    emap = load(args.map)
    base_by_id = {e["id"]: e for e in base["elements"]}

    overlay = []
    for item in spec.get("items", []):
        overlay.extend(render_item(item, emap, base_by_id))

    working = {
        "type": "excalidraw",
        "version": base["version"],
        "source": "pframe-migration",
        "elements": base["elements"] + overlay,   # base verbatim, overlay appended
        "appState": base.get("appState", {"viewBackgroundColor": "#ffffff"}),
        "files": {},
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(working, f, ensure_ascii=False, indent=1)

    base_ids = {e["id"] for e in base["elements"]}
    leaked = [e["id"] for e in overlay if e["id"] in base_ids]
    assert not leaked, f"overlay id collides with base: {leaked}"
    print(f"working scene: {len(base['elements'])} base (locked, untouched) "
          f"+ {len(overlay)} overlay elements -> {args.out}")


if __name__ == "__main__":
    main()
