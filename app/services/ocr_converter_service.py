import io
import os
import threading
import concurrent.futures
from typing import Callable

from .ocr_service import detect_tesseract


def _convert_page_worker(args: tuple) -> tuple[int, bytes]:
    """
    Worker thread: renderiza a página em alta qualidade e converte para PDF pesquisável
    usando pytesseract.image_to_pdf_or_hocr (imagem + camada de texto invisível).
    """
    import fitz
    import pytesseract
    from PIL import Image

    page_idx, pdf_path, dpi, lang = args

    doc = fitz.open(pdf_path)
    page = doc.load_page(page_idx)
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    doc.close()

    # Mantém imagem colorida para preservar aparência original no PDF de saída
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    config = "--psm 6 --oem 3"
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension="pdf", lang=lang, config=config)
    return page_idx, pdf_bytes


class OCRConverterService:
    """
    Converte PDFs digitalizados em PDFs pesquisáveis (com camada de texto OCR).
    Suporta conversão em lote, cancelamento e mesclagem do resultado.
    """

    def __init__(self):
        self._cancel = threading.Event()
        self._last_error: str = ""

    # ── Detecção ──────────────────────────────────────────────────────────────

    @staticmethod
    def is_available() -> tuple[bool, str]:
        return detect_tesseract()

    # ── Conversão ─────────────────────────────────────────────────────────────

    def convert_pdf(
        self,
        input_path: str,
        output_path: str,
        dpi: int,
        lang: str,
        workers: int,
        on_page_progress: Callable[[int, int], None] = None,
    ) -> tuple[bool, str]:
        """
        Converte um PDF digitalizado em PDF pesquisável.
        Retorna (sucesso, mensagem_erro).
        """
        import fitz
        from pypdf import PdfWriter, PdfReader

        self._last_error = ""

        doc = fitz.open(input_path)
        total_pages = len(doc)
        doc.close()

        args_list = [(i, input_path, dpi, lang) for i in range(total_pages)]
        page_pdfs: dict[int, bytes] = {}
        completed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_convert_page_worker, a): a[0] for a in args_list}

            for future in concurrent.futures.as_completed(futures):
                if self._cancel.is_set():
                    for f in futures:
                        f.cancel()
                    return False, "Cancelado pelo usuário."

                page_idx = futures[future]
                try:
                    _, pdf_bytes = future.result()
                    page_pdfs[page_idx] = pdf_bytes
                except Exception as exc:
                    if not self._last_error:
                        self._last_error = str(exc)

                completed += 1
                if on_page_progress:
                    on_page_progress(completed, total_pages)

        if not page_pdfs:
            return False, f"Nenhuma página convertida.\n{self._last_error}"

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        writer = PdfWriter()
        for idx in sorted(page_pdfs.keys()):
            reader = PdfReader(io.BytesIO(page_pdfs[idx]))
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        return True, ""

    def convert_batch(
        self,
        jobs: list[tuple[str, str]],
        dpi: int,
        lang: str,
        workers: int,
        on_file_start: Callable[[int, int, str], None] = None,
        on_page_progress: Callable[[int, int], None] = None,
        on_file_done: Callable[[int, int, str, bool, str], None] = None,
    ) -> list[str]:
        """
        Converte uma lista de (input_path, output_path).
        Retorna lista dos output_paths convertidos com sucesso.
        on_file_start(file_idx, total_files, filename)
        on_page_progress(pages_done, total_pages)
        on_file_done(file_idx, total_files, filename, success, error_msg)
        """
        self._cancel.clear()
        successful_outputs: list[str] = []

        for i, (inp, out) in enumerate(jobs):
            if self._cancel.is_set():
                break

            name = os.path.basename(inp)
            if on_file_start:
                on_file_start(i, len(jobs), name)

            ok, err = self.convert_pdf(inp, out, dpi, lang, workers, on_page_progress)

            if on_file_done:
                on_file_done(i, len(jobs), name, ok, err)

            if ok:
                successful_outputs.append(out)

        return successful_outputs

    def merge_pdfs(self, pdf_paths: list[str], output_path: str) -> None:
        """Mescla uma lista de PDFs em um único arquivo."""
        from pypdf import PdfWriter, PdfReader

        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

    # ── Controle ──────────────────────────────────────────────────────────────

    def cancel(self) -> None:
        self._cancel.set()

    def was_cancelled(self) -> bool:
        return self._cancel.is_set()
