# depth_estimator_4011.py
# Stage 3 — Monocular depth estimation using Depth Anything V2 Metric Outdoor.

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import config_4011 as cfg


class DepthEstimator:
    # Metric outdoor model — outputs depth in metres
    MODEL_ID = "depth-anything/Depth-Anything-V2-Metric-Outdoor-Base-hf"

    def __init__(self):
        print(f"[Depth] Loading {self.MODEL_ID} ...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Depth] Device: {self.device}")

        self.processor = AutoImageProcessor.from_pretrained(self.MODEL_ID)
        self.model     = AutoModelForDepthEstimation.from_pretrained(
            self.MODEL_ID,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device)
        self.model.eval()
        print("[Depth] Metric depth model ready — output in metres.")

    def estimate(self, frame: np.ndarray) -> np.ndarray:
        """
        Run depth inference on a BGR OpenCV frame.

        Returns float32 array (DISPLAY_HEIGHT, DISPLAY_WIDTH).
        Values are approximate depth in METRES.
        Lower value = closer to camera.
        Typical range for urban driving: 0.5m – 80m.
        """
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            depth_m = outputs.predicted_depth.squeeze().cpu().float().numpy()

        # Resize to display resolution so box pixel coords index correctly
        depth_map = cv2.resize(
            depth_m,
            (cfg.DISPLAY_WIDTH, cfg.DISPLAY_HEIGHT),
            interpolation=cv2.INTER_LINEAR,
        )
        return depth_map.astype(np.float32)

    def colourmap(self, depth_map: np.ndarray) -> np.ndarray:
        """
        Visualise depth map. Clamp to 0-50m then apply MAGMA colormap.
        Warm = close, cool = far.
        """
        clamped = np.clip(depth_map, 0, 50)
        uint8   = (clamped / 50 * 255).astype(np.uint8)
        return cv2.applyColorMap(uint8, cv2.COLORMAP_MAGMA)
