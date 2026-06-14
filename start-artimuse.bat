@echo off
chcp 65001 >nul
rem ============================================================
rem  MuseDigest one-click launcher (ArtiMuse ONLINE backend)
rem  Double-click: if not logged in, the system Edge opens the demo
rem  for you to sign in to intern-ai.org.cn; then each image is scored
rem  and a gallery (with radar charts) opens. Status printed in Chinese.
rem
rem  First time only, install playwright (Edge is used, no download):
rem      ..\.venv\Scripts\python.exe -m pip install playwright
rem ============================================================
cd /d "%~dp0"

set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" run.py --backend artimuse_browser --open %*

echo.
pause
