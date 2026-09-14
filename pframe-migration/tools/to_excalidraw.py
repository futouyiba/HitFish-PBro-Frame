#!/usr/bin/env python3
"""Layer A (normalized) -> Layer B (Excalidraw scene) + Layer C (element map).

Graphic migration only. Deterministic: seeds/nonces derived from element ids,
`updated` pinned to a fixed migration timestamp, so reruns are byte-stable.

Modes:
  default          full migration -> pframe-base.excalidraw + element map
  --only id,id,... pilot subset (plus connectors whose both ends are included)
  --overlay-test   additionally emit base+OVR_TEST_* scene proving
                   "Base locked + Overlay editable"
"""
import argparse
import json
import os
import zlib
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UPDATED_MS = int(datetime(2026, 9, 14, 4, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
SCENE_VERSION = 2
FONT_FAMILY_NORMAL = 2
LINE_HEIGHT = 1.25

# ---------------------------------------------------------------- helpers


def seed_of(tag):
    return (zlib.crc32(tag.encode()) & 0x7FFFFFFF) or 1


def nonce_of(tag):
    return (zlib.crc32(("nonce:" + tag).encode()) & 0x7FFFFFFF) or 7


def is_wide(ch):
    """CJK / fullwidth punctuation roughly one em wide."""
    o = ord(ch)
    return o >= 0x2E80 or (0xFF00 <= o <= 0xFFEF) or (0x3000 <= o <= 0x303F)


def text_width(s, font_size):
    return sum(font_size if is_wide(c) else font_size * 0.6 for c in s)


def wrap_lines(value, font_size, max_width):
    """Conservative wrap estimate; Excalidraw re-measures with real fonts."""
    lines = []
    for raw in value.split("\n"):
        if not raw:
            lines.append("")
            continue
        cur, cur_w = "", 0.0
        for ch in raw:
            w = font_size if is_wide(ch) else font_size * 0.6
            if max_width and cur_w + w > max_width and cur:
                lines.append(cur)
                cur, cur_w = ch, w
            else:
                cur, cur_w = cur + ch, cur_w + w
        lines.append(cur)
    return lines


def common_fields(eid, etype, x, y, w, h, stroke_color, group_ids, locked,
                  bound_elements=None):
    return {
        "id": eid,
        "type": etype,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": "thin",
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": group_ids,
        "frameId": None,
        "roundness": None,
        "seed": seed_of(eid),
        "version": 1,
        "versionNonce": nonce_of(eid),
        "isDeleted": False,
        "boundElements": bound_elements or [],
        "updated": UPDATED_MS,
        "link": None,
        "locked": locked,
    }


ALIGN_H = {"left": "left", "center": "center", "right": "right"}
ALIGN_V = {"top": "top", "mid": "middle", "bottom": "bottom"}


def make_bound_text(tid, container, text, group_ids):
    """Text element bound into a shape/arrow container (label)."""
    fs = (text.get("fontSize") or 14)
    value = text["value"]
    lines = wrap_lines(value, fs, container["width"])
    est_w = min(container["width"], max((text_width(l, fs) for l in lines), default=fs))
    est_h = len(lines) * fs * LINE_HEIGHT
    cy = container["y"] + max(0.0, (container["height"] - est_h) / 2)
    el = common_fields(tid, "text", container["x"], cy, est_w, est_h,
                       text.get("color") or "#1f2329", group_ids, True)
    el.update({
        "fontSize": fs,
        "fontFamily": FONT_FAMILY_NORMAL,
        "text": value,
        "textAlign": ALIGN_H.get(text.get("textAlign"), "center"),
        "verticalAlign": ALIGN_V.get(text.get("verticalAlign"), "middle"),
        "containerId": container["id"],
        "originalText": value,
        "lineHeight": LINE_HEIGHT,
        "baseline": round(fs * 0.9),
    })
    return el


def anchor_abs(by_src, ref):
    t = by_src[ref["targetId"]]
    return (t["x"] + ref["fx"] * t["width"], t["y"] + ref["fy"] * t["height"])


ARROWHEAD = {"line_arrow": "arrow", "none": "none", None: None}

# ---------------------------------------------------------------- builders


class Builder:
    def __init__(self, layer_a):
        self.els = layer_a["elements"]
        self.by_src = {e["sourceId"]: e for e in self.els}
        self.records = []          # element-map records, source order
        self.exc = []              # (sort_key, element dict)
        self.counters = {"RECT": 0, "TEXT": 0, "ARROW": 0, "ARROW_MM": 0}
        self.approx = {}           # sourceId -> reason

    def nid(self, prefix):
        self.counters[prefix] += 1
        return f"BASE_{prefix}_{self.counters[prefix]:03d}"

    def group_of(self, e):
        parent = e.get("parentId")
        if not parent:
            return []
        return [f"BASE_GRP_{self.group_index[parent]}"]

    def prepare_groups(self):
        self.group_index = {}
        gi = 0
        for e in self.els:
            if e["type"] == "group":
                gi += 1
                self.group_index[e["sourceId"]] = gi

    def build_shape(self, e):
        style = e.get("style") or {}
        border = style.get("borderStyle")
        stroke = style.get("borderColor") if border and border != "none" else "transparent"
        fill = style.get("fill") or "transparent"
        gid = self.nid("RECT")
        rect = common_fields(gid, "rectangle", e["x"], e["y"], e["width"], e["height"],
                              stroke, self.group_of(e), True)
        rect["backgroundColor"] = fill
        rect["roundness"] = {"type": 3}
        rect["strokeStyle"] = "dotted" if border == "dot" else "solid"
        exc_ids = [gid]
        text = e.get("text")
        if text and text.get("value"):
            tid = self.nid("TEXT")
            self.exc.append((e["zIndex"], make_bound_text(tid, rect, text, rect["groupIds"])))
            rect["boundElements"] = [{"id": tid, "type": "text"}]
            exc_ids.append(tid)
        elif text is None:
            pass
        self.exc.append((e["zIndex"], rect))
        return exc_ids

    def build_standalone_text(self, e):
        text = e.get("text") or {}
        fs = text.get("fontSize") or 14
        value = text.get("value", "")
        tid = self.nid("TEXT")
        lines = wrap_lines(value, fs, e["width"] or None)
        est_w = max((text_width(l, fs) for l in lines), default=0) or e["width"]
        el = common_fields(tid, "text", e["x"], e["y"], max(est_w, e["width"]), e["height"],
                           text.get("color") or "#1f2329", [], True)
        el.update({
            "fontSize": fs,
            "fontFamily": FONT_FAMILY_NORMAL,
            "text": value,
            "textAlign": ALIGN_H.get(text.get("textAlign"), "left"),
            "verticalAlign": ALIGN_V.get(text.get("verticalAlign"), "top"),
            "containerId": None,
            "originalText": value,
            "lineHeight": LINE_HEIGHT,
            "baseline": round(fs * 0.9),
        })
        self.exc.append((e["zIndex"], el))
        return [tid]

    def build_connector(self, e):
        c = e["connector"]
        start_ref, end_ref = c["start"], c["end"]
        sx, sy = anchor_abs(self.by_src, start_ref)
        ex, ey = anchor_abs(self.by_src, end_ref)
        pts = [[0.0, 0.0]]
        for tp in c.get("turningPoints", []):
            pts.append([e["x"] + tp[0] - sx, e["y"] + tp[1] - sy])
        pts.append([ex - sx, ey - sy])
        aid = self.nid("ARROW")
        w = max(p[0] for p in pts) - min(p[0] for p in pts)
        h = max(p[1] for p in pts) - min(p[1] for p in pts)
        stroke = (e.get("style") or {}).get("borderColor") or "#1f2329"
        el = common_fields(aid, "arrow", sx, sy, w, h, stroke, [], True)
        el.update({
            "points": pts,
            "startArrowhead": ARROWHEAD.get(start_ref.get("arrowStyle"), "none"),
            "endArrowhead": ARROWHEAD.get(end_ref.get("arrowStyle"), "arrow"),
            "startBinding": None if not start_ref["targetId"] else
                {"elementId": self.rect_id_of(start_ref["targetId"]), "focus": 0, "gap": 1, "fixedPoint": None},
            "endBinding": None if not end_ref["targetId"] else
                {"elementId": self.rect_id_of(end_ref["targetId"]), "focus": 0, "gap": 1, "fixedPoint": None},
        })
        exc_ids = [aid]
        cap = c.get("caption")
        if cap and cap.get("text", {}).get("value"):
            tid = self.nid("TEXT")
            pos = cap.get("position") or 0.5
            t = min(max(pos, 0.0), 1.0)
            lens = []
            for a, b in zip(pts, pts[1:]):
                lens.append(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)
            total = sum(lens) or 1.0
            acc, cx, cy = 0.0, pts[0][0], pts[0][1]
            for (a, b), seg in zip(zip(pts, pts[1:]), lens):
                if acc + seg >= total * t or (a, b) == (pts[-2], pts[-1]):
                    frac = (total * t - acc) / seg if seg else 0
                    cx, cy = a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac
                    break
                acc += seg
            fs = cap["text"].get("fontSize") or 14
            value = cap["text"]["value"]
            tw = text_width(value, fs) or 20
            cap_el = common_fields(tid, "text", sx + cx - tw / 2, sy + cy - fs * LINE_HEIGHT / 2,
                                   tw, fs * LINE_HEIGHT,
                                   cap["text"].get("color") or "#1f2329", [], True)
            cap_el.update({
                "fontSize": fs,
                "fontFamily": FONT_FAMILY_NORMAL,
                "text": value,
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": aid,
                "originalText": value,
                "lineHeight": LINE_HEIGHT,
                "baseline": round(fs * 0.9),
            })
            el["boundElements"] = [{"id": tid, "type": "text"}]
            self.exc.append((e["zIndex"] + 0.1, cap_el))
            exc_ids.append(tid)
        self.exc.append((e["zIndex"], el))
        return exc_ids

    def rect_id_of(self, source_id):
        return self._rect_ids[source_id]

    def build_mindmap_edges(self):
        """Edges auto-drawn by the Feishu mindmap renderer. Derived from the
        structural parent_id tree (NOT from visual guessing). Straight lines,
        no bindings, no arrowheads; routed between facing box edges."""
        mm = [e for e in self.els if e["type"].startswith("mindmap")]
        mm.sort(key=lambda e: e["zIndex"])
        floor = min(e["zIndex"] for e in mm) - 0.5
        derived = []
        for child in mm:
            pid = (child.get("mindMap") or {}).get("parentId")
            if not pid or pid not in self.by_src:
                continue
            parent = self.by_src[pid]
            pc = (parent["x"] + parent["width"] / 2, parent["y"] + parent["height"] / 2)
            cc = (child["x"] + child["width"] / 2, child["y"] + child["height"] / 2)
            if cc[0] >= pc[0]:
                a = (parent["x"] + parent["width"], pc[1])
                b = (child["x"], cc[1]) if cc[1] != pc[1] else (child["x"], pc[1])
            else:
                a = (parent["x"], pc[1])
                b = (child["x"] + child["width"], cc[1])
            aid = self.nid("ARROW_MM")
            el = common_fields(aid, "arrow", a[0], a[1], abs(b[0] - a[0]), abs(b[1] - a[1]),
                               (parent.get("style") or {}).get("borderColor") or "#5178c6",
                               [], True)
            el.update({
                "points": [[0.0, 0.0], [b[0] - a[0], b[1] - a[1]]],
                "startArrowhead": None,
                "endArrowhead": None,
                "startBinding": None,
                "endBinding": None,
            })
            self.exc.append((floor, el))
            derived.append({
                "stableId": None,  # assigned after sort, see finalize
                "origin": f"mindmap-edge:{pid}->{child['sourceId']}",
                "excalidrawElementIds": [aid],
                "reason": "Edge auto-drawn by Feishu mindmap renderer; reconstructed "
                          "from structural parent_id, not from pixel inspection.",
            })
        return derived

    # ---------------------------------------------------------------- run

    def run(self, only=None):
        self.prepare_groups()
        selected = set(only) if only else None
        skipped_conn = []
        for e in self.els:
            sid = e["sourceId"]
            if selected is not None and sid not in selected:
                continue
            if e["type"] in ("shape", "mindmap_node", "mindmap_root"):
                exc_ids = self.build_shape(e)
            elif e["type"] == "text":
                exc_ids = self.build_standalone_text(e)
            elif e["type"] == "connector":
                c = e["connector"]
                if selected is not None and not (
                    c["start"]["targetId"] in selected and c["end"]["targetId"] in selected):
                    skipped_conn.append(sid)
                    continue
                exc_ids = self.build_connector(e)
            elif e["type"] == "group":
                exc_ids = [self.rect_id_of(ch) for ch in e["group"]["children"]]
            else:
                exc_ids = []
            text = e.get("text")
            self.records.append({
                "stableId": None,
                "sourceObjectId": sid,
                "normalizedElementId": e["normalizedElementId"],
                "excalidrawElementIds": exc_ids,
                "sourceText": text.get("value") if text else None,
                "semanticId": None,
                "mapping": "full",
            })
        # rect id lookup for connector bindings (post pass)
        derived = self.build_mindmap_edges() if selected is None else []
        return skipped_conn, derived

    def finalize(self, derived):
        """Assign stable ids (source order), rect-id lookup, sort scene."""
        for i, rec in enumerate(self.records):
            rec["stableId"] = f"P_BASE_{i + 1:03d}"
        for j, d in enumerate(derived):
            d["stableId"] = f"P_DERIVED_{j + 1:03d}"
        self.exc.sort(key=lambda t: (t[0], t[1]["id"]))
        return [el for _, el in self.exc]


def first_pass_rect_ids(layer_a, only=None):
    """Reproduce BASE_RECT numbering deterministically for binding lookups."""
    b = Builder(layer_a)
    b.prepare_groups()
    lookup = {}
    for e in b.els:
        if e["type"] in ("shape", "mindmap_node", "mindmap_root"):
            if only is not None and e["sourceId"] not in only:
                continue
            # numbering must match Builder.run ordering: shapes emit RECT first
            b.counters["RECT"] += 1
            lookup[e["sourceId"]] = f"BASE_RECT_{b.counters['RECT']:03d}"
    return lookup


def build_scene(builder, elements_out):
    return {
        "type": "excalidraw",
        "version": SCENE_VERSION,
        "source": "pframe-migration",
        "elements": elements_out,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": {},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalized", default=os.path.join(ROOT, "normalized", "pframe-source-normalized.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "excalidraw", "pframe-base.excalidraw"))
    ap.add_argument("--map", default=os.path.join(ROOT, "metadata", "pframe-element-map.json"))
    ap.add_argument("--only", help="comma-separated source ids (pilot)")
    ap.add_argument("--overlay-test", action="store_true",
                    help="emit base+OVR_TEST_* scene at --overlay-out")
    ap.add_argument("--overlay-out", default=os.path.join(ROOT, "excalidraw", "pframe-overlay-test.excalidraw"))
    args = ap.parse_args()

    with open(args.normalized, encoding="utf-8") as f:
        layer_a = json.load(f)

    only = set(args.only.split(",")) if args.only else None

    builder = Builder(layer_a)
    builder._rect_ids = first_pass_rect_ids(layer_a, only)
    skipped, derived = builder.run(only)
    elements = builder.finalize(derived)

    scene = build_scene(builder, elements)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(scene, f, ensure_ascii=False, indent=1)

    if only is None:
        doc = {
            "meta": {
                "purpose": "Identity / element mapping only. NOT a semantic map.",
                "generatedBy": "tools/to_excalidraw.py",
                "sourceDocumentId": layer_a["sourceDocumentId"],
                "sourceDiagramId": layer_a["sourceDiagramId"],
                "sourceElementCount": len(builder.records),
                "derivedElementCount": len(derived),
                "excalidrawElementCount": len(elements),
                "idRules": {
                    "excalidraw": "BASE_{RECT|TEXT|ARROW|ARROW_MM}_{nnn}; overlay prefix OVR_*",
                    "stable": "P_BASE_{nnn} in Layer A order; P_DERIVED_{nnn} for mindmap edges",
                },
            },
            "elements": builder.records,
            "derivedElements": derived,
        }
        os.makedirs(os.path.dirname(args.map), exist_ok=True)
        with open(args.map, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)

    if args.overlay_test and only is None:
        ov = [dict(e) for e in elements]
        # TEST01 badge + leader line + callout near o1:28 (基础环境亲和配置)
        tgt = next(e for e in ov if e["id"] == builder._rect_ids.get("o1:28"))
        badge = common_fields("OVR_TEST_RECT_001", "rectangle",
                              tgt["x"] - 96, tgt["y"] - 56, 72, 30,
                              "#b45309", [], False)
        badge.update({"backgroundColor": "#fef3c7", "roundness": {"type": 3},
                      "opacity": 90, "boundElements": [{"id": "OVR_TEST_TEXT_001", "type": "text"}]})
        label = make_bound_text("OVR_TEST_TEXT_001", badge,
                                {"value": "TEST01", "fontSize": 14, "color": "#b45309",
                                 "textAlign": "center", "verticalAlign": "mid"}, [])
        label["locked"] = False
        callout = common_fields("OVR_TEST_TEXT_002", "text",
                                tgt["x"] - 110, tgt["y"] - 100, 200, 22,
                                "#b45309", [], False)
        callout.update({"fontSize": 12, "fontFamily": FONT_FAMILY_NORMAL,
                        "text": "Overlay scaffold check (not a real overlay)",
                        "textAlign": "left", "verticalAlign": "top",
                        "containerId": None,
                        "originalText": "Overlay scaffold check (not a real overlay)",
                        "lineHeight": LINE_HEIGHT, "baseline": 11})
        lead = common_fields("OVR_TEST_ARROW_001", "arrow",
                             badge["x"] + badge["width"], badge["y"] + badge["height"] / 2,
                             abs(tgt["x"] - (badge["x"] + badge["width"])),
                             abs((tgt["y"] + tgt["height"] / 2) - (badge["y"] + badge["height"] / 2)),
                             "#b45309", [], False)
        lead.update({"points": [[0.0, 0.0],
                                [tgt["x"] - lead["x"],
                                 (tgt["y"] + tgt["height"] / 2) - lead["y"]]],
                     "startArrowhead": None, "endArrowhead": "arrow",
                     "startBinding": None, "endBinding": None})
        ov.extend([lead, badge, label, callout])
        ov_scene = build_scene(builder, ov)
        with open(args.overlay_out, "w", encoding="utf-8") as f:
            json.dump(ov_scene, f, ensure_ascii=False, indent=1)

    print(f"scene elements: {len(elements)} -> {args.out}")
    if skipped:
        print("skipped connectors (pilot endpoints not all selected):", skipped)
    if only is None:
        print(f"element map: {len(builder.records)} source + {len(derived)} derived")


if __name__ == "__main__":
    main()
