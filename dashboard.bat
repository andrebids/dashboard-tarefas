@echo off
echo ========================================
echo    Dashboard de Tarefas - Python
echo    Inicializador Unificado
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando se o Dashboard ja esta rodando...
tasklist /fi "IMAGENAME eq py.exe" /fi "WINDOWTITLE eq Dashboard*" | find "py.exe" >nul
if %errorlevel% equ 0 (
    echo Dashboard ja esta rodando!
    echo Abrindo interface...
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b 0
)

echo Dashboard nao esta rodando.
echo.

echo Verificando se Python esta instalado...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8+ de: https://python.org
    echo.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Verificando dependencias...
if not exist "requirements.txt" (
    echo ERRO: Arquivo requirements.txt nao encontrado!
    pause
    exit /b 1
)

echo Instalando dependencias...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo Iniciando Dashboard...
echo.

py iniciar_dashboard.py

echo.
echo Dashboard finalizado.
pause 