@echo off
REM EQIX SG4-4A Figure 13 F-N Curves - Windows launcher
cd /d "%~dp0"
python generate_figure13.py
if errorlevel 1 (
    py generate_figure13.py
)
pause
