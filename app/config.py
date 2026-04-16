import os
import shutil as _shutil

# ── Paletas ────────────────────────────────────────────────────────────────────

_DARK = dict(
    bg       = "#08090f",   # preto puro com leve toque azul
    panel    = "#0e1118",   # painéis — preto profundo
    entry    = "#151a24",   # campos / listas
    text     = "#e6f0ff",   # branco-azulado — alto contraste
    muted    = "#8099c0",   # rótulos — azul-cinza mais brilhante
    title    = "#e6f0ff",   # cor do título no header (igual ao texto no dark)
    accent   = "#3d8ef0",   # azul elétrico
    accent_h = "#2577e0",
    green    = "#1ec775",
    green_h  = "#16aa60",
    red      = "#ff4466",
    red_h    = "#e82d52",
    orange   = "#ffaa22",
    orange_h = "#e89000",
    gray     = "#283040",   # cinza-azulado
    gray_h   = "#1e2535",
    border   = "#1c2438",
)

_LIGHT = dict(
    bg       = "#f0ddb0",   # dourado suave — área externa
    panel    = "#fdf5e4",   # creme suave — painéis internos
    entry    = "#fefaf2",   # quase branco quente — campos de entrada (mais interno)
    text     = "#1a0a00",   # marrom-preto — alto contraste
    muted    = "#7a5a30",   # marrom médio para rótulos
    title    = "#7a4010",   # marrom médio para o nome do app no header
    accent   = "#c07818",   # caramelo — cor de destaque
    accent_h = "#a86210",
    green    = "#3a7040",
    green_h  = "#2c5a32",
    red      = "#b83030",
    red_h    = "#942020",
    orange   = "#c87010",
    orange_h = "#a05808",
    gray     = "#c8aa7a",   # areia quente
    gray_h   = "#b09060",
    border   = "#dfc090",
)

# ── Estado global do tema ─────────────────────────────────────────────────────

MODE: str = "dark"
COLORS: dict = {}   # dict mutável — módulos importam a referência, não o valor


def set_theme(mode: str) -> None:
    """Atualiza COLORS in-place — todos os módulos que importaram COLORS veem a mudança."""
    global MODE
    MODE = mode
    COLORS.update(_DARK if mode == "dark" else _LIGHT)


# Inicializar com tema escuro
set_theme("dark")

# ── Janela ────────────────────────────────────────────────────────────────────
WINDOW_TITLE    = "Arquivoz"
WINDOW_GEOMETRY = "1200x780"
WINDOW_MIN      = (980, 660)

# ── Cache OCR ─────────────────────────────────────────────────────────────────
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".arquivoz_cache")

# ── Caminhos Tesseract (Windows) ──────────────────────────────────────────────
_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tesseract.exe"),
    os.path.join(_APP_ROOT, "tesseract", "tesseract.exe"),
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    _shutil.which("tesseract") or "",
]

LOCAL_TESSDATA_DIR = os.path.join(_APP_ROOT, "tessdata")

TESSDATA_URLS = {
    "por": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata",
    "eng": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata",
}
