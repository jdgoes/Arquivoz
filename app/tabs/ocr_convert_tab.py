import os
import threading
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from ..config import COLORS as C
from ..services.ocr_converter_service import OCRConverterService
from ..utils import safe_filename


class OCRConvertTab(ctk.CTkFrame):
    """
    Aba 4 — Converter PDFs digitalizados em PDFs pesquisáveis (com camada OCR).
    Mantém o nome original de cada arquivo. Suporta lote e mesclagem.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._service = OCRConverterService()
        self._files: list[str] = []

        available, error_msg = OCRConverterService.is_available()
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

    # ── UI principal ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=2, minsize=240)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        left = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Arquivos PDF",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 4))

        lf = ctk.CTkFrame(left, fg_color=C["entry"], corner_radius=8)
        lf.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 4))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)

        self._listbox = ctk.CTkTextbox(
            lf, fg_color=C["entry"],
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=C["text"],
            activate_scrollbars=True, state="disabled")
        self._listbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self._file_count = ctk.CTkLabel(left, text="0 arquivos",
                                        text_color=C["muted"],
                                        font=ctk.CTkFont(size=10))
        self._file_count.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 4))

        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))
        ctk.CTkButton(btn_frame, text="+ Adicionar PDFs", height=34,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      command=self._add_files).pack(fill="x", pady=(0, 4))
        ctk.CTkButton(btn_frame, text="Remover último", height=30,
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      command=self._remove_last).pack(fill="x", pady=(0, 4))
        ctk.CTkButton(btn_frame, text="Limpar lista", height=30,
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      command=self._clear_files).pack(fill="x")

    def _build_right_panel(self) -> None:
        right = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(4, weight=1)

        self._build_output_card(right)
        self._build_options_card(right)
        self._build_actions(right)
        self._build_progress(right)
        self._build_results_tree(right)

    def _build_output_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        card.columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="Destino",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6))

        ctk.CTkLabel(card, text="Pasta:",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).grid(
            row=1, column=0, sticky="w", padx=(12, 6), pady=4)

        self._out_dir_var = ctk.StringVar(value="")
        ctk.CTkEntry(card, textvariable=self._out_dir_var,
                     placeholder_text="Selecione a pasta de destino...",
                     fg_color=C["panel"],
                     text_color=C["text"]).grid(
            row=1, column=1, sticky="ew", padx=(0, 6), pady=4)

        ctk.CTkButton(card, text="Selecionar", width=90, height=28,
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      command=self._pick_out_dir).grid(
            row=1, column=2, padx=(0, 12), pady=4)

        ctk.CTkLabel(
            card,
            text="Cada arquivo será salvo com o nome original na pasta selecionada.",
            text_color=C["muted"],
            font=ctk.CTkFont(size=10)).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=12, pady=(0, 6))

        ctk.CTkFrame(card, fg_color=C["border"], height=1).grid(
            row=3, column=0, columnspan=3, sticky="ew", padx=12, pady=4)

        merge_row = ctk.CTkFrame(card, fg_color="transparent")
        merge_row.grid(row=4, column=0, columnspan=3, sticky="ew",
                       padx=12, pady=(2, 10))
        merge_row.columnconfigure(1, weight=1)

        self._merge_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(merge_row, text="Mesclar tudo em um PDF:",
                        variable=self._merge_var,
                        font=ctk.CTkFont(size=11),
                        text_color=C["text"],
                        checkmark_color=C["accent"],
                        fg_color=C["accent"],
                        command=self._toggle_merge).grid(row=0, column=0, sticky="w")

        self._merge_name_var = ctk.StringVar(value="resultado_ocr.pdf")
        self._merge_entry = ctk.CTkEntry(
            merge_row, textvariable=self._merge_name_var,
            state="disabled", width=200,
            fg_color=C["panel"], text_color=C["text"])
        self._merge_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))

    def _build_options_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        card.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))

        ctk.CTkLabel(card, text="Idioma:",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(12, 4), pady=8)
        self._lang_var = ctk.StringVar(value="por (Português)")
        ctk.CTkComboBox(card, variable=self._lang_var, width=175, height=30,
                        values=["por (Português)", "eng (Inglês)", "por+eng (Ambos)"],
                        state="readonly").pack(side="left", padx=(0, 18), pady=8)

        ctk.CTkLabel(card, text="Qualidade (DPI):",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(0, 4))
        self._dpi_var = ctk.StringVar(value="200")
        ctk.CTkSegmentedButton(card, values=["150", "200", "300"],
                               variable=self._dpi_var,
                               selected_color=C["accent"],
                               selected_hover_color=C["accent_h"],
                               width=160).pack(side="left", padx=(0, 18), pady=8)

        ctk.CTkLabel(card, text="Threads:",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text"]).pack(side="left", padx=(0, 4))
        self._workers_var = ctk.StringVar(value="4")
        ctk.CTkComboBox(card, variable=self._workers_var, width=65, height=30,
                        values=["1", "2", "4", "8"],
                        state="readonly").pack(side="left", padx=(0, 12), pady=8)

    def _build_actions(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 4))

        self._start_btn = ctk.CTkButton(
            row, text="Converter PDFs", height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C["accent"], hover_color=C["accent_h"],
            command=self._start)
        self._start_btn.pack(side="left", padx=(0, 8))

        self._cancel_btn = ctk.CTkButton(
            row, text="Cancelar", height=42, width=100,
            fg_color=C["red"], hover_color=C["red_h"],
            command=self._cancel, state="disabled")
        self._cancel_btn.pack(side="left")

    def _build_progress(self, parent) -> None:
        pf = ctk.CTkFrame(parent, fg_color="transparent")
        pf.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 4))
        pf.columnconfigure(0, weight=1)

        self._progress_files = ctk.CTkProgressBar(pf, height=10,
                                                   progress_color=C["accent"])
        self._progress_files.grid(row=0, column=0, sticky="ew")
        self._progress_files.set(0)

        self._progress_pages = ctk.CTkProgressBar(pf, height=5,
                                                   progress_color=C["green"])
        self._progress_pages.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        self._progress_pages.set(0)

        self._status = ctk.CTkLabel(pf, text="", text_color=C["muted"],
                                    font=ctk.CTkFont(size=11), anchor="w")
        self._status.grid(row=2, column=0, sticky="w", pady=(2, 0))

    def _build_results_tree(self, parent) -> None:
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.grid(row=4, column=0, sticky="nsew", padx=14, pady=(4, 0))
        hdr.columnconfigure(0, weight=1)
        hdr.rowconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="Resultados",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        tf = ctk.CTkFrame(hdr, fg_color=C["entry"], corner_radius=8)
        tf.grid(row=1, column=0, sticky="nsew")
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(0, weight=1)

        cols = ("arquivo", "destino", "status")
        self._tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="Dark.Treeview")
        self._tree.heading("arquivo", text="Arquivo original")
        self._tree.heading("destino", text="Salvo como")
        self._tree.heading("status",  text="Status")
        self._tree.column("arquivo", width=220, minwidth=120)
        self._tree.column("destino", width=220, minwidth=120)
        self._tree.column("status",  width=120, minwidth=80, anchor="center")

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0, 4))

        self._tree.tag_configure("ok",      foreground=C["green"])
        self._tree.tag_configure("error",   foreground=C["red"])
        self._tree.tag_configure("running", foreground=C["accent"])
        self._tree.tag_configure("waiting", foreground=C["muted"])

        self._merge_label = ctk.CTkLabel(hdr, text="",
                                         text_color=C["muted"],
                                         font=ctk.CTkFont(size=11))
        self._merge_label.grid(row=2, column=0, sticky="w", pady=(4, 14))

    # ── Arquivos ───────────────────────────────────────────────────────────────

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Selecionar PDFs para converter",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        for p in paths:
            if p not in self._files:
                self._files.append(p)
        self._refresh_listbox()

    def _remove_last(self) -> None:
        if self._files:
            self._files.pop()
            self._refresh_listbox()

    def _clear_files(self) -> None:
        self._files.clear()
        self._refresh_listbox()

    def _refresh_listbox(self) -> None:
        self._listbox.configure(state="normal")
        self._listbox.delete("1.0", "end")
        for f in self._files:
            self._listbox.insert("end", os.path.basename(f) + "\n")
        self._listbox.configure(state="disabled")
        n = len(self._files)
        s = "arquivo" if n == 1 else "arquivos"
        self._file_count.configure(text=f"{n} {s}")

    def _pick_out_dir(self) -> None:
        d = filedialog.askdirectory(title="Selecionar pasta de destino")
        if d:
            self._out_dir_var.set(d)

    def _toggle_merge(self) -> None:
        state = "normal" if self._merge_var.get() else "disabled"
        self._merge_entry.configure(state=state)

    def _get_lang(self) -> str:
        return self._lang_var.get().split(" ")[0]

    def _build_jobs(self, out_dir: str) -> list[tuple[str, str]]:
        jobs = []
        for inp in self._files:
            filename = os.path.basename(inp)
            jobs.append((inp, os.path.join(out_dir, filename)))
        return jobs

    # ── Processamento ──────────────────────────────────────────────────────────

    def _start(self) -> None:
        if not self._files:
            messagebox.showwarning("Atenção", "Adicione ao menos um arquivo PDF.")
            return

        out_dir = self._out_dir_var.get().strip()
        if not out_dir:
            messagebox.showwarning("Atenção", "Selecione a pasta de destino.")
            return

        jobs = self._build_jobs(out_dir)

        overwrites = [os.path.basename(i) for i, o in jobs
                      if os.path.abspath(i) == os.path.abspath(o)]
        if overwrites:
            if not messagebox.askyesno(
                "Atenção",
                f"{len(overwrites)} arquivo(s) serão sobrescritos.\nDeseja continuar?"):
                return

        self._progress_files.set(0)
        self._progress_pages.set(0)
        self._status.configure(text="")
        self._merge_label.configure(text="")
        self._start_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")

        self._clear_tree()
        tree_ids: dict[int, str] = {}
        for i, (inp, out) in enumerate(jobs):
            iid = self._tree.insert("", "end",
                                    values=(os.path.basename(inp),
                                            os.path.basename(out),
                                            "Aguardando"),
                                    tags=("waiting",))
            tree_ids[i] = iid

        threading.Thread(
            target=self._run, args=(jobs, tree_ids), daemon=True
        ).start()

    def _run(self, jobs: list[tuple[str, str]],
             tree_ids: dict[int, str]) -> None:
        total_files = len(jobs)

        def on_file_start(i, total, name):
            iid = tree_ids[i]
            inp, out = jobs[i]

            def _upd(i=i, total=total, name=name,
                     iid=iid, inp=inp, out=out):
                self._status.configure(
                    text=f"Convertendo: {name}  ({i + 1}/{total})")
                self._progress_files.set(i / total)
                self._progress_pages.set(0)
                self._tree.item(iid, values=(
                    os.path.basename(inp),
                    os.path.basename(out),
                    "Convertendo…"), tags=("running",))

            self.after(0, _upd)

        def on_page_progress(done, total):
            pct = done / total if total > 0 else 1.0
            self.after(0, lambda p=pct: self._progress_pages.set(p))

        def on_file_done(i, total, name, ok, err):
            iid = tree_ids[i]
            inp, out = jobs[i]
            tag   = "ok" if ok else "error"
            label = "✓ Concluído" if ok else "✗ Erro"

            def _upd(i=i, total=total, iid=iid,
                     inp=inp, out=out, tag=tag, label=label):
                self._tree.item(iid, values=(
                    os.path.basename(inp),
                    os.path.basename(out),
                    label), tags=(tag,))
                self._progress_files.set((i + 1) / total)

            self.after(0, _upd)

        successful = self._service.convert_batch(
            jobs,
            dpi=int(self._dpi_var.get()),
            lang=self._get_lang(),
            workers=int(self._workers_var.get()),
            on_file_start=on_file_start,
            on_page_progress=on_page_progress,
            on_file_done=on_file_done,
        )

        merge_path = None
        if (self._merge_var.get() and successful
                and not self._service.was_cancelled()):
            merge_path = self._do_merge(
                successful, self._out_dir_var.get().strip())

        self.after(0, lambda: self._finish(successful, total_files, merge_path))

    def _do_merge(self, paths: list[str], out_dir: str) -> str | None:
        merge_name = self._merge_name_var.get().strip() or "resultado_ocr.pdf"
        if not merge_name.lower().endswith(".pdf"):
            merge_name += ".pdf"
        merge_path = os.path.join(out_dir, safe_filename(merge_name))
        try:
            self._service.merge_pdfs(paths, merge_path)
            return merge_path
        except Exception as exc:
            self.after(0, lambda e=str(exc): messagebox.showerror(
                "Erro ao mesclar", f"Não foi possível mesclar os PDFs:\n{e}"))
            return None

    def _finish(self, successful: list[str], total: int,
                merge_path: str | None) -> None:
        self._progress_files.set(1)
        self._progress_pages.set(1)
        self._start_btn.configure(state="normal")
        self._cancel_btn.configure(state="disabled")

        if self._service.was_cancelled():
            self._status.configure(text="Cancelado.")
            return

        n_ok  = len(successful)
        n_err = total - n_ok
        summary = f"{n_ok} arquivo(s) convertido(s)"
        if n_err:
            summary += f"  ·  {n_err} com erro"
        self._status.configure(text=summary)

        if merge_path:
            self._merge_label.configure(
                text=f"PDF mesclado: {os.path.basename(merge_path)}",
                text_color=C["green"])

        if n_ok == total:
            msg = f"Todos os {total} arquivo(s) convertidos com sucesso!"
            if merge_path:
                msg += f"\n\nPDF mesclado salvo em:\n{merge_path}"
            messagebox.showinfo("Concluído", msg)
        else:
            messagebox.showwarning(
                "Concluído com erros",
                f"{n_ok} de {total} arquivo(s) convertidos.\n"
                f"{n_err} falharam — verifique os itens em vermelho.")

    def _cancel(self) -> None:
        self._service.cancel()
        self._status.configure(text="Cancelando...")
        self._cancel_btn.configure(state="disabled")

    def _clear_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
