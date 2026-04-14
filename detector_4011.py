# detector_4011.py

from ultralytics import YOLO
import config_4011 as cfg


class Detector:
    def __init__(self):
        print(f"[Detector] Loading model: {cfg.MODEL_WEIGHTS}")

        import torch
        self.model = YOLO(cfg.MODEL_WEIGHTS)

        if torch.cuda.is_available():
            self.model.to("cuda")
            print("[Detector] Using GPU")
        else:
            print("[Detector] Using CPU")

        self.target_ids = list(cfg.TARGET_CLASSES.keys())
        print(f"[Detector] Watching classes: {cfg.TARGET_CLASSES}")

    # ------------------------------------------------------------------
    def detect(self, frame, use_tracker: bool = False) -> list[dict]:

        if use_tracker:
            # persist=True tells ByteTrack to link detections across frames
            # using its internal Kalman filter + IoU matching.
            results = self.model.track(
                frame,
                classes=self.target_ids,
                conf=cfg.CONFIDENCE_THRESHOLD,
                tracker="bytetrack.yaml",   # bundled with Ultralytics
                persist=True,               # keep track state between calls
                verbose=False,
            )
        else:
            results = self.model(
                frame,
                classes=self.target_ids,
                conf=cfg.CONFIDENCE_THRESHOLD,
                verbose=False,
            )

        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])

                # box.id is a tensor when tracking is on, None otherwise
                if box.id is not None:
                    track_id = int(box.id[0])
                else:
                    track_id = None

                detections.append({
                    "class_id":   class_id,
                    "label":      cfg.TARGET_CLASSES.get(class_id, "unknown"),
                    "confidence": float(box.conf[0]),
                    "box":        [int(v) for v in box.xyxy[0].tolist()],
                    "track_id":   track_id,
                })

        return detections
