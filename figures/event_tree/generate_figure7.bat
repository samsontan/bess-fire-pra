@echo off
REM EQIX SG4-4A Figure 7 Event Tree - Windows launcher
cd /d "%~dp0"
python generate_figure7.py
if errorlevel 1 (
    py generate_figure7.py
)
pause
