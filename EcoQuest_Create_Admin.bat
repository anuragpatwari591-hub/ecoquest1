@echo off
rem Creates your own administrator (or teacher) account. Start EcoQuest first.
cd /d "%~dp0"
python create_admin.py
echo.
pause
