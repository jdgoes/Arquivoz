import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from ..config import COLORS as C


class TermsPanel(ctk.CTkFrame):
    """
    Painel lateral reutilizável para gerenciar uma lista de termos de busca.
    Emite callbacks: on_change(terms: list[str])
    """

    def __init__(self, master, title: str, placeholder: str,
                 on_change=None, **kwargs):
        super().__init__(master, fg_color=C["panel"], width=290,
                         corner_radius=12, **kwargs)
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        self._terms: list[str] = []
        self._on_change = on_change

        self._build(title, placeholder)

    def _build(self, title: str, placeholder: str) -> None:
        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C["text"]).grid(
            row=0, column=0, pady=(14, 6), padx=14, sticky="w")

        # Campo de entrada
        ir = ctk.CTkFrame(self, fg_color="transparent")
        ir.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))
        ir.columnconfigure(0, weight=1)

        self._entry = ctk.CTkEntry(
            ir, placeholder_text=placeholder,
            fg_color=C["entry"], border_width=0, height=34,
            text_color=C["text"])
        self._entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._entry.bind("<Return>", lambda _: self._add())

        ctk.CTkButton(ir, text="+", width=34, height=34,
                      fg_color=C["accent"], hover_color=C["accent_h"],
                      command=self._add).grid(row=0, column=1)

        # Lista
        lf = ctk.CTkFrame(self, fg_color=C["entry"], corner_radius=8)
        lf.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 6))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._listbox = tk.Listbox(
            lf, bg=C["entry"], fg=C["text"],
            selectbackground=C["accent"], selectforeground="#ffffff",
            font=("Segoe UI", 11), relief="flat",
            bd=0, highlightthickness=0, activestyle="none")
        self._listbox.pack(fill="both", expand=True, padx=6, pady=6)

        # Botões de ação
        br = ctk.CTkFrame(self, fg_color="transparent")
        br.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 6))
        ctk.CTkButton(br, text="Remover",
                      fg_color=C["red"], hover_color=C["red_h"],
                      height=30, command=self._remove).pack(side="left", padx=(0, 6))
        ctk.CTkButton(br, text="Limpar",
                      fg_color=C["gray"], hover_color=C["gray_h"],
                      text_color=C["text"],
                      height=30, command=self._clear).pack(side="left")

        ctk.CTkButton(self, text="Importar Lista (.txt)", height=32,
                      fg_color=C["entry"], hover_color=C["gray"],
                      text_color=C["text"],
                      border_width=1, border_color=C["border"],
                      command=self._import).grid(
            row=4, column=0, sticky="ew", padx=14, pady=(0, 6))

        self._count_label = ctk.CTkLabel(
            self, text="0 itens",
            text_color=C["muted"], font=ctk.CTkFont(size=11))
        self._count_label.grid(row=5, column=0, pady=(0, 12))

    # ── Interface pública ──────────────────────────────────────────────────────

    @property
    def terms(self) -> list[str]:
        return list(self._terms)

    def set_terms(self, terms: list[str]) -> None:
        self._clear()
        for t in terms:
            self._add_term(t)

    # ── Ações ──────────────────────────────────────────────────────────────────

    def _add(self) -> None:
        term = self._entry.get().strip()
        if not term:
            return
        self._add_term(term)
        self._entry.delete(0, tk.END)

    def _add_term(self, term: str) -> None:
        if term not in self._terms:
            self._terms.append(term)
            self._listbox.insert(tk.END, term)
            self._notify()

    def _remove(self) -> None:
        sel = self._listbox.curselection()
        if sel:
            self._terms.pop(sel[0])
            self._listbox.delete(sel[0])
            self._notify()

    def _clear(self) -> None:
        self._terms.clear()
        self._listbox.delete(0, tk.END)
        self._notify()

    def _import(self) -> None:
        path = filedialog.askopenfilename(
            title="Importar lista de termos",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not path:
            return
        added = 0
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    term = line.strip()
                    if term and term not in self._terms:
                        self._terms.append(term)
                        self._listbox.insert(tk.END, term)
                        added += 1
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}")
            return
        self._notify()
        s = "item importado" if added == 1 else "itens importados"
        messagebox.showinfo("Importação concluída", f"{added} {s}.")

    def _notify(self) -> None:
        n = len(self._terms)
        s = "item" if n == 1 else "itens"
        self._count_label.configure(text=f"{n} {s}")
        if self._on_change:
            self._on_change(list(self._terms))
