# Drift Report

## Baseline Source Audit
- rules source of truth: `C:\Users\KOSMO\IdeaProjects\BanPick\data\hero_rules22.md`
- 현재 HTML baseline hero source는 `const HEROES`이며, 이후 `KNOWN_KOREAN_HERO_NAMES`를 `ensureHeroExists()`로 대량 확장하는 구조입니다.
- HTML의 pattern source는 `RAW_PACKAGES`, `NUANCED_COUNTERS`, `LOG_ROLE_CONFIDENCE_STATS`, `HIGHROLLER_TURN_ONE` 같은 하드코딩 상수입니다.
- hero_full_legend와 battlecollect는 현재 런타임 보정층이지만, baseline/pattern의 단일 source of truth는 아직 아닙니다.

## md에는 있는데 html 태그에 없는 영웅/태그
- 없음

## html에는 entity로 존재하지만 alias여야 하는 중복 영웅
- 바다의 유령 폴리티스: entity ids=['GHOST_POLITIS', 'SCENT_POLITIS']
- 별의 신탁 엘레나: entity ids=['ELENA_STAR', 'STAR_ELENA']
- 랑디 -> 해군대령 랑디: HTML ids=RANDI,NAVY_LANDY

## hero legend json과 md meta 수치가 충돌하는 영웅
- 해군대령 랑디: md22 win=58.46, legend win=50.42
- 낙월: md22 win=57.00, legend win=51.87
- 밀림: md22 win=57.00, legend win=61.05
- 방랑자 실크: md22 win=57.00, legend win=59.26
- 베니마루: md22 win=57.00, legend win=42.86
- 별의 신탁 엘레나: md22 win=57.00, legend win=52.37
- 비르기타: md22 win=58.96, legend win=78.57
- 어린 여왕 샬롯: md22 win=60.72, legend win=56.52
- 크라우: md22 win=57.00, legend win=47.62
- 키세: md22 win=0.00, legend win=46.43
- 페른: md22 win=57.00, legend win=62.82
- 현자 바알&세잔: md22 win=54.60, legend win=60.43
- 혈검 카린: md22 win=54.20, legend win=59.53
- 후미르: md22 win=57.00, legend win=60.44

## battlecollect에서 추출 가능하지만 현재 html이 거의 활용하지 못하는 패턴
- battlecollect/log 기반 preban pressure map
- final-ban pressure 집계
- rank bucket별 first-pick tendency
- rank bucket별 vanguard tendency
- 발견형 package synergy lookup

## 프리밴/밴가드/선턴 규칙 불일치
- HTML에는 상대 프리밴 스킵 편의 기능이 있어 동시 프리밴 규칙과 완전히 일치하지 않음
- HTML FIRST_TURN_OPENERS 누락: ['AMID', 'DESERT_JEWEL_BASAR', 'MOON_RABBIT_DOMINIEL', 'NAKWOL']
- HTML 내부 패턴 상수에 HEROES 없는 id 참조 존재: ['AOE_CORE', 'BRUISER_CORE', 'CONTROL_CORE', 'DEBUFF_CORE', 'DESIGNER_DILIBET', 'DESIGNER_LILIKA', 'EARLY_PICK_CORE', 'FRONTLINE_CORE', 'GREEN_CORE', 'HIGHROLLER_TURN_ONE', 'HTML', 'JUDGE_VILDRED', 'LILIAS_ALT', 'MODEL_LULUCA', 'NUANCED_COUNTERS', 'PERF_PAIR_POOL_LIMIT', 'SLOW_CORE', 'TURN_ONE_CORE']

## 최소 연결 계획
- `const HEROES`, `HERO_ID_ALIASES`, `KNOWN_KOREAN_HERO_NAMES` 기반 bootstrap을 `compiled_heroes.json` 로더로 교체한다.
- `RAW_PACKAGES`, `NUANCED_COUNTERS`, `LOG_ROLE_CONFIDENCE_STATS`, `HIGHROLLER_TURN_ONE`, battlecollect 런타임 집계를 `compiled_patterns.json` 로더로 교체한다.
- 유지할 함수: `buildStages`, `actualPrebans`, `getVanguard`, `buildSelectionContext`, `canSelectWithContext`, `syncStageIndexFromBoard`.
- 축소/삭제 후보: `ensureHeroExists`의 placeholder 확장, `KNOWN_KOREAN_HERO_NAMES` 전체 주입, HTML 하드코딩 패턴 상수군.
- lookup 전환 대상: `normalizeHeroId`, `canonicalHeroNameById`, `getHeroSynIds`, `getHeroHardIds`, `createRecommendationContext`, `scoreHero`, `computeRecommendations`, `computeSynergyPanels`.
- 이번 단계에서 건드리지 말아야 할 부분: 수동 입력 UX, 프리밴 dedupe 규칙, 밴가드 최종밴 제외 규칙, websocket 입력 흐름, UI 레이아웃.
