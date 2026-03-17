# -*- coding: utf-8 -*-
# herodatancollect_no_detail.py
# 요청사항 반영:
# - /herorecord/cXXXX 상세 페이지로 들어가지 않음
# - 목록 페이지에서 더보기만 끝까지 눌러서 보이는 정보만 수집
# - 별도페이지 상세 차트/상세 지표 수집 제거

import csv
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "https://epic7.onstove.com/ko/gg/herorecord"
OUT_DIR = Path("epic7_hero_record_output")
OUT_DIR.mkdir(exist_ok=True)

TARGET_SEASON = "2026 스프링"
TARGET_GRADE = "레전드 등급"

HEADLESS = False
MAX_LOAD_MORE = 100

# 코드-한글명 매핑 파일
HERO_CODE_MAP_PATH = Path("hero_code_to_korean.json")


def clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def parse_percent(text: str) -> Optional[float]:
    text = clean_text(text).replace("%", "").replace(",", "")
    try:
        return float(text)
    except Exception:
        return None


def sleep_short(sec=0.8):
    time.sleep(sec)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def save_jsonl(path: Path, rows: List[Dict[str, Any]]):
    with path.open("w", encoding="utf-8-sig") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def save_csv(path: Path, rows: List[Dict[str, Any]]):
    if not rows:
        return

    keys = []
    seen = set()
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def make_driver() -> webdriver.Chrome:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=ko-KR")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(60)
    return driver


def build_hero_name_maps(code_map: Dict[str, str]):
    code_to_kr = {}
    kr_to_code = {}

    for code, kr in code_map.items():
        code = clean_text(str(code))
        kr = clean_text(str(kr))
        if not code or not kr:
            continue
        code_to_kr[code] = kr
        kr_to_code[kr] = code

    return code_to_kr, kr_to_code


def code_to_korean(code: str, code_to_kr: Dict[str, str]) -> str:
    code = clean_text(code)
    return code_to_kr.get(code, code)


def maybe_koreanize_name(value: str, code_to_kr: Dict[str, str]) -> str:
    value = clean_text(value)
    if re.fullmatch(r"c\d+", value):
        return code_to_korean(value, code_to_kr)
    return value


def scroll_into_view(driver, elem):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        sleep_short(0.25)
    except Exception:
        pass


def normal_click(driver, elem) -> bool:
    try:
        scroll_into_view(driver, elem)
        elem.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", elem)
            return True
        except Exception:
            return False


def get_select_wrappers(driver):
    return driver.find_elements(By.CSS_SELECTOR, ".selectbox-wrap .el-select__wrapper")


def get_current_select_text(wrapper) -> str:
    try:
        span = wrapper.find_element(By.CSS_SELECTOR, ".el-select__placeholder span")
        return clean_text(span.text)
    except Exception:
        pass

    try:
        sel = wrapper.find_element(By.CSS_SELECTOR, ".el-select__placeholder")
        return clean_text(sel.text)
    except Exception:
        pass

    try:
        return clean_text(wrapper.text)
    except Exception:
        return ""


def choose_dropdown_option_by_text(driver, wrapper, target_text: str) -> bool:
    try:
        current = get_current_select_text(wrapper)
        if current == target_text:
            print(f"[INFO] 이미 선택됨: {target_text}")
            return True

        scroll_into_view(driver, wrapper)
        if not normal_click(driver, wrapper):
            print(f"[WARN] 셀렉트 클릭 실패: {target_text}")
            return False

        sleep_short(1.0)

        option_xpaths = [
            f"//div[contains(@class,'el-select-dropdown') and not(contains(@style,'display: none'))]//*[self::li or self::span][contains(normalize-space(.), '{target_text}')]",
            f"//li[contains(@class,'el-select-dropdown__item')][contains(normalize-space(.), '{target_text}')]",
            f"//span[contains(normalize-space(.), '{target_text}')]",
        ]

        option_elem = None
        for xp in option_xpaths:
            elems = driver.find_elements(By.XPATH, xp)
            for e in elems:
                try:
                    if e.is_displayed():
                        option_elem = e
                        break
                except Exception:
                    pass
            if option_elem is not None:
                break

        if option_elem is None:
            print(f"[WARN] 옵션을 찾지 못함: {target_text}")
            return False

        if not normal_click(driver, option_elem):
            print(f"[WARN] 옵션 클릭 실패: {target_text}")
            return False

        sleep_short(1.2)

        new_current = get_current_select_text(wrapper)
        print(f"[INFO] 선택 후 값: '{new_current}'")
        return new_current == target_text

    except Exception as e:
        print(f"[WARN] choose_dropdown_option_by_text 실패: {target_text} / {e}")
        return False


def find_season_and_grade_wrappers(driver) -> Tuple[Any, Any]:
    wrappers = get_select_wrappers(driver)

    season_wrapper = None
    grade_wrapper = None

    season_keywords = ["2026", "2025", "스프링", "프리 시즌", "정규 시즌"]
    grade_keywords = ["레전드", "엠페러", "챔피언", "마스터"]

    for w in wrappers:
        txt = get_current_select_text(w)
        if any(k in txt for k in season_keywords) and season_wrapper is None:
            season_wrapper = w
        elif any(k in txt for k in grade_keywords) and grade_wrapper is None:
            grade_wrapper = w

    if season_wrapper is None and len(wrappers) >= 1:
        season_wrapper = wrappers[0]
    if grade_wrapper is None and len(wrappers) >= 2:
        grade_wrapper = wrappers[1]

    return season_wrapper, grade_wrapper


def set_filters(driver, season_text: str, grade_text: str):
    print(f"[INFO] 필터 설정 시도: 시즌={season_text}, 등급={grade_text}")

    season_wrapper, grade_wrapper = find_season_and_grade_wrappers(driver)
    if season_wrapper is None or grade_wrapper is None:
        print("[WARN] 시즌/등급 셀렉트를 찾지 못했습니다.")
        return False

    season_before = get_current_select_text(season_wrapper)
    grade_before = get_current_select_text(grade_wrapper)
    print(f"[INFO] 변경 전 시즌='{season_before}', 등급='{grade_before}'")

    ok1 = choose_dropdown_option_by_text(driver, season_wrapper, season_text)
    sleep_short(1.0)

    season_wrapper, grade_wrapper = find_season_and_grade_wrappers(driver)
    season_after = get_current_select_text(season_wrapper) if season_wrapper else ""
    print(f"[INFO] 시즌 설정 결과: success={ok1}, current='{season_after}'")

    ok2 = choose_dropdown_option_by_text(driver, grade_wrapper, grade_text) if grade_wrapper else False
    sleep_short(1.0)

    season_wrapper, grade_wrapper = find_season_and_grade_wrappers(driver)
    grade_after = get_current_select_text(grade_wrapper) if grade_wrapper else ""
    print(f"[INFO] 등급 설정 결과: success={ok2}, current='{grade_after}'")

    ok = True
    if season_after != season_text:
        print(f"[WARN] 시즌이 목표값으로 바뀌지 않았음: target='{season_text}', current='{season_after}'")
        ok = False
    if grade_after != grade_text:
        print(f"[WARN] 등급이 목표값으로 바뀌지 않았음: target='{grade_text}', current='{grade_after}'")
        ok = False

    sleep_short(2.0)
    return ok


def click_load_more_until_end(driver, max_clicks=100):
    print("[INFO] + 더보기 반복 클릭")
    for attempt in range(max_clicks):
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.analybox")
            cur_count = len(rows)
            print(f"[INFO] 현재 목록 수: {cur_count}")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep_short(0.8)

            btns = driver.find_elements(By.CSS_SELECTOR, "button.loadMoreBtn")
            visible_btn = None
            for btn in btns:
                try:
                    if btn.is_displayed():
                        visible_btn = btn
                        break
                except Exception:
                    pass

            if visible_btn is None:
                print("[INFO] 더보기 버튼 없음 - 종료")
                break

            disabled = (visible_btn.get_attribute("disabled") is not None)
            cls = (visible_btn.get_attribute("class") or "").lower()
            aria_disabled = (visible_btn.get_attribute("aria-disabled") or "").lower()

            if disabled or "disabled" in cls or aria_disabled == "true":
                print("[INFO] 마지막 더보기 버튼이 비활성 상태 - 종료")
                break

            if not normal_click(driver, visible_btn):
                print("[WARN] 더보기 클릭 실패 - 종료")
                break

            ok = False
            for _ in range(24):
                time.sleep(0.5)
                new_count = len(driver.find_elements(By.CSS_SELECTOR, "tr.analybox"))
                if new_count > cur_count:
                    print(f"[INFO] 더보기 클릭 성공: {cur_count} -> {new_count}")
                    ok = True
                    break

            if not ok:
                print("[INFO] 클릭 후 목록 수 증가 없음 - 마지막 버튼으로 판단하고 종료")
                break

        except Exception as e:
            print(f"[WARN] 더보기 처리 중단: {e}")
            break


def parse_hero_code_from_href(href: str) -> str:
    m = re.search(r"/herorecord/(c\d+)", href or "")
    return m.group(1) if m else ""


def get_imgs_alt(elems, code_to_kr: Dict[str, str]) -> List[str]:
    vals = []
    for img in elems:
        try:
            alt = clean_text(img.get_attribute("alt"))
            if alt:
                vals.append(maybe_koreanize_name(alt, code_to_kr))
        except Exception:
            pass
    return vals


def parse_list_rows(driver, code_to_kr: Dict[str, str]) -> List[Dict[str, Any]]:
    print("[INFO] 목록 행 파싱")
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.analybox")
    results: List[Dict[str, Any]] = []

    for idx, row in enumerate(rows, 1):
        try:
            hero_a = row.find_element(By.CSS_SELECTOR, "td.icon-hero a")
            href = hero_a.get_attribute("href") or ""
            hero_code_raw = parse_hero_code_from_href(href)
            hero_code = code_to_korean(hero_code_raw, code_to_kr)

            hero_name = ""
            try:
                hero_name = clean_text(row.find_element(By.CSS_SELECTOR, "td.icon-hero i.hero-name").text)
            except Exception:
                pass

            if not hero_name:
                hero_name = code_to_korean(hero_code_raw, code_to_kr)

            tds = row.find_elements(By.CSS_SELECTOR, "td")

            pick_rate = None
            win_rate = None
            ban_rate = None
            top_sets = []
            hard_heroes = []
            with_heroes = []

            if len(tds) >= 7:
                pick_rate = parse_percent(tds[1].text)
                win_rate = parse_percent(tds[2].text)
                ban_rate = parse_percent(tds[3].text)

                try:
                    top_sets = get_imgs_alt(tds[4].find_elements(By.TAG_NAME, "img"), code_to_kr)
                except Exception:
                    pass

                try:
                    hard_heroes = get_imgs_alt(tds[5].find_elements(By.TAG_NAME, "img"), code_to_kr)
                except Exception:
                    pass

                try:
                    with_heroes = get_imgs_alt(tds[6].find_elements(By.TAG_NAME, "img"), code_to_kr)
                except Exception:
                    pass

            results.append({
                "hero_code": hero_code,
                "hero_code_raw": hero_code_raw,
                "hero_name": hero_name,
                "hero_url": href,
                "table_pick_rate": pick_rate,
                "table_win_rate": win_rate,
                "table_ban_rate": ban_rate,
                "list_top_sets": top_sets,
                "list_hard_heroes": hard_heroes,
                "list_with_heroes": with_heroes,
            })

            print(f"[LIST {idx}] {hero_name} ({hero_code_raw} -> {hero_code})")

        except Exception as e:
            print(f"[WARN] 목록 행 파싱 실패 idx={idx}: {e}")

    return results


def postprocess_rows_for_csv(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flat_rows = []

    for row in rows:
        r = dict(row)
        for key in ["list_top_sets", "list_hard_heroes", "list_with_heroes"]:
            if isinstance(r.get(key), list):
                r[key] = " | ".join(str(x) for x in r[key])
        flat_rows.append(r)

    return flat_rows


def main():
    code_map = load_json(HERO_CODE_MAP_PATH)
    code_to_kr, kr_to_code = build_hero_name_maps(code_map)

    print(f"[INFO] 영웅 코드 매핑 로드 완료: {len(code_to_kr)}개")

    driver = make_driver()

    try:
        print("[INFO] 목록 페이지 열기")
        driver.get(BASE_URL)
        sleep_short(2.0)

        set_filters(driver, TARGET_SEASON, TARGET_GRADE)
        click_load_more_until_end(driver, MAX_LOAD_MORE)

        heroes = parse_list_rows(driver, code_to_kr)
        print(f"[INFO] 목록 수집 완료: {len(heroes)}명")

        save_json(OUT_DIR / "hero_list_legend.json", heroes)
        save_jsonl(OUT_DIR / "hero_list_legend.jsonl", heroes)
        save_csv(OUT_DIR / "hero_list_legend.csv", postprocess_rows_for_csv(heroes))

        # 기존 파일명도 유지하고 싶다면 full에도 동일 데이터 저장
        save_json(OUT_DIR / "hero_full_legend.json", heroes)
        save_jsonl(OUT_DIR / "hero_full_legend.jsonl", heroes)
        save_csv(OUT_DIR / "hero_full_legend.csv", postprocess_rows_for_csv(heroes))

        print("[DONE] 상세 페이지 진입 없이 전체 저장 완료")
        print(f"[DONE] 저장 폴더: {OUT_DIR.resolve()}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
