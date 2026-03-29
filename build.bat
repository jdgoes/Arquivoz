@echo off
setlocal
title Arquivoz — Build Instalador

echo ============================================
echo   Arquivoz - Gerando ArquivozSetup.exe
echo ============================================
echo.

REM Instala PyInstaller se necessario
echo [1/3] Verificando PyInstaller...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERRO: nao foi possivel instalar PyInstaller.
    echo Verifique se o Python esta instalado e no PATH.
    pause & exit /b 1
)

REM Instala dependencias do app no ambiente atual
echo [2/3] Instalando dependencias do app...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo AVISO: algumas dependencias podem nao ter sido instaladas.
)

REM Gera o .exe
echo [3/3] Compilando instalador (aguarde, pode demorar alguns minutos)...
python -m PyInstaller setup.spec --clean --noconfirm

echo.
if exist "dist\ArquivozSetup.exe" (
    echo ============================================
    echo   SUCESSO!
    echo   Arquivo gerado: dist\ArquivozSetup.exe
    echo ============================================
    explorer dist
) else (
    echo ERRO: o arquivo dist\ArquivozSetup.exe nao foi gerado.
    echo Verifique os erros acima.
)

pause
endlocal
