@echo off
chcp 65001 >nul
rem ============================================================
rem  MuseDigest one-click launcher (heuristic backend)
rem  No GPU, no login. Double-click to: collect -> build gallery
rem  -> open it in your browser. The script prints status in Chinese.
rem  Advanced: append args, e.g.   start.bat --limit 20
rem ============================================================
cd /d "%~dp0"

set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" run.py --open %*

echo.
pause
