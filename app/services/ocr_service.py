import os
import json
import time
import shutil
import hashlib
import threading
import urllib.request
import concurrent.futures
from typing import Callable

from ..config import TESSERACT_CANDIDATES, CACHE_DIR, LOCAL_TESSDATA_DIR, TESSDATA_URLS

# ── Configuração do Tesseract ─────────────────────────────────────────────────

def _find_tesseract_exe() -> str | None:
    """Localiza o executável do Tesseract nos caminhos conhecidos."""
    for path in TESSERACT_CANDIDATES:
        if path and os.path.exists(path):
            return path
    return None


def _find_system_tessdata(tess_exe: str) -> str | None:
    """Localiza a pasta tessdata junto ao executável do Tesseract."""
    candidate = os.path.join(os.path.dirname(tess_exe), "tessdata")
    return candidate if os.path.exists(candidate) else None


def _ensure_local_tessdata(lang: str, system_tessdata: str | None) -> bool:
    """
    Garante que o arquivo traineddata do idioma está na pasta tessdata local.
    Tenta copiar do sistema primeiro; se falhar, baixa da internet.
    Retorna True se o arquivo estiver disponível.
    """
    os.makedirs(LOCAL_TESSDATA_DIR, exist_ok=True)
    dest = os.path.join(LOCAL_TESSDATA_DIR, f"{lang}.traineddata")

    if os.path.exists(dest):
        return True

    # Tentar copiar do sistema (sem necessidade de admin)
    if system_tessdata:
        src = os.path.join(system_tessdata, f"{lang}.traineddata")
        if os.path.exists(src):
            try:
                shutil.copy2(src, dest)
                return True
            except OSError:
                pass

    # Baixar da internet
    url = TESSDATA_URLS.get(lang)
    if not url:
        return False
    try:
        urllib.request.urlretrieve(url, dest)
        return os.path.exists(dest)
    except Exception:
        return False


def detect_tesseract() -> tuple[bool, str]:
    """
    Localiza o Tesseract, configura pytesseract e prepara tessdata local.
    Retorna (disponivel, mensagem_erro).
    """
    # Verificar PyMuPDF
    try:
        import fitz  # noqa: F401
    except ImportError:
        return False, "PyMuPDF não instalado.\nExecute o setup.pyw para instalar."

    # Verificar pytesseract + Pillow
    try:
        import pytesseract
        from PIL import Image  # noqa: F401
    except ImportError:
        return False, "Dependências faltando.\nExecute: pip install pytesseract Pillow"

    # Localizar executável
    tess_exe = _find_tesseract_exe()
    if not tess_exe:
        return False, (
            "Tesseract OCR não encontrado no sistema.\n\n"
            "Execute o  setup.pyw  para instalar automaticamente.\n\n"
            "Ou baixe manualmente:\n"
            "github.com/UB-Mannheim/tesseract/wiki\n"
            "(marque 'Portuguese' durante a instalação)"
        )

    pytesseract.pytesseract.tesseract_cmd = tess_exe

    # Preparar tessdata local (por + eng)
    system_tessdata = _find_system_tessdata(tess_exe)
    for lang in ("eng", "por"):
        _ensure_local_tessdata(lang, system_tessdata)

    # Copiar pdf.ttf e pastas configs/tessconfigs (necessários para output PDF)
    if system_tessdata:
        for item in ("pdf.ttf", "configs", "tessconfigs"):
            src = os.path.join(system_tessdata, item)
            dst = os.path.join(LOCAL_TESSDATA_DIR, item)
            if os.path.exists(src) and not os.path.exists(dst):
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                except OSError:
                    pass

    # Apontar Tesseract para a pasta tessdata local
    os.environ["TESSDATA_PREFIX"] = LOCAL_TESSDATA_DIR

    # Verificar se Tesseract responde
    try:
        pytesseract.get_tesseract_version()
        return True, ""
    except Exception as exc:
        return False, f"Erro ao inicializar Tesseract:\n{exc}"


# ── Worker de OCR ─────────────────────────────────────────────────────────────

def _preprocess_image(img):
    """
    Pré-processamento para melhorar precisão do OCR em documentos escaneados:
    converte para escala de cinza e aplica binarização adaptativa (Otsu).
    """
    from PIL import ImageFilter, ImageOps
    # Escala de cinza
    img = img.convert("L")
    # Aumentar contraste
    img = ImageOps.autocontrast(img, cutoff=2)
    # Leve sharpening para bordas de texto
    img = img.filter(ImageFilter.SHARPEN)
    return img


def _ocr_worker(args: tuple) -> tuple[int, str]:
    """
    Worker isolado por thread: renderiza página em alta qualidade e executa OCR.
    Cada thread abre sua própria instância do documento (thread-safe com fitz).
    """
    import fitz
    import pytesseract

    page_idx, pdf_path, dpi, lang = args

    # Renderizar página em bitmap
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_idx)
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    doc.close()

    # Converter para PIL e pré-processar
    from PIL import Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = _preprocess_image(img)

    # OCR — oem 3 = LSTM + legado (maior precisão), psm 6 = bloco de texto uniforme
    config = "--psm 6 --oem 3"
    text = pytesseract.image_to_string(img, lang=lang, config=config)
    return page_idx, text


# ── Serviço principal ─────────────────────────────────────────────────────────

class OCRService:
    """
    Responsável pelo processamento OCR de PDFs digitalizados.
    Gerencia cache em disco, paralelismo e cancelamento.

    Princípios aplicados (SOLID):
    - SRP: somente responsabilidade de OCR + cache
    - OCP: workers e preprocessamento são funções extensíveis
    - DIP: dependências (fitz, pytesseract) são injetadas via imports lazy
    """

    def __init__(self):
        self._page_texts: dict[int, str] = {}
        self._cache_key: str = ""
        self._cancel = threading.Event()
        self._last_worker_error: str = ""

    # ── Detecção ──────────────────────────────────────────────────────────────

    @staticmethod
    def is_available() -> tuple[bool, str]:
        """Verifica se OCR está disponível e configura o ambiente."""
        return detect_tesseract()

    # ── Gerenciamento de PDF ───────────────────────────────────────────────────

    def load_pdf(self, pdf_path: str) -> tuple[bool, int]:
        """
        Define o PDF ativo e carrega cache do disco se disponível.
        Retorna (tem_cache, paginas_em_cache).
        """
        stat = os.stat(pdf_path)
        raw = f"{os.path.abspath(pdf_path)}|{stat.st_size}|{stat.st_mtime}"
        self._cache_key = hashlib.md5(raw.encode()).hexdigest()

        cached = self._read_cache()
        if cached:
            texts = {int(k): v for k, v in cached.items()}
            # Invalidate cache se todas as páginas têm texto vazio (OCR anterior falhou)
            if any(v.strip() for v in texts.values()):
                self._page_texts = texts
                return True, len(self._page_texts)

        self._page_texts = {}
        return False, 0

    def get_page_texts(self) -> dict[int, str]:
        return self._page_texts

    # ── Processamento OCR ─────────────────────────────────────────────────────

    def process(
        self,
        pdf_path: str,
        dpi: int,
        lang: str,
        workers: int,
        force: bool,
        on_progress: Callable[[int, int, int, float, float], None] = None,
    ) -> dict[int, str]:
        """
        Executa OCR nas páginas ainda não processadas (ou todas se force=True).
        on_progress(concluidas, total_ocr, em_cache, velocidade_pag_s, eta_s)
        Retorna {page_idx: texto_extraido}.
        """
        import fitz

        self._cancel.clear()
        self._last_worker_error = ""

        if force:
            self._page_texts = {}

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        pages_to_ocr = [i for i in range(total_pages) if i not in self._page_texts]
        cached_count = total_pages - len(pages_to_ocr)

        if pages_to_ocr:
            completed = [0]
            t_start = time.time()
            args_list = [(i, pdf_path, dpi, lang) for i in pages_to_ocr]

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(_ocr_worker, a): a[0] for a in args_list}

                for future in concurrent.futures.as_completed(futures):
                    if self._cancel.is_set():
                        for f in futures:
                            f.cancel()
                        break
                    try:
                        page_idx, text = future.result()
                        self._page_texts[page_idx] = text
                        completed[0] += 1

                        elapsed = time.time() - t_start
                        speed = completed[0] / elapsed if elapsed > 0 else 0
                        eta = (len(pages_to_ocr) - completed[0]) / speed if speed > 0 else 0

                        if on_progress:
                            on_progress(
                                completed[0], len(pages_to_ocr),
                                cached_count, speed, eta,
                            )
                    except Exception as exc:
                        # Página com erro recebe texto vazio e continua o processo
                        page_idx = futures[future]
                        self._page_texts[page_idx] = ""
                        if not self._last_worker_error:
                            self._last_worker_error = str(exc)

            # Só grava cache se ao menos uma página produziu texto real
            if any(v.strip() for v in self._page_texts.values()):
                self._write_cache()

        return self._page_texts

    def search(self, terms: list[str]) -> dict[str, list[int]]:
        """Busca termos no texto extraído. Retorna {termo: [paginas_1_indexed]}."""
        results: dict[str, list[int]] = {}
        for term in terms:
            lower = term.lower()
            for page_idx, text in self._page_texts.items():
                if lower in text.lower():
                    results.setdefault(term, []).append(page_idx + 1)
        return {t: sorted(p) for t, p in results.items()}

    def cancel(self) -> None:
        self._cancel.set()

    def was_cancelled(self) -> bool:
        return self._cancel.is_set()

    def get_last_worker_error(self) -> str:
        return self._last_worker_error

    # ── Cache em disco ────────────────────────────────────────────────────────

    def _read_cache(self) -> dict | None:
        fp = os.path.join(CACHE_DIR, f"{self._cache_key}.json")
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _write_cache(self) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        fp = os.path.join(CACHE_DIR, f"{self._cache_key}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(
                {str(k): v for k, v in self._page_texts.items()},
                f, ensure_ascii=False,
            )
