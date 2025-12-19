@echo off
echo Stopping any running Python processes...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *app.py*" 2>nul

timeout /t 2 /nobreak >nul

echo.
echo Starting Camera Feed Monitor...
echo.

cd /d "%~dp0"

set ENV_NAME=teleops_prompter
set PYTHON_EXE=q:\Software\Miniconda\envs\%ENV_NAME%\python.exe

%PYTHON_EXE% app.py

pause

