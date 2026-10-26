@echo off
cd /d "%~dp0"
python "Unturned_Control_Center_PRO.py"
if errorlevel 1 (echo Erro ao iniciar. Confira se o Python esta instalado. & pause)
