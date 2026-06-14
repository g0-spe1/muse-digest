@echo off
rem Double-click this to open the Chinese menu (PowerShell).
rem Uses -ExecutionPolicy Bypass so it runs even if PS scripts are restricted.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-menu.ps1"
