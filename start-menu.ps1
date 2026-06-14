param([string]$Choice = "")

# 让控制台用 UTF-8，正确显示中文
try { chcp 65001 > $null } catch {}
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $here "..\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$interactive = -not $PSBoundParameters.ContainsKey('Choice')

function Show-Menu {
    Write-Host ""
    Write-Host "========= MuseDigest · 妙析速递 =========" -ForegroundColor Cyan
    Write-Host "  1. 一键采集生成图库（heuristic，无需 GPU / 登录）"
    Write-Host "  2. ArtiMuse 在线评分（需登录，含雷达图）"
    Write-Host "  3. 仅登录 ArtiMuse（保存会话）"
    Write-Host "  4. ArtiMuse 连接自检（打印抓到的分数+维度）"
    Write-Host "  5. 导入本地图片/文件夹分析" -ForegroundColor Green
    Write-Host "  6. 打开上次生成的图库"
    Write-Host "  7. 清空图库（重新开始）"
    Write-Host "  0. 退出"
    Write-Host "========================================="
    Write-Host ""
}

if (-not $Choice) {
    Show-Menu
    $Choice = Read-Host "请输入序号并回车"
}

switch ($Choice) {
    "1" { & $py (Join-Path $here "run.py") --open }
    "2" { & $py (Join-Path $here "run.py") --backend artimuse_browser --open }
    "3" { & $py (Join-Path $here "tools\artimuse_login.py") }
    "4" { & $py (Join-Path $here "tools\artimuse_selftest.py") }
    "5" {
        $p = Read-Host "请输入图片或文件夹的完整路径（可直接把文件拖进来）"
        $p = $p.Trim().Trim('"')
        if ($p) { & $py (Join-Path $here "run.py") --import $p --open }
        else { Write-Host "未输入路径。" -ForegroundColor Yellow }
    }
    "6" {
        $g = Join-Path $here "data\gallery\index.html"
        if (Test-Path $g) { Start-Process $g }
        else { Write-Host "还没有生成过图库，请先选 1 / 5。" -ForegroundColor Yellow }
    }
    "7" { & $py (Join-Path $here "run.py") --clear }
    "0" { return }
    default { Write-Host "无效的选择：$Choice" -ForegroundColor Yellow }
}

if ($interactive) {
    Write-Host ""
    Read-Host "完成。按 Enter 关闭窗口"
}


