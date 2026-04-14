# main_4011.py — Stage 5 complete.

import cv2, time
import config_4011 as cfg
from detector_4011 import Detector
from display_4011  import render

IS_COLAB = True
print("IS_COLAB =", IS_COLAB)

if cfg.ENABLE_TRACKING:
    from tracker_4011 import Tracker
if cfg.ENABLE_RISK:
    from depth_estimator_4011 import DepthEstimator
    from risk_engine_4011     import score as risk_score
if cfg.ENABLE_OCCLUSION:
    from occlusion_4011 import check as occlusion_check
if cfg.ENABLE_WARNINGS:
    from warning_4011 import WarningSystem

OUTPUT_PATH = "output_4011.mp4"

def open_source():
    cap = cv2.VideoCapture(cfg.SOURCE)
    if not cap.isOpened():
        raise RuntimeError(f"[Main] Could not open source: {cfg.SOURCE}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cfg.DISPLAY_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.DISPLAY_HEIGHT)
    print(f"[Main] Source opened: {cfg.SOURCE}")
    return cap

def main():
    print("=" * 55)
    print("  AAE4011 — Pedestrian Detection & Risk Warning System")
    print("  Stage 5: Full System — Complete")
    if IS_COLAB: print(f"  Colab mode → output: {OUTPUT_PATH}")
    else:        print("  Press Q to quit")
    print("=" * 55)

    detector  = Detector()
    cap       = open_source()
    tracker   = Tracker()        if cfg.ENABLE_TRACKING else None
    depth_est = DepthEstimator() if cfg.ENABLE_RISK     else None
    warning   = WarningSystem()  if cfg.ENABLE_WARNINGS else None
    trails    = {}
    depth_map = None
    scene_risk = "GREEN"
    summary    = {}

    writer = None
    if IS_COLAB:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, 20.0,
                                 (cfg.DISPLAY_WIDTH, cfg.DISPLAY_HEIGHT))

    prev_time = time.time()
    fps = 0.0; frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Main] End of stream."); break

        frame = cv2.resize(frame, (cfg.DISPLAY_WIDTH, cfg.DISPLAY_HEIGHT))

        detections = detector.detect(frame, use_tracker=cfg.ENABLE_TRACKING)

        if cfg.ENABLE_TRACKING and tracker:
            trails = tracker.update(detections)

        if cfg.ENABLE_OCCLUSION:
            detections = occlusion_check(detections)

        if cfg.ENABLE_RISK and depth_est:
            depth_map              = depth_est.estimate(frame)
            detections, scene_risk = risk_score(detections, depth_map, trails)
        else:
            scene_risk = "GREEN"

        if cfg.ENABLE_WARNINGS and warning:
            summary = warning.update(scene_risk, detections)
        else:
            summary = {}

        now = time.time()
        fps = 0.9 * fps + 0.1 / (now - prev_time + 1e-9)
        prev_time = now

        frame = render(frame, detections, trails, scene_risk, fps, depth_map, summary)

        if IS_COLAB:
            writer.write(frame)
            frame_count += 1
            if frame_count % 50 == 0:
                print(f"[Main] {frame_count} frames processed...")
        else:
            cv2.imshow("AAE4011 — Pedestrian Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Main] User quit."); break

    cap.release()
    cv2.destroyAllWindows()
    if writer:
        writer.release()
        print(f"[Main] Saved → {OUTPUT_PATH}")
        from IPython.display import HTML, display
        from base64 import b64encode
        mp4      = open(OUTPUT_PATH, "rb").read()
        data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
        display(HTML(f'<video width="960" controls autoplay loop>'
                     f'<source src="{data_url}" type="video/mp4"></video>'))
    print("[Main] Shutdown complete.")

if __name__ == "__main__":
    main()
