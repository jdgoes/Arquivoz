from tkinter import ttk
from .config import COLORS as C


def safe_filename(name: str) -> str:
    """Converte um nome em string segura para nome de arquivo."""
    keep = set(" _-áéíóúàèìòùãõâêîôûçÁÉÍÓÚÀÈÌÒÙÃÕÂÊÎÔÛÇ")
    return "".join(c if (c.isalnum() or c in keep) else "_" for c in name).strip()


def apply_treeview_style() -> None:
    """Aplica o tema atual ao ttk.Treeview. Pode ser chamado novamente ao trocar o tema."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Dark.Treeview",
        background=C["entry"], foreground=C["text"],
        fieldbackground=C["entry"], rowheight=30,
        font=("Segoe UI", 10), borderwidth=0,
    )
    style.configure(
        "Dark.Treeview.Heading",
        background=C["panel"], foreground=C["muted"],
        font=("Segoe UI", 10, "bold"), relief="flat",
        borderwidth=0,
    )
    style.map(
        "Dark.Treeview",
        background=[("selected", C["accent"])],
        foreground=[("selected", "#ffffff")],
    )
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=C["panel"], troughcolor=C["bg"],
        arrowcolor=C["muted"], borderwidth=0,
    )
