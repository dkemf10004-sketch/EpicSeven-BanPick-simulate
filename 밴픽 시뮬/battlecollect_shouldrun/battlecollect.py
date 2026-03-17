import json
import time
from typing import List, Dict, Any, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://epic7.onstove.com/ko/gg"
BATTLE_URL = BASE_URL + "/battlerecord/{server}/{acc_id}"

HEADLESS = True
TARGET_ACCOUNT_COUNT = 100
MAX_REFRESH_TRIES = 500

OUTPUT_JSON = "battle_accounts_merged.json"
TEMP_OUTPUT_JSON = "battle_accounts_temp.json"
HERO_CODE_JSON = "hero_code_to_korean.json"

# 수동 추가 계정
MANUAL_ACCOUNTS = [
    # {"acc_id": "138566626", "server": "world_global", "nickname": "swooshies"},
]


def build_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    if HEADLESS:
        options.add_argument("--headless=new")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Network.enable", {})
    return driver


def load_hero_code_map(path: str) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"[WARN] hero code map load failed: {e}")
        return {}


HERO_NAME_MAP = load_hero_code_map(HERO_CODE_JSON)


def convert_hero_code(code: str) -> str:
    code = str(code or "").strip()
    return HERO_NAME_MAP.get(code, code)


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_performance_logs(driver: webdriver.Chrome) -> None:
    try:
        driver.get_log("performance")
    except Exception:
        pass


def _parse_perf_log_entry(entry: Dict[str, Any]) -> Dict[str, Any] | None:
    try:
        msg = json.loads(entry["message"])["message"]
        if msg.get("method") != "Network.responseReceived":
            return None
        params = msg.get("params", {})
        response = params.get("response", {})
        return {
            "requestId": params.get("requestId"),
            "url": response.get("url", ""),
        }
    except Exception:
        return None


def wait_for_api_json(driver: webdriver.Chrome, keyword: str, timeout: float = 8.0) -> Dict[str, Any] | None:
    deadline = time.time() + timeout
    candidates: List[Dict[str, str]] = []
    seen_req_ids = set()

    while time.time() < deadline:
        try:
            logs = driver.get_log("performance")
        except Exception:
            logs = []

        for entry in logs:
            info = _parse_perf_log_entry(entry)
            if not info:
                continue

            req_id = info.get("requestId")
            url = info.get("url", "")

            if not req_id or req_id in seen_req_ids:
                continue

            if keyword in url:
                seen_req_ids.add(req_id)
                candidates.append(info)

        for info in reversed(candidates):
            req_id = info["requestId"]
            try:
                body_info = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})
                body_text = body_info.get("body", "")
                if not body_text:
                    continue
                parsed = json.loads(body_text)
                if isinstance(parsed, dict) and parsed.get("code") == 0:
                    return parsed
            except Exception:
                continue

        time.sleep(0.3)

    return None


def click_refresh_recommend(driver: webdriver.Chrome) -> bool:
    xpaths = [
        "//button[contains(., '갱신')]",
        "//a[contains(., '갱신')]",
        "//span[contains(., '갱신')]/ancestor::button[1]",
        "//span[contains(., '갱신')]/ancestor::a[1]",
    ]
    for xpath in xpaths:
        try:
            btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            continue
    return False


def dedup_accounts(accounts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    merged: Dict[Tuple[str, str], Dict[str, str]] = {}
    for acc in accounts:
        acc_id = str(acc.get("acc_id", "")).strip()
        server = str(acc.get("server", "")).strip()
        nickname = str(acc.get("nickname", "")).strip()
        if not acc_id or not server:
            continue
        merged[(acc_id, server)] = {
            "acc_id": acc_id,
            "server": server,
            "nickname": nickname,
        }
    return list(merged.values())


def collect_recommend_accounts(driver: webdriver.Chrome) -> List[Dict[str, str]]:
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(., '추천 계승자') or contains(., '갱신')]")
        )
    )

    unique_accounts: Dict[Tuple[str, str], Dict[str, str]] = {}

    for i in range(MAX_REFRESH_TRIES):
        clear_performance_logs(driver)

        if i == 0:
            driver.refresh()
        else:
            clicked = click_refresh_recommend(driver)
            if not clicked:
                driver.refresh()

        resp_json = wait_for_api_json(driver, "getRecommendList", timeout=8.0)
        if not resp_json:
            print(f"[WARN] recommend api miss: {i+1}/{MAX_REFRESH_TRIES}")
            continue

        items = (
            resp_json.get("value", {})
            .get("result_body", {})
            .get("recommend_list", [])
        )

        for item in items:
            acc_id = str(item.get("nick_no", "")).strip()
            server = str(item.get("world_code", "")).strip()
            nickname = str(item.get("nickname", "")).strip()
            if not acc_id or not server:
                continue

            unique_accounts[(acc_id, server)] = {
                "acc_id": acc_id,
                "server": server,
                "nickname": nickname,
            }

        print(f"[INFO] refresh={i+1} unique_accounts={len(unique_accounts)}")

        if len(unique_accounts) >= TARGET_ACCOUNT_COUNT:
            break

    return list(unique_accounts.values())[:TARGET_ACCOUNT_COUNT]


def collect_accounts_with_manual(driver: webdriver.Chrome) -> List[Dict[str, str]]:
    recommend_accounts = collect_recommend_accounts(driver)
    merged = dedup_accounts(recommend_accounts + MANUAL_ACCOUNTS)

    print(f"[INFO] recommend collected: {len(recommend_accounts)}")
    print(f"[INFO] manual accounts   : {len(MANUAL_ACCOUNTS)}")
    print(f"[INFO] merged accounts   : {len(merged)}")

    return merged


def load_more_until_end(driver, max_clicks=9):
    click_count = 0
    while click_count < max_clicks:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.loadMoreBtn")
        if not buttons:
            break

        btn = buttons[0]
        if not btn.is_displayed():
            break

        before_count = len(driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info"))

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        driver.execute_script("arguments[0].click();", btn)

        try:
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")) > before_count
            )
        except Exception:
            break

        click_count += 1
        time.sleep(0.5)

    return len(driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info"))


def close_open_cards(driver):
    open_cards = driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info.open")
    for card in open_cards:
        try:
            btn = card.find_element(By.CSS_SELECTOR, "button.btn-detail")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.2)
        except Exception:
            pass


def parse_team_summary(team_el):
    pick_codes = [
        convert_hero_code(img.get_attribute("alt"))
        for img in team_el.find_elements(By.CSS_SELECTOR, ".pick-hero img")
    ]

    ban_imgs = team_el.find_elements(By.CSS_SELECTOR, ".pick-hero.ban img")
    ban_code = convert_hero_code(ban_imgs[0].get_attribute("alt")) if ban_imgs else ""

    preban_codes = [
        convert_hero_code(img.get_attribute("alt"))
        for img in team_el.find_elements(By.CSS_SELECTOR, ".preban-hero img")
    ]

    firstpick = len(team_el.find_elements(By.CSS_SELECTOR, ".firstpick.show")) > 0

    return {
        "pick_codes": pick_codes,
        "ban_code": ban_code,
        "preban_codes": preban_codes,
        "firstpick": firstpick,
    }


def extract_detail_from_card(card):
    detail_map = {}

    my_boxes = card.find_elements(By.CSS_SELECTOR, ".battle-detail .my-team-detail ul li.herolist-box")
    enemy_boxes = card.find_elements(By.CSS_SELECTOR, ".battle-detail .enemy-team-detail ul li.herolist-box")

    my_codes = set()
    enemy_codes = set()

    for box in my_boxes:
        try:
            raw_code = box.find_element(By.CSS_SELECTOR, ".pic-area img").get_attribute("alt")
            code = convert_hero_code(raw_code)
            my_codes.add(code)
        except Exception:
            pass

    for box in enemy_boxes:
        try:
            raw_code = box.find_element(By.CSS_SELECTOR, ".pic-area img").get_attribute("alt")
            code = convert_hero_code(raw_code)
            enemy_codes.add(code)
        except Exception:
            pass

    def fill_team(boxes, team_label):
        for box in boxes:
            try:
                raw_code = box.find_element(By.CSS_SELECTOR, ".pic-area img").get_attribute("alt")
                code = convert_hero_code(raw_code)

                artifact_imgs = box.find_elements(By.CSS_SELECTOR, ".equip-area .artifact img")
                artifact_name = artifact_imgs[0].get_attribute("alt") if artifact_imgs else ""

                set_codes = [
                    img.get_attribute("alt")
                    for img in box.find_elements(By.CSS_SELECTOR, ".equip-area ul li img")
                ]

                info = detail_map.setdefault((team_label, code), {})
                info["hero_code"] = code
                info["아티팩트"] = artifact_name
                info["set_codes"] = set_codes
            except Exception:
                pass

    fill_team(my_boxes, "아군")
    fill_team(enemy_boxes, "적군")

    for li in card.find_elements(By.CSS_SELECTOR, ".battle-detail .energy-wrap li.hero-energy"):
        try:
            raw_code = li.find_element(By.TAG_NAME, "img").get_attribute("alt")
            code = convert_hero_code(raw_code)
            gauge = li.find_element(By.TAG_NAME, "i").text.strip()

            if code in my_codes:
                team = "아군"
            elif code in enemy_codes:
                team = "적군"
            else:
                cls = li.get_attribute("class") or ""
                if "my-team" in cls:
                    team = "아군"
                elif "enemy-team" in cls:
                    team = "적군"
                else:
                    continue

            info = detail_map.setdefault((team, code), {})
            info["hero_code"] = code
            info["게이지"] = gauge
        except Exception:
            pass

    return detail_map


def open_detail_for_index(driver, idx):
    close_open_cards(driver)

    cards = driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")
    card = cards[idx]

    buttons = card.find_elements(By.CSS_SELECTOR, "button.btn-detail")
    if not buttons:
        return cards[idx]

    btn = buttons[0]
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    driver.execute_script("arguments[0].click();", btn)

    try:
        WebDriverWait(driver, 3).until(
            lambda d: "open" in d.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")[idx].get_attribute("class")
        )
    except Exception:
        pass

    try:
        WebDriverWait(driver, 3).until(
            lambda d: len(
                d.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")[idx]
                .find_elements(By.CSS_SELECTOR, ".battle-detail")
            ) > 0
        )
    except Exception:
        pass

    cards = driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")
    return cards[idx]


def parse_one_card(driver, idx):
    cards = driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info")
    card = cards[idx]

    result = "승" if "win" in (card.get_attribute("class") or "") else "패"

    try:
        battle_time = card.find_element(By.XPATH, ".//p[contains(., 'TIME')]/em").text.strip()
    except Exception:
        battle_time = ""

    if battle_time == "00:00":
        return None

    my_team = card.find_element(By.CSS_SELECTOR, ".my-team")
    enemy_team = card.find_element(By.CSS_SELECTOR, ".enemy-team")

    my_summary = parse_team_summary(my_team)
    enemy_summary = parse_team_summary(enemy_team)

    try:
        enemy_name = enemy_team.find_element(By.CSS_SELECTOR, ".enemy-name").text.strip()
    except Exception:
        enemy_name = ""

    try:
        spans = enemy_team.find_elements(By.CSS_SELECTOR, ".align-row a span")
        enemy_server = spans[-1].text.strip() if spans else ""
    except Exception:
        enemy_server = ""

    card = open_detail_for_index(driver, idx)
    detail_map = extract_detail_from_card(card)

    my_pick_order = {}
    for i, hero_name in enumerate(my_summary["pick_codes"], start=1):
        my_pick_order[hero_name] = i

    enemy_pick_order = {}
    for i, hero_name in enumerate(enemy_summary["pick_codes"], start=1):
        enemy_pick_order[hero_name] = i

    ordered_detail = {}

    for (team, code), info in detail_map.items():
        if team == "아군":
            if code in my_pick_order:
                key = f"아군_{my_pick_order[code]}"
            else:
                key = f"아군_{code}"
        else:
            if code in enemy_pick_order:
                key = f"적군_{enemy_pick_order[code]}"
            else:
                key = f"적군_{code}"

        ordered_detail[key] = info

    return {
        "result": result,
        "enemy_name": enemy_name,
        "enemy_server": enemy_server,
        "my_firstpick": my_summary["firstpick"],
        "my_team": {
            "pick_codes": my_summary["pick_codes"],
            "ban_code": my_summary["ban_code"],
            "preban_codes": my_summary["preban_codes"],
        },
        "enemy_team": {
            "pick_codes": enemy_summary["pick_codes"],
            "ban_code": enemy_summary["ban_code"],
            "preban_codes": enemy_summary["preban_codes"],
        },
        "detail": ordered_detail,
        "battle_index": idx + 1,
    }


def collect_account_battles(
    driver,
    acc_id: str,
    server: str,
    nickname: str,
    all_results_ref: List[Dict[str, Any]] | None = None,
):
    url = BATTLE_URL.format(server=server, acc_id=acc_id)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.battle-list"))
        )
    except Exception:
        print(f"[WARN] battle-list not found: {acc_id}/{server}")
        empty_result = {
            "acc_id": acc_id,
            "server": server,
            "nickname": nickname,
            "battles": [],
        }
        if all_results_ref is not None:
            temp_data = all_results_ref + [empty_result]
            save_json(TEMP_OUTPUT_JSON, temp_data)
            print(f"[TEMP SAVE] {TEMP_OUTPUT_JSON} (battle-list not found)")
        return empty_result

    total_count = load_more_until_end(driver, max_clicks=9)
    print(f"[INFO] {acc_id}/{server} total battle cards after loadMore: {total_count}")

    total_cards = len(driver.find_elements(By.CSS_SELECTOR, "ul.battle-list > li.battle-info"))
    results = []

    for idx in range(total_cards):
        try:
            parsed = parse_one_card(driver, idx)
            if parsed is not None:
                parsed["battle_index"] = len(results) + 1
                results.append(parsed)

                if len(results) % 10 == 0:
                    temp_account_result = {
                        "acc_id": acc_id,
                        "server": server,
                        "nickname": nickname,
                        "battles": results,
                    }

                    if all_results_ref is not None:
                        temp_data = all_results_ref + [temp_account_result]
                    else:
                        temp_data = [temp_account_result]

                    save_json(TEMP_OUTPUT_JSON, temp_data)
                    print(f"[TEMP SAVE] {TEMP_OUTPUT_JSON} / {acc_id}/{server} battles={len(results)}")

        except Exception as e:
            print(f"[WARN] {acc_id}/{server} card {idx+1} failed: {e}")

    final_account_result = {
        "acc_id": acc_id,
        "server": server,
        "nickname": nickname,
        "battles": results,
    }

    if all_results_ref is not None:
        temp_data = all_results_ref + [final_account_result]
    else:
        temp_data = [final_account_result]

    save_json(TEMP_OUTPUT_JSON, temp_data)
    print(f"[TEMP SAVE FINAL] {TEMP_OUTPUT_JSON} / {acc_id}/{server} battles={len(results)}")

    return final_account_result


def main():
    driver = build_driver()
    all_results = []

    try:
        accounts = collect_accounts_with_manual(driver)

        for i, acc in enumerate(accounts, start=1):
            acc_id = acc["acc_id"]
            server = acc["server"]
            nickname = acc.get("nickname", "")

            print(f"[INFO] processing {i}/{len(accounts)}: {acc_id} / {server} / {nickname}")

            account_result = collect_account_battles(
                driver,
                acc_id,
                server,
                nickname,
                all_results_ref=all_results,
            )
            all_results.append(account_result)

            save_json(TEMP_OUTPUT_JSON, all_results)
            print(f"[TEMP SAVE ACCOUNT] {TEMP_OUTPUT_JSON} / accounts={len(all_results)}")

        save_json(OUTPUT_JSON, all_results)
        print(f"[INFO] saved: {OUTPUT_JSON} / accounts={len(all_results)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()