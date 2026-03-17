from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def squish_spaces(value: str) -> str:
    return re.sub(r"\s+", "", (value or "").strip())


def stable_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def parse_alias_map(hero_rules_path: Path) -> Dict[str, str]:
    text = hero_rules_path.read_text(encoding="utf-8-sig")
    alias_map: Dict[str, str] = {}
    for raw_src, raw_dst in re.findall(r"^-\s+(.+?)\s*->\s*(.+?)\s*$", text, re.M):
        src = stable_text(raw_src)
        dst = stable_text(raw_dst)
        if src and dst and src != dst:
            alias_map[src] = dst
    return alias_map


def resolve_alias(name: str, alias_map: Dict[str, str]) -> str:
    current = stable_text(name)
    seen = set()
    while current in alias_map and current not in seen:
        seen.add(current)
        current = stable_text(alias_map[current])
    return current


def build_canonical_map(raw_names: Iterable[str], alias_map: Dict[str, str]) -> Dict[str, str]:
    counter: Counter[str] = Counter()
    resolved_names: List[str] = []
    for raw in raw_names:
        if not raw:
            continue
        resolved = resolve_alias(raw, alias_map)
        if resolved:
            counter[resolved] += 1
            resolved_names.append(resolved)

    canonical_by_compact: Dict[str, str] = {}
    for target in alias_map.values():
        resolved = resolve_alias(target, alias_map)
        key = squish_spaces(resolved)
        if key and key not in canonical_by_compact:
            canonical_by_compact[key] = resolved

    for name, _count in sorted(counter.items(), key=lambda item: (-item[1], len(item[0]), item[0])):
        key = squish_spaces(name)
        if not key:
            continue
        current = canonical_by_compact.get(key)
        if current is None:
            canonical_by_compact[key] = name
            continue
        if " " in name and " " not in current:
            canonical_by_compact[key] = name
    return canonical_by_compact


class NameNormalizer:
    def __init__(self, alias_map: Dict[str, str], canonical_by_compact: Dict[str, str]):
        self.alias_map = alias_map
        self.canonical_by_compact = canonical_by_compact

    def __call__(self, name: str) -> str:
        resolved = resolve_alias(name, self.alias_map)
        return self.canonical_by_compact.get(squish_spaces(resolved), resolved)


class StatBucket(defaultdict):
    def __init__(self):
        super().__init__(int)


def confidence(sample_count: int, midpoint: float) -> float:
    if sample_count <= 0:
        return 0.0
    return sample_count / (sample_count + midpoint)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def normalize_team_names(names: Iterable[str], normalize) -> List[str]:
    normalized = []
    seen = set()
    for raw in names or []:
        name = normalize(raw)
        if not name or name in seen:
            continue
        seen.add(name)
        normalized.append(name)
    return normalized


def package_phase(indices: Tuple[int, int, int]) -> str:
    low = min(indices)
    high = max(indices)
    if high <= 2:
        return "early"
    if low >= 2:
        return "late"
    if high <= 3:
        return "mid"
    return "mixed"


def combo_key(names: Iterable[str]) -> str:
    return "|".join(sorted(names))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile weak pattern lookup data from battle_accounts_merged.json")
    parser.add_argument("--battle-json", default=str(Path("밴픽 시뮬") / "battlecollect_shouldrun" / "battle_accounts_merged.json"))
    parser.add_argument("--hero-rules", default=str(Path("data") / "hero_rules22.md"))
    parser.add_argument("--ranker-logs", default=str(Path("data") / "ranker_logs.md"))
    parser.add_argument("--schema", default=str(Path("data") / "compiled_pattern_schema.md"))
    parser.add_argument("--output", default=str(Path("compiled_pattern_data.json")))
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    battle_path = Path(args.battle_json)
    hero_rules_path = Path(args.hero_rules)
    ranker_logs_path = Path(args.ranker_logs)
    schema_path = Path(args.schema)
    output_path = Path(args.output)

    raw_accounts = json.loads(battle_path.read_text(encoding="utf-8-sig"))
    alias_map = parse_alias_map(hero_rules_path)

    raw_names: List[str] = []
    total_battles = 0
    for account in raw_accounts:
        for battle in account.get("battles", []):
            total_battles += 1
            for side_key in ("my_team", "enemy_team"):
                team = battle.get(side_key, {})
                raw_names.extend(team.get("pick_codes", []))
                raw_names.extend(team.get("preban_codes", []))
                raw_names.append(team.get("ban_code", ""))
            for slot in (battle.get("detail") or {}).values():
                raw_names.append(slot.get("hero_code", ""))

    canonical_by_compact = build_canonical_map(raw_names, alias_map)
    normalize_name = NameNormalizer(alias_map, canonical_by_compact)

    hero_presence: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_win: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_preban: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_first_pick: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_vanguard: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_ban_pressure: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_pair: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_package: Dict[str, StatBucket] = defaultdict(StatBucket)
    hero_sets: Dict[str, Dict[str, StatBucket]] = defaultdict(lambda: defaultdict(StatBucket))
    weak_matchups: Dict[str, StatBucket] = defaultdict(StatBucket)

    hero_detail_games: Counter[str] = Counter()
    first_pick_side_total = 0
    second_pick_side_total = 0
    total_team_slots = 0

    for account in raw_accounts:
        for battle in account.get("battles", []):
            result = stable_text(str(battle.get("result", "")))
            my_win = result == "승"
            my_firstpick = bool(battle.get("my_firstpick"))

            my_team = battle.get("my_team", {}) or {}
            enemy_team = battle.get("enemy_team", {}) or {}
            my_picks = normalize_team_names(my_team.get("pick_codes", []), normalize_name)
            enemy_picks = normalize_team_names(enemy_team.get("pick_codes", []), normalize_name)
            my_prebans = normalize_team_names(my_team.get("preban_codes", []), normalize_name)
            enemy_prebans = normalize_team_names(enemy_team.get("preban_codes", []), normalize_name)
            my_ban = normalize_name(my_team.get("ban_code", "")) if my_team.get("ban_code") else ""
            enemy_ban = normalize_name(enemy_team.get("ban_code", "")) if enemy_team.get("ban_code") else ""

            duplicate_prebans = set(my_prebans) & set(enemy_prebans)
            for hero in my_prebans:
                bucket = hero_preban[hero]
                bucket["total"] += 1
                bucket["myPreban"] += 1
            for hero in enemy_prebans:
                bucket = hero_preban[hero]
                bucket["total"] += 1
                bucket["enemyPreban"] += 1
            for hero in duplicate_prebans:
                hero_preban[hero]["duplicatePreban"] += 1

            if my_firstpick:
                if my_picks:
                    first_hero = my_picks[0]
                    bucket = hero_first_pick[first_hero]
                    bucket["firstPickCount"] += 1
                    bucket["games"] += 1
                    bucket["wins"] += int(my_win)
                first_pick_side_total += 1
                second_pick_side_total += 1
            else:
                if enemy_picks:
                    first_hero = enemy_picks[0]
                    bucket = hero_first_pick[first_hero]
                    bucket["firstPickCount"] += 1
                    bucket["games"] += 1
                    bucket["wins"] += int(not my_win)
                first_pick_side_total += 1
                second_pick_side_total += 1

            team_rows = [
                (my_picks, my_win, my_firstpick, "myTeam"),
                (enemy_picks, not my_win, not my_firstpick, "enemyTeam"),
            ]

            for picks, team_win, team_is_first_pick_side, team_label in team_rows:
                total_team_slots += len(picks)
                for hero in picks:
                    bucket = hero_presence[hero]
                    bucket["total"] += 1
                    bucket[team_label] += 1
                    bucket["firstPickSide" if team_is_first_pick_side else "secondPickSide"] += 1

                    wb = hero_win[hero]
                    wb["games"] += 1
                    wb["wins"] += int(team_win)
                    wb["losses"] += int(not team_win)
                    if team_is_first_pick_side:
                        wb["firstPickGames"] += 1
                        wb["firstPickWins"] += int(team_win)
                    else:
                        wb["secondPickGames"] += 1
                        wb["secondPickWins"] += int(team_win)

                if len(picks) >= 3:
                    vanguard = picks[2]
                    vb = hero_vanguard[vanguard]
                    vb["vanguardCount"] += 1
                    vb["games"] += 1
                    vb["wins"] += int(team_win)
                    if team_is_first_pick_side:
                        vb["firstPickSideCount"] += 1
                    else:
                        vb["secondPickSideCount"] += 1

                for pair in combinations(picks, 2):
                    key = combo_key(pair)
                    pb = hero_pair[key]
                    pb["games"] += 1
                    pb["wins"] += int(team_win)
                    if team_is_first_pick_side:
                        pb["firstPickGames"] += 1
                        pb["firstPickWins"] += int(team_win)
                    else:
                        pb["secondPickGames"] += 1
                        pb["secondPickWins"] += int(team_win)

                indexed_picks = list(enumerate(picks))
                for combo in combinations(indexed_picks, 3):
                    members = [name for _idx, name in combo]
                    indices = tuple(idx for idx, _name in combo)
                    key = combo_key(members)
                    phase = package_phase(indices)
                    pkg = hero_package[key]
                    pkg["games"] += 1
                    pkg["wins"] += int(team_win)
                    pkg[f"phase_{phase}"] += 1

            if my_ban:
                bucket = hero_ban_pressure[my_ban]
                bucket["finalBanCount"] += 1
                bucket["enemyBanTargetCount"] += 1
                bucket["pickedCount"] += int(my_ban in my_picks)
            if enemy_ban:
                bucket = hero_ban_pressure[enemy_ban]
                bucket["finalBanCount"] += 1
                bucket["myBanTargetCount"] += 1
                bucket["pickedCount"] += int(enemy_ban in enemy_picks)

            for my_hero in my_picks:
                for enemy_hero in enemy_picks:
                    bucket = weak_matchups[f"{my_hero}|{enemy_hero}"]
                    bucket["games"] += 1
                    bucket["wins"] += int(my_win)
            for enemy_hero in enemy_picks:
                for my_hero in my_picks:
                    bucket = weak_matchups[f"{enemy_hero}|{my_hero}"]
                    bucket["games"] += 1
                    bucket["wins"] += int(not my_win)

            detail = battle.get("detail") or {}
            for slot_name, slot_value in detail.items():
                hero_name = normalize_name(slot_value.get("hero_code", "")) if isinstance(slot_value, dict) else ""
                if not hero_name:
                    continue
                sets = sorted({stable_text(code) for code in slot_value.get("set_codes", []) if stable_text(code)})
                if not sets:
                    continue
                set_key = "|".join(sets)
                team_win = my_win if slot_name.startswith("아군_") else not my_win
                hero_detail_games[hero_name] += 1
                bucket = hero_sets[hero_name][set_key]
                bucket["games"] += 1
                bucket["wins"] += int(team_win)

    hero_base_win_rate = {
        hero: safe_rate(bucket["wins"], bucket["games"]) * 100.0
        for hero, bucket in hero_win.items()
    }

    hero_presence_out = {}
    for hero, bucket in sorted(hero_presence.items()):
        hero_presence_out[hero] = {
            "total": bucket["total"],
            "myTeam": bucket["myTeam"],
            "enemyTeam": bucket["enemyTeam"],
            "firstPickSide": bucket["firstPickSide"],
            "secondPickSide": bucket["secondPickSide"],
            "presenceRate": round(safe_rate(bucket["total"], total_battles), 6),
        }

    hero_win_out = {}
    for hero, bucket in sorted(hero_win.items()):
        conf = confidence(bucket["games"], 24.0)
        win_rate = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        hero_win_out[hero] = {
            "games": bucket["games"],
            "wins": bucket["wins"],
            "losses": bucket["losses"],
            "winRate": round(win_rate, 4),
            "firstPickWinRate": round(safe_rate(bucket["firstPickWins"], bucket["firstPickGames"]) * 100.0, 4),
            "secondPickWinRate": round(safe_rate(bucket["secondPickWins"], bucket["secondPickGames"]) * 100.0, 4),
            "confidence": round(conf, 6),
            "reliabilityScore": round(((win_rate - 50.0) / 100.0) * conf, 6),
        }

    hero_preban_out = {}
    for hero, bucket in sorted(hero_preban.items()):
        conf = confidence(bucket["total"], 18.0)
        preban_rate = safe_rate(bucket["total"], total_battles)
        hero_preban_out[hero] = {
            "total": bucket["total"],
            "myPreban": bucket["myPreban"],
            "enemyPreban": bucket["enemyPreban"],
            "duplicatePreban": bucket["duplicatePreban"],
            "prebanRate": round(preban_rate, 6),
            "pressureScore": round(preban_rate * conf, 6),
        }

    hero_first_pick_out = {}
    for hero, bucket in sorted(hero_first_pick.items()):
        conf = confidence(bucket["firstPickCount"], 12.0)
        fp_rate = safe_rate(bucket["firstPickCount"], total_battles)
        fp_win = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        hero_first_pick_out[hero] = {
            "firstPickCount": bucket["firstPickCount"],
            "firstPickRate": round(fp_rate, 6),
            "firstPickWinRate": round(fp_win, 4),
            "openerScore": round(((fp_win - 50.0) / 100.0) * conf * fp_rate, 6),
        }

    hero_vanguard_out = {}
    for hero, bucket in sorted(hero_vanguard.items()):
        conf = confidence(bucket["vanguardCount"], 10.0)
        v_rate = safe_rate(bucket["vanguardCount"], total_battles * 2)
        v_win = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        hero_vanguard_out[hero] = {
            "vanguardCount": bucket["vanguardCount"],
            "vanguardRate": round(v_rate, 6),
            "vanguardWinRate": round(v_win, 4),
            "protectedCoreScore": round(((v_win - 50.0) / 100.0) * conf * (0.5 + v_rate), 6),
        }

    hero_ban_pressure_out = {}
    for hero, bucket in sorted(hero_ban_pressure.items()):
        conf = confidence(bucket["finalBanCount"], 10.0)
        banned_when_picked = safe_rate(bucket["finalBanCount"], bucket["pickedCount"])
        hero_ban_pressure_out[hero] = {
            "finalBanCount": bucket["finalBanCount"],
            "bannedWhenPicked": round(banned_when_picked, 6),
            "myBanTargetCount": bucket["myBanTargetCount"],
            "enemyBanTargetCount": bucket["enemyBanTargetCount"],
            "banPressureScore": round(banned_when_picked * conf, 6),
        }

    hero_pair_out = {}
    for key, bucket in sorted(hero_pair.items()):
        if bucket["games"] < 3:
            continue
        a_name, b_name = key.split("|")
        base = (hero_base_win_rate.get(a_name, 50.0) + hero_base_win_rate.get(b_name, 50.0)) / 2.0
        conf = confidence(bucket["games"], 14.0)
        win_rate = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        first_lift = (safe_rate(bucket["firstPickWins"], bucket["firstPickGames"]) * 100.0 - base) if bucket["firstPickGames"] else 0.0
        second_lift = (safe_rate(bucket["secondPickWins"], bucket["secondPickGames"]) * 100.0 - base) if bucket["secondPickGames"] else 0.0
        hero_pair_out[key] = {
            "games": bucket["games"],
            "wins": bucket["wins"],
            "winRate": round(win_rate, 4),
            "lift": round((win_rate - base) * conf, 6),
            "firstPickLift": round(first_lift * confidence(bucket["firstPickGames"], 8.0), 6),
            "secondPickLift": round(second_lift * confidence(bucket["secondPickGames"], 8.0), 6),
            "confidence": round(conf, 6),
        }

    hero_package_out = {}
    for key, bucket in sorted(hero_package.items()):
        if bucket["games"] < 3:
            continue
        members = key.split("|")
        base = sum(hero_base_win_rate.get(name, 50.0) for name in members) / len(members)
        conf = confidence(bucket["games"], 16.0)
        win_rate = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        phase_counts = {phase.replace("phase_", ""): bucket[phase] for phase in bucket if phase.startswith("phase_")}
        dominant_phase = max(phase_counts.items(), key=lambda item: item[1])[0] if phase_counts else "mixed"
        hero_package_out[key] = {
            "games": bucket["games"],
            "wins": bucket["wins"],
            "winRate": round(win_rate, 4),
            "lift": round((win_rate - base) * conf, 6),
            "phase": dominant_phase,
            "confidence": round(conf, 6),
        }

    hero_set_out = {}
    for hero, set_map in sorted(hero_sets.items()):
        hero_entry = {}
        total_sets_for_hero = hero_detail_games[hero]
        for set_key, bucket in sorted(set_map.items()):
            if bucket["games"] < 2:
                continue
            hero_entry[set_key] = {
                "games": bucket["games"],
                "winRate": round(safe_rate(bucket["wins"], bucket["games"]) * 100.0, 4),
                "pickRateWithinHero": round(safe_rate(bucket["games"], total_sets_for_hero), 6),
            }
        if hero_entry:
            hero_set_out[hero] = hero_entry

    weak_matchup_out = {}
    for key, bucket in sorted(weak_matchups.items()):
        if bucket["games"] < 5:
            continue
        hero_name, opp_name = key.split("|")
        base_win = hero_base_win_rate.get(hero_name, 50.0)
        matchup_win = safe_rate(bucket["wins"], bucket["games"]) * 100.0
        delta = matchup_win - base_win
        if delta >= -2.0:
            continue
        conf = confidence(bucket["games"], 14.0)
        hint_score = clamp(abs(delta) / 100.0 * conf, 0.0, 0.18)
        if hint_score < 0.015:
            continue
        weak_matchup_out[key] = {
            "games": bucket["games"],
            "winRate": round(matchup_win, 4),
            "deltaVsBaseline": round(delta, 4),
            "hintScore": round(hint_score, 6),
            "confidence": round(conf, 6),
        }

    compiled = {
        "version": 1,
        "source": {
            "battle_accounts_merged": {
                "path": str(battle_path),
                "accounts": len(raw_accounts),
                "battles": total_battles,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "hero_rules22_md": str(hero_rules_path),
            "ranker_logs_md": str(ranker_logs_path),
            "compiled_pattern_schema_md": str(schema_path),
        },
        "normalization": {
            "hero_name_key": "space-insensitive + hero_rules22 alias-resolved",
            "vanguard_index": 3,
            "global_preban_mode": "union_dedupe",
            "aliasCount": len(alias_map),
        },
        "heroPresenceStats": hero_presence_out,
        "heroWinStats": hero_win_out,
        "heroPrebanStats": hero_preban_out,
        "heroFirstPickStats": hero_first_pick_out,
        "heroVanguardStats": hero_vanguard_out,
        "heroBanPressureStats": hero_ban_pressure_out,
        "heroPairStats": hero_pair_out,
        "heroPackageStats": hero_package_out,
        "heroSetStats": hero_set_out,
        "weakMatchupHintStats": weak_matchup_out,
    }

    output_path.write_text(json.dumps(compiled, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output_path}")
    print(f"battles={total_battles}")
    print(f"heroes={len(hero_presence_out)} pairs={len(hero_pair_out)} packages={len(hero_package_out)} weakHints={len(weak_matchup_out)}")


if __name__ == "__main__":
    main()
