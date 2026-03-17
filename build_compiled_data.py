import argparse, itertools, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DEF_RULES=ROOT/'data'/'hero_rules22.md'
DEF_LOGS=ROOT/'data'/'ranker_logs.md'
DEF_LEGEND=ROOT/'밴픽 시뮬'/'밴픽 시뮬'/'epic7_hero_record_output'/'hero_full_legend.json'
DEF_BC=ROOT/'밴픽 시뮬'/'밴픽 시뮬'/'battlecollect_shouldrun'/'battle_accounts_merged.json'
DEF_HTML=ROOT/'밴픽 시뮬'/'밴픽 시뮬'/'밴픽 최종 v2_merged.html'
DEF_HEROES=ROOT/'compiled_heroes.json'
DEF_PATTERNS=ROOT/'compiled_patterns.json'
DEF_REPORT=ROOT/'compiled_drift_report.md'

def rt(p): return Path(p).read_text(encoding='utf-8-sig')
def rj(p): return json.loads(rt(p))
def nk(v): return re.sub(r'[^0-9a-z가-힣]+','',str(v or '').strip().lower())
def gid(name):
    s=re.sub(r'[^0-9A-Z가-힣]+','_',str(name or '').strip().upper()).strip('_')
    return f'EXT_{s}' if s else 'EXT_UNKNOWN'
def pair(a,b): return '|'.join(sorted([a,b]))
def combo(ids): return '|'.join(sorted(set(i for i in ids if i)))
def weak(w,l,cap=1.0,scale=60):
    t=w+l
    if t<=0: return 0.0
    c=min(1.0, math.log1p(t)/math.log1p(scale))
    e=(w-l)/t
    return round(max(-cap,min(cap,e*c*cap)),4)
def pct(s):
    m=re.search(r'(-?\d+(?:\.\d+)?)%', str(s or ''))
    return float(m.group(1)) if m else None
def split_heroes(raw):
    raw=str(raw or '').strip()
    if not raw: return []
    parts=raw.split(' / ') if ' / ' in raw else [x.strip() for x in re.split(r'\s*,\s*', raw) if x.strip()]
    out=[]
    for p in parts:
        n=re.sub(r'\([^)]*\)','',p).strip()
        if n: out.append(n)
    return out

def extract(text, marker, open_char, close_char):
    s=text.index(marker)+len(marker); depth=1; i=s
    while i<len(text):
        ch=text[i]
        if ch==open_char: depth+=1
        elif ch==close_char:
            depth-=1
            if depth==0: return text[s:i]
        i+=1
    raise ValueError(marker)

def html_data(path):
    text=rt(path)
    hb=extract(text,'const HEROES = [','[',']')
    hp=re.compile(r"\{id:'(?P<id>[^']+)',\s*name:'(?P<name>[^']+)',\s*pick:(?P<pick>-?\d+(?:\.\d+)?),\s*win:(?P<win>-?\d+(?:\.\d+)?),\s*ban:(?P<ban>-?\d+(?:\.\d+)?)(?P<rest>[^}]*)\}")
    heroes={}
    for m in hp.finditer(hb):
        rest=m.group('rest')
        arr=lambda key: re.findall(r"'([^']+)'", (re.search(fr"{key}:\[([^\]]*)\]", rest) or [None,''])[1] if re.search(fr"{key}:\[([^\]]*)\]", rest) else '')
        note=(re.search(r"note:'([^']*)'", rest) or [None,''])[1] if re.search(r"note:'([^']*)'", rest) else ''
        heroes[m.group('id')]={'id':m.group('id'),'name':m.group('name'),'pick':float(m.group('pick')),'win':float(m.group('win')),'ban':float(m.group('ban')),'hard':arr('hard'),'syn':arr('syn'),'tags':arr('tags'),'note':note}
    alias_raw=extract(text,'const HERO_ID_ALIASES = {','{','}')
    aliases={a:b for a,b in re.findall(r"([A-Z0-9_가-힣]+):'([^']+)'", alias_raw)}
    fto=re.findall(r"'([^']+)'", extract(text,'const FIRST_TURN_OPENERS = [','[',']'))
    return {'text':text,'heroes':heroes,'aliases':aliases,'first_turn_openers':fto}

def rules_data(path):
    text=rt(path); aliases={}; profiles={}; meta_table={}; cur=None; sub=''
    for line in text.splitlines():
        s=line.strip()
        if s.startswith('|') and not s.startswith('|---') and '??' not in s:
            cols=[c.strip() for c in s.strip('|').split('|')]
            if len(cols)>=4:
                meta_table[cols[0]]={'pick':pct(cols[1]),'win':pct(cols[2]),'ban':pct(cols[3])}
        if s.startswith('- '):
            body=s[2:]
            if ' -> ' in body:
                a,b=[x.strip() for x in body.split(' -> ',1)]; aliases[a]=b
            elif ' = ' in body and '???' not in body and '?? ??' not in body:
                a,b=[x.strip() for x in body.split(' = ',1)]; aliases[a]=b
        if line.startswith('### '):
            cur=line[4:].strip(); profiles[cur]={'name':cur,'meta_win':None,'hard':[],'syn':[],'tags':set(),'personal':[],'raw':[]}; sub=''; continue
        if not cur: continue
        if line.startswith('#### '): sub=line[5:].strip(); continue
        if not s: continue
        profiles[cur]['raw'].append(s)
        if sub=='?? ???': profiles[cur]['personal'].append(s)
        if '??? ??:' in s: profiles[cur]['meta_win']=pct(s)
        if '???? ??? ??:' in s: profiles[cur]['hard']+=split_heroes(s.split(':',1)[1])
        if '?? ??? ??:' in s or '???:' in s: profiles[cur]['syn']+=split_heroes(s.split(':',1)[1])
        if '????' in s: profiles[cur]['tags']|={'first_turn','speed_contest'}
        if '???? ???? ?? ????' in s: profiles[cur]['tags']|={'first_turn','first_turn_vanguard_only'}
        if '??' in s or '?? ??' in s: profiles[cur]['tags'].add('followup')
        if '????' in s and ('???' in s or '????' in s): profiles[cur]['tags'].add('harseti_sensitive')
    return {'text':text,'aliases':aliases,'profiles':profiles,'meta_table':meta_table}

def bucket(line):
    if '1위' in line: return 'rank1'
    if any(x in line for x in ['2위','3위','4위','5위']): return 'rank2_5'
    if any(x in line for x in ['6위','7위','8위','9위','10위']): return 'rank6_10'
    return 'legend_avg'

class Resolver:
    def __init__(self, html, legend, md_aliases, html_aliases):
        self.by_norm={}; self.redirect={}; self.seen=defaultdict(set); self.html=html
        for h in html.values(): self.reg(h['id'], h['name'])
        for row in legend:
            name=str(row.get('hero_name') or row.get('hero_code') or '').strip(); code=str(row.get('hero_code') or '').strip()
            if not name and not code: continue
            found=self.by_norm.get(nk(name)) or self.by_norm.get(nk(code))
            hid=found[0] if found else gid(name or code); hname=found[1] if found else (name or code)
            self.reg(hid,hname)
            if code: self.redirect[nk(code)]=hname
        for aid,tid in html_aliases.items():
            if tid in html: self.redirect[nk(aid)]=html[tid]['name']
        for a,t in md_aliases.items(): self.redirect[nk(a)]=t
    def reg(self,hid,name):
        if hid and name:
            self.by_norm.setdefault(nk(hid),(hid,name)); self.by_norm.setdefault(nk(name),(hid,name))
    def resolve(self, raw):
        raw=str(raw or '').strip()
        if not raw: return ('','')
        key=nk(raw); red=self.redirect.get(key)
        if red: raw=red; key=nk(raw)
        hid,name=self.by_norm.get(key,(gid(raw),raw))
        self.reg(hid,name); self.seen[hid].add(str(raw).strip())
        return hid,name

def logs_data(path,res):
    text=rt(path); buck='rank1'; battles=[]; cur=None
    def flush():
        nonlocal cur
        if not cur or not cur['my_team'] or not cur['enemy_team']: cur=None; return
        my=[res.resolve(x)[0] for x in reversed(cur['my_team'])]
        en=[res.resolve(x)[0] for x in cur['enemy_team']]
        battles.append({'bucket':cur['bucket'],'source':'ranker_logs','result':cur['result'],'my_order':my,'enemy_order':en,'my_prebans':[res.resolve(x)[0] for x in cur['my_prebans']],'enemy_prebans':[res.resolve(x)[0] for x in cur['enemy_prebans']],'my_ban':res.resolve(cur['my_ban'])[0] if cur['my_ban'] else None,'enemy_ban':res.resolve(cur['enemy_ban'])[0] if cur['enemy_ban'] else None,'my_firstpick':cur['my_firstpick'],'first_pick_hero':res.resolve(cur['first_pick_name'])[0] if cur['first_pick_name'] else None})
        cur=None
    for raw in text.splitlines():
        s=raw.strip()
        if not s: continue
        if s.startswith('## '): flush(); buck=bucket(s); continue
        m=re.match(r'^\d+\.\s*(승리|패배)', s)
        if m:
            flush(); cur={'bucket':buck,'result':m.group(1),'my_team':[],'enemy_team':[],'my_prebans':[],'enemy_prebans':[],'my_ban':None,'enemy_ban':None,'my_firstpick':None,'first_pick_name':None}; continue
        if not cur: continue
        if '내 팀:' in s:
            body=s.split('내 팀:',1)[1]; cur['my_team']=split_heroes(body)
            for tok in body.split(' / '):
                nm=re.sub(r'\([^)]*\)','',tok).strip(); fl=re.search(r'\(([^)]*)\)',tok)
                if fl and '선픽' in fl.group(1): cur['my_firstpick']=True; cur['first_pick_name']=nm
            continue
        if '상대:' in s:
            body=s.split('상대:',1)[1]; cur['enemy_team']=split_heroes(body)
            for tok in body.split(' / '):
                nm=re.sub(r'\([^)]*\)','',tok).strip(); fl=re.search(r'\(([^)]*)\)',tok)
                if fl and '선픽' in fl.group(1): cur['my_firstpick']=False; cur['first_pick_name']=nm
            continue
        if '프리밴:' in s:
            body=s.split('프리밴:',1)[1]
            if ' vs ' in body:
                a,b=body.split(' vs ',1); cur['my_prebans']=split_heroes(a); cur['enemy_prebans']=split_heroes(b)
            continue
        if '최종 밴:' in s:
            body=s.split('최종 밴:',1)[1]; m1=re.search(r'내 밴\s*([^/]+)',body); m2=re.search(r'상대 밴\s*([^/]+)',body)
            if m1: cur['my_ban']=m1.group(1).strip()
            if m2: cur['enemy_ban']=m2.group(1).strip()
    flush(); return {'text':text,'battles':battles}

def bc_data(path,res):
    data=rj(path); battles=[]
    for acc in data:
        for b in acc.get('battles',[]):
            my=[res.resolve(x)[0] for x in b.get('my_team',{}).get('pick_codes',[])]
            en=[res.resolve(x)[0] for x in b.get('enemy_team',{}).get('pick_codes',[])]
            if not my or not en: continue
            battles.append({'bucket':'battlecollect_general','source':'battlecollect','result':str(b.get('result','')).strip(),'my_order':my,'enemy_order':en,'my_prebans':[res.resolve(x)[0] for x in b.get('my_team',{}).get('preban_codes',[])],'enemy_prebans':[res.resolve(x)[0] for x in b.get('enemy_team',{}).get('preban_codes',[])],'my_ban':res.resolve(b.get('my_team',{}).get('ban_code'))[0] if b.get('my_team',{}).get('ban_code') else None,'enemy_ban':res.resolve(b.get('enemy_team',{}).get('ban_code'))[0] if b.get('enemy_team',{}).get('ban_code') else None,'my_firstpick':bool(b.get('my_firstpick')),'first_pick_hero':(my[0] if b.get('my_firstpick') else en[0])})
    return {'battles':battles}

def compile_heroes(html,rules,legend,res,logs,bcs):
    profiles=rules['profiles']; meta_table=rules.get('meta_table',{}); htmlh=html['heroes']; legend_by={}; md_by={}; md_meta_by={}; log_only=set()
    for row in legend:
        hid,_=res.resolve(row.get('hero_name') or row.get('hero_code'))
        if hid: legend_by[hid]=row; res.seen[hid]|={str(row.get('hero_name') or '').strip(), str(row.get('hero_code') or '').strip()}
    for p in profiles.values():
        hid,_=res.resolve(p['name'])
        if hid: md_by[hid]=p
    for name,meta in meta_table.items():
        hid,_=res.resolve(name)
        if hid: md_meta_by[hid]=meta
    for b in itertools.chain(logs,bcs):
        for hid in itertools.chain(b['my_order'],b['enemy_order'],b['my_prebans'],b['enemy_prebans']):
            if hid and hid not in htmlh and hid not in legend_by and hid not in md_by and hid not in md_meta_by: log_only.add(hid)
    out={}
    for hid in sorted(set(htmlh)|set(legend_by)|set(md_by)|set(md_meta_by)|log_only):
        hh=htmlh.get(hid); lg=legend_by.get(hid); md=md_by.get(hid); mm=md_meta_by.get(hid)
        name=(hh['name'] if hh else '') or str(lg.get('hero_name') if lg else '') or (md['name'] if md else '') or res.resolve(hid)[1]
        if not name: continue
        pick=(float(mm.get('pick')) if mm and mm.get('pick') is not None else (float(lg.get('table_pick_rate')) if lg and lg.get('table_pick_rate') is not None else (hh['pick'] if hh else 0.0)))
        win=(float(mm.get('win')) if mm and mm.get('win') is not None else (float(lg.get('table_win_rate')) if lg and lg.get('table_win_rate') is not None else ((hh['win'] if hh else 0.0) or (md['meta_win'] if md and md['meta_win'] else 0.0))))
        ban=(float(mm.get('ban')) if mm and mm.get('ban') is not None else (float(lg.get('table_ban_rate')) if lg and lg.get('table_ban_rate') is not None else (hh['ban'] if hh else 0.0)))
        hard=[]; syn=[]
        if hh: hard+=hh['hard']; syn+=hh['syn']
        if lg: hard+=lg.get('list_hard_heroes') or []; syn+=lg.get('list_with_heroes') or []
        if md: hard+=md['hard']; syn+=md['syn']
        tags=set(hh['tags'] if hh else [])
        if md: tags|=md['tags']
        if hid in html['first_turn_openers']: tags|={'first_turn','speed_contest'}
        flags={'from_md':hid in md_by or hid in md_meta_by,'from_legend_json':hid in legend_by,'from_logs_only':hid in log_only}
        cov={'meta':bool(pick or win or ban),'relations':bool(hard or syn),'tags':bool(tags),'memo':bool(md and md['personal'])}
        sc=0.25*flags['from_md']+0.45*flags['from_legend_json']+0.15*flags['from_logs_only']+0.15*bool(hh and (hh['pick']>0.05 or hh['win']!=50 or hh['ban']>0.05))
        conf=round(min(1.0,0.2+sc+0.15*cov['meta']+0.1*cov['relations']+0.05*cov['tags']),3)
        aliases=sorted(a for a in res.seen.get(hid,set()) if a and nk(a) not in {nk(hid),nk(name)})
        out[hid]={'id':hid,'name':name,'aliases':aliases,'meta':{'pick':round(pick,2),'win':round(win,2),'ban':round(ban,2)},'hard':sorted(set(res.resolve(x)[0] for x in hard if x)),'syn':sorted(set(res.resolve(x)[0] for x in syn if x)),'tags':{'first_turn':'first_turn' in tags,'speed_contest':'speed_contest' in tags or 'first_turn' in tags,'first_turn_vanguard_only':'first_turn_vanguard_only' in tags,'followup':'followup' in tags,'harseti_sensitive':'harseti_sensitive' in tags},'source_flags':flags,'confidence':conf,'coverage':cov,'memo':{'personal':md['personal'] if md else []}}
    return {'generated_from':{'hero_rules_md':str(DEF_RULES),'hero_legend_json':str(DEF_LEGEND),'ranker_logs_md':str(DEF_LOGS),'battlecollect_json':str(DEF_BC),'current_html_runtime':str(DEF_HTML)},'aliases':{a:res.resolve(t)[0] for a,t in rules['aliases'].items()},'heroes':out}

def inc(store,key,buck,field):
    ent=store.setdefault(key,{'by_bucket':defaultdict(Counter),'totals':Counter()})
    ent['by_bucket'][buck][field]+=1; ent['totals'][field]+=1

def fin_pair(store, cap=1.0, scale=60, min_samples=3, min_abs=0.0):
    out={}
    for k,v in store.items():
        w=v['totals'].get('wins',0); l=v['totals'].get('losses',0); s=w+l
        if s<min_samples: continue
        bb={}
        for buck,c in v['by_bucket'].items():
            bw=c.get('wins',0); bl=c.get('losses',0); bs=bw+bl
            if bs>0: bb[buck]={'wins':bw,'losses':bl,'score':weak(bw,bl,cap,scale),'samples':bs}
        score=weak(w,l,cap,scale)
        if abs(score)<min_abs: continue
        out[k]={'score':score,'wins':w,'losses':l,'samples':s,'by_bucket':bb}
    return out

def fin_count(store):
    out={}; total=sum(v['totals'].get('count',0) for v in store.values()) or 1
    for k,v in store.items():
        c=v['totals'].get('count',0)
        if c<=0: continue
        out[k]={'count':c,'share':round(c/total,6),'by_bucket':{b:{'count':bc.get('count',0)} for b,bc in v['by_bucket'].items() if bc.get('count',0)>0}}
    return out

def compile_patterns(logs,bcs):
    pair_s={}; pkg_s={}; ctr_s={}; fp_s={}; vg_s={}; pre_s={}; ban_s={}
    for b in itertools.chain(logs,bcs):
        buck=b['bucket']; win=b['my_order'] if b['result']=='승리' else b['enemy_order']; lose=b['enemy_order'] if b['result']=='승리' else b['my_order']
        for p in itertools.combinations(sorted(set(win)),2): inc(pair_s,pair(*p),buck,'wins')
        for p in itertools.combinations(sorted(set(lose)),2): inc(pair_s,pair(*p),buck,'losses')
        for size in (3,4):
            for c in itertools.combinations(sorted(set(win)),size): inc(pkg_s,combo(c),buck,'wins')
            for c in itertools.combinations(sorted(set(lose)),size): inc(pkg_s,combo(c),buck,'losses')
        for a in set(win):
            for d in set(lose): inc(ctr_s,f'{a}|{d}',buck,'wins')
        for order in (b['my_order'], b['enemy_order']):
            if order: inc(fp_s,order[0],buck,'count')
            if len(order)>=3: inc(vg_s,order[2],buck,'count')
        for hid in set(b['my_prebans']+b['enemy_prebans']): inc(pre_s,hid,buck,'count')
        for hid in filter(None,[b['my_ban'],b['enemy_ban']]): inc(ban_s,hid,buck,'count')
    raw_ctr=fin_pair(ctr_s,0.95,90,5,0.06); weak_ctr={}
    for k,v in raw_ctr.items():
        a,b=k.split('|',1); rev=raw_ctr.get(f'{b}|{a}')
        if rev and rev['samples']>v['samples'] and abs(rev['score'])>=abs(v['score']): continue
        weak_ctr[k]=v
    return {'generated_from':{'ranker_logs_md':str(DEF_LOGS),'battlecollect_json':str(DEF_BC)},'rank_bucket_weights':{'rank1':{'weight':0.35,'special':True,'note':'특수 장비/주도권 패턴 소스'},'rank2_5':{'weight':1.0,'special':False,'note':'상위권 핵심 패턴'},'rank6_10':{'weight':0.92,'special':False,'note':'상위권 일반화 가능 패턴'},'legend_avg':{'weight':0.8,'special':False,'note':'일반 평균 검증 로그'},'battlecollect_general':{'weight':0.78,'special':False,'note':'대량 표본 기반 약한 보정'}},'pair_synergy':fin_pair(pair_s,1.05,90,4,0.05),'package_synergy':fin_pair(pkg_s,0.9,70,6,0.08),'first_pick_tendency':fin_count(fp_s),'vanguard_tendency':fin_count(vg_s),'preban_pressure':fin_count(pre_s),'final_ban_pressure':fin_count(ban_s),'weak_counter_hints':weak_ctr}

def report(comp_h, comp_p, html, rules, legend):
    htmlh=html['heroes']; heroes=comp_h['heroes']; profiles=rules['profiles']
    md_missing=[]
    for p in profiles.values():
        if not p['tags']: continue
        n=nk(p['name']); hh=next((h for h in htmlh.values() if nk(h['name'])==n), None); ch=next((h for h in heroes.values() if nk(h['name'])==n), None)
        if not ch: md_missing.append(f"{p['name']}: HTML/compiled hero 없음, md tags={sorted(p['tags'])}"); continue
        ht=set(hh['tags'] if hh else []); miss=sorted(t for t in p['tags'] if t not in ht and not ch['tags'].get(t,False))
        if miss: md_missing.append(f"{p['name']}: 누락 tags={miss}")
    dup=defaultdict(list)
    for h in htmlh.values(): dup[nk(h['name'])].append(h['id'])
    alias_need=[]
    for ids in dup.values():
        if len(ids)>=2: alias_need.append(f"{htmlh[ids[0]]['name']}: entity ids={ids}")
    for a,t in rules['aliases'].items():
        ha=next((h for h in htmlh.values() if nk(h['name'])==nk(a)),None); ht=next((h for h in htmlh.values() if nk(h['name'])==nk(t)),None)
        if ha and ht and ha['id']!=ht['id']: alias_need.append(f"{a} -> {t}: HTML ids={ha['id']},{ht['id']}")
    lmap={nk(str(r.get('hero_name') or r.get('hero_code') or '')):r for r in legend}; conflicts=[]
    for name,meta in rules.get('meta_table',{}).items():
        if meta.get('win') is None: continue
        lg=lmap.get(nk(name))
        if lg and abs(float(lg.get('table_win_rate') or 0)-meta['win'])>=0.7: conflicts.append(f"{name}: md22 win={meta['win']:.2f}, legend win={float(lg.get('table_win_rate') or 0):.2f}")
    patterns=[]
    if comp_p['preban_pressure']: patterns.append('battlecollect/log 기반 preban pressure map')
    if comp_p['final_ban_pressure']: patterns.append('final-ban pressure 집계')
    if comp_p['first_pick_tendency']: patterns.append('rank bucket별 first-pick tendency')
    if comp_p['vanguard_tendency']: patterns.append('rank bucket별 vanguard tendency')
    if comp_p['package_synergy']: patterns.append('발견형 package synergy lookup')
    drift=[]
    if 'oppPrebanSkipEnabled' in html['text']: drift.append('HTML에는 상대 프리밴 스킵 편의 기능이 있어 동시 프리밴 규칙과 완전히 일치하지 않음')
    md_ft={hid for hid,h in heroes.items() if h['tags']['first_turn']}; missing_ft=sorted(md_ft-set(html['first_turn_openers']))
    if missing_ft: drift.append(f"HTML FIRST_TURN_OPENERS 누락: {missing_ft[:12]}")
    bad=sorted(set(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', html['text']))-set(htmlh)-set(html['aliases']))
    bad=[x for x in bad if x not in {'UTF','DOCTYPE','ASCII','JSON','WS','URL'} and not x.startswith(('HERO','FIRST','RAW','LOG','OPEN','COMMON','CLEAN','ALIAS','PACKAGES','KNOWN','WS','EXT_'))][:20]
    if bad: drift.append(f"HTML 내부 패턴 상수에 HEROES 없는 id 참조 존재: {bad}")
    lines=['# Drift Report','','## Baseline Source Audit',f'- rules source of truth: `{DEF_RULES}`','- 현재 HTML baseline hero source는 `const HEROES`이며, 이후 `KNOWN_KOREAN_HERO_NAMES`를 `ensureHeroExists()`로 대량 확장하는 구조입니다.','- HTML의 pattern source는 `RAW_PACKAGES`, `NUANCED_COUNTERS`, `LOG_ROLE_CONFIDENCE_STATS`, `HIGHROLLER_TURN_ONE` 같은 하드코딩 상수입니다.','- hero_full_legend와 battlecollect는 현재 런타임 보정층이지만, baseline/pattern의 단일 source of truth는 아직 아닙니다.','','## md에는 있는데 html 태그에 없는 영웅/태그']
    lines += [f'- {x}' for x in md_missing[:40]] or ['- 없음']
    lines += ['','## html에는 entity로 존재하지만 alias여야 하는 중복 영웅']
    lines += [f'- {x}' for x in alias_need[:40]] or ['- 없음']
    lines += ['','## hero legend json과 md meta 수치가 충돌하는 영웅']
    lines += [f'- {x}' for x in conflicts[:40]] or ['- 없음']
    lines += ['','## battlecollect에서 추출 가능하지만 현재 html이 거의 활용하지 못하는 패턴']
    lines += [f'- {x}' for x in patterns[:20]] or ['- 없음']
    lines += ['','## 프리밴/밴가드/선턴 규칙 불일치']
    lines += [f'- {x}' for x in drift[:20]] or ['- 없음']
    lines += ['','## 최소 연결 계획','- `const HEROES`, `HERO_ID_ALIASES`, `KNOWN_KOREAN_HERO_NAMES` 기반 bootstrap을 `compiled_heroes.json` 로더로 교체한다.','- `RAW_PACKAGES`, `NUANCED_COUNTERS`, `LOG_ROLE_CONFIDENCE_STATS`, `HIGHROLLER_TURN_ONE`, battlecollect 런타임 집계를 `compiled_patterns.json` 로더로 교체한다.','- 유지할 함수: `buildStages`, `actualPrebans`, `getVanguard`, `buildSelectionContext`, `canSelectWithContext`, `syncStageIndexFromBoard`.','- 축소/삭제 후보: `ensureHeroExists`의 placeholder 확장, `KNOWN_KOREAN_HERO_NAMES` 전체 주입, HTML 하드코딩 패턴 상수군.','- lookup 전환 대상: `normalizeHeroId`, `canonicalHeroNameById`, `getHeroSynIds`, `getHeroHardIds`, `createRecommendationContext`, `scoreHero`, `computeRecommendations`, `computeSynergyPanels`.','- 이번 단계에서 건드리지 말아야 할 부분: 수동 입력 UX, 프리밴 dedupe 규칙, 밴가드 최종밴 제외 규칙, websocket 입력 흐름, UI 레이아웃.']
    return '\n'.join(lines)+'\n'

def wj(p,data): Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--hero-rules',type=Path,default=DEF_RULES); ap.add_argument('--ranker-logs',type=Path,default=DEF_LOGS); ap.add_argument('--hero-legend',type=Path,default=DEF_LEGEND); ap.add_argument('--battlecollect',type=Path,default=DEF_BC); ap.add_argument('--html',type=Path,default=DEF_HTML); ap.add_argument('--compiled-heroes',type=Path,default=DEF_HEROES); ap.add_argument('--compiled-patterns',type=Path,default=DEF_PATTERNS); ap.add_argument('--drift-report',type=Path,default=DEF_REPORT); a=ap.parse_args()
    rules=rules_data(a.hero_rules); legend=rj(a.hero_legend); html=html_data(a.html); res=Resolver(html['heroes'],legend,rules['aliases'],html['aliases']); logs=logs_data(a.ranker_logs,res); bcs=bc_data(a.battlecollect,res)
    comp_h=compile_heroes(html,rules,legend,res,logs['battles'],bcs['battles']); comp_p=compile_patterns(logs['battles'],bcs['battles']); rep=report(comp_h,comp_p,html,rules,legend)
    wj(a.compiled_heroes,comp_h); wj(a.compiled_patterns,comp_p); Path(a.drift_report).write_text(rep,encoding='utf-8')
    print(f'compiled heroes: {a.compiled_heroes}'); print(f'compiled patterns: {a.compiled_patterns}'); print(f'drift report: {a.drift_report}')

if __name__=='__main__': main()



