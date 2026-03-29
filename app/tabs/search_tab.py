import threading
import os
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from ..config import COLORS as C
from ..models import SearchResult
from ..services.search_service import PDFSearchService
from ..services.pdf_service import PDFService
from ..widgets.terms_panel import TermsPanel


class SearchTab(ctk.CTkFrame):
    """Aba 1 — Buscar termos em PDFs e extrair páginas por resultado."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._search_service = PDFSearchService()
        self._pdf_service    = PDFService()
        self._pdf_path: str | None = None
        self._results: list[SearchResult] = []

        self._build()

    # ── Construção ─────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._terms_panel = TermsPanel(
            self,
            title="Termos de Busca",
            placeholder="Digite o nome ou termo...")
        self._terms_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(4, weight=1)

        self._build_pdf_section(right)
        self._build_action_row(right)
        self._build_progress(right)
        self._build_results_header(right)
        self._build_results_tree(right)

    def _build_pdf_section(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        card.columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Arquivo PDF",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        fr = ctk.CTkFrame(card, fg_color="transparent")
        fr.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        fr.columnconfigure(0, weight=1)

        self._pdf_label = ctk.CTkLabel(
            fr, text="Nenhum arquivo selecionado",
            text_color=C["muted"], anchor="w", wraplength=500)
        self._pdf_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(fr, text="Selecionar PDF", width=130,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      command=self._select_pdf).grid(row=0, column=1, padx=(10, 0))

    def _build_action_row(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 4))
        row.columnconfigure(3, weight=1)   # espaçador

        ctk.CTkButton(row, text="Buscar", height=38, width=110,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._start_search).grid(row=0, column=0, padx=(0, 8))

        self._extract_btn = ctk.CTkButton(
            row, text="Extrair PDFs", height=38, width=120,
            fg_color=C["green"], hover_color=C["green_h"],
            command=self._extract_pdfs, state="disabled")
        self._extract_btn.grid(row=0, column=1, padx=(0, 8))

        self._report_btn = ctk.CTkButton(
            row, text="Exportar Relatório", height=38, width=155,
            fg_color=C["gray"], hover_color=C["gray_h"],
            text_color=C["text"],
            command=self._export_report, state="disabled")
        self._report_btn.grid(row=0, column=2)

    def _build_progress(self, parent) -> None:
        pf = ctk.CTkFrame(parent, fg_color="transparent")
        pf.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 0))
        pf.columnconfigure(0, weight=1)

        self._progress = ctk.CTkProgressBar(pf, height=6,
                                             progress_color=C["accent"])
        self._progress.grid(row=0, column=0, sticky="ew")
        self._progress.set(0)

        self._status = ctk.CTkLabel(pf, text="", text_color=C["muted"],
                                    font=ctk.CTkFont(size=11), anchor="w")
        self._status.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def _build_results_header(self, parent) -> None:
        rh = ctk.CTkFrame(parent, fg_color="transparent")
        rh.grid(row=3, column=0, sticky="ew", padx=14, pady=(8, 4))
        ctk.CTkLabel(rh, text="Resultados",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).pack(side="left")
        self._found_label = ctk.CTkLabel(rh, text="",
                                         text_color=C["muted"],
                                         font=ctk.CTkFont(size=11))
        self._found_label.pack(side="left", padx=(12, 0))

    def _build_results_tree(self, parent) -> None:
        tf = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        tf.grid(row=4, column=0, sticky="nsew", padx=14, pady=(0, 14))
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(0, weight=1)

        cols = ("nome", "paginas", "total", "status")
        self._tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="Dark.Treeview")
        self._tree.heading("nome",    text="Termo")
        self._tree.heading("paginas", text="Páginas encontradas")
        self._tree.heading("total",   text="Qtd.")
        self._tree.heading("status",  text="Status")
        self._tree.column("nome",    width=200, minwidth=120)
        self._tree.column("paginas", width=300, minwidth=150)
        self._tree.column("total",   width=60,  minwidth=40, anchor="center")
        self._tree.column("status",  width=120, minwidth=80, anchor="center")

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0, 4))

        self._tree.tag_configure("found",     foreground=C["green"])
        self._tree.tag_configure("not_found", foreground=C["red"])

    # ── Lógica ─────────────────────────────────────────────────────────────────

    def _select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if path:
            self._pdf_path = path
            self._pdf_label.configure(
                text=os.path.basename(path), text_color=C["text"])
            self._results = []
            self._extract_btn.configure(state="disabled")
            self._report_btn.configure(state="disabled")
            self._clear_tree()
            self._progress.set(0)
            self._status.configure(text="")
            self._found_label.configure(text="")

    def _start_search(self) -> None:
        if not self._pdf_path:
            messagebox.showwarning("Atenção", "Selecione um arquivo PDF primeiro.")
            return
        if not self._terms_panel.terms:
            messagebox.showwarning("Atenção", "Adicione ao menos um termo de busca.")
            return
        self._clear_tree()
        self._results = []
        self._extract_btn.configure(state="disabled")
        self._report_btn.configure(state="disabled")
        self._found_label.configure(text="")
        self._progress.set(0)
        self._status.configure(text="Iniciando busca...")
        threading.Thread(target=self._run_search, daemon=True).start()

    def _run_search(self) -> None:
        def on_progress(page, total):
            self.after(0, lambda p=page/total: self._progress.set(p))
            self.after(0, lambda p=page, t=total:
                       self._status.configure(
                           text=f"Analisando página {p} de {t}..."))

        try:
            results = self._search_service.search(
                self._pdf_path, self._terms_panel.terms, on_progress)
            self._results = results
            self.after(0, self._show_results)
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro ao processar o PDF:\n{err}"))
            self.after(0, lambda: self._status.configure(text="Erro ao processar."))

    def _show_results(self) -> None:
        self._progress.set(1)
        found   = [r for r in self._results if r.found]
        missing = [r for r in self._results if not r.found]

        for result in self._results:
            self._tree.insert("", "end",
                              values=(result.name, result.pages_str,
                                      result.count, result.status_text),
                              tags=(result.row_tag,))

        self._status.configure(text="Busca concluída.")
        self._found_label.configure(
            text=f"{len(found)} encontrado(s)  ·  {len(missing)} não encontrado(s)",
            text_color=C["muted"])

        if found:
            self._extract_btn.configure(state="normal")
        self._report_btn.configure(state="normal")

        if missing:
            messagebox.showwarning(
                "Não encontrados",
                "Termos NÃO encontrados no PDF:\n\n" +
                "\n".join(f"  •  {r.name}" for r in missing))
        else:
            messagebox.showinfo(
                "Busca concluída",
                f"Todos os {len(self._results)} termos foram encontrados!")

    def _extract_pdfs(self) -> None:
        found = {r.name: r.pages for r in self._results if r.found}
        if not found:
            return
        out_dir = filedialog.askdirectory(title="Selecionar pasta de destino")
        if not out_dir:
            return
        self._progress.set(0)
        self._status.configure(text="Extraindo...")
        threading.Thread(target=self._run_extract,
                         args=(found, out_dir), daemon=True).start()

    def _run_extract(self, found: dict, out_dir: str) -> None:
        def on_progress(idx, total, name):
            self.after(0, lambda p=idx/total: self._progress.set(p))
            self.after(0, lambda n=name:
                       self._status.configure(text=f"Extraindo: {n}..."))
        try:
            n = self._pdf_service.extract_multiple(
                self._pdf_path, found, out_dir, on_progress)
            self.after(0, lambda: self._progress.set(1))
            self.after(0, lambda: self._status.configure(text="Extração concluída!"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"{n} PDF(s) salvo(s) em:\n{out_dir}"))
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro ao extrair:\n{err}"))

    def _export_report(self) -> None:
        if not self._results:
            return
        path = filedialog.asksaveasfilename(
            title="Salvar relatório", defaultextension=".txt",
            filetypes=[("Texto", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Relatório de Busca — {os.path.basename(self._pdf_path or '')}\n")
                f.write("=" * 60 + "\n\nENCONTRADOS:\n")
                for r in self._results:
                    if r.found:
                        f.write(f"  {r.name}  →  páginas: {r.pages_str}\n")
                f.write("\nNÃO ENCONTRADOS:\n")
                for r in self._results:
                    if not r.found:
                        f.write(f"  {r.name}\n")
            messagebox.showinfo("Salvo", f"Relatório salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _clear_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
