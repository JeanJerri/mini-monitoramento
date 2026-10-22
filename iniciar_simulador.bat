@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   INICIANDO SIMULADOR DE ROTEADOR SNMP (PORTAS 161 / 1161)
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" simulador_roteador.py
) else (
    py -3.13 simulador_roteador.py
)

pause
