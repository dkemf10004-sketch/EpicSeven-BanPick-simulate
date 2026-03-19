"""
embed_overlay.py
────────────────
compiled_runtime_overlay.json 을 밴픽_최종_v2_merged.html 에 인라인으로 삽입합니다.
이 스크립트를 실행하면 로컬 서버 없이 HTML 파일을 더블클릭으로 열어도
overlay(상대 대응 점수)가 정상 동작합니다.

사용법:
  두 파일(html, json)과 같은 폴더에서 실행
  $ python embed_overlay.py
"""

import json
import re
import os

HTML_FILE = '밴픽_최종_v2_merged.html'
JSON_FILE = 'compiled_runtime_overlay.json'

PLACEHOLDER = r'window\.__COMPILED_RUNTIME_OVERLAY__\s*=\s*null;\s*/\* 여기에 JSON 붙여넣기 \*/'

def main():
    if not os.path.exists(HTML_FILE):
        print(f'❌ {HTML_FILE} 파일을 찾을 수 없습니다.')
        return
    if not os.path.exists(JSON_FILE):
        print(f'❌ {JSON_FILE} 파일을 찾을 수 없습니다.')
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        overlay_data = json.load(f)

    # heroes, meta 키 존재 여부 확인
    if 'heroes' not in overlay_data or 'meta' not in overlay_data:
        print(f'❌ {JSON_FILE} 형식이 올바르지 않습니다 (heroes/meta 키 없음).')
        return

    hero_count = len(overlay_data.get('heroes', {}))
    print(f'✅ overlay JSON 로드 완료 — 영웅 {hero_count}명')

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    if not re.search(PLACEHOLDER, html):
        print('❌ HTML 파일에 임베드 슬롯이 없습니다.')
        print('   수정된 밴픽_최종_v2_merged.html 파일을 사용하고 있는지 확인하세요.')
        return

    json_str = json.dumps(overlay_data, ensure_ascii=False, separators=(',', ':'))
    replacement = f'window.__COMPILED_RUNTIME_OVERLAY__ = {json_str}; /* 여기에 JSON 붙여넣기 */'

    html_out = re.sub(PLACEHOLDER, replacement, html)

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_out)

    size_kb = len(html_out.encode('utf-8')) / 1024
    print(f'✅ 임베드 완료 — {HTML_FILE} ({size_kb:.0f} KB)')
    print('   이제 HTML 파일을 더블클릭으로 열어도 overlay가 동작합니다.')

if __name__ == '__main__':
    main()
