@echo off
chcp 65001 >nul
title Dashboard de Tarefas - Iniciar

echo ========================================
echo   Dashboard de Tarefas - Python
echo   Script de Inicialização
echo ========================================
echo.

:: Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo Por favor, instale o Python 3.8+ e tente novamente.
    echo.
    pause
    exit /b 1
)

:: Verificar se o dashboard já está rodando
echo Verificando se o dashboard já está rodando...
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" | find "python.exe" >nul
if %errorlevel% equ 0 (
    echo [AVISO] Dashboard já está rodando!
    echo.
    choice /c SN /m "Deseja iniciar uma nova instância? (S/N)"
    if %errorlevel% equ 2 (
        echo Cancelado pelo usuário.
        pause
        exit /b 0
    )
)

:: Verificar se estamos no diretório correto
if not exist "main.py" (
    echo [ERRO] Arquivo main.py não encontrado!
    echo Certifique-se de executar este script no diretório do dashboard.
    echo.
    pause
    exit /b 1
)

:: Verificar dependências
echo Verificando dependências...
if not exist "requirements.txt" (
    echo [AVISO] Arquivo requirements.txt não encontrado!
    echo As dependências podem não estar instaladas.
) else (
    echo Instalando/atualizando dependências...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [AVISO] Erro ao instalar dependências. Continuando...
    )
)

:: Criar diretórios necessários
echo Criando diretórios necessários...
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "database" mkdir database

:: Iniciar o dashboard
echo.
echo Iniciando Dashboard de Tarefas...
echo.
echo Pressione Ctrl+C para parar o dashboard.
echo.

:: Iniciar em uma nova janela
start "Dashboard de Tarefas" python main.py

if %errorlevel% equ 0 (
    echo [SUCESSO] Dashboard iniciado com sucesso!
    echo.
    echo O dashboard está rodando em uma nova janela.
    echo Você pode fechar esta janela.
) else (
    echo [ERRO] Erro ao iniciar o dashboard!
    echo.
    echo Verifique se:
    echo - Python está instalado corretamente
    echo - Todas as dependências estão instaladas
    echo - O arquivo main.py existe e está correto
)

echo.
pause 