import os
from pypdf import PdfReader, PdfWriter
from ..utils import safe_filename


class PDFService:
    """Responsável por extrair e mesclar arquivos PDF."""

    @staticmethod
    def extract_multiple(
        source: str,
        results: dict[str, list[int]],
        output_dir: str,
        on_progress=None,
    ) -> int:
        """
        Gera um PDF separado para cada nome e suas páginas.
        on_progress(idx: int, total: int, name: str)
        Retorna a quantidade de arquivos gerados.
        """
        reader = PdfReader(source)
        for idx, (name, pages) in enumerate(results.items()):
            if on_progress:
                on_progress(idx, len(results), name)
            writer = PdfWriter()
            for pg in pages:
                writer.add_page(reader.pages[pg - 1])
            out = os.path.join(output_dir, f"{safe_filename(name)}.pdf")
            with open(out, "wb") as f:
                writer.write(f)
        return len(results)

    @staticmethod
    def merge_files(
        pdf_paths: list[str],
        output: str,
        on_progress=None,
    ) -> None:
        """
        Junta múltiplos PDFs em um único arquivo.
        on_progress(idx: int, total: int, filename: str)
        """
        writer = PdfWriter()
        for i, path in enumerate(pdf_paths):
            if on_progress:
                on_progress(i, len(pdf_paths), os.path.basename(path))
            for page in PdfReader(path).pages:
                writer.add_page(page)
        with open(output, "wb") as f:
            writer.write(f)

    @staticmethod
    def merge_pages(
        source: str,
        pages: list[int],
        output: str,
        on_progress=None,
    ) -> int:
        """
        Mescla páginas específicas de um PDF em um novo arquivo.
        Retorna a quantidade de páginas mescladas.
        """
        reader = PdfReader(source)
        writer = PdfWriter()
        unique_pages = sorted(set(pages))
        for i, pg in enumerate(unique_pages):
            if on_progress:
                on_progress(i + 1, len(unique_pages))
            writer.add_page(reader.pages[pg - 1])
        with open(output, "wb") as f:
            writer.write(f)
        return len(unique_pages)
