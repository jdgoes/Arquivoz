import os

import customtkinter as ctk
from PIL import Image, ImageTk

from . import config
from .config import COLORS as C, WINDOW_TITLE, WINDOW_GEOMETRY, WINDOW_MIN
from .utils import apply_treeview_style
from .tabs.search_tab import SearchTab
from .tabs.merge_tab import MergeTab
from .tabs.ocr_tab import OCRTab
from .tabs.ocr_convert_tab import OCRConvertTab

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")


class ArquivozApp(ctk.CTk):
    """Janela principal do Arquivoz."""

    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(*WINDOW_MIN)
        self.configure(fg_color=C["bg"])

        apply_treeview_style()
        self._build()

        # Ícone definido antes do splash aparecer (200 ms após HWND criado)
        self.after(200, self._set_icon)
        # Splash como CTkToplevel — mesma instância Tk, sem conflito de ícone
        self.after(50, self._start_splash)

    # ── Splash screen ─────────────────────────────────────────────────────────

    def _start_splash(self) -> None:
        logo_path = os.path.join(_ASSETS, "logo.png")

        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True)
        splash.configure(fg_color="#1e1e2e")
        splash.attributes("-topmost", True)

        w, h = 420, 280
        photo = None
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((320, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                splash._photo = photo          # evita garbage-collection
                w = max(420, img.width + 80)
                h = img.height + 90
            except Exception:
                pass

        splash.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        splash.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        if photo:
            ctk.CTkLabel(splash, image=photo, text="").pack(pady=(24, 0))
        else:
            ctk.CTkLabel(splash, text="Arquivoz",
                         font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 0))

        ctk.CTkLabel(splash, text="Carregando...",
                     font=ctk.CTkFont(size=10),
                     text_color="#7f8c8d").pack(pady=(10, 0))

        splash.after(2500, splash.destroy)

    # ── Ícone na barra de tarefas ─────────────────────────────────────────────

    def _set_icon(self) -> None:
        logo_path = os.path.join(_ASSETS, "logo.png")
        if not os.path.exists(logo_path):
            return

        ico_path = os.path.join(_ASSETS, "icon.ico")

        # Gera .ico com todos os tamanhos (incluindo 256 para taskbar)
        try:
            img = Image.open(logo_path).convert("RGBA")
            img.save(ico_path, format="ICO",
                     sizes=[(16, 16), (32, 32), (48, 48),
                            (64, 64), (128, 128), (256, 256)])
        except Exception:
            pass

        # wm_iconbitmap — barra de título
        if os.path.exists(ico_path):
            try:
                self.wm_iconbitmap(ico_path)
            except Exception:
                pass

        # iconphoto(True) — barra de tarefas (Tk nativo)
        try:
            img256 = Image.open(logo_path).convert("RGBA").resize((256, 256), Image.LANCZOS)
            self._icon_ref = ImageTk.PhotoImage(img256)
            self.iconphoto(True, self._icon_ref)
        except Exception:
            pass

    # ── Construção ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_header()
        self._build_tabs()

    def _build_header(self) -> None:
        self._header = ctk.CTkFrame(self, fg_color=C["panel"],
                                    corner_radius=0, height=80)
        self._header.grid(row=0, column=0, sticky="ew")
        self._header.grid_propagate(False)
        self._header.columnconfigure(1, weight=1)

        title_frame = ctk.CTkFrame(self._header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        logo_path = os.path.join(_ASSETS, "logo.png")
        if os.path.exists(logo_path):
            try:
                raw = Image.open(logo_path).convert("RGBA")
                w, h = raw.size
                new_h = 100
                new_w = int(w * new_h / h)
                raw = raw.resize((new_w, new_h), Image.LANCZOS)
                self._logo_ctk = ctk.CTkImage(
                    light_image=raw, dark_image=raw, size=(new_w, new_h))
                ctk.CTkLabel(title_frame, image=self._logo_ctk,
                             text="").pack(side="left", padx=(0, 14))
            except Exception:
                pass

        self._title_label = ctk.CTkLabel(
            title_frame,
            text="Gerencie, pesquise e converta seus PDFs",
            font=ctk.CTkFont(size=12),
            text_color=C["muted"],
        )
        self._title_label.pack(side="left")

        self._theme_btn = ctk.CTkButton(
            self._header,
            text="☀  Modo Claro",
            width=130, height=32,
            fg_color=C["gray"], hover_color=C["gray_h"],
            text_color=C["text"],
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            command=self._toggle_theme,
        )
        self._theme_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def _build_tabs(self) -> None:
        self._tabs = ctk.CTkTabview(
            self,
            fg_color=C["bg"],
            segmented_button_fg_color=C["panel"],
            segmented_button_selected_color=C["accent"],
            segmented_button_selected_hover_color=C["accent_h"],
            segmented_button_unselected_color=C["panel"],
            segmented_button_unselected_hover_color=C["gray"],
            text_color=C["text"],
            text_color_disabled=C["muted"],
        )
        self._tabs.grid(row=1, column=0, sticky="nsew", padx=16, pady=(6, 16))

        t1 = self._tabs.add("  Buscar e Extrair  ")
        t2 = self._tabs.add("  Unir PDFs  ")
        t3 = self._tabs.add("  Busca por OCR  ")
        t4 = self._tabs.add("  Converter para Pesquisável  ")

        SearchTab(t1).pack(fill="both", expand=True)
        MergeTab(t2).pack(fill="both", expand=True)
        OCRTab(t3).pack(fill="both", expand=True)
        OCRConvertTab(t4).pack(fill="both", expand=True)

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self) -> None:
        new_mode = "light" if config.MODE == "dark" else "dark"
        config.set_theme(new_mode)

        ctk.set_appearance_mode("Light" if new_mode == "light" else "Dark")

        self.configure(fg_color=C["bg"])
        self._header.configure(fg_color=C["panel"])
        self._title_label.configure(text_color=C["muted"])
        self._theme_btn.configure(
            text="🌙  Modo Escuro" if new_mode == "light" else "☀  Modo Claro",
            fg_color=C["gray"], hover_color=C["gray_h"],
            text_color=C["text"],
        )

        apply_treeview_style()
        self._tabs.destroy()
        self._build_tabs()
