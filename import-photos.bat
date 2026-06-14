@echo off
chcp 65001 >nul
rem ============================================================
rem  Drag image files or a folder onto this icon to analyze them.
rem  (Builds/updates your gallery from your OWN photos.)
rem  Or run from a terminal:  import-photos.bat photo1.jpg folder ...
rem ============================================================
cd /d "%~dp0"

set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

if "%~1"=="" (
  echo Drag image files or a folder onto this .bat icon.
  echo Status will be shown in Chinese.
  echo.
  pause
  exit /b
)

"%PY%" run.py --import %* --open

echo.
pause
