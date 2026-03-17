# Compiled Pattern Schema

기준 입력:
- battle_accounts_merged.json
- hero_rules22.md
- ranker_logs.md
- 밴픽 최종_v2.html

원칙:
- hero_rules22.md는 baseline source of truth다.
- ranker_logs.md는 패턴 evidence 문서다.
- battle_accounts_merged.json은 패턴 보정층의 1차 source다.
- HTML 런타임은 raw battle_accounts_merged.json을 다시 순회하지 않는다.

## battle_accounts_merged.json에서 직접 추출 가능한 항목
- heroPresenceStats
  - hero별 총 등장 수, 내팀 등장 수, 상대팀 등장 수, 선픽/후픽별 등장 수
- heroWinStats
  - hero별 등장 시 승/패, 내팀 기준 승률, firstpick 상태별 승률
- heroPrebanStats
  - hero별 프리밴 빈도, 내 프리밴/상대 프리밴 분리 빈도, 중복 프리밴 빈도
- heroFirstPickStats
  - my_firstpick true/false와 실제 1픽 영웅 분포, first-pick opener 경향
- heroVanguardStats
  - 각 팀 세 번째 영웅(밴가드) 등장 빈도, 밴가드 승률, firstpick 연계 빈도
- heroBanPressureStats
  - 최종 밴 대상 빈도, 내 밴/상대 밴 분리, preban 대비 final ban pressure
- heroPairStats
  - 팀 내 2인 동시 등장 빈도, 승률 lift, 선/후픽 구간 분리 가능
- heroPackageStats
  - 팀 내 3인 이상 패키지 빈도, 승률 lift, early/mid/late package 분리
- heroSetStats
  - hero별 set_codes 출현 빈도, 대표 세트 조합, 승률 차이
- weakMatchupHintStats
  - hero A가 있을 때 상대 hero B 조합 상대로 승률이 약하게 낮아지는 pair hint

## compiled_patterns.json 최종 스키마
```json
{
  "version": 1,
  "source": {
    "battle_accounts_merged": {
      "accounts": 100,
      "battles": 0,
      "generated_at": "ISO-8601"
    },
    "hero_rules22_md": "path",
    "ranker_logs_md": "path"
  },
  "normalization": {
    "hero_name_key": "space-insensitive",
    "vanguard_index": 3,
    "global_preban_mode": "union_dedupe"
  },
  "heroPresenceStats": {
    "영웅명": {
      "total": 0,
      "myTeam": 0,
      "enemyTeam": 0,
      "firstPickSide": 0,
      "secondPickSide": 0,
      "presenceRate": 0.0
    }
  },
  "heroWinStats": {
    "영웅명": {
      "games": 0,
      "wins": 0,
      "losses": 0,
      "winRate": 0.0,
      "firstPickWinRate": 0.0,
      "secondPickWinRate": 0.0,
      "confidence": 0.0
    }
  },
  "heroPrebanStats": {
    "영웅명": {
      "total": 0,
      "myPreban": 0,
      "enemyPreban": 0,
      "duplicatePreban": 0,
      "prebanRate": 0.0,
      "pressureScore": 0.0
    }
  },
  "heroFirstPickStats": {
    "영웅명": {
      "firstPickCount": 0,
      "firstPickRate": 0.0,
      "firstPickWinRate": 0.0,
      "openerScore": 0.0
    }
  },
  "heroVanguardStats": {
    "영웅명": {
      "vanguardCount": 0,
      "vanguardRate": 0.0,
      "vanguardWinRate": 0.0,
      "protectedCoreScore": 0.0
    }
  },
  "heroBanPressureStats": {
    "영웅명": {
      "finalBanCount": 0,
      "bannedWhenPicked": 0.0,
      "myBanTargetCount": 0,
      "enemyBanTargetCount": 0,
      "banPressureScore": 0.0
    }
  },
  "heroPairStats": {
    "영웅A|영웅B": {
      "games": 0,
      "wins": 0,
      "winRate": 0.0,
      "lift": 0.0,
      "firstPickLift": 0.0,
      "secondPickLift": 0.0,
      "confidence": 0.0
    }
  },
  "heroPackageStats": {
    "영웅A|영웅B|영웅C": {
      "games": 0,
      "wins": 0,
      "winRate": 0.0,
      "lift": 0.0,
      "phase": "early|mid|late|mixed",
      "confidence": 0.0
    }
  },
  "heroSetStats": {
    "영웅명": {
      "set_counter|set_immune": {
        "games": 0,
        "winRate": 0.0,
        "pickRateWithinHero": 0.0
      }
    }
  },
  "weakMatchupHintStats": {
    "영웅A|영웅B": {
      "games": 0,
      "winRate": 0.0,
      "deltaVsBaseline": 0.0,
      "hintScore": 0.0,
      "confidence": 0.0
    }
  }
}
```

## HTML 엔진 연결 계획
- heroPresenceStats
  - 후보 기본 노출 빈도 보정. meta를 대체하지 않고 low-weight presence bonus로만 사용.
- heroWinStats
  - scoreHero의 약한 안정성 보정. baseline meta보다 낮은 가중치.
- heroPrebanStats
  - preban urgency / contested pool 힌트. 추천 설명과 초반 선점 경고에 연결.
- heroFirstPickStats
  - 초반 1픽/오프너 점수 보정. first_turn 태그 강화용 약한 계층.
- heroVanguardStats
  - 3번째 픽 보호 가치, 뱅가드 적합성 보정에 연결.
- heroBanPressureStats
  - final ban exposure penalty / decoy value 보정에 연결.
- heroPairStats
  - 2인 페어 추천과 scoreHero의 pair synergy bonus에 연결.
- heroPackageStats
  - package bonus, core completion bonus, package disruption 설명에 연결.
- heroSetStats
  - 설명 패널용. 추천 점수에는 직접 넣지 않거나 매우 약하게만 사용.
- weakMatchupHintStats
  - hard/syn를 덮지 않는 약한 counter hint 계층으로 연결.

## baseline과 충돌하지 않게 하는 원칙
- hero_rules22 baseline(meta/hard/syn/tags)이 1순위다.
- compiled pattern은 덮어쓰기 금지, additive/attenuated adjustment만 허용한다.
- pair/package/matchup은 confidence와 sample threshold를 통과한 항목만 노출한다.
- ranker_logs는 battlecollect 집계치를 승격시키는 source가 아니라, explanation/evidence 검증층으로만 유지한다.
- low sample hero는 winRate 대신 confidence-discounted score만 사용한다.
- final score에서 compiled pattern 가중치 총합은 baseline meta/hard/syn 영향보다 작게 유지한다.
