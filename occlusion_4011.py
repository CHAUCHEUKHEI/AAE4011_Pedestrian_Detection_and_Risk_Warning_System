# occlusion_4011.py
# Stage 4 — Occlusion detection.


import config_4011 as cfg


# COCO IDs that can hide other objects
_OCCLUSION_SOURCE_IDS = {2, 5, 7}       # car, bus, truck

# COCO IDs that can be hidden (vulnerable road users)
_VULNERABLE_IDS = {0, 1, 3, 15, 16}    # person, bicycle, motorcycle, cat, dog


def _intersection_area(a: list, b: list) -> float:

    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    return float((ix2 - ix1) * (iy2 - iy1))


def _box_area(box: list) -> float:
    return float(max(0, box[2] - box[0]) * max(0, box[3] - box[1]))


def check(detections: list) -> list:

    # Split into sources and vulnerable objects
    sources    = [d for d in detections if d["class_id"] in _OCCLUSION_SOURCE_IDS]
    vulnerable = [d for d in detections if d["class_id"] in _VULNERABLE_IDS]

    # Default everyone to non-occluded first
    for det in detections:
        det["occluded"] = False

    for v in vulnerable:
        v_area = _box_area(v["box"])
        if v_area <= 0:
            continue

        for s in sources:
            inter   = _intersection_area(v["box"], s["box"])
            overlap = inter / v_area
            if overlap >= cfg.OCCLUSION_OVERLAP_THRESHOLD:
                v["occluded"] = True
                break   # one overlapping source is enough to flag

    return detections
