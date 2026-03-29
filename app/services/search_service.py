import threading
import pdfplumber
from ..models import SearchResult


class PDFSearchService:
    """Responsável por buscar nomes em PDFs com texto nativo."""

    def __init__(self):
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def search(
        self,
        pdf_path: str,
        names: list[str],
        on_progress=None,
    ) -> list[SearchResult]:
        """
        Busca cada nome nas páginas do PDF.
        on_progress(page_num: int, total: int)
        """
        self._cancel.clear()
        results = {name: SearchResult(name) for name in names}

        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                if self._cancel.is_set():
                    break
                if on_progress:
                    on_progress(i + 1, total)
                text = (page.extract_text() or "").lower()
                for name, result in results.items():
                    if name.lower() in text:
                        result.pages.append(i + 1)

        return list(results.values())
