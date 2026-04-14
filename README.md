
### Step 5 — (Optional) Extract Frames for Offline Inspection

```bash
python3 ~/catkin_ws/src/aae4011_vehicle_detection/scripts/extract_from_bag.py \
  --bag /path/to/assignment.bag \
  --output ./extracted_frames
```

This saves every annotated frame as a numbered JPEG (`det_00001.jpg`, `det_00002.jpg`, …) for inspection without running the full ROS pipeline.

### Step 6 — Launch the Full Detection Pipeline

Open two terminals:

**Terminal 1 — Start roscore:**

```bash
roscore
```

**Terminal 2 — Launch detector + rosbag player:**

```bash
roslaunch aae4011_vehicle_detection detect.launch \
  bag_file:=/path/to/assignment.bag
```

The detector node will begin subscribing to `/hikcamera/image_2/compressed` and printing detection counts to the console.

### Step 7 — Open the Web Dashboard

**Terminal 3:**

```bash
python3 ~/catkin_ws/src/aae4011_vehicle_detection/scripts/web_ui.py
```

Open a browser and navigate to: [http://localhost:5000](http://localhost:5000)

Use the **Play** button to cycle through annotated frames and view live detection statistics.

---

## 📊 Sample Results

### Image Extraction Summary

| Property | Value |
|---|---|
| ROS Topic | `/hikcamera/image_2/compressed` |
| Message Type | `sensor_msgs/CompressedImage` |
| Total frames in bag | 1,142 |
| Frames processed (ROS pipeline) | 442 |
| Bag duration | 1 min 54 sec |
| Frame resolution | 1920 × 1080 px |

> **Why 442 frames processed vs 1,142 total?**
> The ROS subscriber uses `queue_size=1` and processes only the latest available frame to prevent queue buildup when inference is slower than the publish rate. Frames are dropped intentionally to maintain real-time responsiveness.

### Detection Statistics (Full ROS Pipeline — 442 frames)

| Class | COCO ID | Total Detections | % of Total |
|---|---|---|---|
| Car | 2 | 923 | 90.2% |
| Bus | 5 | 74 | 7.2% |
| Truck | 7 | 26 | 2.5% |
| Motorcycle | 3 | 1 | 0.1% |
| **Total** | — | **1,024** | **100%** |

The dominance of cars (~90%) is consistent with Hong Kong urban road traffic composition, validating that the model is producing plausible detections rather than false positives from irrelevant classes.

> **Note on Web UI numbers:** The Web UI samples every 10th extracted frame (115 frames), giving proportionally smaller counts (~203 cars, ~21 buses, ~8 trucks). This is a deliberate performance optimisation for browser rendering — the per-class detection ratio is consistent with the full pipeline, confirming stable model performance across the dataset.

### Sample Detection Screenshots

![Frame 10 — Truck and car detection](screenshots/frame_010.png)
*Frame 10 — Truck detected (conf: 0.85) and ego-vehicle car (conf: 0.78)*

![Frame 50 — Multiple car detections](screenshots/frame_050.png)
*Frame 50 — Two cars detected (conf: 0.83, 0.49) and ego-vehicle car (conf: 0.73)*

> White boxes = car, yellow boxes = truck. Confidence scores shown above each bounding box.

---

## 🎬 Video Demonstration

[![Demo Video](https://img.shields.io/badge/▶%20Watch%20on%20YouTube-Unlisted-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtu.be/J1dSmeUI28c)

📺 **Link:** https://youtu.be/J1dSmeUI28c  
⏱️ **Duration:** 3 minutes 09 seconds

The video demonstrates all three required components:

**(a) Launching the ROS Package**
Shows opening two WSL2 terminals, running `roscore` in the first, then executing `roslaunch aae4011_vehicle_detection detect.launch bag_file:=...` in the second. The terminal output confirms the detector node has initialised YOLOv8n and is actively subscribing to `/hikcamera/image_2/compressed`, with detection counts printing to console in real time.

**(b) The UI Displaying Detection Results**
Shows the Flask web dashboard at `http://localhost:5000`. The **Play** button is pressed to cycle through annotated frames. Each frame shows bounding boxes with class labels and confidence scores. The live statistics panel updates counts for Car, Bus, Truck, and Motorcycle as frames advance.

**(c) Brief Explanation of Results**
On-screen narration explains: 442 frames were processed from a 1 min 54 sec rosbag, producing 1,024 total vehicle detections. Cars account for ~90% of detections, consistent with typical urban Hong Kong traffic density. YOLOv8n ran at approximately 15–25 fps on the host machine without GPU acceleration.

---

## 💬 Reflection & Critical Analysis

### (a) What Did You Learn?

**Skill 1 — ROS publish/subscribe architecture and message decoding:**
Constructing a subscriber node from scratch taught how nodes interact asynchronously through named topics and how the rosbag player serves as a publisher replaying messages at original timestamps. A key practical lesson was the `queue_size` parameter: `queue_size=1` ensures the callback always processes the newest frame rather than building a backlog — critical when inference occasionally exceeds the inter-frame interval. An important discovery was the internal structure of `sensor_msgs/CompressedImage`: the `data` field is a raw JPEG byte array decodable directly with `numpy.frombuffer` and `cv2.imdecode`, eliminating the need for `cv_bridge` (which caused build errors in WSL2).

**Skill 2 — Integrating deep learning inference inside a ROS callback:**
Placing a YOLOv8 inference call inside a ROS subscriber callback exposed the practical constraints of event-driven neural network execution. The most important lesson: the model must be loaded in `__init__`, not inside the callback — reloading weights per frame adds hundreds of milliseconds of latency and renders the pipeline unusable. Building custom overlays from the structured `results[0].boxes` object (`.xyxy`, `.cls`, `.conf`) using `cv2.rectangle` and `cv2.putText` was also a valuable hands-on skill. Filtering by a confidence threshold of `conf > 0.4` substantially reduced false positives on partially occluded vehicles.

### (b) How Did You Use AI Tools?

**Primary tool:** Perplexity AI, with Claude used for cross-checking specific ROS API questions.

| Use Case | How AI Helped |
|---|---|
| Boilerplate generation | Generated initial `CMakeLists.txt` and `package.xml` with correct `<depend>` tags for `rospy`, `sensor_msgs`, and `std_msgs` — saved ~2–3 hours |
| Debugging | Diagnosed `catkin_make` failures caused by LIO-SAM's unresolved dependencies in the same workspace; suggested `--pkg` flag |
| Message format clarification | Explained the difference between `sensor_msgs/CompressedImage` and `sensor_msgs/Image`, and why `cv_bridge` is not needed for NumPy decoding |
| Flask UI scaffolding | Wrote the HTML/JavaScript template for the image slideshow with `setInterval` cycling and AJAX statistics refresh |
| Research | Helped identify and understand relevant papers and VisDrone/UAVDT datasets efficiently |
| Writing | Provided style suggestions, improved readability of technical sections, and assisted with language error checking |

**Limitations encountered:** The AI occasionally proposed ROS2 syntax (`colcon build`, `rclpy`) instead of ROS Noetic equivalents. These errors were immediately caught by cross-referencing the official ROS Noetic documentation before implementation. The AI also could not inspect the actual bag file to verify the compressed image topic name — that required running `rosbag info` manually. Overall, AI was a highly effective boilerplate and debugging accelerator, but domain verification remained the student's responsibility.

### (c) How to Improve Accuracy?

**Strategy 1 — Fine-tune on aerial and drone-perspective imagery:**
YOLOv8n was pretrained exclusively on ground-level COCO images where vehicles appear at familiar aspect ratios and viewpoints. Elevated or drone-mounted cameras capture vehicles from a top-down or near-top-down perspective, creating a viewpoint mismatch that reduces detection confidence and recall. Fine-tuning on aerial-specific datasets such as VisDrone or UAVDT — both containing thousands of labelled vehicle examples from UAV perspectives — would directly condition the model to these viewpoints. Even 500–1,000 labelled aerial images added to the training set can boost mAP@0.5 on aerial benchmarks by 5–15 percentage points.

**Strategy 2 — Increase inference resolution from 640 to 1280 pixels:**
YOLOv8n defaults to 640×640 input resolution. A 1920×1080 frame downsampled to 640 pixels can reduce small or distant vehicles to as few as 10×10 pixels — below the practical detection threshold for most YOLO variants. Setting `imgsz=1280` in `model.predict()` preserves significantly more spatial detail and improves recall for far-field vehicles. The trade-off is ~2–3× inference time per frame; however, for offline rosbag processing where real-time throughput is not strictly required, this is an acceptable cost. On dedicated GPU hardware (e.g., RTX 3060), 1280-resolution inference can still exceed 15 fps.

### (d) Real-World Challenges

**Challenge 1 — Computational constraints on embedded drone hardware:**
Operational drones use lightweight embedded computers (NVIDIA Jetson Nano, Orin NX, Raspberry Pi CM4) rather than full desktop workstations. YOLOv8n at 1920×1080 on a Jetson Nano yields approximately 8–15 fps unoptimised — potentially insufficient to keep pace with the camera frame rate. Addressing this requires model compression: post-training INT8 quantisation with NVIDIA TensorRT improves throughput by 3–4× with minimal accuracy loss on Jetson hardware. Alternatively, reducing input resolution to 416×416 or deploying purpose-built edge models (YOLOv8n-TensorRT, NanoDet) can meet compute budgets while maintaining acceptable accuracy for large, close-range vehicles.

**Challenge 2 — Image degradation during active flight:**
The rosbag footage was recorded under near-static, controlled conditions. During real drone flight, several physical effects systematically degrade image quality: (i) **motion blur** from high-speed translational or rotational manoeuvres blurs vehicle boundaries and reduces bounding box confidence; (ii) **vibration jitter** from propellers can temporarily saturate or underexpose the image, dropping confidence scores below detection thresholds; (iii) **rolling shutter distortion** from CMOS sensors warps fast-moving objects. Mitigation requires a combination of hardware stabilisation (3-axis gimbal, vibration-damping mounts), software frame-quality gating to skip degraded frames before inference, and training data augmentation (motion blur kernels, brightness/contrast jitter, noise injection) to improve model robustness.

---

## 📚 References

1. Jocher, G., Chaurasia, A., & Qiu, J. (2023). *Ultralytics YOLOv8*. GitHub. https://github.com/ultralytics/ultralytics

2. ROS Noetic Documentation. (2020). *ROS Wiki — Noetic Ninjemys*. http://wiki.ros.org/noetic

3. Lin, T.-Y., Maire, M., Belongie, S., et al. (2014). *Microsoft COCO: Common Objects in Context*. ECCV 2014. https://arxiv.org/abs/1405.0312

4. Zhu, P., Wen, L., Du, D., Bian, X., Fan, H., Hu, Q., & Ling, H. (2021). *Detection and Tracking Meet Drones Challenge*. IEEE Transactions on Pattern Analysis and Machine Intelligence. https://doi.org/10.1109/TPAMI.2021.3119563

5. Du, D., Qi, Y., Yu, H., Yang, Y., Duan, K., Li, G., Zhang, W., Huang, Q., & Tian, Q. (2018). *The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking*. ECCV 2018. https://doi.org/10.1007/978-3-030-01249-6_23

6. ROS Noetic — *sensor_msgs/CompressedImage Message*. http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/CompressedImage.html

---

<p align="center">
  Submitted for AAE4011 Assignment 1 &nbsp;|&nbsp; PolyU AAE &nbsp;|&nbsp; March 2026
</p>
