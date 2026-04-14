# warning_4011.py
# Stage 5 — Warning output layer.
#

import threading
import config_4011 as cfg

# ── Audio backend selection ────────────────────────────────────────────────────
_USE_BEEPY  = False
_USE_TTS    = False

try:
    import beepy
    _USE_BEEPY = True
except ImportError:
    pass

if not _USE_BEEPY:
    try:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", 160)
        _USE_TTS = True
    except Exception:
        pass


# ── Beep IDs in beepy ─────────────────────────────────────────────────────────
# 1=coin, 2=robot_error, 3=ping, 4=error, 5=ready, 6=success
_BEEP_AMBER = 3   # ping  — gentle
_BEEP_RED   = 4   # error — urgent


# ── Internal helpers ───────────────────────────────────────────────────────────

def _play_async(fn):
    """Run audio function in a daemon thread — never blocks the camera loop."""
    t = threading.Thread(target=fn, daemon=True)
    t.start()


def _alert_amber():
    if _USE_BEEPY:
        beepy.beep(sound=_BEEP_AMBER)
    elif _USE_TTS:
        _tts_engine.say("Caution")
        _tts_engine.runAndWait()


def _alert_red():
    if _USE_BEEPY:
        beepy.beep(sound=_BEEP_RED)
        beepy.beep(sound=_BEEP_RED)   # double beep = more urgent
    elif _USE_TTS:
        _tts_engine.say("Warning")
        _tts_engine.runAndWait()


# ── Public class ───────────────────────────────────────────────────────────────

class WarningSystem:
    

    _PRIORITY = {"GREEN": 0, "AMBER": 1, "RED": 2}

    def __init__(self):
        self._prev_risk    = "GREEN"
        self._audio_available = _USE_BEEPY or _USE_TTS
        if self._audio_available:
            backend = "beepy" if _USE_BEEPY else "pyttsx3"
            print(f"[Warning] Audio backend: {backend}")
        else:
            print("[Warning] No audio backend found — visual warnings only.")
            print("[Warning] Install beepy:   pip install beepy")

    # ------------------------------------------------------------------
    def update(self, scene_risk: str, detections: list) -> dict:
    
        prev = self._prev_risk
        curr = scene_risk

        transition = None
        if self._PRIORITY[curr] > self._PRIORITY[prev]:
            transition = f"{prev}→{curr}"
            if curr == "RED":
                _play_async(_alert_red)
            elif curr == "AMBER":
                _play_async(_alert_amber)

        self._prev_risk = curr

        # Build summary counts
        by_risk  = {"GREEN": 0, "AMBER": 0, "RED": 0}
        occluded = 0
        for det in detections:
            r = det.get("risk", "GREEN")
            if r in by_risk:
                by_risk[r] += 1
            if det.get("occluded", False):
                occluded += 1

        return {
            "scene_risk": curr,
            "total":      len(detections),
            "by_risk":    by_risk,
            "occluded":   occluded,
            "transition": transition,
        }
