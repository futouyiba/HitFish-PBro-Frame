#!/usr/bin/env python3
"""Cross-validate the three migration layers -> metadata/migration-report.json.

Checks:
  1. counts & 1:1 source<->normalized mapping
  2. element-map: every excalidrawElementIds exists in the scene;
     every non-group source has >= 1 excalidraw element
  3. text fidelity: byte-equal text on mapped elements
  4. connector bindings: arrowheads, binding targets, point counts
  5. lock: every BASE_* element locked
  6. determinism: regenerating the scene reproduces the on-disk file
  7. approximations inventory (unmapped / partially_mapped / approximated)
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

spec = importlib.util.spec_from_file_location("to_excalidraw", os.path.join(HERE, "to_excalidraw.py"))
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    raw = load(os.path.join(ROOT, "source", "feishu-original.json"))
    norm = load(os.path.join(ROOT, "normalized", "pframe-source-normalized.json"))
    scene = load(os.path.join(ROOT, "excalidraw", "pframe-base.excalidraw"))
    emap = load(os.path.join(ROOT, "metadata", "pframe-element-map.json"))

    problems = []
    warn = []
    approx = []
    partial = []
    unmapped = []

    by_src_norm = {e["sourceId"]: e for e in norm["elements"]}
    els_by_id = {e["id"]: e for e in scene["elements"]}

    # 1. counts
    if not (len(raw["nodes"]) == len(norm["elements"]) == emap["meta"]["sourceElementCount"]):
        problems.append("count mismatch raw/normalized/map")
    for i, (n, e) in enumerate(zip(raw["nodes"], norm["elements"])):
        if n["id"] != e["sourceId"]:
            problems.append(f"order/id mismatch at {i}: {n['id']} vs {e['sourceId']}")

    # 2. map coverage
    for rec in emap["elements"]:
        for eid in rec["excalidrawElementIds"]:
            if eid not in els_by_id:
                problems.append(f"{rec['sourceObjectId']} -> missing scene element {eid}")
        if rec["sourceObjectId"] in by_src_norm and by_src_norm[rec["sourceObjectId"]]["type"] != "group":
            if not rec["excalidrawElementIds"]:
                unmapped.append(rec["sourceObjectId"])
    for d in emap["derivedElements"]:
        for eid in d["excalidrawElementIds"]:
            if eid not in els_by_id:
                problems.append(f"derived {d['origin']} -> missing {eid}")

    # 3. text fidelity
    for rec in emap["elements"]:
        st = rec.get("sourceText")
        if st is None:
            continue
        scene_texts = [els_by_id[eid].get("text", "")
                       for eid in rec["excalidrawElementIds"]
                       if els_by_id[eid]["type"] == "text"]
        joined = "\n".join(scene_texts)
        if st not in scene_texts and joined != st:
            # caption texts live on connector entries via sourceText? no: connector
            # sourceText is null; captions checked below
            problems.append(f"text mismatch for {rec['sourceObjectId']}: {st[:30]!r}")

    # captions
    cap_ok = cap_bad = 0
    for e in norm["elements"]:
        if e["type"] != "connector":
            continue
        cap = e["connector"].get("caption")
        if not cap:
            continue
        rec = next(r for r in emap["elements"] if r["sourceObjectId"] == e["sourceId"])
        texts = [els_by_id[i].get("text") for i in rec["excalidrawElementIds"]
                 if els_by_id[i]["type"] == "text"]
        if cap["text"]["value"] in texts:
            cap_ok += 1
        else:
            cap_bad += 1
            problems.append(f"caption text mismatch on {e['sourceId']}")
    if cap_bad == 0:
        approx.extend([f"caption-position:{e['sourceId']}"
                       for e in norm["elements"]
                       if e["type"] == "connector" and e["connector"].get("caption")])

    # 4. connectors
    n_arrow = 0
    for e in norm["elements"]:
        if e["type"] != "connector":
            continue
        rec = next(r for r in emap["elements"] if r["sourceObjectId"] == e["sourceId"])
        arr = next(els_by_id[i] for i in rec["excalidrawElementIds"]
                   if els_by_id[i]["type"] == "arrow")
        n_arrow += 1
        if arr["startArrowhead"] != "none" or arr["endArrowhead"] != "arrow":
            problems.append(f"arrowhead mismatch on {e['sourceId']}")
        want_pts = len(e["connector"].get("turningPoints", [])) + 2
        if len(arr["points"]) != want_pts:
            problems.append(f"point count mismatch on {e['sourceId']}: "
                            f"{len(arr['points'])} != {want_pts}")
        for side, key in (("start", "startBinding"), ("end", "endBinding")):
            tgt = e["connector"][side]["targetId"]
            want = [i for r in emap["elements"] if r["sourceObjectId"] == tgt
                    for i in r["excalidrawElementIds"]
                    if els_by_id[i]["type"] == "rectangle"][0]
            if arr[key]["elementId"] != want:
                problems.append(f"binding mismatch on {e['sourceId']} {side}")

    # 5. lock
    bad_lock = [e["id"] for e in scene["elements"]
                if e["id"].startswith("BASE_") and not e.get("locked")]
    if bad_lock:
        problems.append(f"unlocked BASE elements: {bad_lock[:5]}...")

    # 6. determinism
    layer_a = norm
    builder = conv.Builder(layer_a)
    builder._rect_ids = conv.first_pass_rect_ids(layer_a, None)
    _, derived = builder.run(None)
    regenerated = builder.finalize(derived)
    reg_scene = conv.build_scene(builder, regenerated)
    determinism_ok = json.dumps(reg_scene, ensure_ascii=False, sort_keys=True) == \
        json.dumps(scene, ensure_ascii=False, sort_keys=True)
    if not determinism_ok:
        problems.append("regenerated scene differs from on-disk file")

    # 7. approximations
    approx.append("round_rect2->round_rect:" + next(
        e["sourceId"] for e in norm["elements"]
        if e.get("subtype") == "round_rect2"))
    approx.append("bold-unsupported:" + next(
        e["sourceId"] for e in norm["elements"]
        if (e.get("text") or {}).get("fontWeight") == "bold"))
    approx.append("font-substitution:all-text (feishu default font -> excalidraw Normal/system)")
    approx.append("border-none->transparent-stroke:" + str(sum(
        1 for e in norm["elements"]
        if e.get("type") in ("shape",) and (e.get("style") or {}).get("borderStyle") == "none")))
    approx.append("mindmap-edge-derived:16 (reconstructed from parent_id)")
    empty_texts = [e["sourceId"] for e in norm["elements"]
                   if e["type"] == "text" and not (e.get("text") or {}).get("value")]
    if empty_texts:
        approx.append("empty-text-shapes-preserved-invisible:" + str(len(empty_texts)))

    report = {
        "source": {
            "documentId": norm["sourceDocumentId"],
            "diagramId": norm["sourceDiagramId"],
            "sourceElementCount": len(raw["nodes"]),
            "normalizedElementCount": len(norm["elements"]),
        },
        "excalidrawElementCount": len(scene["elements"]),
        "elementCounts": {
            t: sum(1 for e in scene["elements"] if e["type"] == t)
            for t in ("rectangle", "text", "arrow")},
        "mappedSourceElements": len(emap["elements"]),
        "unmappedSourceElements": len(unmapped),
        "derivedElements": len(emap["derivedElements"]),
        "captions": {"ok": cap_ok, "bad": cap_bad},
        "connectorArrows": n_arrow,
        "lockedBaseElements": sum(1 for e in scene["elements"] if e.get("locked")),
        "unlockedElements": [e["id"] for e in scene["elements"] if not e.get("locked")],
        "determinismRegenerationEqualsFile": determinism_ok,
        "unmapped": unmapped,
        "partially_mapped": partial,
        "approximated": approx,
        "warnings": [p for p in problems] if problems else [],
        "warningCount": len(problems),
    }
    out = os.path.join(ROOT, "metadata", "migration-report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
