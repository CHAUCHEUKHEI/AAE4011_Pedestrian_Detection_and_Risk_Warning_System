# risk_engine_4011.py
# Stage 3/4 — Metric depth risk scoring + trajectory prediction.

import numpy as np
from collections import deque
import config_4011 as cfg

RISK_COLOUR = {
    "GREEN": (0,   210,   0),
    "AMBER": (0,   165, 255),
    "RED":   (0,     0, 220),
}

_PRIORITY    = {"GREEN": 0, "AMBER": 1, "RED": 2}
_VULN_IDS    = {0, 1, 3, 15, 16}
_VEHICLE_IDS = {2, 5, 7}

# Per-track downgrade history
_risk_history: dict = {}
_HISTORY_LEN  = 3
_MIN_AGREE    = 2


# ── Lane corridor ──────────────────────────────────────────────────────────────

def lane_corridor_x_bounds() -> tuple:
    half = int(cfg.DISPLAY_WIDTH * cfg.LANE_CORRIDOR_FRACTION / 2)
    cx   = cfg.DISPLAY_WIDTH // 2
    return cx - half, cx + half


def _in_lane(px: float) -> bool:
    x_left, x_right = lane_corridor_x_bounds()
    return x_left <= px <= x_right


# ── Object depth sampling (now in metres) ──────────────────────────────────────

def _sample_object_depth_m(depth_map, x1, y1, x2, y2) -> float:
    """
    20th-percentile metric depth from lower-centre patch of bounding box.
    Returns metres. Lower = closer.
    """
    h  = y2 - y1;  w  = x2 - x1
    sy1 = y1 + int(h * 0.55);  sy2 = y2
    sx1 = x1 + int(w * 0.20);  sx2 = x2 - int(w * 0.20)
    H, W = depth_map.shape
    sy1, sy2 = max(0, sy1), min(H, sy2)
    sx1, sx2 = max(0, sx1), min(W, sx2)
    if sy1 >= sy2 or sx1 >= sx2:
        return 999.0   # degenerate → treat as very far
    return float(np.percentile(depth_map[sy1:sy2, sx1:sx2], 20))


# ── Trajectory prediction ──────────────────────────────────────────────────────

def _smooth_velocity(trail: list) -> tuple:
    n   = cfg.VELOCITY_SMOOTH_N
    pts = trail[-(n + 1):]
    if len(pts) < 2:
        return 0.0, 0.0
    dx = [pts[i+1][0] - pts[i][0] for i in range(len(pts)-1)]
    dy = [pts[i+1][1] - pts[i][1] for i in range(len(pts)-1)]
    return float(np.mean(dx)), float(np.mean(dy))


def _trajectory_risk(det: dict, trails: dict) -> str:
    tid   = det.get("track_id")
    trail = trails.get(tid, []) if tid is not None else []
    if len(trail) < 2:
        return "GREEN"

    vx, vy  = _smooth_velocity(trail)
    x1, y1, x2, y2 = det["box"]
    cx_obj  = (x1 + x2) / 2.0
    cx_lane = cfg.DISPLAY_WIDTH / 2.0

    moving_inward = (cx_obj < cx_lane and vx > 0) or \
                    (cx_obj > cx_lane and vx < 0)
    if not moving_inward and abs(vx) < 1.0:
        return "GREEN"

    px, py = float(cx_obj), float((y1 + y2) / 2.0)
    for t in range(1, cfg.TRAJ_LOOKAHEAD + 1):
        px += vx;  py += vy
        if _in_lane(px):
            if   t <= cfg.TRAJ_RED_FRAMES:   return "RED"
            elif t <= cfg.TRAJ_AMBER_FRAMES:  return "AMBER"
            return "GREEN"
    return "GREEN"


# ── Asymmetric temporal smoothing ──────────────────────────────────────────────

def _smoothed_risk(tid, raw_risk: str, prev_smooth: str) -> str:

    global _risk_history

    if tid is None:
        return raw_risk

    if tid not in _risk_history:
        _risk_history[tid] = deque(maxlen=_HISTORY_LEN)
    _risk_history[tid].append(raw_risk)

    # Upgrade path: if raw is higher than previous, apply immediately
    if _PRIORITY[raw_risk] > _PRIORITY[prev_smooth]:
        return raw_risk

    # Downgrade path: only downgrade if recent history agrees
    hist   = list(_risk_history[tid])
    counts = {"GREEN": 0, "AMBER": 0, "RED": 0}
    for r in hist:
        counts[r] += 1

    if counts["RED"]   >= _MIN_AGREE: return "RED"
    if counts["AMBER"] >= _MIN_AGREE: return "AMBER"
    # Not enough agreement to downgrade — hold current level
    return prev_smooth


def _cleanup_history(active_ids: set):
    gone = [tid for tid in _risk_history if tid not in active_ids]
    for tid in gone:
        del _risk_history[tid]


def _upgrade(a: str, b: str) -> str:
    return b if _PRIORITY[b] > _PRIORITY[a] else a


# ── Public API ─────────────────────────────────────────────────────────────────

# Track previous smoothed risk per object for asymmetric smoothing
_prev_smooth: dict = {}


def score(detections: list,
          depth_map:  np.ndarray,
          trails:     dict = None) -> tuple:

    if trails is None:
        trails = {}

    global _prev_smooth
    scene_risk = "GREEN"
    frame_area = cfg.DISPLAY_WIDTH * cfg.DISPLAY_HEIGHT
    active_ids = set()

    for det in detections:
        tid = det.get("track_id")
        if tid is not None:
            active_ids.add(tid)

        prev = _prev_smooth.get(tid, "GREEN")

        # ── Occluded → force AMBER (immediate)
        if det.get("occluded", False):
            det.update({"risk": "AMBER", "depth": None, "depth_delta": None})
            scene_risk = _upgrade(scene_risk, "AMBER")
            _prev_smooth[tid] = "AMBER"
            continue

        x1, y1, x2, y2 = det["box"]
        cx       = (x1 + x2) / 2.0
        box_area = (x2 - x1) * (y2 - y1)
        cid      = det["class_id"]

        det["depth"]       = None
        det["depth_delta"] = None
        raw_risk           = "GREEN"

        # ── Car bonnet reject ──────────────────────────────────────
        if y2 > cfg.DISPLAY_HEIGHT * 0.88:
            det["risk"] = "GREEN"
            _prev_smooth[tid] = "GREEN"
            continue

        # ── Giant-box skip: vehicles only ──────────────────────────
        if cid in _VEHICLE_IDS and box_area > frame_area * 0.40:
            det["risk"] = "GREEN"
            _prev_smooth[tid] = "GREEN"
            continue

        # ── Trajectory + proximity (vulnerable outside corridor) ────────
        if cid in _VULN_IDS and not _in_lane(cx):
            raw_risk = _trajectory_risk(det, trails)
            # Proximity fallback: even if not moving inward, flag AMBER
            # if physically close — catches stationary dogs, slow pedestrians
            if raw_risk == "GREEN":
                prox_depth = _sample_object_depth_m(depth_map, x1, y1, x2, y2)
                if prox_depth < cfg.METRIC_AMBER_M:
                    raw_risk = "AMBER"
                    det["depth"] = prox_depth

        # ── Metric depth scoring (in lane) ─────────────────────────
        elif _in_lane(cx):
            depth_m      = _sample_object_depth_m(depth_map, x1, y1, x2, y2)
            det["depth"] = depth_m

            if depth_m < cfg.METRIC_RED_M:
                # Vehicles: require minimum box size to confirm RED.
                # A small vehicle box = far away = depth model likely wrong.
                # Vulnerable objects (pedestrians etc.) skip this gate.
                if cid in _VEHICLE_IDS:
                    min_area = frame_area * cfg.VEHICLE_RED_MIN_BOX_FRACTION
                    raw_risk = "RED" if box_area >= min_area else "AMBER"
                else:
                    raw_risk = "RED"
            elif depth_m < cfg.METRIC_AMBER_M:
                raw_risk = "AMBER"
            det["depth_delta"] = depth_m

        # ── Asymmetric temporal smoothing ──────────────────────────
        smooth = _smoothed_risk(tid, raw_risk, prev)
        det["risk"]       = smooth
        _prev_smooth[tid] = smooth
        scene_risk        = _upgrade(scene_risk, smooth)

    _cleanup_history(active_ids)
    # Clean up prev_smooth for gone IDs too
    gone = [tid for tid in _prev_smooth if tid not in active_ids]
    for tid in gone:
        del _prev_smooth[tid]

    return detections, scene_risk
