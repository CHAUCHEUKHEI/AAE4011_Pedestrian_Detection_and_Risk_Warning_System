# config_4011.py
# Central configuration for the pedestrian detection & risk warning system.

# ---------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------
MODEL_WEIGHTS = "yolov8m.pt" 

CONFIDENCE_THRESHOLD = 0.45    # Detections below this confidence are ignored.

# ---------------------------------------------------------------------------
# TARGET CLASSES  (COCO dataset class IDs)
# We detect everything that can move on or near a road.
# Parked cars / trucks are included because they create occlusion zones
# where a child could be hidden.
# ---------------------------------------------------------------------------
TARGET_CLASSES = {
    0:  "person",
    1:  "bicycle",
    2:  "car",          # occlusion source
    3:  "motorcycle",
    5:  "bus",          # occlusion source
    7:  "truck",        # occlusion source
    15: "cat",
    16: "dog",
}

# Classes we treat as occlusion sources (large parked objects)
OCCLUSION_CLASSES = {2, 5, 7}   # car, bus, truck

# ---------------------------------------------------------------------------
# DISPLAY COLOURS  (BGR format for OpenCV)
# One colour per class so the driver can read the scene at a glance.
# ---------------------------------------------------------------------------
CLASS_COLOURS = {
    0:  (255, 255, 255),   # person      — white
    1:  (255, 165,   0),   # bicycle     — orange
    2:  (180, 180, 180),   # car         — grey
    3:  (255, 100, 100),   # motorcycle  — light blue
    5:  (120, 120, 255),   # bus         — red-ish
    7:  (100,  60, 200),   # truck       — purple
    15: (0,   255, 150),   # cat         — teal
    16: (0,   200, 255),   # dog         — yellow
}

# ---------------------------------------------------------------------------
# RISK WARNING COLOURS  (BGR)
# ---------------------------------------------------------------------------
RISK_COLOURS = {
    "GREEN":  (0, 220,   0),
    "AMBER":  (0, 165, 255),
    "RED":    (0,   0, 255),
}

# ---------------------------------------------------------------------------
# CAMERA / VIDEO SOURCE
# ---------------------------------------------------------------------------
# 0 = default webcam.
SOURCE = "WhatsApp Video 2026-04-10 at 01.18.14.mp4"

# Target display resolution (width, height). Frames are resized to this.
DISPLAY_WIDTH  = 1280
DISPLAY_HEIGHT = 720


# STAGE FLAGS  — flip these to True when each stage

# ── Stage 2: Tracking ─────────────────────────────────────────
ENABLE_TRACKING = True
TRAIL_LENGTH    = 30

# ── Stage 3: Metric Depth Risk ─────────────────────────────────
ENABLE_RISK = True

LANE_CORRIDOR_FRACTION = 0.35

# Real distance thresholds in METRES
METRIC_RED_M   =  4.0    # closer than ?m  → RED
METRIC_AMBER_M = 10.0    # closer than ?m → AMBER

# Trajectory prediction
TRAJ_LOOKAHEAD    = 25
TRAJ_RED_FRAMES   = 10
TRAJ_AMBER_FRAMES = 20
VELOCITY_SMOOTH_N = 5

# ── Stage 4: Occlusion ────────────────────────────────────────
ENABLE_OCCLUSION = True

# Fraction of a vulnerable object's box that must be covered
# by a vehicle box before it's considered occluded.
# 0.20 = if ?% of the pedestrian box is hidden → flag it.
OCCLUSION_OVERLAP_THRESHOLD = 0.20

# ── Stage 5: Warnings ─────────────────────────────────────────
ENABLE_WARNINGS = False