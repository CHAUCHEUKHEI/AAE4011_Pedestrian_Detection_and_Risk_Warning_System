# 🚗 Real-time Pedestrian Detection & Risk Warning System for Autonomous Vehicles

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/YOLOv8m-Ultralytics-FF6B35" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Course-AAE4011-orange" alt="Course">
  <img src="https://img.shields.io/badge/YouTube-Demo%20Video-FF0000?logo=youtube&logoColor=white" alt="YouTube">
</p>

<p align="center">
  <b>AAE4011 – Artificial Intelligence in Unmanned Autonomous Systems</b><br>
  The Hong Kong Polytechnic University<br>
  Instructor: Dr. Weisong WEN
</p>

> **Group Members:** AL AKIB Ahmad Munjir (23096168D) &nbsp;|&nbsp; CHAU Cheuk Hei (23089671D) &nbsp;|&nbsp; **Date:** April 14, 2026

<p align="center">
  <a href="https://youtu.be/mdRpK6RcI6A">
    <img src="https://img.shields.io/badge/▶%20Watch%20Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch Demo">
  </a>
  &nbsp;
  <a href="https://github.com/CHAUCHEUKHEI/AAE4011_Pedestrian_Detection_and_Risk_Warning_System">
    <img src="https://img.shields.io/badge/View%20on-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Methodology](#-methodology)
- [Repository Structure](#-repository-structure)
- [Prerequisites](#-prerequisites)
- [How to Run](#-how-to-run)
- [Sample Results](#-sample-results)
- [Video Demonstration](#-video-demonstration)
- [Reflection & Critical Analysis](#-reflection--critical-analysis)
- [References](#-references)

---

## 🔍 Overview

This project implements a real-time, end-to-end **Pedestrian Detection and Risk Warning System** designed for autonomous vehicles and drone-based surveillance. The system addresses a fundamental limitation in standard object detection pipelines: knowing not merely *what* objects are present in a scene, but *how immediately dangerous each one is*.

The pipeline integrates five AI-driven stages:

- 🎯 **YOLOv8m detection** of 8 target classes including pedestrians, cyclists, and large vehicles
- 🔁 **ByteTrack multi-object tracking** with persistent IDs and motion trails
- 📏 **Depth Anything V2** monocular metric depth estimation in real metres
- 🫥 **Overlap-fraction occlusion detection** for pedestrians hidden behind parked vehicles
- 🚦 **Risk classification engine** producing GREEN / AMBER / RED scene-level warnings with audio alerts

The system is designed to be modular, configuration-driven, and hardware-agnostic — running on both GPU-accelerated and CPU-only platforms without code changes.

---

## 🎯 Methodology

### Model: YOLOv8m — Pretrained on COCO

The detection backbone is **YOLOv8-medium (YOLOv8m)**, loaded from Ultralytics pretrained weights on the COCO dataset. The medium variant was specifically chosen over the nano, small, large, and extra-large variants based on a deliberate accuracy-speed trade-off.

**⚡ Why YOLOv8m over nano (YOLOv8n)?**
YOLOv8n achieves ~37.3% mAP₅₀ on COCO, while YOLOv8m achieves ~50.2%. For a pedestrian risk warning system where missed detections carry a higher cost than reduced throughput, the medium variant's superior recall on small and partially visible objects justifies the added inference cost. In a safety-critical pipeline, a missed pedestrian at 3 metres is an unacceptable failure mode.

**⚡ Why not YOLOv8l or YOLOv8x?**
Larger variants offer marginal accuracy gains at substantially higher latency. At the operating speeds of campus rovers and low-altitude UAVs (10–30 km/h), the medium model's ~8 fps end-to-end throughput provides sufficient temporal resolution for real-time risk assessment.

**🔄 Why not Faster R-CNN or SSD?**

| Model | Speed | Accuracy | Verdict |
|---|---|---|---|
| **YOLOv8m** ✅ | Fast (single-pass, anchor-free) | mAP₅₀ ~50.2% | Best balance for real-time safety pipeline |
| Faster R-CNN | 5–10× slower (two-stage: RPN + classifier) | Higher mAP on benchmarks | Unacceptable latency for continuous video stream |
| SSD | Faster than Faster R-CNN | Lower precision on small/occluded objects | Insufficient recall for distant pedestrians |

**✅ Why no fine-tuning required?**
The COCO dataset already contains all eight target classes: `person` (0), `bicycle` (1), `car` (2), `motorcycle` (3), `bus` (5), `truck` (7), `cat` (15), and `dog` (16). Pretrained weights generalise directly to urban driving footage without additional training or data preparation.

---

### 🔁 Tracking: ByteTrack

Multi-object tracking uses **ByteTrack**, which associates *every* detection box — including low-confidence ones — with existing tracklets in a two-stage matching process via Kalman filter and IoU association. Unlike high-confidence-only trackers, ByteTrack significantly reduces identity switches and tracklet fragmentation in occluded or crowded scenes. Each track carries a persistent integer ID and a 30-frame motion trail history (~1 second at 30 fps), used both for visualisation and velocity estimation.

---

### 📏 Depth Estimation: Depth Anything V2 Metric

Depth estimation is performed by **Depth Anything V2 Metric Outdoor Base**, which outputs depth in **absolute metres** — a critical distinction from relative depth models whose normalised outputs cannot be mapped to physically meaningful safety thresholds.

A relative depth model might indicate that object A is "closer than" object B, but cannot answer: *Is object A within 4 metres?* For a risk warning system with hard distance thresholds (RED < 4 m, AMBER < 10 m), metric depth is a non-negotiable requirement. Per-object depth is sampled from the 20th percentile of the lower-centre bounding-box patch to avoid ground-plane bias and handle partial occlusion robustly.

---

### 🫥 Occlusion Detection: Overlap Fraction (not IoU)

Occlusion is detected by computing the fraction of a vulnerable object's bounding box that is covered by a large vehicle's bounding box:
