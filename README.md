
All stages read from `config_4011.py` for global parameters.

---

## 🚦 Risk Classification Logic

| Condition | Risk Level |
|---|---|
| In-lane object, depth < 4.0 m | 🔴 RED |
| In-lane object, depth < 10.0 m | 🟠 AMBER |
| Out-of-lane object, enters lane within 10 frames | 🔴 RED |
| Out-of-lane object, enters lane within 20 frames | 🟠 AMBER |
| Occluded vulnerable object (any depth) | 🟠 AMBER (forced) |
| All other detections | 🟢 GREEN |

**Asymmetric smoothing:** Risk upgrades are immediate; downgrades require 2/3 frame consensus to prevent flickering.

---

## 📊 Performance

| Metric | Value |
|---|---|
| End-to-end FPS (GPU, Colab) | ~7.5 – 8.6 fps |
| Output resolution | 1280 × 720 |
| Detection model | YOLOv8m |
| Depth model | Depth Anything V2 Metric Outdoor Base |
| Output format | MP4 (H.264, 20 fps) |

---

## 📦 Key Dependencies

| Library | Purpose |
|---|---|
| `ultralytics` | YOLOv8 detection and ByteTrack tracking |
| `transformers` | Depth Anything V2 model loading |
| `torch` / `torchvision` | Model inference backend |
| `opencv-python` | Frame I/O and visualisation |
| `numpy` | Array operations |
| `beepy` | Audio alert backend (Colab) |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🎓 Course Information

| Field | Detail |
|---|---|
| Course | AAE4011 – Artificial Intelligence in Unmanned Autonomous Systems |
| Institution | The Hong Kong Polytechnic University |
| Department | Aeronautical and Aviation Engineering |
| Semester | Semester 2, 2025/26 |
| Submission Date | April 14, 2026 |

---

## 📄 License

This project is submitted for academic assessment purposes at PolyU. All code is original work by the group members unless otherwise cited.
