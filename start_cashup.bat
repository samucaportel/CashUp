@echo off
setlocal
cd /d "%~dp0"

echo Starting CashUp Integration...
echo -----------------------------------------------

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Verifique se o Python esta instalado e no PATH.
    pause
    exit /b %errorlevel%
)

:: Executa a aplicacao
python run.py

if %errorlevel% neq 0 (
    echo [ERRO] A aplicacao parou subitamente (erro: %errorlevel%).
    pause
)

endlocal
