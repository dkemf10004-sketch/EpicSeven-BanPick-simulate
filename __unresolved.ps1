function Normalize-Key([string]$text){ if($null -eq $text){ return '' }; ($text.Trim() -replace '[\s''"·,&\-\./()]+','').ToUpperInvariant() }
$html = Get-Content -Raw -Encoding UTF8 'e7_banpick_simulator_rebalanced.html'
$nameMap = @{}
[regex]::Matches($html, "\{id:'([^']+)',\s*name:'([^']+)'") | ForEach-Object { $nameMap[(Normalize-Key $_.Groups[2].Value)] = $_.Groups[1].Value }
$aliasPairs = @(@('별의엘레나','STAR_ELENA'),@('별의신탁엘레나','STAR_ELENA'),@('풍기위원아리아','PUNISH_PUNISH_ARIA'),@('보검의주인이세리아','ISEPUNISH_ARIA'),@('잿빛숲의이세리아','ASHEN_ISERIA'),@('바다의향기폴리티스','GHOST_POLITIS'),@('바다의유령폴리티스','GHOST_POLITIS'),@('폴리티스','GHOST_POLITIS'),@('율하','YULHA'),@('보건교사율하','YULHA'),@('어린세나','BABY_SHENNA'),@('하르테시','HARSETI'))
foreach($pair in $aliasPairs){ $nameMap[(Normalize-Key $pair[0])] = $pair[1] }
function Resolve-HeroId([string]$name){ $key = Normalize-Key $name; if($nameMap.ContainsKey($key)){ return $nameMap[$key] }; return $null }
function Split-HeroTokens([string]$text){ if([string]::IsNullOrWhiteSpace($text)){ return @() }; [regex]::Split($text, '\s*/\s*|\s*,\s*') | Where-Object { $_ } }
$counts=@{}
Get-Content -Encoding UTF8 'data/ranker_logs.md' | ForEach-Object {
  if($_ -match '^\s*-\s*(내 팀|상대)\s*:\s*(.*)$'){
    foreach($tok in Split-HeroTokens $matches[2]){
      $name = $tok.Trim(); if($name -match '^(.*?)\('){ $name = $matches[1].Trim() }
      if(-not (Resolve-HeroId $name)){
        $counts[$name] = 1 + $(if($counts.ContainsKey($name)){$counts[$name]}else{0})
      }
    }
  }
}
$counts.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object { "{0}`t{1}" -f $_.Key,$_.Value }
