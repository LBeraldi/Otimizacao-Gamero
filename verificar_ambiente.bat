@echo off
REM Script de verificação de ambiente - SwOPy & Sewer Optimizer
REM Execute este arquivo para verificar se tudo está configurado corretamente

echo.
echo ============================================
echo  Verificacao de Ambiente - SwOPy/Optimizer
echo ============================================
echo.

REM Verificar Python
echo [1/3] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Python NAO encontrado!
    echo.
    echo   Passos para resolver:
    echo   1. Acesse: https://www.python.org/downloads/
    echo   2. Baixe e instale Python 3.11+
    echo   3. IMPORTANTE: Marque "Add Python to PATH"
    echo   4. Reabra este prompt e execute novamente
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo   ✓ %%i encontrado
)
echo.

REM Verificar arquivos necessarios
echo [2/3] Verificando arquivos...
if not exist "sample_network.csv" (
    echo   ⚠ sample_network.csv nao encontrado
) else (
    echo   ✓ sample_network.csv encontrado
)

if not exist "sample_config.json" (
    echo   ⚠ sample_config.json nao encontrado
) else (
    echo   ✓ sample_config.json encontrado
)

if not exist "sewer_optimizer.py" (
    echo   ❌ sewer_optimizer.py nao encontrado!
) else (
    echo   ✓ sewer_optimizer.py encontrado
)
echo.

REM Testar execucao
echo [3/3] Testando execucao basica...
python sewer_optimizer.py --help >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Erro ao executar sewer_optimizer.py
    echo.
    echo   Tente rodar manualmente:
    echo   python sewer_optimizer.py --help
    echo.
    pause
    exit /b 1
) else (
    echo   ✓ sewer_optimizer.py pode ser executado
)
echo.

echo ============================================
echo  ✅ TUDO OK! Seu ambiente esta pronto!
echo ============================================
echo.
echo Proximos passos:
echo   python sewer_optimizer.py --help
echo   python sewer_optimizer.py --generate-samples
echo   python sewer_optimizer.py --network sample_network.csv --config sample_config.json
echo.
pause
