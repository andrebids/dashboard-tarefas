@echo off
echo ========================================
echo    Limpeza Preventiva - Planka
echo    Previne arquivos corrompidos
echo ========================================
echo.

cd /d "%~dp0\..\..\planka-personalizado"

echo 🧹 LIMPANDO ARQUIVOS POTENCIALMENTE CORROMPIDOS...
echo.

echo 📁 Removendo diretórios problemáticos...
if exist "server\.venv" (
    echo   • Removendo server\.venv...
    rmdir /s /q "server\.venv"
    echo   ✅ server\.venv removido
) else (
    echo   • server\.venv não existe
)

if exist "server\node_modules" (
    echo   • Removendo server\node_modules...
    rmdir /s /q "server\node_modules"
    echo   ✅ server\node_modules removido
) else (
    echo   • server\node_modules não existe
)

if exist "client\node_modules" (
    echo   • Removendo client\node_modules...
    rmdir /s /q "client\node_modules"
    echo   ✅ client\node_modules removido
) else (
    echo   • client\node_modules não existe
)

echo.
echo 🐳 LIMPANDO CACHE DO DOCKER...
docker system prune -f
docker builder prune -f
echo ✅ Cache do Docker limpo

echo.
echo 🔍 VERIFICANDO ARQUIVOS PYTHON CORROMPIDOS...
for /r "server" %%f in (*.py) do (
    if %%~zf==0 (
        echo   ⚠️ Arquivo corrompido encontrado: %%f
        del "%%f"
        echo   ✅ Arquivo corrompido removido: %%f
    )
)

echo.
echo ✅ LIMPEZA PREVENTIVA CONCLUÍDA!
echo.
echo 💡 DICAS PARA EVITAR ARQUIVOS CORROMPIDOS:
echo   1. Não interrompa processos de instalação
echo   2. Mantenha espaço livre no disco
echo   3. Execute esta limpeza semanalmente
echo   4. Use apenas um modo por vez (dev OU produção)
echo.
pause 