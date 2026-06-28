@echo off
chcp 65001 >nul
rem ============================================================
rem  MuseDigest iOS gallery launcher
rem  Renders the existing library into a mobile/iOS-optimized,
rem  self-contained gallery and opens it. No GPU, no re-analysis.
rem
rem    start-ios.bat            build + open in browser
rem    start-ios.bat --serve   also start a LAN server so an iPhone
rem                            on the same WiFi can open it in Safari
rem ============================================================
cd /d "%~dp0"

set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" build_ios_gallery.py --open %*

echo.
pause
