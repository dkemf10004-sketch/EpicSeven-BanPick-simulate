# Overlay Validation Report

## Top1-10 HeroIds

1. 기원의 라스 (ORIGIN_RAS) | pick 30.73
2. 조장 아룬카 (ARUNKA) | pick 30.05
3. 보건교사 율하 (YULHA) | pick 29.20
4. 빛의 루엘 (RUEL) | pick 24.04
5. 프리렌 (FRIEREN) | pick 22.69
6. 어둠의 목자 디에네 (DARK_DIEANE) | pick 22.16
7. 리나크 (RINAK) | pick 21.13
8. 창공의 일리나브 (SKY_ILLYNAV) | pick 19.44
9. 벨리안 (BELIAN) | pick 18.52
10. 쾌속의 기수 세크레트 (SECRET) | pick 17.65

## Top1-10 Quality Summary

### 기원의 라스 (ORIGIN_RAS)
- counts: helpsWith 12 / goodVs 12 / badVs 12
- A/B/C: helpsWith 4/8/0 | goodVs 12/0/0 | badVs 12/0/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - none

### 조장 아룬카 (ARUNKA)
- counts: helpsWith 12 / goodVs 12 / badVs 12
- A/B/C: helpsWith 7/5/0 | goodVs 12/0/0 | badVs 12/0/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - goodVs 바다의 유령 폴리티스 (SCENT_POLITIS) | source legendHard | grade A | confidence 0.7473 | sampleCount 245

### 보건교사 율하 (YULHA)
- counts: helpsWith 12 / goodVs 12 / badVs 13
- A/B/C: helpsWith 7/5/0 | goodVs 12/0/0 | badVs 12/1/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - none

### 빛의 루엘 (RUEL)
- counts: helpsWith 12 / goodVs 12 / badVs 17
- A/B/C: helpsWith 6/6/0 | goodVs 12/0/0 | badVs 12/5/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - none

### 프리렌 (FRIEREN)
- counts: helpsWith 12 / goodVs 13 / badVs 16
- A/B/C: helpsWith 6/6/0 | goodVs 12/1/0 | badVs 12/4/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - none

### 어둠의 목자 디에네 (DARK_DIEANE)
- counts: helpsWith 12 / goodVs 16 / badVs 14
- A/B/C: helpsWith 6/6/0 | goodVs 13/3/0 | badVs 12/2/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - none

### 리나크 (RINAK)
- counts: helpsWith 12 / goodVs 13 / badVs 13
- A/B/C: helpsWith 9/3/0 | goodVs 13/0/0 | badVs 12/1/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - goodVs 죄악의 안젤리카 (EXT_죄악의_안젤리카) | source legendHard | grade A | confidence 0.4319 | sampleCount 46

### 창공의 일리나브 (SKY_ILLYNAV)
- counts: helpsWith 12 / goodVs 18 / badVs 12
- A/B/C: helpsWith 7/5/0 | goodVs 12/6/0 | badVs 12/0/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - goodVs 디에네 (EXT_디에네) | source legendHard | grade A | confidence 0.3998 | sampleCount 52

### 벨리안 (BELIAN)
- counts: helpsWith 12 / goodVs 16 / badVs 14
- A/B/C: helpsWith 3/9/0 | goodVs 12/4/0 | badVs 12/2/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - goodVs 잔영의 비올레토 (EXT_잔영의_비올레토) | source legendHard | grade A | confidence 0.3596 | sampleCount 28

### 쾌속의 기수 세크레트 (SECRET)
- counts: helpsWith 12 / goodVs 16 / badVs 14
- A/B/C: helpsWith 5/7/0 | goodVs 13/3/0 | badVs 12/2/0
- fallback count: total 0 | helpsWith 0 / goodVs 0 / badVs 0
- added counter anchors
  - goodVs 자하크 (EXT_자하크) | source legendHard | grade A | confidence 0.3596 | sampleCount 28

## Top10 Counter Coverage Audit

- unevaluated pair count: 0

### 기원의 라스 (ORIGIN_RAS)
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 조장 아룬카 (ARUNKA)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 보건교사 율하 (YULHA)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: badVs | confidence: 0.7081
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: badVs | confidence: 0.6808
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 빛의 루엘 (RUEL)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: badVs | confidence: 0.6942
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: badVs | confidence: 0.6991
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: badVs | confidence: 0.7160
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6676
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: badVs | confidence: 0.6798
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: badVs | confidence: 0.6780
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 프리렌 (FRIEREN)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.6942
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: badVs | confidence: 0.6976
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6826
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: badVs | confidence: 0.6993
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: badVs | confidence: 0.6796
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 어둠의 목자 디에네 (DARK_DIEANE)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; goodVs:inverse legendHard:legendHard; badVs:direct legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; badVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: goodVs | confidence: 0.7081
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.6991
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.6976
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6236
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: goodVs | confidence: 0.7031
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: badVs | confidence: 0.6709
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 리나크 (RINAK)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.7160
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6896
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: goodVs | confidence: 0.7800
  source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: badVs | confidence: 0.7077
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 창공의 일리나브 (SKY_ILLYNAV)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.6676
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.6826
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: goodVs | confidence: 0.6236
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: goodVs | confidence: 0.6896
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: goodVs | confidence: 0.6514
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: goodVs | confidence: 0.6820
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 벨리안 (BELIAN)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: goodVs | confidence: 0.6808
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.6798
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.6993
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: badVs | confidence: 0.7031
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6514
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 쾌속의 기수 세크레트 (SECRET) | evaluated: yes | result: goodVs | confidence: 0.6783
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### 쾌속의 기수 세크레트 (SECRET)
- 기원의 라스 (ORIGIN_RAS) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 조장 아룬카 (ARUNKA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 보건교사 율하 (YULHA) | evaluated: yes | result: badVs | confidence: 0.7800
  source list: badVs:final:legendHard; badVs:direct legendHard:legendHard; badVs:observed matchup edge:strongMatchupEdge; badVs:existing overlay edge:top10ExistingOverlay; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 빛의 루엘 (RUEL) | evaluated: yes | result: goodVs | confidence: 0.6780
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 프리렌 (FRIEREN) | evaluated: yes | result: goodVs | confidence: 0.6796
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 어둠의 목자 디에네 (DARK_DIEANE) | evaluated: yes | result: goodVs | confidence: 0.6709
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 리나크 (RINAK) | evaluated: yes | result: goodVs | confidence: 0.7077
  source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 창공의 일리나브 (SKY_ILLYNAV) | evaluated: yes | result: badVs | confidence: 0.6820
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a
- 벨리안 (BELIAN) | evaluated: yes | result: badVs | confidence: 0.6783
  source list: badVs:final:top10WeakCounterHint; badVs:compiled patterns weak counter hint:top10WeakCounterHint
  why none if none: n/a

### Spotlight: 벨리안 (BELIAN) vs 프리렌 (FRIEREN)
- evaluated: yes
- result: goodVs
- source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
- confidence: 0.6993
- why none if none: n/a

### Spotlight: 리나크 (RINAK) vs 프리렌 (FRIEREN)
- evaluated: yes
- result: goodVs
- source list: goodVs:final:legendHard; goodVs:inverse legendHard:legendHard; goodVs:observed matchup edge:strongMatchupEdge; goodVs:reciprocal observed relation:reciprocalObservedBadVs; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
- confidence: 0.7800
- why none if none: n/a

### Spotlight: 벨리안 (BELIAN) vs 빛의 루엘 (RUEL)
- evaluated: yes
- result: goodVs
- source list: goodVs:final:top10WeakCounterHint; goodVs:compiled patterns weak counter hint:top10WeakCounterHint
- confidence: 0.6798
- why none if none: n/a

## Regression

- Opp Board: [RUEL, FRIEREN]

### 벨리안 (BELIAN)
- goodVs anchor snapshot
  - 아키 (AKI) | source legendHard | grade A | confidence 0.4823 | sampleCount 142
  - 라스트 라이더 크라우 (LRK) | source legendHard | grade A | confidence 0.4840 | sampleCount 112
  - 후미르 (HUMIR) | source legendHard | grade A | confidence 0.4092 | sampleCount 80
  - 뒤틀린 망령 카일론 (TWISTED_KAYRON) | source legendHard | grade A | confidence 0.4074 | sampleCount 73
  - 프리다 (EXT_프리다) | source legendHard | grade A | confidence 0.3896 | sampleCount 38
- badVs anchor snapshot
  - 조장 아룬카 (ARUNKA) | source legendHard | grade A | confidence 0.7800 | sampleCount 437
  - 기원의 라스 (ORIGIN_RAS) | source legendHard | grade A | confidence 0.7800 | sampleCount 437
  - 리나크 (RINAK) | source legendHard | grade A | confidence 0.7800 | sampleCount 437
  - 신월의 루나 (MOON_LUNA) | source strongMatchupEdge | grade A | confidence 0.4456 | sampleCount 593
  - 란 (RAN) | source strongMatchupEdge | grade A | confidence 0.2400 | sampleCount 480
- goodVs board dump
  - 빛의 루엘 (RUEL) | source top10WeakCounterHint | grade B | confidence 0.6798 | sampleCount 336 | weighted 0.2447
  - 프리렌 (FRIEREN) | source top10WeakCounterHint | grade B | confidence 0.6993 | sampleCount 459 | weighted 0.2517
- badVs board dump
  - none
- reciprocal positive source dump
  - 빛의 루엘 (RUEL) | source top10WeakCounterHint | grade B | confidence 0.6798 | sampleCount 336 | weighted 0.2447
  - 프리렌 (FRIEREN) | source top10WeakCounterHint | grade B | confidence 0.6993 | sampleCount 459 | weighted 0.2517
- reciprocal negative source dump
  - none
- final counter: 3.7313
- why zero if zero: n/a

### 리나크 (RINAK)
- goodVs anchor snapshot
  - 설화 (SEOLHWA) | source legendHard | grade A | confidence 0.7800 | sampleCount 691
  - 어둠의 목자 디에네 (DARK_DIEANE) | source legendHard | grade A | confidence 0.7800 | sampleCount 798
  - 프리렌 (FRIEREN) | source legendHard | grade A | confidence 0.7800 | sampleCount 703
  - 벨리안 (BELIAN) | source legendHard | grade A | confidence 0.7800 | sampleCount 437
  - 바다의 유령 폴리티스 (SCENT_POLITIS) | source legendHard | grade A | confidence 0.7473 | sampleCount 245
- badVs anchor snapshot
  - 조장 아룬카 (ARUNKA) | source legendHard | grade A | confidence 0.7800 | sampleCount 866
  - 기원의 라스 (ORIGIN_RAS) | source legendHard | grade A | confidence 0.7800 | sampleCount 866
  - 보건교사 율하 (YULHA) | source legendHard | grade A | confidence 0.7800 | sampleCount 866
  - 쾌속의 기수 세크레트 (SECRET) | source top10WeakCounterHint | grade A | confidence 0.7077 | sampleCount 525
  - 스트라제스 (STRAZE) | source strongMatchupEdge | grade A | confidence 0.2400 | sampleCount 918
- goodVs board dump
  - 빛의 루엘 (RUEL) | source top10WeakCounterHint | grade A | confidence 0.7160 | sampleCount 629 | weighted 0.2578
  - 프리렌 (FRIEREN) | source legendHard | grade A | confidence 0.7800 | sampleCount 703 | weighted 0.5704
- badVs board dump
  - none
- reciprocal positive source dump
  - 빛의 루엘 (RUEL) | source top10WeakCounterHint | grade A | confidence 0.7160 | sampleCount 629 | weighted 0.2578
  - 프리렌 (FRIEREN) | source legendHard | grade A | confidence 0.7800 | sampleCount 703 | weighted 0.5704
- reciprocal negative source dump
  - none
- final counter: 5.8000
- why zero if zero: n/a

### 프리렌 (FRIEREN)
- goodVs anchor snapshot
  - 보건교사 율하 (YULHA) | source legendHard | grade A | confidence 0.7800 | sampleCount 865
  - 축제의 에다 (FESTIVAL_EDA) | source legendHard | grade A | confidence 0.6459 | sampleCount 383
  - 전승의 아미키 (AMIKI) | source legendHard | grade A | confidence 0.5075 | sampleCount 271
  - 라스트 라이더 크라우 (LRK) | source legendHard | grade A | confidence 0.4840 | sampleCount 112
  - 어린 셰나 (BABY_SHENNA) | source legendHard | grade A | confidence 0.4488 | sampleCount 181
- badVs anchor snapshot
  - 조장 아룬카 (ARUNKA) | source legendHard | grade A | confidence 0.7800 | sampleCount 703
  - 기원의 라스 (ORIGIN_RAS) | source legendHard | grade A | confidence 0.7800 | sampleCount 703
  - 리나크 (RINAK) | source legendHard | grade A | confidence 0.7800 | sampleCount 703
  - 방관자 화영 (HWAYOUNG) | source strongMatchupEdge | grade A | confidence 0.5381 | sampleCount 1045
  - 셀린 (CELINE) | source strongMatchupEdge | grade A | confidence 0.2400 | sampleCount 770
- final counter: 1.8599
- why zero if zero: n/a

### 설화 (SEOLHWA)
- goodVs anchor snapshot
  - 설계자 라이카 (EXT_설계자_라이카) | source legendHard | grade A | confidence 0.4303 | sampleCount 45
  - 하솔 (EXT_하솔) | source legendHard | grade A | confidence 0.4133 | sampleCount 37
  - 사자왕 체르미아 (LIONHEART_CERMIA) | source legendHard | grade A | confidence 0.4836 | sampleCount 267
  - 비브리스 (EXT_비브리스) | source legendHard | grade A | confidence 0.3769 | sampleCount 31
  - 어둠의 목자 디에네 (DARK_DIEANE) | source strongMatchupEdge | grade A | confidence 0.6200 | sampleCount 1050
- badVs anchor snapshot
  - 조장 아룬카 (ARUNKA) | source legendHard | grade A | confidence 0.7800 | sampleCount 691
  - 기원의 라스 (ORIGIN_RAS) | source legendHard | grade A | confidence 0.7800 | sampleCount 691
  - 리나크 (RINAK) | source legendHard | grade A | confidence 0.7800 | sampleCount 691
  - 방관자 화영 (HWAYOUNG) | source strongMatchupEdge | grade A | confidence 0.5381 | sampleCount 886
  - 축제의 에다 (FESTIVAL_EDA) | source strongMatchupEdge | grade A | confidence 0.4199 | sampleCount 770
- final counter: 0.0000
- why zero if zero: no direct or reciprocal counter relation matched the board

### 지오 (GIO)
- goodVs anchor snapshot
  - 폴리티스 (BASE_POLITIS) | source legendHard | grade A | confidence 0.4760 | sampleCount 110
  - 엘비라 (ELVIRA) | source legendHard | grade A | confidence 0.4614 | sampleCount 90
  - 바캉스 유피네 (VACATION_YUFINE) | source legendHard | grade A | confidence 0.4360 | sampleCount 50
  - 자애의 로만 (EXT_자애의_로만) | source legendHard | grade A | confidence 0.4158 | sampleCount 38
  - 미지의 가능성 아카테스 (MYTH_ACHATES) | source legendHard | grade A | confidence 0.4280 | sampleCount 113
- badVs anchor snapshot
  - 어둠의 목자 디에네 (DARK_DIEANE) | source legendHard | grade A | confidence 0.7460 | sampleCount 294
  - 빛의 루엘 (RUEL) | source legendHard | grade A | confidence 0.7460 | sampleCount 294
  - 보건교사 율하 (YULHA) | source legendHard | grade A | confidence 0.7460 | sampleCount 294
  - 호반의 마녀 테네브리아 (TENEBRIA) | source strongMatchupEdge | grade A | confidence 0.5242 | sampleCount 380
  - 란 (RAN) | source strongMatchupEdge | grade A | confidence 0.2441 | sampleCount 393
- final counter: -3.0000
- why zero if zero: n/a
