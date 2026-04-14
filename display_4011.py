# display_4011.py
# Handles ALL drawing onto the frame — bounding boxes, labels, and the
# 3-colour warning banner at the top of the screen.
# Nothing here does any detection or risk logic; it just visualises what
# the other modules decide.

import cv2
import numpy as np
import config_4011 as cfg
from risk_engine_4011 import RISK_COLOUR, lane_corridor_x_bounds


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _draw_box(frame, detection, risk_level="GREEN"):
    """
    Draw a single bounding box with label and confidence.
    Box colour comes from the class; border thickness increases with risk.
    """
    x1, y1, x2, y2 = detection["box"]
    class_id = detection["class_id"]
    label    = detection["label"]
    conf     = detection["confidence"]

    colour    = cfg.CLASS_COLOURS.get(class_id, (200, 200, 200))
    thickness = 2 if risk_level == "GREEN" else 3

    # Bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, thickness)

    # Label background pill
    tid = detection.get("track_id")

    text = f"#{tid} {label} {conf:.0%}" if tid is not None \
       else f"{label} {conf:.0%}"
    font     = cv2.FONT_HERSHEY_SIMPLEX
    scale    = 0.55
    (tw, th), baseline = cv2.getTextSize(text, font, scale, 1)
    pad = 4
    cv2.rectangle(frame,
                  (x1, y1 - th - pad * 2),
                  (x1 + tw + pad * 2, y1),
                  colour, -1)   # filled rectangle

    # Text — dark for readability on bright backgrounds
    cv2.putText(frame, text,
                (x1 + pad, y1 - pad),
                font, scale, (20, 20, 20), 1, cv2.LINE_AA)


def _draw_warning_banner(frame, risk_level, counts):
    """
    Coloured banner across the top of the frame.
    Shows risk level and count of detected objects per class.
    """
    banner_h = 48
    colour   = cfg.RISK_COLOURS[risk_level]

    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], banner_h), colour, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # Risk level text (left side)
    label_text = f"  RISK: {risk_level}"
    cv2.putText(frame, label_text, (8, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

    # Detection summary (right side) — e.g. "person:2  bicycle:1"
    summary = "  ".join(
        f"{lbl}:{n}" for lbl, n in counts.items() if n > 0
    )
    if summary:
        (tw, _), _ = cv2.getTextSize(summary, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        x_right = frame.shape[1] - tw - 16
        cv2.putText(frame, summary, (x_right, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)


def _draw_fps(frame, fps):
    cv2.putText(frame, f"FPS: {fps:.1f}",
                (8, frame.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1, cv2.LINE_AA)

def _draw_dashed_rect(frame, x1, y1, x2, y2, colour, thickness=2, gap=10):
    """Draw a dashed rectangle by alternating drawn/skipped segments."""
    pts = [
        ((x1, y1), (x2, y1)),   # top
        ((x2, y1), (x2, y2)),   # right
        ((x2, y2), (x1, y2)),   # bottom
        ((x1, y2), (x1, y1)),   # left
    ]
    for (sx, sy), (ex, ey) in pts:
        length = max(abs(ex - sx), abs(ey - sy))
        steps  = length // (gap * 2)
        for i in range(steps + 1):
            t0 = min(1.0,  i       * 2 * gap / (length + 1e-8))
            t1 = min(1.0, (i * 2 + 1) * gap / (length + 1e-8))
            p0 = (int(sx + t0 * (ex - sx)), int(sy + t0 * (ey - sy)))
            p1 = (int(sx + t1 * (ex - sx)), int(sy + t1 * (ey - sy)))
            cv2.line(frame, p0, p1, colour, thickness)


# ---------------------------------------------------------------------------
# Public interface — called by main_4011.py
# ---------------------------------------------------------------------------

def render(frame, detections, trails, scene_risk, fps, depth_map=None, summary=None):

    # ── Lane corridor overlay ──────────────────────────────────
    x_left, x_right = lane_corridor_x_bounds()
    corridor_colour  = RISK_COLOUR[scene_risk]
    overlay = frame.copy()
    cv2.rectangle(overlay, (x_left, 0), (x_right, cfg.DISPLAY_HEIGHT),corridor_colour, -1)
    cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
    cv2.rectangle(frame, (x_left, 0), (x_right, cfg.DISPLAY_HEIGHT),corridor_colour, 2)

    # ── Depth map thumbnail (top-right corner) ─────────────────
    if depth_map is not None:
        thumb_w, thumb_h = 200, 120
        uint8   = (depth_map * 255).astype(np.uint8)
        coloured = cv2.applyColorMap(uint8, cv2.COLORMAP_MAGMA)
        thumb   = cv2.resize(coloured, (thumb_w, thumb_h))
        x_off   = cfg.DISPLAY_WIDTH - thumb_w - 8
        frame[8:8+thumb_h, x_off:x_off+thumb_w] = thumb
        cv2.rectangle(frame, (x_off, 8),
                      (x_off+thumb_w, 8+thumb_h), (200,200,200), 1)
        cv2.putText(frame, "Depth", (x_off+4, 8+thumb_h-4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220,220,220), 1)

    # ── Motion trails ──────────────────────────────────────────
    for det in detections:
        tid = det.get("track_id")
        if tid not in trails:
            continue
        colour = RISK_COLOUR.get(det.get("risk", "GREEN"))
        pts    = trails[tid]
        for i in range(1, len(pts)):
            thickness = max(1, int(3 * i / len(pts)))
            cv2.line(frame, pts[i-1], pts[i], colour, thickness)

    # ── Bounding boxes + labels (with occlusion) ──────────────
    for det in detections:
        colour          = RISK_COLOUR.get(det.get("risk", "GREEN"))
        x1, y1, x2, y2 = det["box"]
        occluded        = det.get("occluded", False)

        if occluded:
            # Dashed box for occluded objects
            _draw_dashed_rect(frame, x1, y1, x2, y2, colour, thickness=2)
            label = "? OCCLUDED"
        else:
            # Regular solid box
            cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
            tid   = det.get("track_id")
            depth = det.get("depth")
            d_str = f" {depth:.1f}m" if depth is not None else ""
            label = f"{det['label']} {det['confidence']:.2f}{d_str}"

        # Draw the label above the box
        cv2.putText(frame, label, (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, colour, 2)

        # ── Scene banner ───────────────────────────────────────────
        banner_colour = RISK_COLOUR[scene_risk]
        cv2.rectangle(frame, (0, 0), (cfg.DISPLAY_WIDTH, 36),
                    banner_colour, -1)
        cv2.putText(frame, f"RISK: {scene_risk}   FPS: {fps:.1f}",
                    (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2)

    # ── Summary panel (bottom-left) ────────────────────────────
    if summary:
        by_risk  = summary.get("by_risk",  {})
        occluded = summary.get("occluded", 0)
        total    = summary.get("total",    0)
        trans    = summary.get("transition")

        panel_y = cfg.DISPLAY_HEIGHT - 90
        cv2.rectangle(frame, (0, panel_y),
                      (260, cfg.DISPLAY_HEIGHT), (30, 30, 30), -1)

        lines = [
            f"Objects: {total}",
            f"  RED  : {by_risk.get('RED',   0)}",
            f"  AMBER: {by_risk.get('AMBER', 0)}   Occluded: {occluded}",
            f"  GREEN: {by_risk.get('GREEN', 0)}",
        ]
        for i, line in enumerate(lines):
            cv2.putText(frame, line, (8, panel_y + 20 + i * 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50,
                        (220, 220, 220), 1)

        # Flash transition label in top banner for 1 second (≈30 frames)
        if trans:
            cv2.putText(frame, f"  [{trans}]",
                        (220, 26), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (255, 255, 255), 2)
    return frame