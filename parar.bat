@echo off
chcp 65001 >nul
title Dashboard de Tarefas - Parar

echo ========================================
echo   Dashboard de Tarefas - Python
echo   Script de Parada
echo ========================================
echo.

:: Verificar se o dashboard está rodando
echo Verificando se o dashboard está rodando...
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" | find "python.exe" >nul
if %errorlevel% neq 0 (
    echo [INFO] Dashboard não está rodando.
    echo.
    pause
    exit /b 0
)

:: Mostrar processos encontrados
echo Processos do Dashboard encontrados:
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*"

echo.
choice /c SN /m "Deseja parar o dashboard? (S/N)"
if %errorlevel% equ 2 (
    echo Cancelado pelo usuário.
    pause
    exit /b 0
)

:: Parar processos do dashboard
echo.
echo Parando processos do dashboard...
taskkill /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [SUCESSO] Dashboard parado com sucesso!
) else (
    echo [AVISO] Nenhum processo foi parado ou erro ao parar.
)

:: Verificar se ainda há processos
echo.
echo Verificando se ainda há processos rodando...
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" | find "python.exe" >nul
if %errorlevel% equ 0 (
    echo [AVISO] Ainda há processos do dashboard rodando.
    echo Tentando parar forçadamente...
    taskkill /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" /f >nul 2>&1
) else (
    echo [SUCESSO] Todos os processos foram parados.
)

echo.
pause 