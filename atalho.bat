@echo off
chcp 65001 >nul
title Dashboard de Tarefas - Atalho Inteligente

echo ========================================
echo   Dashboard de Tarefas - Python
echo   Atalho Inteligente
echo ========================================
echo.

:: Verificar se o dashboard está rodando
echo Verificando status do dashboard...
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" | find "python.exe" >nul
if %errorlevel% equ 0 (
    echo [INFO] Dashboard está rodando.
    echo.
    choice /c SP /m "O que deseja fazer? (S=Parar / P=Iniciar Nova Instância)"
    if %errorlevel% equ 1 (
        echo.
        echo Parando dashboard...
        call parar.bat
    ) else (
        echo.
        echo Iniciando nova instância...
        call iniciar.bat
    )
) else (
    echo [INFO] Dashboard não está rodando.
    echo.
    choice /c SI /m "O que deseja fazer? (S=Iniciar / I=Sair)"
    if %errorlevel% equ 1 (
        echo.
        echo Iniciando dashboard...
        call iniciar.bat
    ) else (
        echo Cancelado pelo usuário.
    )
)

echo.
echo Atalho concluído.
pause 