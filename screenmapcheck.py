import time

import cv2
import dxcam
import numpy as np
from typing import Dict, Tuple

WINDOW_MAIN = "ROI Overlay"
WINDOW_CROP = "ROI Crop"

# 전체 화면이면 None
# 특정 영역을 쓸 거면 (left, top, right, bottom)
CAPTURE_REGION = None

ROIS: Dict[str, Tuple[int, int, int, int]] = {
    # 왼쪽 아군 5픽
    "ally_1":  (181, 407, 471, 630),
    "ally_2":  (183, 690, 445, 924),
    "ally_3":  (180, 980, 470, 1220),
    "ally_4":  (144, 1264, 477, 1501),
    "ally_5":  (142, 1553, 477, 1788),

    # 오른쪽 적군 5픽
    "enemy_1": (2595, 411, 2896, 615),
    "enemy_2": (2583, 694, 2910, 914),
    "enemy_3": (2594, 974, 2922, 1195),
    "enemy_4": (2586, 1264, 2878, 1490),
    "enemy_5": (2583, 1559, 2896, 1772),

    # 하단 프리밴 4칸
    "preban_1": (1199, 1948, 1295, 2048),
    "preban_2": (1363, 1956, 1456, 2045),
    "preban_3": (1576, 1952, 1667, 2046),
    "preban_4": (1735, 1952, 1825, 2046),
}


def draw_bbox(img, bbox, color=(0, 255, 255), thickness=2, label=None):
    x1, y1, x2, y2 = bbox
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)

    if label:
        tx = x1 + 5
        ty = y1 + 22 if y1 + 22 < img.shape[0] else y1 - 8
        cv2.putText(
            img,
            label,
            (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            color,
            2,
            cv2.LINE_AA
        )


def crop_bbox(frame, bbox):
    x1, y1, x2, y2 = bbox

    h, w = frame.shape[:2]
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h))

    if x2 <= x1 or y2 <= y1:
        return np.zeros((100, 200, 3), dtype=np.uint8)

    return frame[y1:y2, x1:x2].copy()


def main():
    slot_names = list(ROIS.keys())
    current_idx = 0
    freeze = False
    frozen_frame = None
    last_frame = None

    camera = dxcam.create(output_color="BGR")
    camera.start(region=CAPTURE_REGION, target_fps=20)

    cv2.namedWindow(WINDOW_MAIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_MAIN, 1600, 900)

    cv2.namedWindow(WINDOW_CROP, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_CROP, 700, 350)

    try:
        while True:
            if freeze and frozen_frame is not None:
                frame = frozen_frame.copy()
            else:
                frame = camera.get_latest_frame()
                if frame is None:
                    if last_frame is None:
                        time.sleep(0.01)
                        continue
                    frame = last_frame.copy()
                else:
                    last_frame = frame.copy()

            view = frame.copy()

            # 전체 bbox 표시
            for i, name in enumerate(slot_names):
                bbox = ROIS[name]
                color = (0, 255, 255)
                if i == current_idx:
                    color = (0, 0, 255)

                draw_bbox(view, bbox, color=color, thickness=2, label=name)

            current_name = slot_names[current_idx]
            current_bbox = ROIS[current_name]
            crop = crop_bbox(frame, current_bbox)

            info = f"[{current_idx+1}/{len(slot_names)}] {current_name} | F:freeze N/P:next/prev ESC:exit"
            cv2.putText(
                view,
                info,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.imshow(WINDOW_MAIN, view)
            cv2.imshow(WINDOW_CROP, crop)

            key = cv2.waitKey(10) & 0xFF

            if key == 27:  # ESC
                break
            elif key in (ord("n"), ord("N")):
                current_idx = (current_idx + 1) % len(slot_names)
            elif key in (ord("p"), ord("P")):
                current_idx = (current_idx - 1) % len(slot_names)
            elif key in (ord("f"), ord("F")):
                freeze = not freeze
                if freeze and last_frame is not None:
                    frozen_frame = last_frame.copy()

    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()