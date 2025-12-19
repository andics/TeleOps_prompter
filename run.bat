@echo off

REM Change to the script's directory
cd /d "%~dp0"

echo ========================================
echo Camera Feed Monitor - AI Vision Filters
echo ========================================
echo.
echo Working directory: %CD%
echo.

set ENV_NAME=teleops_prompter
set PYTHON_EXE=q:\Software\Miniconda\envs\%ENV_NAME%\python.exe

REM Check if conda environment exists
echo Checking for conda environment '%ENV_NAME%'...
conda info --envs | findstr /C:"%ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Environment '%ENV_NAME%' not found. Creating it...
    conda create -n %ENV_NAME% python=3.10 -y
    if errorlevel 1 (
        echo Error creating conda environment!
        pause
        exit /b 1
    )
    echo.
) else (
    echo Environment '%ENV_NAME%' already exists.
    echo.
)

REM Activate conda environment
echo Activating conda environment '%ENV_NAME%'...
call conda activate %ENV_NAME%
if errorlevel 1 (
    echo Error activating conda environment!
    echo Make sure conda is properly installed and initialized.
    pause
    exit /b 1
)
echo.

REM Check if requirements are installed
echo Checking dependencies...
%PYTHON_EXE% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing dependencies!
        pause
        exit /b 1
    )
    echo.
) else (
    echo Dependencies already installed.
    echo.
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo ============================================
    echo WARNING: .env file not found!
    echo ============================================
    echo Please create a .env file with your OPENAI_API_KEY
    echo You can copy .env.example to .env and edit it.
    echo.
    echo Example:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
)

REM Run the application
echo Starting application...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo Using Python: %PYTHON_EXE%
echo.

%PYTHON_EXE% app.py

pause

