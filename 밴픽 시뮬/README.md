# 에픽세븐 밴픽 시뮬레이터

레전드 10위권 랭커 전적 9,700판을 기반으로 통계를 산출한 실전형 밴픽 추천 도구입니다.  
픽률·승률·밴률 지표, 상성, 시너지, 조합 완성도, 선픽/밴가드/최종밴 가치를 종합해 최적 픽을 추천합니다.

---

## 실행 방법

### 방법 A — 더블클릭으로 바로 실행 (권장)

`embed_overlay.py`로 JSON이 HTML에 통합된 `banpick.html`은 별도 서버 없이 더블클릭으로 실행됩니다.

### 방법 B — 로컬 서버로 실행

JSON을 HTML에 임베드하지 않은 경우, `밴픽 시뮬` 폴더에서 로컬 서버를 켜야 합니다.

```bash
cd "밴픽 시뮬"
python -m http.server 8000
```

브라우저에서 `http://localhost:8000/banpick.html` 접속.

---

## 폴더 구조

```
BanPick/
├── 밴픽 시뮬/
│   ├── banpick.html                  # 메인 시뮬레이터 (실행 파일)
│   ├── compiled_runtime_overlay.json # 상성·시너지·역할 점수 데이터
│   ├── compiled_matchup_matrix.json  # 전체 상성 매트릭스
│   ├── compiled_synergy_matrix.json  # 전체 시너지 매트릭스
│   ├── compiled_role_scores.json     # 선픽·밴가드·프리밴 역할 점수
│   ├── compiled_heroes.json          # 영웅 기본 데이터 (빌드 전용)
│   ├── compiled_patterns.json        # 전적 패턴 데이터 (빌드 전용)
│   ├── embed_overlay.py              # JSON → HTML 인라인 임베드 스크립트
│   ├── hero_images/                  # 영웅 아이콘 이미지
│   ├── set_images/                   # 장비 세트 아이콘 이미지
│   ├── epic7_hero_record_output/
│   │   └── hero_full_legend.json     # 영웅 상세 전적 데이터
│   └── battlecollect_shouldrun/
│       └── battle_accounts_merged.json  # 원본 전적 데이터 (9,700판)
├── tools/
│   ├── build_relation_matrices.py    # 핵심 빌드 스크립트
│   ├── build_compiled_data.py        # 영웅 데이터 빌드
│   ├── compile_pattern_data.py       # 패턴 데이터 컴파일
│   └── build_draft_compiled_data.py  # 드래프트 데이터 빌드
└── data/
    └── hero_rules.md                 # 영웅별 수동 규칙 정의
```

---

## 데이터 업데이트 및 재빌드 방법

전적 데이터나 영웅 규칙이 바뀌었을 때 아래 순서로 재빌드합니다.

### 1. 전적 데이터 수집

`herodatancollect_no_detail.py`로 최신 전적을 수집해 `battle_accounts_merged.json`을 갱신합니다.

### 2. 매트릭스 및 overlay 재빌드

```bash
cd tools
python build_relation_matrices.py
```

빌드 완료 시 아래 파일들이 자동 갱신됩니다.
- `compiled_matchup_matrix.json`
- `compiled_synergy_matrix.json`
- `compiled_role_scores.json`
- `compiled_runtime_overlay.json`
- `overlay_validation_report.md`

### 3. HTML에 JSON 임베드

```bash
cd "밴픽 시뮬"
python embed_overlay.py
```

`banpick.html`에 최신 overlay JSON이 인라인으로 삽입됩니다. 이후 서버 없이 더블클릭으로 실행 가능합니다.

---

## 영웅 데이터 수동 수정 방법

### 상성(hard) 관계 수정

`밴픽 시뮬/epic7_hero_record_output/hero_full_legend.json`에서 해당 영웅의 `list_hard_heroes` 배열을 수정합니다.

```json
{
  "hero_name": "보검의 군주 이세리아",
  "list_hard_heroes": ["조장 아룬카", "보건교사 율하"]
}
```

`list_hard_heroes`의 의미: **"이 영웅들이 나를 카운터한다"** (내 천적 목록)

수정 후 반드시 `build_relation_matrices.py` → `embed_overlay.py` 순서로 재빌드해야 반영됩니다.

### 영웅 규칙(extraRules) 추가

`밴픽 시뮬/compiled_heroes.json`에서 해당 영웅의 `extraRules` 배열에 규칙 문자열을 추가합니다.

```json
{
  "id": "ASHEN_ISERIA",
  "extraRules": ["카운터: 메이드 클로에"]
}
```

---

## 점수 구성 요소

`scoreHero()` 함수가 아래 버킷을 합산해 최종 추천 점수를 산출합니다.

| 버킷 | 설명 | 데이터 소스 |
|---|---|---|
| `meta` | 픽률·승률·밴률 기반 범용 체급 | 전적 통계 |
| `synergy` | 내 현재 조합과의 시너지 | overlay helpsWith |
| `counters` | 상대 보드 상성 우위/불리 | overlay goodVs/badVs |
| `completion` | 내 조합 완성도 기여 | overlay helpsWith + 보드 |
| `early` | 1~2픽 선점 가치 | overlay firstpick + presence |
| `urgency` | 프리밴 압박 가치 | overlay preban + banPressure |
| `vanguard` | 3픽(밴가드) 가치 | overlay vanguard |
| `exposure` | 최종 밴 노출 위험 감점 | 전적 ban 수치 |
| `relief` | 밴 유도 디코이 가치 | 전적 ban 수치 |
| `archetype` | 선턴 템포 아키타입 보너스 | 영웅 태그 + 보드 |
| `reproducibility` | 초고스펙 로그 재현성 패널티 | 영웅 태그 + 보드 |
| `openCounter` | 오픈 카운터 리스크 패널티 | overlay badVs + 예측 위협 |
| `speedContest` | 속도 경쟁 상황 보너스 | speed_contest 태그 |

---

## 기능 추가 방법

### 새 점수 버킷 추가

1. `scoreHero()` 함수 안에 새 변수를 계산합니다.
2. `total` 계산식에 해당 변수를 추가합니다.
3. `breakdown` 반환 객체에 키를 추가합니다.
4. `renderRecs()` 함수의 `items` 배열에 표시 레이블과 값을 추가합니다.

### 새 영웅 추가

1. `compiled_heroes.json`의 `heroes` 배열에 영웅 항목을 추가합니다.
2. `hero_full_legend.json`에 해당 영웅의 전적 행을 추가합니다.
3. `hero_images/` 폴더에 영웅 아이콘을 추가합니다.
4. `build_relation_matrices.py` → `embed_overlay.py` 순서로 재빌드합니다.

### overlay 품질 개선

- **상성 데이터 보완**: `hero_full_legend.json`의 `list_hard_heroes` 수동 수정
- **시너지 데이터 보완**: `compiled_heroes.json`의 `syn` 배열 수정
- **top60 범위 조정**: `build_relation_matrices.py`의 `TOP60_COUNT` 상수 변경 (현재 60)
- **top10 정밀 평가 범위 조정**: `TOP_FOCUS_COUNT` 상수 변경 (현재 10)

---

## Git 작업 흐름

```bash
# 작업 시작 전 항상 최신 코드 받기
git pull origin main

# 작업 후 push
git add .
git commit -m "수정 내용 설명"
git push origin main

# 공개 레포에 배포
git push public main
```

> **주의**: pull 없이 push하면 충돌이 발생할 수 있습니다. 항상 pull 먼저.

---

## 주요 파일 역할 요약

| 파일 | 역할 | 수정 빈도 |
|---|---|---|
| `banpick.html` | 시뮬레이터 본체 (UI + 점수 로직) | 기능 추가·버그 수정 시 |
| `build_relation_matrices.py` | overlay/매트릭스 빌드 핵심 스크립트 | 데이터 파이프라인 수정 시 |
| `compiled_runtime_overlay.json` | 상성·시너지 실시간 데이터 | 빌드 후 자동 갱신 |
| `hero_full_legend.json` | 영웅 전적·상성 원천 데이터 | 수동 보정 시 |
| `embed_overlay.py` | JSON을 HTML에 통합 | 배포 시마다 실행 |
| `battle_accounts_merged.json` | 원본 전적 9,700판 | 데이터 수집 후 갱신 |

---

## 데이터 기준

- **수집 기간**: 2026년 3월 10일 기준
- **표본**: 레전드 10위권 랭커 계정 100개, 총 9,700판
- **영웅 수**: 167명
- **참고용 도구**이며 실전 결과를 보장하지 않습니다.

---

*제작: 용제 / 제작자는 여러분의 실레나 점수에 아무런 책임이 없습니다.*
