import os
import threading
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from ..config import COLORS as C
from ..services.ocr_service import OCRService
from ..services.pdf_service import PDFService
from ..widgets.terms_panel import TermsPanel


class OCRTab(ctk.CTkFrame):
    """Aba 3 — Busca por OCR em PDFs digitalizados."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._ocr_service = OCRService()
        self._pdf_service  = PDFService()
        self._pdf_path: str | None = None
        self._results: dict[str, list[int]] = {}

        available, error_msg = OCRService.is_available()
        if not available:
            self._build_warning(error_msg)
        else:
            self._build_ui()

    # ── Aviso ──────────────────────────────────────────────────────────────────

    def _build_warning(self, msg: str) -> None:
        frame = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="OCR não disponível",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=C["orange"]).pack(pady=(40, 10))

        ctk.CTkLabel(frame, text=msg,
                     font=ctk.CTkFont(family="Consolas", size=12),
                     text_color=C["text"], justify="left").pack(pady=10, padx=60)

        ctk.CTkButton(frame, text="Fechar aplicativo",
                      width=220, height=40,
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      command=lambda: self.winfo_toplevel().destroy()
                      ).pack(pady=20)

    # ── UI principal ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._terms_panel = TermsPanel(
            self,
            title="Termos de Busca",
            placeholder="Nome ou trecho do documento...")
        self._terms_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        self._build_pdf_card(right)
        self._build_options(right)
        self._build_actions(right)
        self._build_progress(right)
        self._build_results_header(right)
        self._build_results_tree(right)
        self._build_bottom_buttons(right)

    def _build_pdf_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        card.columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Arquivo PDF digitalizado",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        fr = ctk.CTkFrame(card, fg_color="transparent")
        fr.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        fr.columnconfigure(0, weight=1)

        self._pdf_label = ctk.CTkLabel(fr, text="Nenhum arquivo selecionado",
                                       text_color=C["muted"], anchor="w",
                                       wraplength=440)
        self._pdf_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(fr, text="Selecionar PDF", width=130,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      command=self._select_pdf).grid(row=0, column=1, padx=(10, 0))

        self._cache_label = ctk.CTkLabel(card, text="",
                                         font=ctk.CTkFont(size=10),
                                         text_color=C["muted"])
        self._cache_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))

    def _build_options(self, parent) -> None:
        opts = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        opts.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))

        ctk.CTkLabel(opts, text="Idioma:",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(12, 4), pady=8)
        self._lang_var = ctk.StringVar(value="por (Português)")
        ctk.CTkComboBox(opts, variable=self._lang_var, width=175, height=30,
                        values=["por (Português)", "eng (Inglês)", "por+eng (Ambos)"],
                        state="readonly").pack(side="left", padx=(0, 18), pady=8)

        ctk.CTkLabel(opts, text="Qualidade (DPI):",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(0, 4))
        self._dpi_var = ctk.StringVar(value="200")
        ctk.CTkSegmentedButton(opts, values=["150", "200", "300"],
                               variable=self._dpi_var,
                               selected_color=C["accent"],
                               selected_hover_color=C["accent_h"],
                               width=160).pack(side="left", padx=(0, 18), pady=8)

        ctk.CTkLabel(opts, text="Threads:",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(0, 4))
        self._workers_var = ctk.StringVar(value="4")
        ctk.CTkComboBox(opts, variable=self._workers_var, width=65, height=30,
                        values=["1", "2", "4", "8"],
                        state="readonly").pack(side="left", padx=(0, 12), pady=8)

    def _build_actions(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 4))

        self._start_btn = ctk.CTkButton(
            row, text="Processar e Buscar", height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C["accent"], hover_color=C["accent_h"],
            command=self._start_ocr)
        self._start_btn.pack(side="left", padx=(0, 8))

        self._cancel_btn = ctk.CTkButton(
            row, text="Cancelar", height=40, width=100,
            fg_color=C["red"], hover_color=C["red_h"],
            command=self._cancel, state="disabled")
        self._cancel_btn.pack(side="left", padx=(0, 16))

        self._force_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row, text="Reprocessar (ignorar cache)",
                        variable=self._force_var,
                        text_color=C["muted"],
                        font=ctk.CTkFont(size=11),
                        checkmark_color=C["accent"],
                        fg_color=C["accent"]).pack(side="left")

    def _build_progress(self, parent) -> None:
        pf = ctk.CTkFrame(parent, fg_color="transparent")
        pf.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 4))
        pf.columnconfigure(0, weight=1)

        self._progress = ctk.CTkProgressBar(pf, height=8,
                                             progress_color=C["accent"])
        self._progress.grid(row=0, column=0, sticky="ew")
        self._progress.set(0)

        self._status = ctk.CTkLabel(pf, text="", text_color=C["muted"],
                                    font=ctk.CTkFont(size=11), anchor="w")
        self._status.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def _build_results_header(self, parent) -> None:
        rh = ctk.CTkFrame(parent, fg_color="transparent")
        rh.grid(row=4, column=0, sticky="ew", padx=14, pady=(6, 4))
        ctk.CTkLabel(rh, text="Resultados",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).pack(side="left")
        self._found_label = ctk.CTkLabel(rh, text="",
                                         text_color=C["muted"],
                                         font=ctk.CTkFont(size=11))
        self._found_label.pack(side="left", padx=(12, 0))

    def _build_results_tree(self, parent) -> None:
        tf = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        tf.grid(row=5, column=0, sticky="nsew", padx=14, pady=(0, 4))
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(0, weight=1)

        cols = ("termo", "paginas", "total", "status")
        self._tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="Dark.Treeview")
        self._tree.heading("termo",   text="Termo buscado")
        self._tree.heading("paginas", text="Páginas encontradas")
        self._tree.heading("total",   text="Qtd.")
        self._tree.heading("status",  text="Status")
        self._tree.column("termo",   width=200, minwidth=120)
        self._tree.column("paginas", width=300, minwidth=150)
        self._tree.column("total",   width=55,  minwidth=40, anchor="center")
        self._tree.column("status",  width=120, minwidth=80, anchor="center")

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0, 4))

        self._tree.tag_configure("found",     foreground=C["green"])
        self._tree.tag_configure("not_found", foreground=C["red"])

    def _build_bottom_buttons(self, parent) -> None:
        bot = ctk.CTkFrame(parent, fg_color="transparent")
        bot.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 14))

        self._extract_btn = ctk.CTkButton(
            bot, text="Extrair Separados", height=34,
            fg_color=C["green"], hover_color=C["green_h"],
            command=self._extract_separate, state="disabled")
        self._extract_btn.pack(side="left", padx=(0, 8))

        self._merge_btn = ctk.CTkButton(
            bot, text="Mesclar em um PDF", height=34,
            fg_color=C["orange"], hover_color=C["orange_h"],
            command=self._merge_results, state="disabled")
        self._merge_btn.pack(side="left", padx=(0, 8))

        self._report_btn = ctk.CTkButton(
            bot, text="Exportar Relatório", height=34,
            fg_color=C["gray"], hover_color=C["gray_h"],
            text_color=C["text"],
            command=self._export_report, state="disabled")
        self._report_btn.pack(side="left")

    # ── Lógica ─────────────────────────────────────────────────────────────────

    def _get_lang(self) -> str:
        return self._lang_var.get().split(" ")[0]

    def _select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar PDF digitalizado",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if not path:
            return
        self._pdf_path = path
        self._pdf_label.configure(text=os.path.basename(path), text_color=C["text"])

        has_cache, n = self._ocr_service.load_pdf(path)
        if has_cache:
            self._cache_label.configure(
                text=f"Cache disponível: {n} página(s) — a busca será instantânea.",
                text_color=C["green"])
        else:
            self._cache_label.configure(
                text="Sem cache — o OCR será executado agora.",
                text_color=C["muted"])

        self._results = {}
        self._clear_tree()
        self._progress.set(0)
        self._status.configure(text="")
        self._found_label.configure(text="")
        self._extract_btn.configure(state="disabled")
        self._merge_btn.configure(state="disabled")
        self._report_btn.configure(state="disabled")

    def _start_ocr(self) -> None:
        if not self._pdf_path:
            messagebox.showwarning("Atenção", "Selecione um arquivo PDF primeiro.")
            return
        if not self._terms_panel.terms:
            messagebox.showwarning("Atenção", "Adicione ao menos um termo de busca.")
            return
        self._clear_tree()
        self._results = {}
        self._found_label.configure(text="")
        self._progress.set(0)
        self._start_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._extract_btn.configure(state="disabled")
        self._merge_btn.configure(state="disabled")
        self._report_btn.configure(state="disabled")
        threading.Thread(target=self._run_ocr, daemon=True).start()

    def _run_ocr(self) -> None:
        def on_progress(done, total_ocr, cached, speed, eta):
            pct = (done + cached) / (total_ocr + cached) if (total_ocr + cached) > 0 else 1
            self.after(0, lambda p=pct: self._progress.set(p))
            self.after(0, lambda d=done, t=total_ocr, s=speed, e=eta:
                       self._status.configure(
                           text=f"OCR: {d}/{t} páginas  ·  {s:.1f} pág/s  ·  ETA: {e:.0f}s"))

        try:
            self._ocr_service.process(
                self._pdf_path,
                dpi=int(self._dpi_var.get()),
                lang=self._get_lang(),
                workers=int(self._workers_var.get()),
                force=self._force_var.get(),
                on_progress=on_progress,
            )
            if self._ocr_service.was_cancelled():
                self.after(0, lambda: self._status.configure(
                    text="Cancelado — cache parcial salvo."))
                self.after(0, self._done_cleanup)
                return

            page_texts = self._ocr_service.get_page_texts()
            if page_texts and not any(t.strip() for t in page_texts.values()):
                worker_err = self._ocr_service.get_last_worker_error()
                msg = ("O OCR não extraiu texto de nenhuma página.\n\n"
                       "Verifique:\n"
                       "  • A pasta tessdata/ existe na pasta do aplicativo?\n"
                       "  • Os arquivos .traineddata do idioma estão presentes?\n")
                if worker_err:
                    msg += f"\nDetalhes do erro:\n{worker_err}"
                self.after(0, lambda m=msg: messagebox.showerror("Falha no OCR", m))
                self.after(0, lambda: self._status.configure(text="Falha no OCR."))
                self.after(0, self._done_cleanup)
                return

            self._results = self._ocr_service.search(self._terms_panel.terms)
            self.after(0, self._show_results)

        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro no processamento OCR:\n{err}"))
            self.after(0, self._done_cleanup)

    def _show_results(self) -> None:
        self._progress.set(1)
        self._done_cleanup()

        terms = self._terms_panel.terms
        found   = [t for t in terms if t in self._results]
        missing = [t for t in terms if t not in self._results]

        for term in terms:
            if term in self._results:
                pages = self._results[term]
                self._tree.insert("", "end",
                                  values=(term,
                                          ", ".join(map(str, pages)),
                                          len(pages), "Encontrado"),
                                  tags=("found",))
            else:
                self._tree.insert("", "end",
                                  values=(term, "—", "0", "Não encontrado"),
                                  tags=("not_found",))

        n_cached = len(self._ocr_service.get_page_texts())
        self._cache_label.configure(
            text=f"Cache: {n_cached} página(s) — próximas buscas serão instantâneas.",
            text_color=C["green"])

        self._found_label.configure(
            text=f"{len(found)} encontrado(s)  ·  {len(missing)} não encontrado(s)",
            text_color=C["muted"])
        self._status.configure(text="Processamento concluído.")

        if found:
            self._extract_btn.configure(state="normal")
            self._merge_btn.configure(state="normal")
        self._report_btn.configure(state="normal")

        if missing:
            messagebox.showwarning(
                "Não encontrados",
                "Termos NÃO encontrados no PDF:\n\n" +
                "\n".join(f"  •  {t}" for t in missing))
        else:
            messagebox.showinfo(
                "Concluído",
                f"Todos os {len(terms)} termos foram encontrados!")

    def _done_cleanup(self) -> None:
        self._start_btn.configure(state="normal")
        self._cancel_btn.configure(state="disabled")

    def _cancel(self) -> None:
        self._ocr_service.cancel()
        self._status.configure(text="Cancelando...")
        self._cancel_btn.configure(state="disabled")

    def _extract_separate(self) -> None:
        if not self._results:
            return
        out_dir = filedialog.askdirectory(title="Selecionar pasta de destino")
        if not out_dir:
            return
        self._progress.set(0)
        threading.Thread(target=self._run_extract,
                         args=(dict(self._results), out_dir), daemon=True).start()

    def _run_extract(self, results: dict, out_dir: str) -> None:
        def on_progress(idx, total, name):
            self.after(0, lambda p=idx/total: self._progress.set(p))
            self.after(0, lambda n=name:
                       self._status.configure(text=f"Extraindo: {n}..."))
        try:
            n = self._pdf_service.extract_multiple(
                self._pdf_path, results, out_dir, on_progress)
            self.after(0, lambda: self._progress.set(1))
            self.after(0, lambda: self._status.configure(text="Extração concluída!"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"{n} PDF(s) extraído(s) em:\n{out_dir}"))
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro ao extrair:\n{err}"))

    def _merge_results(self) -> None:
        if not self._results:
            return
        out = filedialog.asksaveasfilename(
            title="Salvar PDF mesclado", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        all_pages = sorted(set(p for pages in self._results.values() for p in pages))
        self._progress.set(0)
        threading.Thread(target=self._run_merge,
                         args=(all_pages, out), daemon=True).start()

    def _run_merge(self, pages: list[int], out: str) -> None:
        def on_progress(done, total):
            self.after(0, lambda p=done/total: self._progress.set(p))
        try:
            n = self._pdf_service.merge_pages(self._pdf_path, pages, out, on_progress)
            self.after(0, lambda: self._progress.set(1))
            self.after(0, lambda: self._status.configure(text="Mesclagem concluída!"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"{n} página(s) salvas em:\n{out}"))
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro ao mesclar:\n{err}"))

    def _export_report(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Salvar relatório OCR", defaultextension=".txt",
            filetypes=[("Texto", "*.txt")])
        if not path:
            return
        try:
            terms = self._terms_panel.terms
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Relatório OCR — {os.path.basename(self._pdf_path or '')}\n")
                f.write("=" * 60 + "\n\nENCONTRADOS:\n")
                for t in terms:
                    if t in self._results:
                        f.write(f"  {t}  →  páginas: {', '.join(map(str, self._results[t]))}\n")
                f.write("\nNÃO ENCONTRADOS:\n")
                for t in terms:
                    if t not in self._results:
                        f.write(f"  {t}\n")
            messagebox.showinfo("Salvo", f"Relatório salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _clear_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
