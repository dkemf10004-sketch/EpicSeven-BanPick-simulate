import asyncio
import json
import os
from collections import Counter
from typing import Dict, Tuple, Optional, List, Set

import cv2
import numpy as np
import websockets
import dxcam


# =========================================================
# 기본 설정
# =========================================================
HOST = "127.0.0.1"
PORT = 8765

HERO_IMAGE_DIR = "hero_images"
TOPK = 5

PREBAN_THRESHOLD = 0.26
PICK_THRESHOLD = 0.45

POLL_INTERVAL = 0.35
CHANGE_HASH_THRESHOLD = 8
CONFIRM_COUNT = 1
RECONFIRM_COUNT = 2

PREBAN_MULTI_SCAN_COUNT = 2
PREBAN_MULTI_SCAN_DELAY = 0.1

# 같은 결과가 오래 유지되면 frozen 처리
UNCHANGED_SKIP_COUNT = 15

# 파일명 -> HTML heroId 매핑이 다를 때 여기에 추가
NAME_TO_HTML_ID = {
    # "기원의 라스": "ORIGIN_RAS",
    # "보건교사 율하": "YULHA",
}


# =========================================================
# dxcam 설정
# =========================================================
camera = dxcam.create(output_idx=0)
REGION = (0, 0, 3200, 2065)


def normalize_output_name(name: str) -> str:
    if not name:
        return name

    # 끝에 붙는 불필요한 표기 제거
    suffixes = [
        "_스킨2_회전",
        "_스킨_회전",
        "_스킨2",
        "_스킨",
        "_회전",
    ]

    changed = True
    while changed:
        changed = False
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                changed = True

    # 끝에 남은 쉼표/공백 정리
    name = name.rstrip(" ,")
    return name


def grab_screen() -> np.ndarray:
    frame = camera.grab(region=REGION)
    if frame is None:
        raise RuntimeError("dxcam 캡처 실패")
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


# =========================================================
# ROI
# =========================================================
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

PREBAN_ROIS = {k: v for k, v in ROIS.items() if k.startswith("preban_")}
PICK_ROIS = {k: v for k, v in ROIS.items() if k.startswith("ally_") or k.startswith("enemy_")}


# =========================================================
# 이미지 유틸
# =========================================================
def imread_unicode(path: str) -> Optional[np.ndarray]:
    if not os.path.exists(path):
        return None
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def resize_keep(img: np.ndarray, size=(256, 128)) -> np.ndarray:
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def crop_roi(frame: np.ndarray, roi: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    x1, y1, x2, y2 = roi
    h, w = frame.shape[:2]

    x1 = max(0, min(x1, w - 1))
    y1 = max(0, min(y1, h - 1))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))

    if x2 <= x1 or y2 <= y1:
        return None

    crop = frame[y1:y2, x1:x2]
    if crop is None or crop.size == 0:
        return None
    return crop


def mask_ui_regions(img: np.ndarray) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    out[0:int(h * 0.22), 0:int(w * 0.22)] = 0
    out[int(h * 0.82):h, :] = 0
    out[0:int(h * 0.18), int(w * 0.82):w] = 0
    return out


def make_multi_crops(img: np.ndarray) -> Dict[str, np.ndarray]:
    h, w = img.shape[:2]
    crops = {
        "full": img,
        "top75": img[0:int(h * 0.75), :],
        "left75": img[:, 0:int(w * 0.75)],
        "right75": img[:, int(w * 0.25):w],
        "center80": img[int(h * 0.10):int(h * 0.90), int(w * 0.10):int(w * 0.90)],
    }
    out = {}
    for k, v in crops.items():
        if v is not None and v.size > 0:
            out[k] = resize_keep(v, (256, 128))
    return out


def preprocess(img: np.ndarray, flip: bool = False) -> np.ndarray:
    if flip:
        img = cv2.flip(img, 1)
    img = resize_keep(img, (256, 128))
    img = mask_ui_regions(img)
    return img


# =========================================================
# ORB
# =========================================================
orb = cv2.ORB_create(nfeatures=1000, fastThreshold=12)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)


def orb_desc(img: np.ndarray):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    kp, desc = orb.detectAndCompute(gray, None)
    return kp, desc


def orb_score(desc1, desc2) -> float:
    if desc1 is None or desc2 is None:
        return 0.0
    if len(desc1) < 8 or len(desc2) < 8:
        return 0.0

    matches = bf.knnMatch(desc1, desc2, k=2)
    good = []
    for pair in matches:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if not good:
        return 0.0

    mean_dist = float(np.mean([m.distance for m in good]))
    quantity = min(1.0, len(good) / 80.0)
    quality = max(0.0, 1.0 - mean_dist / 64.0)
    return 0.65 * quantity + 0.35 * quality


def load_refs_from_hero_images(folder: str):
    refs = {}
    if not os.path.isdir(folder):
        print(f"[오류] hero_images 폴더가 없습니다: {folder}")
        return refs

    for fn in os.listdir(folder):
        path = os.path.join(folder, fn)
        if not os.path.isfile(path):
            continue
        if not fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue

        hero_name = os.path.splitext(fn)[0]
        img = imread_unicode(path)
        if img is None:
            print(f"[skip] 이미지 읽기 실패: {path}")
            continue

        img = preprocess(img, flip=False)
        crops = make_multi_crops(img)

        descs = {}
        for crop_name, crop in crops.items():
            _, desc = orb_desc(crop)
            descs[crop_name] = desc

        refs[hero_name] = descs

    print(f"[info] hero_images 기준 로드 수: {len(refs)}")
    return refs


def recognize_slot(slot_img: np.ndarray, refs, is_enemy=False, topk=5):
    if slot_img is None or slot_img.size == 0:
        return "unknown", 0.0, []

    slot_img = preprocess(slot_img, flip=is_enemy)
    slot_crops = make_multi_crops(slot_img)

    slot_descs = {}
    for k, crop in slot_crops.items():
        _, desc = orb_desc(crop)
        slot_descs[k] = desc

    hero_best = {}
    for hero, ref_descs in refs.items():
        best = 0.0
        best_crop = None
        for crop_name, slot_desc in slot_descs.items():
            ref_desc = ref_descs.get(crop_name)
            score = orb_score(slot_desc, ref_desc)
            if score > best:
                best = score
                best_crop = crop_name
        hero_best[hero] = (best, best_crop)

    ranked = sorted(hero_best.items(), key=lambda x: x[1][0], reverse=True)[:topk]
    if not ranked:
        return "unknown", 0.0, []

    pred = ranked[0][0]
    score = ranked[0][1][0]
    result = []
    for hero, (s, crop_name) in ranked:
        result.append({
            "hero": hero,
            "score": float(s),
            "crop": crop_name,
        })

    return pred, score, result


REFS = load_refs_from_hero_images(HERO_IMAGE_DIR)


def map_name_to_html_id(pred_name: str) -> Optional[str]:
    clean_name = normalize_output_name(pred_name)
    return NAME_TO_HTML_ID.get(clean_name, clean_name)


# =========================================================
# 상태
# =========================================================
last_hashes: Dict[str, np.ndarray] = {}
slot_memory: Dict[str, dict] = {}
sent_slots: Dict[str, str] = {}
blocked_sent: Dict[str, str] = {}

confirmed_slots = {
    "ally":  [None, None, None, None, None],
    "enemy": [None, None, None, None, None],
}

html_empty_slots: Set[str] = set()
frozen_slots: Set[str] = set()
preban_pending_slots: Set[str] = set()
running = False


def reset_all_states():
    global last_hashes, slot_memory, sent_slots, blocked_sent
    global confirmed_slots, html_empty_slots, frozen_slots, preban_pending_slots, running

    last_hashes = {}
    slot_memory = {}
    sent_slots = {}
    blocked_sent = {}
    html_empty_slots = set()
    frozen_slots = set()
    preban_pending_slots = set()
    confirmed_slots = {
        "ally":  [None, None, None, None, None],
        "enemy": [None, None, None, None, None],
    }
    running = False
    print("[state] reset done")


# =========================================================
# 해시 변경 감지
# =========================================================
def ahash(img, hash_size=8):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (hash_size, hash_size), interpolation=cv2.INTER_AREA)
    avg = gray.mean()
    return (gray >= avg).astype(np.uint8).flatten()


def hamming(a, b):
    return int(np.count_nonzero(a != b))


def slot_changed(slot_name, crop, threshold=CHANGE_HASH_THRESHOLD):
    cur = ahash(crop)
    old = last_hashes.get(slot_name)
    last_hashes[slot_name] = cur

    if old is None:
        return True
    return hamming(cur, old) >= threshold


# =========================================================
# 슬롯 관리
# =========================================================
def parse_slot(slot_name: str):
    side, idx = slot_name.split("_")
    return side, int(idx)


def get_confirmed_prefix_count(side: str) -> int:
    arr = confirmed_slots[side]
    cnt = 0
    for v in arr:
        if v is not None:
            cnt += 1
        else:
            break
    return cnt


def get_last_confirmed_index(side: str) -> int:
    arr = confirmed_slots[side]
    last = 0
    for i, v in enumerate(arr, start=1):
        if v is not None:
            last = i
    return last


def get_watch_slots_for_side(side: str) -> List[str]:
    last = get_last_confirmed_index(side)

    if last == 0:
        watch = [1, 2]
    elif last in (1, 2):
        watch = [1, 2, 3]
    elif last == 3:
        watch = [2, 3, 4]
    elif last == 4:
        watch = [3, 4, 5]
    else:
        watch = [4, 5]

    return [f"{side}_{i}" for i in watch]


def get_watch_slots() -> List[str]:
    base = set(get_watch_slots_for_side("ally") + get_watch_slots_for_side("enemy"))
    base.update(html_empty_slots)
    base = {s for s in base if (s not in frozen_slots) or (s in html_empty_slots)}
    return sorted(base)


def clear_slot_runtime_state(slot_name: str):
    side, idx = parse_slot(slot_name)

    confirmed_slots[side][idx - 1] = None
    sent_slots.pop(slot_name, None)
    blocked_sent.pop(slot_name, None)
    frozen_slots.discard(slot_name)
    last_hashes.pop(slot_name, None)

    slot_memory[slot_name] = {
        "last_pred": None,
        "count": 0,
        "locked": None,
        "stable_pred": None,
        "stable_count": 0,
        "candidate_new": None,
        "candidate_new_count": 0,
    }


def can_lock_slot(side: str, idx: int) -> Tuple[bool, Optional[int]]:
    arr = confirmed_slots[side]
    for prev in range(1, idx):
        if arr[prev - 1] is None:
            return False, prev
    return True, None


def update_slot_memory(slot_name: str, pred: Optional[str]):
    info = slot_memory.setdefault(slot_name, {
        "last_pred": None,
        "count": 0,
        "locked": None,
        "stable_pred": None,
        "stable_count": 0,
        "candidate_new": None,
        "candidate_new_count": 0,
    })

    if pred == info["stable_pred"]:
        info["stable_count"] += 1
    else:
        info["stable_pred"] = pred
        info["stable_count"] = 1

    # 아직 확정되지 않은 슬롯: 기존 확정 로직 사용
    if info["locked"] is None:
        if pred == info["last_pred"]:
            info["count"] += 1
        else:
            info["last_pred"] = pred
            info["count"] = 1

        if pred is not None and info["count"] >= CONFIRM_COUNT:
            info["locked"] = pred
            info["candidate_new"] = None
            info["candidate_new_count"] = 0
            return True, pred

        return False, None

    # 이미 확정된 슬롯: 같은 값이거나 인식 실패면 유지
    if pred is None or pred == info["locked"]:
        info["candidate_new"] = None
        info["candidate_new_count"] = 0
        return False, info["locked"]

    # 다른 값이 보이면 재확정 후보로 누적
    if pred == info["candidate_new"]:
        info["candidate_new_count"] += 1
    else:
        info["candidate_new"] = pred
        info["candidate_new_count"] = 1

    # 같은 새 값이 연속으로 일정 횟수 나오면 확정값 교체
    if info["candidate_new_count"] >= RECONFIRM_COUNT:
        info["locked"] = pred
        info["last_pred"] = pred
        info["count"] = CONFIRM_COUNT
        info["candidate_new"] = None
        info["candidate_new_count"] = 0
        return True, pred

    return False, info["locked"]


# =========================================================
# 인식
# =========================================================
def recognize_preban(crop: np.ndarray):
    pred, _, top5 = recognize_slot(crop, refs=REFS, is_enemy=False, topk=TOPK)
    top1 = top5[0]["score"] if len(top5) > 0 else 0.0
    top2 = top5[1]["score"] if len(top5) > 1 else 0.0
    return pred, top1, top2, top5


def recognize_pick(crop: np.ndarray, is_enemy: bool = False):
    pred, _, top5 = recognize_slot(crop, refs=REFS, is_enemy=is_enemy, topk=TOPK)
    top1 = top5[0]["score"] if len(top5) > 0 else 0.0
    top2 = top5[1]["score"] if len(top5) > 1 else 0.0
    return pred, top1, top2, top5


# =========================================================
# WebSocket 송신
# =========================================================
async def send_json(websocket, payload: dict):
    await websocket.send(json.dumps(payload, ensure_ascii=False))


async def send_log(websocket, message: str):
    await send_json(websocket, {"type": "log", "message": message})
    print("[log]", message)


async def send_preban_to_html(websocket, idx: int, hero_id: Optional[str]):
    await send_json(websocket, {
        "type": "set_preban",
        "slot": idx,
        "heroId": hero_id,
    })


async def send_pick_to_html(websocket, side: str, idx: int, hero_id: str):
    await send_json(websocket, {
        "type": "set_pick",
        "side": side,
        "slot": idx,
        "heroId": hero_id,
    })


async def send_blocked_message(websocket, side: str, idx: int, missing_idx: int, hero_id: str):
    slot_name = f"{side}_{idx}"
    key = f"{slot_name}:{hero_id}:missing{missing_idx}"
    if blocked_sent.get(slot_name) == key:
        return

    blocked_sent[slot_name] = key
    message = f"{slot_name}에서 {hero_id}가 감지됐지만 {side}_{missing_idx}이 아직 없어서 확정하지 않음"

    await send_json(websocket, {
        "type": "slot_blocked",
        "side": side,
        "slot": idx,
        "heroId": hero_id,
        "message": message,
        "missingSlot": missing_idx,
    })


async def clear_block_message(websocket, side: str, idx: int):
    slot_name = f"{side}_{idx}"
    blocked_sent.pop(slot_name, None)


async def send_missing_preban(websocket):
    slots = sorted(preban_pending_slots)
    await send_json(websocket, {
        "type": "missing_preban",
        "slots": slots,
    })


async def send_missing_pick(websocket):
    missing = []
    for side in ["ally", "enemy"]:
        watch = get_watch_slots_for_side(side)
        for slot_name in watch:
            if slot_name in sent_slots:
                continue
            side_name, idx = parse_slot(slot_name)
            if confirmed_slots[side_name][idx - 1] is None:
                missing.append(slot_name)

    await send_json(websocket, {
        "type": "missing_pick",
        "slots": missing,
    })


async def send_prebans_to_html(websocket, picks: List[Optional[str]]):
    for i, hero_id in enumerate(picks, start=1):
        await send_preban_to_html(websocket, i, hero_id)


# =========================================================
# 프리밴
# =========================================================
def recognize_preban_once(frame: np.ndarray, slot_name: str) -> Tuple[Optional[str], float, float, list]:
    roi = PREBAN_ROIS[slot_name]
    crop = crop_roi(frame, roi)
    if crop is None:
        return None, 0.0, 0.0, []

    pred, top1, top2, top5 = recognize_preban(crop)

    print("=" * 60)
    print(f"[{slot_name}] pred={pred} top1={top1:.4f} top2={top2:.4f} threshold={PREBAN_THRESHOLD:.2f}")
    for i, item in enumerate(top5, 1):
        print(f"  {i}. {item['hero']} score={item['score']:.4f} crop={item['crop']}")

    accepted = None
    if top1 >= PREBAN_THRESHOLD:
        accepted = map_name_to_html_id(pred)

    return accepted, top1, top2, top5


def select_best_preban_candidate(candidates: List[Tuple[Optional[str], float]]) -> Optional[str]:
    valid = [(hero_id, score) for hero_id, score in candidates if hero_id]
    if not valid:
        return None

    freq = Counter(hero_id for hero_id, _ in valid)
    max_count = max(freq.values())
    most_common = [hero_id for hero_id, cnt in freq.items() if cnt == max_count]

    if len(most_common) == 1:
        return most_common[0]

    best_hero = None
    best_score = -1.0
    for hero_id in most_common:
        hero_best = max(score for h, score in valid if h == hero_id)
        if hero_best > best_score:
            best_score = hero_best
            best_hero = hero_id
    return best_hero


async def scan_prebans_multi(websocket) -> List[Optional[str]]:
    global preban_pending_slots

    if not REFS:
        print("[오류] 기준 이미지가 없습니다.")
        return [None, None, None, None]

    collected: Dict[str, List[Tuple[Optional[str], float]]] = {
        slot_name: [] for slot_name in PREBAN_ROIS.keys()
    }

    for _ in range(PREBAN_MULTI_SCAN_COUNT):
        frame = grab_screen()
        for slot_name in PREBAN_ROIS.keys():
            accepted, top1, _, _ = recognize_preban_once(frame, slot_name)
            collected[slot_name].append((accepted, top1))
        await asyncio.sleep(PREBAN_MULTI_SCAN_DELAY)

    results: List[Optional[str]] = []
    pending = set()

    for slot_name in PREBAN_ROIS.keys():
        final_hero = select_best_preban_candidate(collected[slot_name])
        results.append(final_hero)
        if final_hero is None:
            pending.add(slot_name)

    preban_pending_slots = pending
    return results


async def poll_pending_prebans(websocket, frame: np.ndarray):
    global preban_pending_slots

    if not preban_pending_slots:
        return

    resolved = []

    for slot_name in sorted(preban_pending_slots):
        crop = crop_roi(frame, PREBAN_ROIS[slot_name])
        if crop is None:
            continue

        accepted, _, _, _ = recognize_preban_once(frame, slot_name)
        confirmed, locked_pred = update_slot_memory(slot_name, accepted)
        info = slot_memory.get(slot_name, {})
        final_pred = locked_pred if locked_pred else accepted

        if not final_pred:
            if info.get("stable_count", 0) > UNCHANGED_SKIP_COUNT and slot_name not in frozen_slots:
                frozen_slots.add(slot_name)
            continue

        idx = int(slot_name.split("_")[1])

        if confirmed and locked_pred:
            await send_preban_to_html(websocket, idx, locked_pred)
            await send_log(websocket, f"{slot_name} 확정: {locked_pred}")
            resolved.append(slot_name)
        elif accepted:
            await send_preban_to_html(websocket, idx, accepted)
            await send_log(websocket, f"{slot_name} 감지: {accepted}")
            resolved.append(slot_name)

    for slot_name in resolved:
        preban_pending_slots.discard(slot_name)

    await send_missing_preban(websocket)


# =========================================================
# 실시간 픽 감시
# =========================================================
async def poll_live_picks(websocket):
    global html_empty_slots

    while True:
        try:
            if not running:
                await asyncio.sleep(0.2)
                continue

            if not REFS:
                await asyncio.sleep(1.0)
                continue

            frame = grab_screen()
            await poll_pending_prebans(websocket, frame)

            watch_slots = set(get_watch_slots())

            for slot_name, roi in PICK_ROIS.items():
                if slot_name not in watch_slots:
                    continue

                crop = crop_roi(frame, roi)
                if crop is None:
                    continue

                force_scan = slot_name in html_empty_slots
                if (not force_scan) and (not slot_changed(slot_name, crop)):
                    continue

                side, idx = parse_slot(slot_name)
                is_enemy = (side == "enemy")

                pred, top1, top2, top5 = recognize_pick(crop, is_enemy=is_enemy)

                print("=" * 60)
                print(f"[{slot_name}] pred={pred} top1={top1:.4f} top2={top2:.4f} threshold={PICK_THRESHOLD:.2f}")
                for i, item in enumerate(top5, 1):
                    print(f"  {i}. {item['hero']} score={item['score']:.4f} crop={item['crop']}")

                accepted = None
                if top1 >= PICK_THRESHOLD:
                    accepted = map_name_to_html_id(pred)

                confirmed, locked_pred = update_slot_memory(slot_name, accepted)
                info = slot_memory.get(slot_name, {})
                final_pred = locked_pred if locked_pred else accepted

                if not final_pred:
                    continue

                if info.get("stable_count", 0) > UNCHANGED_SKIP_COUNT:
                    if slot_name not in frozen_slots and slot_name not in html_empty_slots:
                        frozen_slots.add(slot_name)
                        print(f"[freeze] {slot_name} same recognized result {info['stable_count']}회 -> 검색 제외")

                if not (confirmed and locked_pred):
                    continue

                if sent_slots.get(slot_name) == final_pred:
                    continue

                ok, missing_idx = can_lock_slot(side, idx)
                if not ok:
                    await send_blocked_message(websocket, side, idx, missing_idx, final_pred)
                    continue

                blocked_sent.pop(slot_name, None)
                confirmed_slots[side][idx - 1] = final_pred
                sent_slots[slot_name] = final_pred

                await send_pick_to_html(websocket, side, idx, final_pred)
                await send_log(websocket, f"{slot_name} 확정: {final_pred}")

                if slot_name in html_empty_slots:
                    html_empty_slots.discard(slot_name)

            await send_missing_pick(websocket)
            await asyncio.sleep(POLL_INTERVAL)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print("[poll_live_picks error]", e)
            await asyncio.sleep(0.5)


# =========================================================
# HTML -> Python sync 처리
# =========================================================
def parse_sync_empty_slots_message(msg: dict) -> Set[str]:
    result: Set[str] = set()

    if isinstance(msg.get("slots"), list):
        for s in msg.get("slots", []):
            if s in PICK_ROIS:
                result.add(s)
        return result

    empty = msg.get("empty")
    if isinstance(empty, dict):
        ally_arr = empty.get("ally", [])
        enemy_arr = empty.get("enemy", [])

        if isinstance(ally_arr, list):
            for i, is_empty in enumerate(ally_arr, start=1):
                if is_empty and f"ally_{i}" in PICK_ROIS:
                    result.add(f"ally_{i}")

        if isinstance(enemy_arr, list):
            for i, is_empty in enumerate(enemy_arr, start=1):
                if is_empty and f"enemy_{i}" in PICK_ROIS:
                    result.add(f"enemy_{i}")

    return result


# =========================================================
# WebSocket 서버
# =========================================================
async def handler(websocket):
    global running, html_empty_slots

    print("[ws] 클라이언트 연결됨")
    live_task = asyncio.create_task(poll_live_picks(websocket))

    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except Exception:
                print("[ws] 잘못된 JSON:", raw)
                continue

            msg_type = msg.get("type")
            print("[ws] 받음:", msg)

            if msg_type == "start":
                running = False
                await send_log(websocket, "시작 요청 수신 - 프리밴 다중 스캔 시작")

                prebans = await scan_prebans_multi(websocket)
                await send_prebans_to_html(websocket, prebans)
                await send_missing_preban(websocket)

                await send_log(websocket, f"프리밴 1차 완료: {prebans}")
                if preban_pending_slots:
                    await send_log(websocket, f"미검출 프리밴 지속 감시: {sorted(preban_pending_slots)}")

                running = True
                await send_log(websocket, "실시간 픽 감시 시작")

            elif msg_type == "stop":
                running = False
                await send_log(websocket, "실시간 감시 중지")

            elif msg_type == "reset_all":
                reset_all_states()
                await send_json(websocket, {"type": "reset_all"})
                await send_log(websocket, "상태 초기화 완료")

            elif msg_type == "sync_empty_slots":
                valid = parse_sync_empty_slots_message(msg)

                for s in valid:
                    clear_slot_runtime_state(s)

                html_empty_slots = valid
                await send_missing_pick(websocket)

    except Exception as e:
        print("[ws] handler error:", e)

    finally:
        live_task.cancel()
        try:
            await live_task
        except Exception:
            pass
        print("[ws] 클라이언트 연결 종료")


async def main():
    print(f"[ws] 서버 시작: ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT, max_size=2**20):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
