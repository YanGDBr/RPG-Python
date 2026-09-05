@echo off
setlocal

if not exist .venv\Scripts\python.exe (
    echo Primeira vez rodando: criando ambiente e instalando dependencias...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip >nul
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

.venv\Scripts\python.exe main.py
pause
