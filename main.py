import sys
import os

# Define a identidade do processo ANTES de qualquer janela.
# Sem isso o Windows agrupa a janela com pythonw.exe e mostra o ícone do Python.
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Arquivoz.App.1")
except Exception:
    pass

if __name__ == "__main__":
    from app.app import ArquivozApp
    ArquivozApp().mainloop()
