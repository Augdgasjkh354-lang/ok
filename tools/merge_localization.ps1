# 《卡拉迪亚：烽烟与暗流》汉化合并工具（Windows PowerShell 5.1 及以上，无需 Python）
# 规则与 merge_localization.py 相同：只新增条目、只更新本 Mod 自有条目，
# 不删除、不改写玩家原有的汉化；首次合并前的原文件保存为 *.csv.bak。
param(
    [Parameter(Position = 0)][string]$ModulePath,
    [Parameter(Position = 1)][string]$Lang
)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ownedPrefixes = @('menu_af', 'mno_af', 'trp_af', 'pt_af', 'menu_fb', 'mno_fb', 'trp_fb', 'pt_fb', ('qstr_' + [char]0xE6))
$strictUtf8 = New-Object System.Text.UTF8Encoding($false, $true)
$bomUtf8 = New-Object System.Text.UTF8Encoding($true)

function Fail([string]$msg) {
    Write-Host ''
    Write-Host "失败：$msg" -ForegroundColor Red
    Write-Host '没有修改任何文件。'
    exit 1
}

function Read-Utf8([string]$path) {
    $bytes = [System.IO.File]::ReadAllBytes($path)
    try { $text = $strictUtf8.GetString($bytes) }
    catch { Fail "$path 不是 UTF-8 编码（可能是 GBK），为避免损坏原汉化已停止。" }
    if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) { $text = $text.Substring(1) }
    return $text
}

function Parse-Csv([string]$text) {
    $order = New-Object 'System.Collections.Generic.List[string]'
    $map = New-Object 'System.Collections.Generic.Dictionary[string,string]' ([System.StringComparer]::Ordinal)
    foreach ($line in ($text -split "`r?`n")) {
        $i = $line.IndexOf('|')
        if ($i -lt 0) { continue }
        $key = $line.Substring(0, $i).TrimStart([char]0xFEFF)
        $value = $line.Substring($i + 1)
        if (-not $map.ContainsKey($key)) { $order.Add($key) }
        $map[$key] = $value
    }
    return @{ Order = $order; Map = $map }
}

function Is-Owned([string]$key) {
    foreach ($p in $ownedPrefixes) { if ($key.StartsWith($p, [System.StringComparison]::Ordinal)) { return $true } }
    return $false
}

Write-Host '《烽烟与暗流》汉化合并工具'
Write-Host '-----------------------------'
if (-not $ModulePath) {
    Write-Host '请把游戏的 Modules\TestMod 文件夹拖进这个窗口（或输入完整路径），然后按回车：'
    $ModulePath = Read-Host
}
$ModulePath = $ModulePath.Trim().Trim('"').TrimEnd('\', '/')
if (-not $ModulePath -or -not (Test-Path -LiteralPath (Join-Path $ModulePath 'module.ini') -PathType Leaf)) {
    Fail "“$ModulePath” 里没有 module.ini，不像模组文件夹。请拖入 Modules\TestMod 这一层。"
}

$langRoot = Join-Path $ModulePath 'languages'
if (-not $Lang) {
    if ((Test-Path -LiteralPath (Join-Path $langRoot 'cn_s')) -and -not (Test-Path -LiteralPath (Join-Path $langRoot 'cns'))) { $Lang = 'cn_s' } else { $Lang = 'cns' }
}
if ($Lang -ne 'cns' -and $Lang -ne 'cn_s') { Fail "语言只能是 cns 或 cn_s，收到：$Lang" }

$source = $null
foreach ($cand in @((Join-Path $here $Lang), (Join-Path (Join-Path (Split-Path -Parent $here) 'localization') $Lang))) {
    if ((Test-Path -LiteralPath $cand -PathType Container) -and (Get-ChildItem -LiteralPath $cand -Filter '*.csv')) { $source = $cand; break }
}
if (-not $source) { Fail "找不到 $Lang 的汉化源文件，请确认没有把本工具从解压出来的文件夹里单独拿出来。" }

$target = Join-Path $langRoot $Lang
Write-Host "模组：$ModulePath"
Write-Host "语言目录：languages\$Lang"
Write-Host ''

# 先全部读取、校验并算出结果；任何文件有问题都在写入前停止。
$plans = @()
foreach ($incoming in (Get-ChildItem -LiteralPath $source -Filter '*.csv' | Sort-Object Name)) {
    $name = $incoming.Name -replace '\.merge\.csv$', '.csv'
    $dest = Join-Path $target $name
    if (-not (Test-Path -LiteralPath $dest -PathType Leaf)) {
        # 模组里原本没有的文件一律不新建：只含少量条目的新文件会挡住游戏自带的中文。
        Write-Host "${name}: 模组里原本没有此文件，跳过（新建会挡住游戏自带的中文）"
        continue
    }
    $old = Parse-Csv (Read-Utf8 $dest)
    $new = Parse-Csv (Read-Utf8 $incoming.FullName)
    $inserted = 0; $updated = 0
    foreach ($key in $new.Order) {
        if (-not $old.Map.ContainsKey($key)) {
            $old.Order.Add($key); $old.Map[$key] = $new.Map[$key]; $inserted++
        } elseif ((Is-Owned $key) -and $old.Map[$key] -cne $new.Map[$key]) {
            $old.Map[$key] = $new.Map[$key]; $updated++
        }
    }
    # 游戏会把每个语言 CSV 的第一行当表头跳过（官方文件以空行开头），必须保留这个空行。
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append("`r`n")
    foreach ($key in $old.Order) { [void]$sb.Append($key).Append('|').Append($old.Map[$key]).Append("`r`n") }
    $plans += , @($dest, $sb.ToString(), $inserted, $updated, $old.Order.Count)
}

foreach ($plan in $plans) {
    $dest = $plan[0]
    $backup = $dest + '.bak'
    if ((Test-Path -LiteralPath $dest) -and -not (Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $dest -Destination $backup }
    [System.IO.File]::WriteAllText($dest, $plan[1], $bomUtf8)
    Write-Host ("{0}: 新增 {1} 条，更新 {2} 条，共 {3} 条" -f (Split-Path -Leaf $dest), $plan[2], $plan[3], $plan[4])
}
Write-Host ''
Write-Host '完成。原文件在首次合并前的版本已保存为 *.csv.bak，重复运行不会覆盖它。' -ForegroundColor Green
