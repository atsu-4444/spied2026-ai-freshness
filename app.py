import time

import cv2

from src.camera import CameraStream
from src.classifier import FreshnessClassifier
from src.config import (
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_ID,
    CAMERA_WIDTH,
    DASHBOARD_HEIGHT,
    DASHBOARD_WIDTH,
    INFERENCE_INTERVAL,
    MAX_CAMERA_FAILURES,
    MODEL_DIR,
    MODEL_ID,
    SCAN_DURATION_SECONDS,
    SLOT_COUNT,
    WINDOW_NAME,
)
from src.freshness import (
    PredictionVoteBuffer,
    extract_food_name,
    food_display_name,
    get_condition_group,
    select_priority_slot,
)
from src.gui import FreshnessDashboard


STATE_READY = "READY"
STATE_SCANNING = "SCANNING"
STATE_RESULTS = "RESULTS"


def _build_slot_result(slot_number, label, confidence, winner_count, sample_count):
    food_key = extract_food_name(label)
    return {
        "slot": slot_number,
        "label": label,
        "confidence": confidence,
        "food": food_display_name(food_key),
        "condition": get_condition_group(label),
        "winner_count": winner_count,
        "sample_count": sample_count,
    }


def main():
    print("=" * 64)
    print("SP!ED 2026 - 4-Slot Food Freshness Priority Scanner")
    print("=" * 64)
    print("ENTER: scan current slot / reset result")
    print("Q or ESC: quit")

    classifier = FreshnessClassifier(MODEL_ID, MODEL_DIR)
    print(f"Device: {classifier.device}")
    print(f"Classes: {classifier.num_labels}")

    camera = CameraStream(
        camera_id=CAMERA_ID,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        fps=CAMERA_FPS,
        max_failures=MAX_CAMERA_FAILURES,
    )
    camera.start()

    if not camera.wait_until_ready(timeout=10.0):
        camera.stop()
        raise RuntimeError(
            f"Camera {CAMERA_ID} could not be started. "
            "Try changing CAMERA_ID in src/config.py."
        )

    dashboard = FreshnessDashboard(
        width=DASHBOARD_WIDTH,
        height=DASHBOARD_HEIGHT,
        window_name=WINDOW_NAME,
        slot_count=SLOT_COUNT,
    )

    state = STATE_READY
    slots = []
    target_slot = None

    scan_votes = PredictionVoteBuffer()
    scan_started_at = None
    last_inference = 0.0
    latest_inference_time = None
    live_prediction = None
    status_message = f"Press ENTER to scan Slot 1"

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.02)
                continue

            now = time.monotonic()

            if state == STATE_SCANNING:
                if now - last_inference >= INFERENCE_INTERVAL:
                    label, confidence, latest_inference_time = classifier.predict(frame)
                    scan_votes.add(label, confidence)
                    live_prediction = {
                        "label": label,
                        "confidence": confidence,
                        "food": food_display_name(extract_food_name(label)),
                        "condition": get_condition_group(label),
                    }
                    last_inference = now

                elapsed = now - scan_started_at
                remaining = max(0.0, SCAN_DURATION_SECONDS - elapsed)
                status_message = (
                    f"Scanning Slot {len(slots) + 1}... {remaining:.1f}s"
                )

                if elapsed >= SCAN_DURATION_SECONDS:
                    label, confidence, winner_count, sample_count = scan_votes.result()

                    if label is None:
                        state = STATE_READY
                        status_message = (
                            f"Scan failed. Press ENTER to retry Slot {len(slots) + 1}"
                        )
                    else:
                        slot = _build_slot_result(
                            slot_number=len(slots) + 1,
                            label=label,
                            confidence=confidence,
                            winner_count=winner_count,
                            sample_count=sample_count,
                        )
                        slots.append(slot)
                        live_prediction = None

                        if len(slots) >= SLOT_COUNT:
                            target_slot = select_priority_slot(slots)
                            state = STATE_RESULTS
                            status_message = "Priority decision complete - press ENTER to reset"
                        else:
                            state = STATE_READY
                            status_message = (
                                f"Slot {slot['slot']} saved - press ENTER to scan "
                                f"Slot {len(slots) + 1}"
                            )

            scan_progress = 0.0
            if state == STATE_SCANNING and scan_started_at is not None:
                scan_progress = min(
                    1.0,
                    (now - scan_started_at) / SCAN_DURATION_SECONDS,
                )

            dashboard.show(
                frame=frame,
                slots=slots,
                state=state,
                target_slot=target_slot,
                next_slot=min(len(slots) + 1, SLOT_COUNT),
                live_prediction=live_prediction,
                scan_progress=scan_progress,
                status_message=status_message,
                device=str(classifier.device),
                inference_time=latest_inference_time,
            )

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q"), 27):
                break

            # OpenCV may report ENTER as 13 (CR) or 10 (LF), depending on OS.
            if key in (10, 13):
                if state == STATE_READY:
                    scan_votes.clear()
                    scan_started_at = time.monotonic()
                    last_inference = 0.0
                    latest_inference_time = None
                    live_prediction = None
                    state = STATE_SCANNING
                    status_message = f"Scanning Slot {len(slots) + 1}..."

                elif state == STATE_RESULTS:
                    # First ENTER after the result only resets the session.
                    # A second ENTER starts the next Slot 1 scan.
                    slots = []
                    target_slot = None
                    scan_votes.clear()
                    scan_started_at = None
                    live_prediction = None
                    latest_inference_time = None
                    state = STATE_READY
                    status_message = "Reset complete - press ENTER to scan Slot 1"

    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
