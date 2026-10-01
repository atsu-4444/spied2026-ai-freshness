from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_ID = "Dhahlan2000/freshness_detector_updated"
MODEL_DIR = PROJECT_ROOT / "models" / "freshness_detector_updated"

CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15
MAX_CAMERA_FAILURES = 20

# One ENTER press starts a repeated-recognition scan for the current slot.
SLOT_COUNT = 4
SCAN_DURATION_SECONDS = 3.0
INFERENCE_INTERVAL = 0.4

WINDOW_NAME = "SP!ED 2026 - 4-Slot Priority Scanner"
DASHBOARD_WIDTH = 1400
DASHBOARD_HEIGHT = 820
