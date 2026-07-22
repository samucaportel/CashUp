@echo off
setlocal
cd /d "%~dp0"

echo Starting CashUp Integration...
echo -----------------------------------------------

:: Usa o Python do ambiente virtual (venv), nao o global do PATH
set "VENV_PY=%~dp0venv\Scripts\python.exe"

:: Verifica se o venv existe
if not exist "%VENV_PY%" (
    echo [ERRO] Ambiente virtual nao encontrado em:
    echo        %VENV_PY%
    echo.
    echo Crie e instale as dependencias com:
    echo        python -m venv venv
    echo        venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

:: Executa a aplicacao com o Python do venv
"%VENV_PY%" run.py

if %errorlevel% neq 0 (
    echo [ERRO] A aplicacao parou subitamente (erro: %errorlevel%).
    pause
)

endlocal
