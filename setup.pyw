"""
Arquivoz — Instalador
Instala todas as dependências, Tesseract OCR e cria atalhos no Desktop e Menu Iniciar.
"""
import sys
import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Bootstrap: instala customtkinter se necessário ────────────────────────────
def _bootstrap():
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        root = tk.Tk()
        root.title("Arquivoz — Preparando...")
        root.geometry("420x120")
        root.configure(bg="#1e1e2e")
        root.resizable(False, False)
        tk.Label(root, text="Preparando o instalador...",
                 bg="#1e1e2e", fg="white",
                 font=("Segoe UI", 12)).pack(pady=16)
        pb = ttk.Progressbar(root, mode="indeterminate", length=340)
        pb.pack()
        pb.start(10)
        root.update()
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "customtkinter", "--quiet"],
            capture_output=True)
        root.destroy()

_bootstrap()

import customtkinter as ctk  # noqa: E402

# ── Constantes ────────────────────────────────────────────────────────────────
DARK_BG  = "#1e1e2e"
PANEL_BG = "#2a2a3e"
ENTRY_BG = "#313145"
GREEN    = "#2ecc71"
GREEN_H  = "#27ae60"
RED      = "#e74c3c"
TEXT     = "#dfe6e9"
MUTED    = "#7f8c8d"
ACCENT   = "#3498db"
ORANGE   = "#e67e22"

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Origem dos arquivos do app (quando frozen, usa sys._MEIPASS)
if getattr(sys, 'frozen', False):
    SOURCE_DIR = sys._MEIPASS
else:
    SOURCE_DIR = APP_DIR

# Caminho padrão de instalação
DEFAULT_INSTALL = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Arquivoz")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Termos de uso ─────────────────────────────────────────────────────────────
TERMS_TEXT = """TERMOS DE USO — ARQUIVOZ
Versão 1.0  |  Março de 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ACEITAÇÃO DOS TERMOS
Ao instalar, copiar ou utilizar o Arquivoz ("Software"), você ("Usuário") declara ter lido, compreendido e concordado integralmente com estes Termos de Uso. Caso não concorde com qualquer disposição aqui prevista, interrompa imediatamente a instalação e não utilize o Software.

2. CONCESSÃO DE LICENÇA
O desenvolvedor do Arquivoz concede ao Usuário uma licença pessoal, intransferível, não exclusiva e gratuita para instalar e utilizar o Software exclusivamente para fins pessoais ou internos, sem fins comerciais. É expressamente vedado:
  a) Redistribuir, vender, sublicenciar ou alugar o Software;
  b) Modificar, descompilar, fazer engenharia reversa ou derivar obras do Software sem autorização prévia e por escrito do desenvolvedor;
  c) Remover avisos de direitos autorais ou identificações do Software.

3. DESCRIÇÃO DO SOFTWARE
O Arquivoz é uma ferramenta desktop para gerenciamento, pesquisa e conversão de arquivos PDF. Suas funcionalidades incluem busca e extração de texto, unificação de documentos, reconhecimento óptico de caracteres (OCR) e conversão de PDFs para formato pesquisável, com suporte aos idiomas Português e Inglês.

4. DEPENDÊNCIAS DE TERCEIROS
Para seu funcionamento, o Arquivoz instala e utiliza componentes de terceiros distribuídos sob licenças de código aberto:
  • Tesseract OCR — Apache License 2.0 (UB Mannheim / Google)
  • customtkinter — MIT License
  • pdfplumber — MIT License
  • PyMuPDF (fitz) — GNU Affero GPL v3
  • pypdf — BSD License
  • Pillow — HPND License
  • pytesseract — Apache License 2.0
O Usuário reconhece e aceita os termos de licença de cada componente instalado. O desenvolvedor do Arquivoz não é responsável por eventuais alterações nas licenças de terceiros.

5. PRIVACIDADE E PROTEÇÃO DE DADOS
O Arquivoz processa todos os arquivos e documentos exclusivamente no dispositivo local do Usuário. Nenhum dado, documento, conteúdo ou informação pessoal é transmitido a servidores externos, terceiros ou qualquer outro destinatário. A única comunicação de rede realizada pelo instalador ocorre para download de dependências (pacotes Python e Tesseract OCR) durante o processo de instalação, conforme indicado no log de progresso.

6. ISENÇÃO DE GARANTIAS
O Software é fornecido "NO ESTADO EM QUE SE ENCONTRA" ("AS IS"), sem garantias de qualquer natureza, expressas ou implícitas, incluindo, sem limitação:
  • Garantia de adequação a um propósito específico;
  • Garantia de não violação de direitos de terceiros;
  • Garantia de ausência de erros, interrupções ou perda de dados;
  • Garantia de compatibilidade com todo hardware ou sistema operacional.
O Usuário assume integralmente os riscos decorrentes do uso do Software.

7. LIMITAÇÃO DE RESPONSABILIDADE
Na máxima extensão permitida pela legislação aplicável, o desenvolvedor não será responsável por quaisquer danos diretos, indiretos, incidentais, especiais, exemplares ou consequenciais decorrentes do uso ou da impossibilidade de uso do Software, incluindo, sem limitação: perda de dados, corrupção de arquivos, interrupção de atividades, lucros cessantes ou danos morais, ainda que tenha sido advertido da possibilidade de tais danos.

8. ATUALIZAÇÕES E MODIFICAÇÕES
O desenvolvedor reserva-se o direito de lançar atualizações, correções ou novas versões do Software a qualquer momento, sem aviso prévio. O uso continuado após a disponibilização de nova versão implica aceitação dos termos revisados. O desenvolvedor também pode modificar, suspender ou descontinuar o Software, no todo ou em parte, sem responsabilidade ao Usuário.

9. RESCISÃO
Esta licença vigora enquanto o Usuário cumprir estes Termos. O descumprimento de qualquer disposição implicará rescisão automática da licença, obrigando o Usuário a remover imediatamente todas as cópias do Software de seus dispositivos.

10. DISPOSIÇÕES GERAIS
  a) Integralidade: Estes Termos constituem o acordo integral entre as partes quanto ao Software, substituindo quaisquer negociações, declarações ou acordos anteriores.
  b) Divisibilidade: Caso alguma disposição seja considerada inválida ou inexequível, as demais permanecerão em pleno vigor.
  c) Renúncia: A tolerância do desenvolvedor em relação ao descumprimento de qualquer disposição não constituirá renúncia ao direito de exigi-la futuramente.

11. LEI APLICÁVEL E FORO
Estes Termos são regidos e interpretados de acordo com as leis da República Federativa do Brasil. Fica eleito o foro da comarca do domicílio do desenvolvedor para dirimir quaisquer controvérsias decorrentes deste instrumento, com renúncia expressa a qualquer outro, por mais privilegiado que seja.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ao prosseguir com a instalação, o Usuário declara ter lido e aceito na íntegra
todos os termos e condições acima estabelecidos.
"""


# ── Python executável (sistema) ───────────────────────────────────────────────
def _find_system_python() -> str:
    """Localiza o Python do sistema quando rodando como EXE congelado."""
    for cmd in ['pythonw', 'python', 'py']:
        try:
            r = subprocess.run(
                [cmd, '-c', 'import sys; print(sys.executable)'],
                capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return r.stdout.strip()
        except Exception:
            continue
    return 'python'

PYTHON_EXE = sys.executable if not getattr(sys, 'frozen', False) else _find_system_python()


# ── Helpers de ícone ──────────────────────────────────────────────────────────
def _resolve_ico() -> str:
    """Retorna o caminho do .ico, gerando-o da logo se necessário."""
    candidates_ico  = [os.path.join(SOURCE_DIR, "app", "assets", "icon.ico")]
    candidates_logo = [
        os.path.join(SOURCE_DIR, "logo.png"),
        os.path.join(SOURCE_DIR, "app", "assets", "logo.png"),
    ]

    for p in candidates_ico:
        if os.path.exists(p):
            return p

    # Gera o .ico a partir da logo
    for logo in candidates_logo:
        if os.path.exists(logo):
            try:
                from PIL import Image
                img = Image.open(logo).convert("RGBA")
                ico_path = candidates_ico[0]
                os.makedirs(os.path.dirname(ico_path), exist_ok=True)
                img.save(ico_path, format="ICO",
                         sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
                return ico_path
            except Exception:
                pass
    return ""


# ── Funções de instalação ─────────────────────────────────────────────────────
def install_pip_packages(log):
    packages = ["customtkinter", "pdfplumber", "pypdf", "Pillow",
                "pymupdf", "pytesseract"]
    log(f"Instalando {len(packages)} pacotes Python...")
    result = subprocess.run(
        [PYTHON_EXE, "-m", "pip", "install"] + packages +
        ["--quiet", "--no-warn-script-location"],
        capture_output=True, text=True)
    if result.returncode != 0:
        log(f"AVISO: {result.stderr[:200]}")
    else:
        log("  Pacotes Python: OK")
    return result.returncode == 0


def find_tesseract():
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(local_appdata, "Tesseract-OCR", "tesseract.exe"),
        os.path.join(APP_DIR, "tesseract", "tesseract.exe"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


def install_tesseract(log):
    existing = find_tesseract()
    if existing:
        log(f"  Tesseract: já instalado")
        return True, os.path.dirname(existing)

    log("  Tesseract não encontrado. Baixando instalador...")
    installer = os.path.join(os.environ.get("TEMP", APP_DIR), "tess_setup.exe")

    ps_download = (
        "try {"
        "  $r = Invoke-RestMethod 'https://api.github.com/repos/UB-Mannheim/tesseract/releases/latest';"
        "  $a = $r.assets | Where-Object { $_.name -match 'w64-setup.*\\.exe$' } | Select -First 1;"
        f"  Invoke-WebRequest -Uri $a.browser_download_url -OutFile '{installer}' -UseBasicParsing;"
        "  Write-Host ('OK:' + $r.tag_name)"
        "} catch { Write-Host ('ERR:' + $_.Exception.Message) }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_download],
        capture_output=True, text=True, timeout=180)

    if "ERR:" in result.stdout or not os.path.exists(installer):
        log("  ERRO: não foi possível baixar o Tesseract.")
        log("  Baixe manualmente: github.com/UB-Mannheim/tesseract/wiki")
        return False, None

    log("  Instalando Tesseract (aguarde)...")
    subprocess.run([installer, "/S"], timeout=120)

    tess_dir = r"C:\Program Files\Tesseract-OCR"
    if os.path.exists(os.path.join(tess_dir, "tesseract.exe")):
        log("  Tesseract: instalado com sucesso")
        return True, tess_dir
    log("  AVISO: instalação pode ter sido bloqueada.")
    return False, None


def install_tessdata(tess_dir: str, install_dir: str, log):
    import urllib.request

    local_tessdata = os.path.join(install_dir, "tessdata")
    os.makedirs(local_tessdata, exist_ok=True)

    system_tessdata = os.path.join(tess_dir, "tessdata") if tess_dir else None

    urls = {
        "eng": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata",
        "por": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata",
    }

    for lang, url in urls.items():
        dest = os.path.join(local_tessdata, f"{lang}.traineddata")
        if os.path.exists(dest):
            log(f"  {lang}.traineddata: já disponível")
            continue

        copied = False
        if system_tessdata:
            src = os.path.join(system_tessdata, f"{lang}.traineddata")
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dest)
                    log(f"  {lang}.traineddata: copiado do sistema")
                    copied = True
                except OSError:
                    pass

        if not copied:
            log(f"  Baixando {lang}.traineddata...")
            try:
                urllib.request.urlretrieve(url, dest)
                sz = os.path.getsize(dest) // 1024
                log(f"  {lang}.traineddata: baixado ({sz} KB)")
            except Exception as e:
                log(f"  AVISO: falha ao obter {lang}.traineddata: {e}")

    return os.path.exists(os.path.join(local_tessdata, "por.traineddata"))


def copy_app_files(install_dir: str, log) -> bool:
    """Copia os arquivos do app para o diretório de instalação."""
    try:
        log(f"  Copiando arquivos para: {install_dir}")
        os.makedirs(install_dir, exist_ok=True)

        items = ["app", "main.py", "requirements.txt", "logo.png"]
        tessdata_src = os.path.join(SOURCE_DIR, "tessdata")
        if os.path.exists(tessdata_src):
            items.append("tessdata")

        for item in items:
            src = os.path.join(SOURCE_DIR, item)
            dst = os.path.join(install_dir, item)
            if not os.path.exists(src):
                log(f"  (ignorado: {item} não encontrado na origem)")
                continue
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            log(f"  Copiado: {item}")

        log("  Arquivos copiados: OK")
        return True
    except Exception as e:
        log(f"  ERRO ao copiar arquivos: {e}")
        return False


def create_shortcut(target_path: str, shortcut_path: str, working_dir: str,
                    description: str, icon_path: str = "") -> bool:
    pythonw = PYTHON_EXE.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = PYTHON_EXE

    icon_line = f'$s.IconLocation = "{icon_path}";' if icon_path else ""
    ps = (
        f'$sh = New-Object -ComObject WScript.Shell;'
        f'$s = $sh.CreateShortcut("{shortcut_path}");'
        f'$s.TargetPath = "{pythonw}";'
        f'$s.Arguments = \'"{target_path}"\';'
        f'$s.WorkingDirectory = "{working_dir}";'
        f'$s.Description = "{description}";'
        f'{icon_line}'
        f'$s.Save()'
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True)
    return result.returncode == 0


def create_shortcuts(install_dir: str, log):
    main_py   = os.path.join(install_dir, "main.py")
    icon_path = os.path.join(install_dir, "app", "assets", "icon.ico")

    desktop  = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut = os.path.join(desktop, "Arquivoz.lnk")
    if create_shortcut(main_py, shortcut, install_dir, "Arquivoz", icon_path):
        log("  Atalho Desktop: criado")
    else:
        log("  AVISO: não foi possível criar atalho no Desktop.")

    start_menu = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs")
    if os.path.exists(start_menu):
        sm_shortcut = os.path.join(start_menu, "Arquivoz.lnk")
        if create_shortcut(main_py, sm_shortcut, install_dir, "Arquivoz", icon_path):
            log("  Menu Iniciar: criado")


# ── Interface do instalador ───────────────────────────────────────────────────
class InstallerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Arquivoz — Instalação")
        self.geometry("600x620")
        self.resizable(False, False)
        self.configure(fg_color=DARK_BG)
        self._install_path = DEFAULT_INSTALL
        # Ícone da janela do instalador
        self.after(150, self._apply_window_icon)
        self._build()

    def _apply_window_icon(self):
        ico = _resolve_ico()
        if ico:
            try:
                self.wm_iconbitmap(ico)
            except Exception:
                pass
        logo = next(
            (p for p in [os.path.join(SOURCE_DIR, "logo.png"),
                         os.path.join(SOURCE_DIR, "app", "assets", "logo.png")]
             if os.path.exists(p)), None)
        if logo:
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo).convert("RGBA").resize((256, 256), Image.LANCZOS)
                self._win_icon_ref = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._win_icon_ref)
            except Exception:
                pass

    def _build(self):
        # ── Cabeçalho ─────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        logo_shown = False
        for logo_candidate in [
            os.path.join(SOURCE_DIR, "logo.png"),
            os.path.join(SOURCE_DIR, "app", "assets", "logo.png"),
        ]:
            if os.path.exists(logo_candidate):
                try:
                    from PIL import Image
                    img = Image.open(logo_candidate).convert("RGBA")
                    h_logo = 56
                    w_logo = int(img.width * h_logo / img.height)
                    img = img.resize((w_logo, h_logo), Image.LANCZOS)
                    self._logo_img = ctk.CTkImage(
                        light_image=img, dark_image=img, size=(w_logo, h_logo))
                    ctk.CTkLabel(hdr, image=self._logo_img, text="").pack(
                        side="left", padx=16, pady=12)
                    logo_shown = True
                    break
                except Exception:
                    pass

        if not logo_shown:
            ctk.CTkLabel(hdr, text="  Arquivoz",
                         font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=TEXT).pack(side="left", padx=24, pady=20)

        ctk.CTkLabel(hdr, text="Instalação",
                     font=ctk.CTkFont(size=13), text_color=MUTED).pack(
            side="left", pady=24)

        # ── Container de etapas ───────────────────────────────────────────
        self._container = ctk.CTkFrame(self, fg_color=DARK_BG)
        self._container.pack(fill="both", expand=True)

        self._show_welcome()

    # ── Etapa 1: Bem-vindo ────────────────────────────────────────────────
    def _show_welcome(self):
        self._clear_container()
        f = ctk.CTkFrame(self._container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=24)

        ctk.CTkLabel(f, text="Bem-vindo ao Arquivoz",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 14))

        info = (
            "Este instalador irá configurar o Arquivoz no seu computador.\n\n"
            "O que será instalado:\n"
            "  • Bibliotecas Python necessárias\n"
            "  • Tesseract OCR (para leitura de documentos escaneados)\n"
            "  • Dados do idioma Português\n"
            "  • Atalhos no Desktop e Menu Iniciar\n\n"
            "Requisito: Python 3.10+ instalado no sistema."
        )
        ctk.CTkLabel(f, text=info, font=ctk.CTkFont(size=12),
                     text_color=TEXT, justify="left",
                     fg_color=PANEL_BG, corner_radius=8,
                     wraplength=480).pack(fill="x", pady=8, ipady=14, ipadx=16)

        ver = sys.version.split()[0]
        ctk.CTkLabel(f, text=f"Python detectado: {ver}",
                     text_color=GREEN, font=ctk.CTkFont(size=11)).pack(pady=(6, 0))

        # Seleção de caminho
        path_frame = ctk.CTkFrame(f, fg_color=PANEL_BG, corner_radius=8)
        path_frame.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(path_frame, text="Pasta de instalação:",
                     font=ctk.CTkFont(size=11), text_color=TEXT).pack(
            anchor="w", padx=12, pady=(10, 4))
        row = ctk.CTkFrame(path_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))
        row.columnconfigure(0, weight=1)
        self._path_var = tk.StringVar(value=self._install_path)
        ctk.CTkEntry(row, textvariable=self._path_var,
                     fg_color=ENTRY_BG, border_width=0,
                     height=34, font=ctk.CTkFont(size=11)).grid(
            row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(row, text="Procurar", width=84, height=34,
                      fg_color=ACCENT, hover_color="#2980b9",
                      command=self._browse_path).grid(row=0, column=1)

        ctk.CTkButton(f, text="Próximo  →", height=44, width=200,
                      fg_color=ACCENT, hover_color="#2980b9",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._go_to_terms).pack(pady=(20, 0))

    def _browse_path(self):
        path = filedialog.askdirectory(
            title="Selecione a pasta de instalação",
            initialdir=os.path.dirname(self._path_var.get()))
        if path:
            self._path_var.set(os.path.normpath(os.path.join(path, "Arquivoz")))

    # ── Etapa 2: Termos de uso ────────────────────────────────────────────
    def _go_to_terms(self):
        self._install_path = os.path.normpath(self._path_var.get())
        self._show_terms()

    def _show_terms(self):
        self._clear_container()
        f = ctk.CTkFrame(self._container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(f, text="Termos de Uso",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(f, text="Leia atentamente antes de continuar.",
                     font=ctk.CTkFont(size=11), text_color=MUTED).pack(pady=(0, 10))

        # Área de texto com scroll
        txt_frame = tk.Frame(f, bg=ENTRY_BG, bd=0)
        txt_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(txt_frame, bg=PANEL_BG, troughcolor=ENTRY_BG,
                          relief="flat", bd=0, width=10)
        sb.pack(side="right", fill="y", padx=(0, 2))

        txt = tk.Text(txt_frame, bg=ENTRY_BG, fg=TEXT,
                      font=("Consolas", 9), relief="flat", bd=0,
                      highlightthickness=0, wrap="word",
                      yscrollcommand=sb.set, cursor="arrow",
                      state="normal", padx=12, pady=10)
        txt.insert("1.0", TERMS_TEXT)
        txt.configure(state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        sb.config(command=txt.yview)

        # Checkbox de aceite
        bottom = ctk.CTkFrame(f, fg_color="transparent")
        bottom.pack(fill="x", pady=(10, 0))

        self._accept_var = tk.BooleanVar(value=False)
        self._accept_btn = ctk.CTkButton(
            bottom, text="Aceitar e Instalar", height=44, width=220,
            fg_color=ENTRY_BG, hover_color=ENTRY_BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=MUTED, state="disabled",
            command=self._start_install)
        self._accept_btn.pack(side="right")

        cb = ctk.CTkCheckBox(
            bottom,
            text="Li e aceito os Termos de Uso",
            font=ctk.CTkFont(size=12),
            variable=self._accept_var,
            command=self._on_accept_toggle,
            checkbox_width=20, checkbox_height=20,
            fg_color=GREEN, hover_color=GREEN_H)
        cb.pack(side="left", pady=8)

        ctk.CTkButton(bottom, text="← Voltar", width=90, height=36,
                      fg_color=ENTRY_BG, hover_color=PANEL_BG,
                      font=ctk.CTkFont(size=12),
                      command=self._show_welcome).pack(side="left", padx=(12, 0))

    def _on_accept_toggle(self):
        if self._accept_var.get():
            self._accept_btn.configure(
                state="normal", fg_color=GREEN, hover_color=GREEN_H,
                text_color="white")
        else:
            self._accept_btn.configure(
                state="disabled", fg_color=ENTRY_BG, hover_color=ENTRY_BG,
                text_color=MUTED)

    # ── Etapa 3: Instalando ───────────────────────────────────────────────
    def _show_installing(self):
        self._clear_container()
        f = ctk.CTkFrame(self._container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(f, text="Instalando...",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 12))

        self._progress_bar = ctk.CTkProgressBar(f, height=12)
        self._progress_bar.pack(fill="x", pady=(0, 4))
        self._progress_bar.set(0)

        self._progress_label = ctk.CTkLabel(f, text="Iniciando...",
                                            text_color=MUTED,
                                            font=ctk.CTkFont(size=11))
        self._progress_label.pack(anchor="w", pady=(0, 10))

        log_frame = ctk.CTkFrame(f, fg_color=ENTRY_BG, corner_radius=8)
        log_frame.pack(fill="both", expand=True)

        self._log_text = tk.Text(log_frame, bg=ENTRY_BG, fg=TEXT,
                                 font=("Consolas", 10), relief="flat",
                                 bd=0, highlightthickness=0,
                                 state="disabled", wrap="word")
        self._log_text.pack(fill="both", expand=True, padx=8, pady=8)

    # ── Etapa 4: Concluído ────────────────────────────────────────────────
    def _show_done(self, success: bool):
        self._clear_container()
        f = ctk.CTkFrame(self._container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=30)

        if success:
            ctk.CTkLabel(f, text="Instalação concluída!",
                         font=ctk.CTkFont(size=20, weight="bold"),
                         text_color=GREEN).pack(pady=(0, 12))
            ctk.CTkLabel(f,
                         text="O Arquivoz foi instalado com sucesso.\n"
                              "Um atalho foi criado no seu Desktop.",
                         font=ctk.CTkFont(size=13), text_color=TEXT,
                         justify="center").pack(pady=10)
            ctk.CTkButton(f, text="Abrir Arquivoz", height=44, width=220,
                          fg_color=GREEN, hover_color=GREEN_H,
                          font=ctk.CTkFont(size=14, weight="bold"),
                          command=self._launch_app).pack(pady=(20, 8))
        else:
            ctk.CTkLabel(f, text="Instalação concluída com avisos",
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=ORANGE).pack(pady=(0, 12))
            ctk.CTkLabel(f,
                         text="Algumas etapas não foram concluídas.\n"
                              "Consulte o log acima para mais detalhes.\n\n"
                              "O app pode funcionar parcialmente.",
                         font=ctk.CTkFont(size=12), text_color=TEXT,
                         justify="center").pack(pady=10)
            ctk.CTkButton(f, text="Abrir Arquivoz mesmo assim",
                          height=44, width=260,
                          command=self._launch_app).pack(pady=(20, 8))

        ctk.CTkButton(f, text="Fechar instalador", height=36, width=160,
                      fg_color=ENTRY_BG,
                      command=self.destroy).pack()

    # ── Lógica ────────────────────────────────────────────────────────────
    def _start_install(self):
        self._show_installing()
        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self):
        steps = [
            (0.15, self._step_copy_files),
            (0.35, self._step_pip),
            (0.75, self._step_tesseract),
            (0.95, self._step_shortcuts),
        ]
        all_ok = True
        for target_pct, step_fn in steps:
            ok = step_fn()
            if not ok:
                all_ok = False
            self.after(0, lambda p=target_pct: self._progress_bar.set(p))

        self.after(0, lambda: self._progress_bar.set(1))
        self.after(0, lambda: self._progress_label.configure(text="Concluído!"))
        self.after(500, lambda: self._show_done(all_ok))

    def _step_copy_files(self) -> bool:
        self.after(0, lambda: self._progress_label.configure(
            text="Copiando arquivos do app..."))
        if os.path.normpath(SOURCE_DIR) == os.path.normpath(self._install_path):
            self._log("  Instalando no diretório atual: sem cópia necessária")
            return True
        return copy_app_files(self._install_path, self._log)

    def _step_pip(self) -> bool:
        self.after(0, lambda: self._progress_label.configure(
            text="Instalando pacotes Python..."))
        return install_pip_packages(self._log)

    def _step_tesseract(self) -> bool:
        self.after(0, lambda: self._progress_label.configure(
            text="Verificando Tesseract OCR..."))
        ok, tess_dir = install_tesseract(self._log)
        if ok and tess_dir:
            install_tessdata(tess_dir, self._install_path, self._log)
        return ok

    def _step_shortcuts(self) -> bool:
        self.after(0, lambda: self._progress_label.configure(
            text="Criando atalhos..."))
        create_shortcuts(self._install_path, self._log)
        return True

    def _log(self, msg: str):
        def _update():
            self._log_text.configure(state="normal")
            self._log_text.insert("end", msg + "\n")
            self._log_text.see("end")
            self._log_text.configure(state="disabled")
        self.after(0, _update)

    def _launch_app(self):
        self.destroy()
        main_py  = os.path.join(self._install_path, "main.py")
        pythonw  = PYTHON_EXE.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = PYTHON_EXE
        subprocess.Popen([pythonw, main_py], cwd=self._install_path)

    def _clear_container(self):
        for w in self._container.winfo_children():
            w.destroy()


# ── Entrada ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    InstallerApp().mainloop()
