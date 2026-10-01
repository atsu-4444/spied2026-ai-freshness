import cv2
import numpy as np


BG = (242, 244, 247)
PANEL = (255, 255, 255)
BORDER = (214, 219, 225)
TEXT = (35, 39, 45)
MUTED = (105, 112, 120)
DARK = (28, 32, 38)
GREEN = (74, 158, 92)
ORANGE = (70, 153, 224)
RED = (75, 78, 220)
GRAY = (145, 150, 158)
BLUE = (214, 126, 52)


def _draw_text(image, text, x, y, scale=0.55, color=TEXT, thickness=1):
    cv2.putText(
        image,
        str(text),
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def _fit_scale(text, max_width, preferred=0.8, thickness=2, minimum=0.34):
    scale = preferred
    while scale > minimum:
        (width, _), _ = cv2.getTextSize(
            str(text), cv2.FONT_HERSHEY_SIMPLEX, scale, thickness
        )
        if width <= max_width:
            return scale
        scale -= 0.03
    return minimum


def _draw_fitted(
    image,
    text,
    x,
    y,
    max_width,
    preferred=0.8,
    color=TEXT,
    thickness=2,
):
    scale = _fit_scale(text, max_width, preferred, thickness)
    _draw_text(image, text, x, y, scale, color, thickness)


def _condition_color(condition):
    if condition == "ROTTEN":
        return RED
    if condition == "RIPE":
        return ORANGE
    if condition == "FRESH":
        return GREEN
    return GRAY


class FreshnessDashboard:
    def __init__(
        self,
        width=1400,
        height=820,
        window_name="SP!ED 2026 - 4-Slot Priority Scanner",
        slot_count=4,
    ):
        self.width = width
        self.height = height
        self.window_name = window_name
        self.slot_count = slot_count

    def _camera_panel(self, canvas, frame, state, next_slot, live_prediction, scan_progress):
        x1, y1 = 40, 128
        x2, y2 = 790, 662
        panel_w, panel_h = x2 - x1, y2 - y1

        cv2.rectangle(canvas, (x1, y1), (x2, y2), DARK, -1)

        if frame is None:
            _draw_text(
                canvas,
                "Waiting for camera...",
                x1 + 210,
                y1 + 275,
                0.75,
                (225, 225, 225),
                2,
            )
            return

        fh, fw = frame.shape[:2]
        scale = min(panel_w / fw, panel_h / fh)
        new_w, new_h = max(1, int(fw * scale)), max(1, int(fh * scale))
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        px = x1 + (panel_w - new_w) // 2
        py = y1 + (panel_h - new_h) // 2
        canvas[py : py + new_h, px : px + new_w] = resized

        if state == "SCANNING":
            overlay_y1 = y2 - 92
            cv2.rectangle(canvas, (x1, overlay_y1), (x2, y2), (20, 20, 20), -1)
            _draw_text(
                canvas,
                f"SCANNING SLOT {next_slot}",
                x1 + 24,
                overlay_y1 + 34,
                0.64,
                (255, 255, 255),
                2,
            )

            if live_prediction:
                preview = (
                    f"{live_prediction['food']} / {live_prediction['condition']}  "
                    f"{live_prediction['confidence'] * 100:.1f}%"
                )
                _draw_fitted(
                    canvas,
                    preview,
                    x1 + 24,
                    overlay_y1 + 68,
                    panel_w - 48,
                    0.56,
                    (230, 230, 230),
                    1,
                )

            bar_x1, bar_y1 = x1 + 24, y2 - 13
            bar_x2 = x2 - 24
            cv2.rectangle(canvas, (bar_x1, bar_y1), (bar_x2, bar_y1 + 5), (80, 80, 80), -1)
            fill_x = int(bar_x1 + (bar_x2 - bar_x1) * max(0.0, min(1.0, scan_progress)))
            cv2.rectangle(canvas, (bar_x1, bar_y1), (fill_x, bar_y1 + 5), (235, 235, 235), -1)

    def _slot_row(self, canvas, y, slot_number, slot=None, is_target=False):
        x1, x2 = 830, self.width - 40
        row_h = 94
        bg = (247, 249, 251) if not is_target else (240, 246, 255)
        border = BLUE if is_target else BORDER
        thickness = 3 if is_target else 1

        cv2.rectangle(canvas, (x1, y), (x2, y + row_h), bg, -1)
        cv2.rectangle(canvas, (x1, y), (x2, y + row_h), border, thickness)

        _draw_text(canvas, f"SLOT {slot_number}", x1 + 20, y + 31, 0.54, MUTED, 1)

        if slot is None:
            _draw_text(canvas, "Waiting for scan", x1 + 20, y + 67, 0.63, GRAY, 1)
            return

        _draw_fitted(
            canvas,
            slot["food"],
            x1 + 130,
            y + 38,
            190,
            0.72,
            TEXT,
            2,
        )

        condition = slot["condition"]
        color = _condition_color(condition)
        badge_x1, badge_y1 = x1 + 330, y + 18
        badge_x2, badge_y2 = x1 + 445, y + 53
        cv2.rectangle(canvas, (badge_x1, badge_y1), (badge_x2, badge_y2), color, -1)
        _draw_fitted(
            canvas,
            condition,
            badge_x1 + 10,
            badge_y1 + 25,
            badge_x2 - badge_x1 - 20,
            0.53,
            (255, 255, 255),
            2,
        )

        _draw_text(
            canvas,
            f"{slot['confidence'] * 100:.1f}%",
            x1 + 462,
            y + 43,
            0.57,
            TEXT,
            1,
        )
        _draw_fitted(
            canvas,
            f"vote {slot['winner_count']}/{slot['sample_count']}  |  {slot['label']}",
            x1 + 130,
            y + 72,
            x2 - x1 - 155,
            0.40,
            MUTED,
            1,
        )

        if is_target:
            _draw_text(canvas, "CHECK FIRST", x1 + 20, y + 67, 0.48, BLUE, 2)

    def _right_panel(self, canvas, slots, state, target_slot):
        x1, x2 = 830, self.width - 40

        _draw_text(canvas, "4-SLOT PRIORITY SCAN", x1, 139, 0.72, TEXT, 2)
        _draw_text(
            canvas,
            "ROTTEN > RIPE > FRESH",
            x1,
            168,
            0.47,
            MUTED,
            1,
        )

        slot_by_number = {slot["slot"]: slot for slot in slots}
        target_number = target_slot["slot"] if target_slot else None

        y = 188
        for slot_number in range(1, self.slot_count + 1):
            slot = slot_by_number.get(slot_number)
            self._slot_row(
                canvas,
                y,
                slot_number,
                slot=slot,
                is_target=(state == "RESULTS" and slot_number == target_number),
            )
            y += 106

        result_y = y + 2
        if state == "RESULTS" and target_slot:
            cv2.rectangle(canvas, (x1, result_y), (x2, result_y + 88), DARK, -1)
            _draw_text(canvas, "PRIORITY RESULT", x1 + 20, result_y + 28, 0.48, (190, 195, 202), 1)
            summary = (
                f"Slot {target_slot['slot']}  |  "
                f"{target_slot['food']}  |  {target_slot['condition']}"
            )
            _draw_fitted(
                canvas,
                summary,
                x1 + 20,
                result_y + 64,
                x2 - x1 - 40,
                0.72,
                (255, 255, 255),
                2,
            )
        else:
            cv2.rectangle(canvas, (x1, result_y), (x2, result_y + 88), PANEL, -1)
            cv2.rectangle(canvas, (x1, result_y), (x2, result_y + 88), BORDER, 1)
            _draw_text(canvas, "Priority result appears after all 4 slots are scanned.", x1 + 20, result_y + 51, 0.48, MUTED, 1)

    def render(
        self,
        frame,
        slots,
        state,
        target_slot,
        next_slot,
        live_prediction,
        scan_progress,
        status_message,
        device="cpu",
        inference_time=None,
    ):
        canvas = np.full((self.height, self.width, 3), BG, dtype=np.uint8)

        _draw_text(canvas, "SP!ED 2026", 40, 48, 0.72, MUTED, 2)
        _draw_text(canvas, "AI Food Freshness - Priority Scanner", 40, 91, 1.0, TEXT, 3)

        self._camera_panel(
            canvas,
            frame,
            state=state,
            next_slot=next_slot,
            live_prediction=live_prediction,
            scan_progress=scan_progress,
        )
        self._right_panel(canvas, slots, state, target_slot)

        status_y = 694
        cv2.rectangle(canvas, (40, status_y), (self.width - 40, status_y + 64), PANEL, -1)
        cv2.rectangle(canvas, (40, status_y), (self.width - 40, status_y + 64), BORDER, 1)

        if state == "SCANNING":
            control = "Scanning..."
        elif state == "RESULTS":
            control = "ENTER: Reset   |   Q / ESC: Quit"
        else:
            control = f"ENTER: Scan Slot {next_slot}   |   Q / ESC: Quit"

        _draw_fitted(canvas, status_message, 58, status_y + 27, 770, 0.56, TEXT, 2)
        _draw_fitted(canvas, control, 850, status_y + 27, 480, 0.49, MUTED, 1)

        footer = f"Device: {device}"
        if inference_time is not None:
            footer += f"   |   Inference: {inference_time * 1000:.0f} ms"
        footer += "   |   Manual slot scan replaces the original motorized rotation."
        _draw_fitted(
            canvas,
            footer,
            40,
            self.height - 22,
            self.width - 80,
            0.43,
            MUTED,
            1,
        )

        return canvas

    def show(self, **kwargs):
        canvas = self.render(**kwargs)
        cv2.imshow(self.window_name, canvas)
