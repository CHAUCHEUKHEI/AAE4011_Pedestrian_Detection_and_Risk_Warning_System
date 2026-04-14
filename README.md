
---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/[YOUR-USERNAME]/AAE4011-Group7.git
cd AAE4011-Group7

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run on a video file
python main_4011.py

# 4. (Optional) Enable audio warnings
# In config_4011.py, set: ENABLE_WARNINGS = True
```

---

## 🛠️ Installation & Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/[YOUR-USERNAME]/AAE4011-Group7.git
cd AAE4011-Group7
```

### Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **GPU acceleration:** PyTorch automatically detects and uses CUDA if available. No extra configuration required. The system runs on CPU-only machines without code modification.

### Step 3 — Set Your Video Source

Open `config_4011.py` and set the video path:

```python
# config_4011.py
VIDEO_SOURCE = "path/to/your/video.mp4"   # video file
# VIDEO_SOURCE = 0                         # live webcam
```

### Step 4 — Run the System

```bash
python main_4011.py
```

The annotated output is saved as `output4011.mp4` in the working directory.

### Running in Google Colab

```python
# Mount Drive (if video is on Drive)
from google.colab import drive
drive.mount('/content/drive')

# Run the pipeline
!python main_4011.py
```

---

## ⚙️ Configuration

All tunable parameters are centralised in `config_4011.py`. Each pipeline stage can be independently enabled or disabled:

```python
# ── Model ────────────────────────────────────────────
MODEL_WEIGHTS          = "yolov8m.pt"   # nano / small / medium / large
CONFIDENCE_THRESHOLD   = 0.45

# ── Stage Toggles ────────────────────────────────────
ENABLE_TRACKING        = True
ENABLE_RISK            = True
ENABLE_OCCLUSION       = True
ENABLE_WARNINGS        = False          # Set True for audio alerts

# ── Display ──────────────────────────────────────────
DISPLAY_WIDTH          = 1280
DISPLAY_HEIGHT         = 720

# ── Risk Thresholds ──────────────────────────────────
METRIC_RED_M           = 4.0            # metres
METRIC_AMBER_M         = 10.0           # metres
LANE_CORRIDOR_FRACTION = 0.35           # fraction of frame width

# ── Trajectory Prediction ────────────────────────────
TRAJ_LOOKAHEAD         = 25             # frames
TRAJ_RED_FRAMES        = 10             # lane entry within N frames → RED
TRAJ_AMBER_FRAMES      = 20             # lane entry within N frames → AMBER
VELOCITY_SMOOTH_N      = 5              # velocity averaging window

# ── Tracking ─────────────────────────────────────────
TRAIL_LENGTH           = 30             # motion trail history (frames)

# ── Occlusion ────────────────────────────────────────
OCCLUSION_OVERLAP_THRESHOLD = 0.20     # overlap fraction threshold
```

---

## 📦 Requirements

| Library | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Runtime |
| `torch` / `torchvision` | 2.0+ | Model inference backend |
| `opencv-python` | 4.8+ | Frame I/O and rendering |
| `ultralytics` | ≥ 8.0.0 | YOLOv8 detection + ByteTrack |
| `transformers` | ≥ 4.40 | Depth Anything V2 |
| `numpy` | ≥ 1.24 | Array operations |
| `beepy` | latest | Audio beep alerts *(optional)* |
| `pyttsx3` | latest | Text-to-speech alerts *(optional)* |

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## 📊 Results

| Metric | Value |
|---|---|
| End-to-end FPS (GPU, Colab) | ~7.5 – 8.6 fps |
| Output resolution | 1280 × 720 |
| Detection model | YOLOv8m (float32) |
| Depth model precision | float16 (GPU) |
| Output format | MP4 (H.264, 20 fps) |

**Key achievements:**

- ✅ **Real-time performance** at ~8 fps on Google Colab GPU
- ✅ **Metric depth generalisation** — distance thresholds apply consistently across different scenes without per-scene calibration
- ✅ **Occlusion detection** — pedestrians behind parked vehicles correctly flagged as AMBER with dashed box rendering
- ✅ **Trajectory prediction** — out-of-lane cyclists and pedestrians moving inward correctly elevated to AMBER/RED
- ✅ **Flicker-free warnings** — asymmetric smoothing prevents rapid toggling at depth boundaries without delaying genuine risk upgrades

---

## 📸 Screenshots

> *(Replace paths with actual screenshots)*

**GREEN — Clear road, distant vehicles only:**
![GREEN Scene](screenshots/scenario_green.png)

**AMBER — Pedestrian in lane at medium range:**
![AMBER Scene](screenshots/scenario_amber.png)

**AMBER (Occlusion) — Pedestrian behind parked car:**
![Occlusion Scene](screenshots/scenario_occlusion.png)

**RED — Close-range object in lane:**
![RED Scene](screenshots/scenario_red.png)

---

## 🙏 Acknowledgments

- **YOLOv8** — [Ultralytics](https://github.com/ultralytics/ultralytics) by Jocher et al.
- **ByteTrack** — Zhang et al., *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*, ECCV 2022
- **Depth Anything V2** — Yang et al., *Depth Anything V2*, NeurIPS 2024
- **COCO Dataset** — Lin et al., *Microsoft COCO: Common Objects in Context*, ECCV 2014
- **Dr. Weisong WEN** — Course instructor, AAE4011, The Hong Kong Polytechnic University

---

## 📄 License

This project is submitted for academic assessment at The Hong Kong Polytechnic University.
