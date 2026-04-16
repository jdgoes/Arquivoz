#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "============================================"
echo "  Arquivoz - Gerando ArquivozSetup"
echo "============================================"
echo

VENV_DIR=".venv"
BASE_PYTHON=""

for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        BASE_PYTHON=$(command -v "$cmd")
        break
    fi
done

if [ -z "$BASE_PYTHON" ]; then
    echo "ERRO: nenhum interpretador Python encontrado no PATH."
    exit 1
fi

if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
else
    if [ ! -d "$VENV_DIR" ]; then
        echo "Criando venv com $BASE_PYTHON..."
        $BASE_PYTHON -m venv "$VENV_DIR"
    fi
    PYTHON="$VENV_DIR/bin/python"
    source "$VENV_DIR/bin/activate"
fi

echo "Python: $PYTHON ($($PYTHON --version))"
echo

echo "[1/3] Verificando PyInstaller..."
if ! $PYTHON -m pip install pyinstaller --quiet; then
    echo "ERRO: nao foi possivel instalar PyInstaller."
    exit 1
fi

echo "[2/3] Instalando dependencias do app..."
if ! $PYTHON -m pip install -r requirements.txt --quiet; then
    echo "AVISO: algumas dependencias podem nao ter sido instaladas."
fi

echo "[3/3] Compilando instalador (aguarde, pode demorar alguns minutos)..."
$PYTHON -m PyInstaller setup.pyw --name ArquivozSetup --onefile --clean --noconfirm

echo

if [ -f "dist/ArquivozSetup" ]; then
    echo "============================================"
    echo "  SUCESSO!"
    echo "  Arquivo gerado: dist/ArquivozSetup"
    echo "============================================"
    if command -v xdg-open &> /dev/null; then
        xdg-open dist/ &
    fi
else
    echo "ERRO: o arquivo dist/ArquivozSetup nao foi gerado."
    echo "Verifique os erros acima."
    exit 1
fi
