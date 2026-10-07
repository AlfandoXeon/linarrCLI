@echo off
setlocal
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
if exist "%VENV_PYTHON%" goto check_rich

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv "%~dp0.venv"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo PYTHON 3.10 OR NEWER WAS NOT FOUND. INSTALL PYTHON AND TRY AGAIN.
        pause
        exit /b 1
    )
    python -m venv "%~dp0.venv"
)
if errorlevel 1 (
    echo FAILED TO CREATE THE PROJECT VIRTUAL ENVIRONMENT.
    pause
    exit /b 1
)

:check_rich
"%VENV_PYTHON%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo PYTHON 3.10 OR NEWER IS REQUIRED. UPDATE PYTHON AND TRY AGAIN.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo INSTALLING THE REQUIRED RICH DEPENDENCY...
    "%VENV_PYTHON%" -m pip install rich
    if errorlevel 1 (
        echo FAILED TO INSTALL RICH. CHECK YOUR INTERNET CONNECTION.
        pause
        exit /b 1
    )
)

set "PYTHONPATH=%~dp0src"
"%VENV_PYTHON%" -m pemrograman_linear_solution
set "APP_EXIT_CODE=%ERRORLEVEL%"

if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo THE APPLICATION EXITED WITH AN ERROR.
    pause
)
exit /b %APP_EXIT_CODE%
