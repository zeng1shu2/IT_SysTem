@echo off
chcp 65001 >nul 2>&1
setlocal
set "SCRIPT=%~dp0manage.ps1"
if "%~1"=="" (set "ARG=status") else (set "ARG=%~1")
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" %ARG%
if "%ARG%"=="status" (
  echo.
  pause
) else (
  echo.
  pause
)
endlocal
