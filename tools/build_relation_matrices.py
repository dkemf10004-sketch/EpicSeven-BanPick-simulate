from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / '밴픽 시뮬'
COMPILED_HEROES_PATH = DATA_DIR / 'compiled_heroes.json'
LEGEND_PATH = DATA_DIR / 'epic7_hero_record_output' / 'hero_full_legend.json'
PATTERNS_PATH = DATA_DIR / 'compiled_patterns.json'
MATCHUP_OUT = DATA_DIR / 'compiled_matchup_matrix.json'
SYNERGY_OUT = DATA_DIR / 'compiled_synergy_matrix.json'
ROLE_OUT = DATA_DIR / 'compiled_role_scores.json'


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sample_confidence(sample: float, pivot: float) -> float:
    if sample <= 0:
        return 0.0
    return clamp(math.log1p(sample) / math.log1p(pivot), 0.0, 1.0)


def round4(value: float) -> float:
    return round(float(value), 4)


def zero_relation() -> dict:
    return {
        'score': 0.0,
        'rawScore': 0.0,
        'confidence': 0.0,
        'sample': 0,
        'cap': 0.0,
        'sources': {},
    }


def build_role_entry(rate: float, raw_score: float, sample: int, cap: float, pivot: float, presence_gate: float) -> dict:
    confidence = sample_confidence(sample, pivot) * (0.34 + presence_gate * 0.66)
    score = clamp(raw_score, 0.0, cap) * confidence
    return {
        'rate': round4(rate),
        'rawScore': round4(raw_score),
        'score': round4(score),
        'confidence': round4(confidence),
        'sample': int(sample),
        'cap': round4(cap),
    }


def main() -> None:
    compiled_heroes = read_json(COMPILED_HEROES_PATH)
    legend_rows = read_json(LEGEND_PATH)
    patterns = read_json(PATTERNS_PATH)

    heroes = compiled_heroes['heroes']
    hero_count = len(heroes)
    name_to_id = {hero['name']: hero['id'] for hero in heroes}
    id_to_name = {hero['id']: hero['name'] for hero in heroes}
    hero_by_id = {hero['id']: hero for hero in heroes}
    legend_by_name = {row['hero_name']: row for row in legend_rows if row.get('hero_name') in name_to_id}

    presence_stats = patterns.get('heroPresenceStats', {})
    firstpick_stats = patterns.get('heroFirstPickStats', {})
    vanguard_stats = patterns.get('heroVanguardStats', {})
    preban_stats = patterns.get('heroPrebanStats', {})
    ban_pressure_stats = patterns.get('heroBanPressureStats', {})
    pair_stats = patterns.get('heroPairStats', {})
    package_stats = patterns.get('heroPackageStats', {})
    weak_hints = patterns.get('weakMatchupHintStats', {})
    total_teams = int(patterns.get('source', {}).get('totalTeams') or 0)

    pair_package_support: dict[tuple[str, str], list[dict]] = {}
    for key, stat in package_stats.items():
        names = [part.strip() for part in str(key).split('|') if part.strip() in name_to_id]
        ids = sorted({name_to_id[name] for name in names})
        if len(ids) < 2:
            continue
        lift = max(0.0, float(stat.get('lift') or 0.0))
        games = int(stat.get('games') or 0)
        if lift <= 0 or games <= 0:
            continue
        support = clamp(lift * 0.34, 0.0, 0.28)
        weighted = support * (0.30 + sample_confidence(games, 84) * 0.70)
        for a, b in combinations(ids, 2):
            pair_package_support.setdefault((a, b), []).append({
                'games': games,
                'lift': round4(lift),
                'support': round4(weighted),
            })

    role_scores = {
        'version': 1,
        'source': {
            'legend': str(LEGEND_PATH.relative_to(ROOT)).replace('\\', '/'),
            'compiled_patterns': str(PATTERNS_PATH.relative_to(ROOT)).replace('\\', '/'),
        },
        'firstpick': {},
        'vanguard': {},
        'preban': {},
        'banPressure': {},
        'presence': {},
        'protection': {},
        'buildSummary': {},
    }

    low_pick_suppressed = 0
    for hero in heroes:
        hero_id = hero['id']
        name = hero['name']
        presence = presence_stats.get(name, {})
        presence_rate = float(presence.get('presenceRate') or 0.0)
        presence_total = int(presence.get('total') or 0)
        fallback_pick_rate = float(hero.get('pick') or 0.0) / 100.0
        effective_presence = max(presence_rate, fallback_pick_rate * 0.82)
        presence_gate = clamp((effective_presence - 0.018) / 0.085, 0.0, 1.0)
        meta_gate = clamp((float(hero.get('pick') or 0.0) - 4.0) / 16.0, 0.0, 1.0)

        fp = firstpick_stats.get(name, {})
        vg = vanguard_stats.get(name, {})
        pb = preban_stats.get(name, {})
        bp = ban_pressure_stats.get(name, {})

        role_scores['firstpick'][hero_id] = build_role_entry(
            float(fp.get('firstPickRate') or 0.0),
            float(fp.get('openerScore') or 0.0) * 3.2,
            int(fp.get('firstPickCount') or 0),
            1.1,
            48,
            presence_gate,
        )
        role_scores['vanguard'][hero_id] = build_role_entry(
            float(vg.get('vanguardRate') or 0.0),
            float(vg.get('protectedCoreScore') or 0.0) * 3.4,
            int(vg.get('vanguardCount') or 0),
            1.2,
            56,
            presence_gate,
        )
        role_scores['preban'][hero_id] = build_role_entry(
            float(pb.get('prebanRate') or 0.0),
            float(pb.get('pressureScore') or 0.0) * 2.8,
            int(pb.get('prebanCount') or 0),
            0.92,
            64,
            presence_gate,
        )
        role_scores['banPressure'][hero_id] = build_role_entry(
            float(bp.get('banRate') or 0.0),
            float(bp.get('banPressureScore') or 0.0) * 2.6,
            int(bp.get('banCount') or 0),
            0.95,
            48,
            presence_gate,
        )
        role_scores['presence'][hero_id] = {
            'rate': round4(effective_presence),
            'rawScore': round4(effective_presence),
            'score': round4(effective_presence),
            'confidence': round4(sample_confidence(presence_total, max(total_teams, 1))),
            'sample': presence_total,
            'cap': 1.0,
        }
        protection = {
            'presenceRate': round4(effective_presence),
            'relationCapScale': round4(0.82 + presence_gate * 1.36),
            'confidenceCapScale': round4(0.72 + presence_gate * 0.88),
            'earlyStageGate': round4(0.58 + max(presence_gate, meta_gate) * 0.42),
            'lateStageRelief': round4(0.92 + (1.0 - presence_gate) * 0.36),
            'suppressed': bool(effective_presence < 0.024 or (float(hero.get('pick') or 0.0) < 5.0 and effective_presence < 0.032)),
        }
        if protection['suppressed']:
            low_pick_suppressed += 1
        role_scores['protection'][hero_id] = protection

    counter_matrix = {
        'version': 1,
        'source': {
            'legend': str(LEGEND_PATH.relative_to(ROOT)).replace('\\', '/'),
            'compiled_patterns': str(PATTERNS_PATH.relative_to(ROOT)).replace('\\', '/'),
        },
        'heroes': [{'id': hero['id'], 'name': hero['name']} for hero in heroes],
        'counterMatrix': {},
        'buildSummary': {},
    }
    synergy_matrix = {
        'version': 1,
        'source': {
            'legend': str(LEGEND_PATH.relative_to(ROOT)).replace('\\', '/'),
            'compiled_patterns': str(PATTERNS_PATH.relative_to(ROOT)).replace('\\', '/'),
        },
        'heroes': [{'id': hero['id'], 'name': hero['name']} for hero in heroes],
        'synergyMatrix': {},
        'buildSummary': {},
    }

    counter_nonzero = 0
    synergy_nonzero = 0
    confidence_weakened = 0

    for hero in heroes:
        a_id = hero['id']
        a_name = hero['name']
        a_presence = float(role_scores['presence'][a_id]['rate'])
        counter_row = {}
        synergy_row = {}
        for opp in heroes:
            b_id = opp['id']
            b_name = opp['name']
            if a_id == b_id:
                counter_row[b_id] = zero_relation()
                synergy_row[b_id] = zero_relation()
                continue

            b_presence = float(role_scores['presence'][b_id]['rate'])
            pair_presence_gate = clamp((min(a_presence, b_presence) - 0.014) / 0.096, 0.0, 1.0)

            legend_hard = a_name in set(legend_by_name.get(b_name, {}).get('list_hard_heroes') or [])
            weak_forward = weak_hints.get(f'{b_name}|{a_name}')
            weak_reverse = weak_hints.get(f'{a_name}|{b_name}')
            ban_support_entry = ban_pressure_stats.get(b_name, {})

            counter_raw = 0.0
            counter_conf = 0.0
            counter_sample = 0
            counter_sources: dict = {}
            if legend_hard:
                counter_raw += 0.92
                counter_conf += 0.58 + pair_presence_gate * 0.12
                counter_sample += 28
                counter_sources['legendHard'] = True
            if weak_forward:
                games = int(weak_forward.get('games') or 0)
                hint = float(weak_forward.get('hintScore') or 0.0)
                weak_conf = sample_confidence(games, 144) * (0.30 + pair_presence_gate * 0.55)
                weak_raw = clamp(hint * 2.25, 0.0, 0.34)
                counter_raw += weak_raw * (0.56 if legend_hard else 1.0)
                counter_conf += weak_conf * (0.50 if legend_hard else 0.64)
                counter_sample += games
                counter_sources['weakHint'] = {
                    'games': games,
                    'hintScore': round4(hint),
                    'weight': round4(weak_raw),
                }
            if weak_reverse:
                games = int(weak_reverse.get('games') or 0)
                hint = float(weak_reverse.get('hintScore') or 0.0)
                reverse_conf = sample_confidence(games, 144) * (0.24 + pair_presence_gate * 0.40)
                reverse_raw = clamp(hint * 1.7, 0.0, 0.22) * reverse_conf * 0.70
                counter_raw -= reverse_raw
                counter_sources['reverseWeakHint'] = {
                    'games': games,
                    'hintScore': round4(hint),
                    'penalty': round4(reverse_raw),
                }
            if counter_raw > 0:
                ban_pressure = float(ban_support_entry.get('banPressureScore') or 0.0)
                ban_count = int(ban_support_entry.get('banCount') or 0)
                if ban_pressure > 0 and ban_count > 0:
                    bonus_cap = 0.05 if legend_hard else 0.03
                    bonus = clamp(ban_pressure * 0.24, 0.0, bonus_cap)
                    counter_raw += bonus
                    counter_conf += sample_confidence(ban_count, 52) * 0.08
                    counter_sample += ban_count
                    counter_sources['banPressure'] = {
                        'count': ban_count,
                        'banPressureScore': round4(ban_pressure),
                        'bonus': round4(bonus),
                    }
            counter_cap = 1.02 if legend_hard else 0.46
            counter_raw = clamp(counter_raw, 0.0, counter_cap)
            if counter_raw <= 0:
                counter_entry = zero_relation()
            else:
                counter_conf = clamp(counter_conf * (0.62 + pair_presence_gate * 0.38), 0.0, 0.93)
                counter_score = counter_raw * counter_conf
                if counter_conf < 0.999:
                    confidence_weakened += 1
                counter_nonzero += 1
                counter_entry = {
                    'score': round4(counter_score),
                    'rawScore': round4(counter_raw),
                    'confidence': round4(counter_conf),
                    'sample': int(counter_sample),
                    'cap': round4(counter_cap),
                    'sources': counter_sources,
                }
            counter_row[b_id] = counter_entry

            legend_syn = b_name in set(legend_by_name.get(a_name, {}).get('list_with_heroes') or [])
            pair_key = '|'.join(sorted([a_name, b_name]))
            pair_entry = pair_stats.get(pair_key)
            package_entries = sorted(pair_package_support.get(tuple(sorted([a_id, b_id])), []), key=lambda item: item['support'], reverse=True)

            synergy_raw = 0.0
            synergy_conf = 0.0
            synergy_sample = 0
            synergy_sources: dict = {}
            if legend_syn:
                synergy_raw += 0.78
                synergy_conf += 0.54 + pair_presence_gate * 0.10
                synergy_sample += 22
                synergy_sources['legendWith'] = True
            if pair_entry:
                games = int(pair_entry.get('games') or 0)
                lift = max(0.0, float(pair_entry.get('lift') or 0.0))
                if games > 0 and lift > 0:
                    lift_gate = clamp((lift - 0.05) / 0.34, 0.0, 1.0)
                    pair_conf = sample_confidence(games, 168) * (0.32 + pair_presence_gate * 0.58) * (0.45 + lift_gate * 0.55)
                    pair_raw = clamp(lift * 0.94, 0.0, 0.42)
                    synergy_raw += pair_raw * (0.62 if legend_syn else 1.0)
                    synergy_conf += pair_conf * (0.54 if legend_syn else 0.66)
                    synergy_sample += games
                    synergy_sources['pairLift'] = {
                        'games': games,
                        'lift': round4(lift),
                        'weight': round4(pair_raw),
                    }
            if package_entries:
                top_entries = package_entries[:2]
                package_support = 0.0
                package_sample = 0
                for index, item in enumerate(top_entries):
                    factor = 1.0 if index == 0 else 0.55
                    package_support += item['support'] * factor
                    package_sample += int(item['games'])
                package_support = clamp(package_support, 0.0, 0.26)
                package_conf = sample_confidence(package_sample, 120) * (0.24 + pair_presence_gate * 0.52)
                synergy_raw += package_support * (0.58 if legend_syn else 0.82)
                synergy_conf += package_conf * 0.36
                synergy_sample += package_sample
                synergy_sources['packageLift'] = {
                    'games': package_sample,
                    'topLift': round4(top_entries[0]['lift']),
                    'weight': round4(package_support),
                }
            synergy_cap = 0.96 if legend_syn else 0.58
            synergy_raw = clamp(synergy_raw, 0.0, synergy_cap)
            if synergy_raw <= 0:
                synergy_entry = zero_relation()
            else:
                synergy_conf = clamp(synergy_conf * (0.58 + pair_presence_gate * 0.42), 0.0, 0.94)
                synergy_score = synergy_raw * synergy_conf
                if synergy_conf < 0.999:
                    confidence_weakened += 1
                synergy_nonzero += 1
                synergy_entry = {
                    'score': round4(synergy_score),
                    'rawScore': round4(synergy_raw),
                    'confidence': round4(synergy_conf),
                    'sample': int(synergy_sample),
                    'cap': round4(synergy_cap),
                    'sources': synergy_sources,
                }
            synergy_row[b_id] = synergy_entry

        counter_matrix['counterMatrix'][a_id] = counter_row
        synergy_matrix['synergyMatrix'][a_id] = synergy_row

    counter_matrix['buildSummary'] = {
        'baselineHeroCount': hero_count,
        'nonzeroRelations': counter_nonzero,
        'confidenceWeakenedRelations': confidence_weakened,
    }
    synergy_matrix['buildSummary'] = {
        'baselineHeroCount': hero_count,
        'nonzeroRelations': synergy_nonzero,
        'confidenceWeakenedRelations': confidence_weakened,
    }
    role_scores['buildSummary'] = {
        'baselineHeroCount': hero_count,
        'lowPickSuppressedHeroes': low_pick_suppressed,
    }

    write_json(MATCHUP_OUT, counter_matrix)
    write_json(SYNERGY_OUT, synergy_matrix)
    write_json(ROLE_OUT, role_scores)

    summary = {
        'baseline_hero_count': hero_count,
        'counter_matrix_size': hero_count * hero_count,
        'synergy_matrix_size': hero_count * hero_count,
        'counter_nonzero_relations': counter_nonzero,
        'synergy_nonzero_relations': synergy_nonzero,
        'confidence_weakened_relations': confidence_weakened,
        'low_pick_suppressed_heroes': low_pick_suppressed,
        'outputs': [
            str(MATCHUP_OUT.relative_to(ROOT)).replace('\\', '/'),
            str(SYNERGY_OUT.relative_to(ROOT)).replace('\\', '/'),
            str(ROLE_OUT.relative_to(ROOT)).replace('\\', '/'),
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

