import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..config import COLORS as C
from ..services.pdf_service import PDFService


class MergeTab(ctk.CTkFrame):
    """Aba 2 — Unir múltiplos PDFs em um único arquivo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._pdf_service = PDFService()
        self._files: list[str] = []

        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Organize os PDFs na ordem desejada e clique em Unir PDFs.",
            text_color=C["muted"],
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        content = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_list(content)
        self._build_controls(content)
        self._build_progress(content)
        self._build_merge_button(content)

    def _build_list(self, parent) -> None:
        lf = ctk.CTkFrame(parent, fg_color=C["entry"], corner_radius=8)
        lf.grid(row=0, column=0, sticky="nsew", padx=14, pady=(14, 6))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)

        self._listbox = tk.Listbox(
            lf, bg=C["entry"], fg=C["text"],
            selectbackground=C["accent"], selectforeground="#ffffff",
            font=("Segoe UI", 11), relief="flat",
            bd=0, highlightthickness=0, activestyle="none")
        self._listbox.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = tk.Scrollbar(lf, orient="vertical",
                           command=self._listbox.yview,
                           bg=C["panel"], troughcolor=C["bg"])
        self._listbox.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", pady=8)

    def _build_controls(self, parent) -> None:
        ctrl = ctk.CTkFrame(parent, fg_color="transparent")
        ctrl.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))

        ctk.CTkButton(ctrl, text="Adicionar PDFs", height=32,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      command=self._add_pdfs).pack(side="left", padx=(0, 8))

        ctk.CTkButton(ctrl, text="↑ Acima", height=32,
                      fg_color=C["entry"], hover_color=C["gray"],
                      text_color=C["text"],
                      command=lambda: self._move(-1)).pack(side="left", padx=(0, 5))

        ctk.CTkButton(ctrl, text="↓ Abaixo", height=32,
                      fg_color=C["entry"], hover_color=C["gray"],
                      text_color=C["text"],
                      command=lambda: self._move(1)).pack(side="left", padx=(0, 8))

        ctk.CTkButton(ctrl, text="Remover", height=32,
                      fg_color=C["red"], hover_color=C["red_h"],
                      command=self._remove_pdf).pack(side="left", padx=(0, 6))

        ctk.CTkButton(ctrl, text="Limpar", height=32,
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      command=self._clear).pack(side="left")

        self._count_label = ctk.CTkLabel(ctrl, text="",
                                         text_color=C["muted"],
                                         font=ctk.CTkFont(size=11))
        self._count_label.pack(side="right", padx=4)

    def _build_progress(self, parent) -> None:
        self._progress = ctk.CTkProgressBar(parent, height=6,
                                             progress_color=C["accent"])
        self._progress.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 4))
        self._progress.set(0)

        self._status = ctk.CTkLabel(parent, text="",
                                    text_color=C["muted"],
                                    font=ctk.CTkFont(size=11))
        self._status.grid(row=3, column=0, sticky="w", padx=14)

    def _build_merge_button(self, parent) -> None:
        ctk.CTkButton(parent, text="Unir PDFs", height=44,
                      fg_color=C["green"], hover_color=C["green_h"],
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._merge).grid(
            row=4, column=0, padx=14, pady=14, sticky="ew")

    # ── Lógica ─────────────────────────────────────────────────────────────────

    def _add_pdfs(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Selecionar PDFs", filetypes=[("PDF", "*.pdf")])
        for p in paths:
            if p not in self._files:
                self._files.append(p)
                self._listbox.insert(tk.END, os.path.basename(p))
        self._update_count()

    def _remove_pdf(self) -> None:
        sel = self._listbox.curselection()
        if sel:
            self._files.pop(sel[0])
            self._listbox.delete(sel[0])
            self._update_count()

    def _clear(self) -> None:
        self._files.clear()
        self._listbox.delete(0, tk.END)
        self._progress.set(0)
        self._status.configure(text="")
        self._update_count()

    def _move(self, direction: int) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self._files):
            return
        self._files[idx], self._files[new_idx] = self._files[new_idx], self._files[idx]
        a, b = self._listbox.get(idx), self._listbox.get(new_idx)
        self._listbox.delete(idx)
        self._listbox.insert(idx, b)
        self._listbox.delete(new_idx)
        self._listbox.insert(new_idx, a)
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(new_idx)

    def _update_count(self) -> None:
        n = len(self._files)
        s = "arquivo" if n == 1 else "arquivos"
        self._count_label.configure(text=f"{n} {s}")

    def _merge(self) -> None:
        if len(self._files) < 2:
            messagebox.showwarning("Atenção", "Adicione pelo menos 2 PDFs para unir.")
            return
        out = filedialog.asksaveasfilename(
            title="Salvar PDF unificado", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        self._progress.set(0)
        self._status.configure(text="Combinando PDFs...")
        threading.Thread(target=self._run_merge,
                         args=(list(self._files), out), daemon=True).start()

    def _run_merge(self, files: list[str], out: str) -> None:
        def on_progress(idx, total, name):
            self.after(0, lambda p=(idx+1)/total: self._progress.set(p))
            self.after(0, lambda n=name:
                       self._status.configure(text=f"Adicionando: {n}"))
        try:
            self._pdf_service.merge_files(files, out, on_progress)
            self.after(0, lambda: self._progress.set(1))
            self.after(0, lambda: self._status.configure(text="Concluído!"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"PDF salvo em:\n{out}"))
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erro", f"Erro ao unir PDFs:\n{err}"))
