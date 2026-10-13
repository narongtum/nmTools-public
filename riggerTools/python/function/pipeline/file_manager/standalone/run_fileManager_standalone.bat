@echo off
setlocal
title File Manager Standalone

:: Switch to the directory where this script is located
cd /d "%~dp0"

:: 1. Detect Python executable
set "PYTHON_EXE="

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
)

if not defined PYTHON_EXE (
    echo [ERROR] Python was not found in PATH or at %LOCALAPPDATA%\Programs\Python\Python310\python.exe
    pause
    exit /b 1
)

:: 2. Ensure riggerTools/python is in PYTHONPATH
set "RIGGER_TOOLS_PY=%~dp0..\..\..\..\"
set "PYTHONPATH=%RIGGER_TOOLS_PY%;%PYTHONPATH%"

:: 3. Launch File Manager Standalone
echo Starting File Manager Standalone...
"%PYTHON_EXE%" "%~dp0run_ui_standalone.py" %*

:: 4. If application crashes or returns error, keep console open for inspection
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] File Manager exited with error code %ERRORLEVEL%.
    pause
)
