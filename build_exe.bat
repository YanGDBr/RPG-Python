@echo off
setlocal

if not exist .venv\Scripts\python.exe (
    echo Criando ambiente virtual...
    python -m venv .venv
)

echo Instalando dependencias de build (jogo + PyInstaller)...
.venv\Scripts\python.exe -m pip install --upgrade pip >nul
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
if errorlevel 1 goto :erro

echo.
echo Compilando RPG_Habusken.exe (isso demora um pouco)...
.venv\Scripts\pyinstaller.exe --onefile --console --name RPG_Habusken --distpath dist --workpath build --specpath . main.py
if errorlevel 1 goto :erro

echo.
echo Pronto! O executavel esta em dist\RPG_Habusken.exe
echo Ele roda sozinho em qualquer PC Windows, sem precisar instalar Python.
pause
goto :fim

:erro
echo.
echo Alguma coisa deu errado durante o build. Veja a mensagem acima.
pause

:fim
