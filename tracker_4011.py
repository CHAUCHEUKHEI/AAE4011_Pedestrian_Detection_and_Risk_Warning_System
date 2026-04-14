# tracker_4011.py
# Stage 2 — ByteTrack integration with motion trails.

from collections import deque
import config_4011 as cfg


class Tracker:
    def __init__(self):
        self.trails: dict = {}
        print(f"[Tracker] ByteTrack ready  |  trail={cfg.TRAIL_LENGTH}f")

    def update(self, detections: list) -> dict:
        """
        Update trails from current detections.
        Returns trails: dict  track_id → list of (cx, cy), oldest first.
        """
        active_ids = set()

        for det in detections:
            tid = det.get("track_id")
            if tid is None:
                continue
            active_ids.add(tid)
            x1, y1, x2, y2 = det["box"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            if tid not in self.trails:
                self.trails[tid] = deque(maxlen=cfg.TRAIL_LENGTH)
            self.trails[tid].append((cx, cy))

        gone = [tid for tid in self.trails if tid not in active_ids]
        for tid in gone:
            del self.trails[tid]

        return {tid: list(pts) for tid, pts in self.trails.items()}
