function Normalize-Key([string]$text){ if($null -eq $text){ return '' }; ($text.Trim() -replace '[\s''"·,&\-\./()]+','').ToUpperInvariant() }
function Split-HeroTokens([string]$text){
  $items = New-Object System.Collections.Generic.List[string]
  if([string]::IsNullOrWhiteSpace($text)){ return @() }
  $sb = New-Object System.Text.StringBuilder
  $depth = 0
  foreach($ch in $text.ToCharArray()){
    if($ch -eq '('){ $depth++ }
    elseif($ch -eq ')' -and $depth -gt 0){ $depth-- }
    if(($ch -eq ',' -or $ch -eq '/') -and $depth -eq 0){
      $token = $sb.ToString().Trim(); if($token){ [void]$items.Add($token) }; [void]$sb.Clear(); continue
    }
    [void]$sb.Append($ch)
  }
  $tail = $sb.ToString().Trim(); if($tail){ [void]$items.Add($tail) }
  return @($items)
}
$html = Get-Content -Raw -Encoding UTF8 'e7_banpick_simulator_rebalanced.html'
$nameMap = @{}
[regex]::Matches($html, "\{id:'([^']+)',\s*name:'([^']+)'") | ForEach-Object { $nameMap[(Normalize-Key $_.Groups[2].Value)] = $_.Groups[1].Value }
$aliasPairs = @(
  @('별의엘레나','STAR_ELENA'), @('별의신탁엘레나','STAR_ELENA'), @('풍기위원아리아','PUNISH_PUNISH_ARIA'), @('풍기위원아리아','PUNISH_PUNISH_ARIA'),
  @('보검의주인이세리아','ISEPUNISH_ARIA'), @('잿빛숲의이세리아','ASHEN_ISERIA'), @('바다의향기폴리티스','GHOST_POLITIS'), @('바다의유령폴리티스','GHOST_POLITIS'),
  @('폴리티스','GHOST_POLITIS'), @('율하','YULHA'), @('보건교사율하','YULHA'), @('어린세나','BABY_SHENNA'), @('하르테시','HARSETI'),
  @('루엘','RUEL'), @('빛의루엘','RUEL'), @('설계자라이카','DESIGNER_LILIKA'), @('집행관빌트레드','JUDGE_VILDRED'), @('어둠의코르부스','DARK_CORVUS'),
  @('라이아','LILIAS_ALT'), @('디자이너디리벳','DESIGNER_DILIBET'), @('최강모델루루카','MODEL_LULUCA'), @('월광아라민타','SILVER_ARAMINTA'),
  @('여름방학샬롯','SUMMER_CHARLOTTE'), @('여름방학샬롯','SUMMER_CHARLOTTE'), @('뒤틀린망령의카일론','TWISTED_KAYRON')
)
foreach($pair in $aliasPairs){ $nameMap[(Normalize-Key $pair[0])] = $pair[1] }
function Resolve-HeroId([string]$name){ $key = Normalize-Key $name; if($nameMap.ContainsKey($key)){ return $nameMap[$key] }; return $null }
function Parse-HeroToken([string]$token){
  $trim = $token.Trim(); $name = $trim; $tags = @();
  if($trim -match '^(.*?)\(([^)]*)\)\s*$'){ $name = $matches[1].Trim(); $tags = $matches[2].Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ } }
  [pscustomobject]@{ Name=$name; Id=(Resolve-HeroId $name); Tags=$tags }
}
function Team-Order($heroes, [bool]$isMySide){ $ids = @($heroes | ForEach-Object { $_.Id } | Where-Object { $_ }); if($isMySide){ [array]::Reverse($ids) }; return $ids }
$lines = Get-Content -Encoding UTF8 'data/ranker_logs.md'
$games = @(); $currentRank=''; $current=$null
foreach($line in $lines){
  if($line -match '^##\s+(\d+)\)'){ $currentRank = $matches[1]; continue }
  if($line -match '^\s*(\d+)\.\s*(승리|패배)'){ if($current){ $games += [pscustomobject]$current }; $current=@{Rank=$currentRank; Result=$matches[2]; My=''; Opp=''; Final=''}; continue }
  if(-not $current){ continue }
  if($line -match '^\s*-\s*내 팀\s*:\s*(.*)$'){ $current.My = $matches[1]; continue }
  if($line -match '^\s*-\s*상대\s*:\s*(.*)$'){ $current.Opp = $matches[1]; continue }
  if($line -match '^\s*-\s*최종 밴\s*:\s*(.*)$'){ $current.Final = $matches[1]; continue }
}
if($current){ $games += [pscustomobject]$current }
$first=@{}; $early=@{}; $vanguard=@{}; $ban=@{}; $pairAll=@{}; $pairWin=@{}
function Ensure-Role([hashtable]$map, [string]$id){ if(-not $map.ContainsKey($id)){ $map[$id]=[pscustomobject]@{w=0;l=0;sources=@{};winsBySource=@{}} } }
function Add-Role([hashtable]$map, [string]$id, [string]$rank, [bool]$won){ if(-not $id){ return }; Ensure-Role $map $id; if($won){ $map[$id].w += 1; $cur=0; if($map[$id].winsBySource.ContainsKey($rank)){ $cur=$map[$id].winsBySource[$rank] }; $map[$id].winsBySource[$rank]=$cur+1 } else { $map[$id].l += 1 }; $map[$id].sources[$rank]=1 }
function Add-Ban([hashtable]$map, [string]$id, [string]$rank){ if(-not $id){ return }; if(-not $map.ContainsKey($id)){ $map[$id]=[pscustomobject]@{c=0;sources=@{}} }; $map[$id].c += 1; $map[$id].sources[$rank]=1 }
function Add-Pairs([hashtable]$map, [string[]]$ids){ $unique = @($ids | Where-Object { $_ } | Select-Object -Unique); for($i=0;$i -lt $unique.Count;$i++){ for($j=$i+1;$j -lt $unique.Count;$j++){ $a=$unique[$i]; $b=$unique[$j]; if([string]::CompareOrdinal($a,$b) -gt 0){ $tmp=$a; $a=$b; $b=$tmp }; $key="$a|$b"; $cur=0; if($map.ContainsKey($key)){$cur=$map[$key]}; $map[$key]=$cur+1 } } }
$unresolved=@{}
foreach($g in $games){
  $myHeroes = @(Split-HeroTokens $g.My | ForEach-Object { Parse-HeroToken $_ })
  $oppHeroes = @(Split-HeroTokens $g.Opp | ForEach-Object { Parse-HeroToken $_ })
  foreach($h in @($myHeroes+$oppHeroes)){ if(-not $h.Id){ $unresolved[$h.Name]=1+$(if($unresolved.ContainsKey($h.Name)){$unresolved[$h.Name]}else{0}) } }
  $myOrder = @(Team-Order $myHeroes $true)
  $oppOrder = @(Team-Order $oppHeroes $false)
  $myWon = $g.Result -eq '승리'; $oppWon = -not $myWon
  if($myOrder.Count -ge 1){ Add-Role $first $myOrder[0] $g.Rank $myWon }
  if($oppOrder.Count -ge 1){ Add-Role $first $oppOrder[0] $g.Rank $oppWon }
  foreach($id in @($myOrder | Select-Object -First 2)){ Add-Role $early $id $g.Rank $myWon }
  foreach($id in @($oppOrder | Select-Object -First 2)){ Add-Role $early $id $g.Rank $oppWon }
  if($myOrder.Count -ge 3){ Add-Role $vanguard $myOrder[2] $g.Rank $myWon }
  if($oppOrder.Count -ge 3){ Add-Role $vanguard $oppOrder[2] $g.Rank $oppWon }
  $banned = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach($h in @($myHeroes + $oppHeroes)){ if($h.Id -and ($h.Tags | Where-Object { $_ -match '밴' -and $_ -notmatch '밴가드' })){ [void]$banned.Add($h.Id) } }
  if($g.Final){ foreach($m in [regex]::Matches($g.Final, '밴\s+([^/]+?)(?=\s*/|$)')){ $id = Resolve-HeroId $m.Groups[1].Value.Trim(); if($id){ [void]$banned.Add($id) } } }
  foreach($id in $banned){ Add-Ban $ban $id $g.Rank }
  $myIds = @($myHeroes | ForEach-Object { $_.Id } | Where-Object { $_ })
  $oppIds = @($oppHeroes | ForEach-Object { $_.Id } | Where-Object { $_ })
  Add-Pairs $pairAll $myIds; Add-Pairs $pairAll $oppIds
  if($myWon){ Add-Pairs $pairWin $myIds } else { Add-Pairs $pairWin $oppIds }
}
$result = [ordered]@{
  totalGames = $games.Count
  rank5Games = @($games | Where-Object { $_.Rank -eq '5' }).Count
  unresolved = @($unresolved.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object { [pscustomobject]@{name=$_.Key; c=$_.Value} })
  first = @($first.GetEnumerator() | ForEach-Object { [pscustomobject]@{id=$_.Key; w=$_.Value.w; l=$_.Value.l; s=$_.Value.sources.Count; m=($(if($_.Value.winsBySource.Count){[int](($_.Value.winsBySource.Values | Measure-Object -Maximum).Maximum)}else{0}))} } | Sort-Object { -($_.w - $_.l) }, { -($_.w + $_.l) })
  early = @($early.GetEnumerator() | ForEach-Object { [pscustomobject]@{id=$_.Key; w=$_.Value.w; l=$_.Value.l; s=$_.Value.sources.Count; m=($(if($_.Value.winsBySource.Count){[int](($_.Value.winsBySource.Values | Measure-Object -Maximum).Maximum)}else{0}))} } | Sort-Object { -($_.w - $_.l) }, { -($_.w + $_.l) })
  vanguard = @($vanguard.GetEnumerator() | ForEach-Object { [pscustomobject]@{id=$_.Key; w=$_.Value.w; l=$_.Value.l; s=$_.Value.sources.Count; m=($(if($_.Value.winsBySource.Count){[int](($_.Value.winsBySource.Values | Measure-Object -Maximum).Maximum)}else{0}))} } | Sort-Object { -($_.w - $_.l) }, { -($_.w + $_.l) })
  ban = @($ban.GetEnumerator() | ForEach-Object { [pscustomobject]@{id=$_.Key; c=$_.Value.c; s=$_.Value.sources.Count} } | Sort-Object { -($_.c) })
  pairAll = @($pairAll.GetEnumerator() | ForEach-Object { [pscustomobject]@{key=$_.Key; c=$_.Value} } | Sort-Object { -($_.c) })
  pairWin = @($pairWin.GetEnumerator() | ForEach-Object { [pscustomobject]@{key=$_.Key; c=$_.Value} } | Sort-Object { -($_.c) })
}
$result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 '__ranker_sync.json'
