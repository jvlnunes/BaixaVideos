import flet as ft
import yt_dlp
import threading
import os
import sys
import json
import time

# --- Detecção de unidades removíveis (somente Windows) ---
try:
    import win32api
    import win32file
    WINDOWS_DRIVE_DETECTION = True
except ImportError:
    WINDOWS_DRIVE_DETECTION = False


# =============================================================
# Utilitários
# =============================================================

def get_base_path():
    """Diretório base — funciona com .py e com .exe empacotado."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    """Procura ffmpeg.exe/ffmpeg na raiz do projeto."""
    base = get_base_path()
    for name in ("ffmpeg.exe", "ffmpeg"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return path
    return None


def get_config_path():
    return os.path.join(get_base_path(), "config.json")


def load_config():
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg):
    try:
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# =============================================================
# Detecção de unidades removíveis (USB)
# =============================================================

def listar_unidades_removiveis():
    """Retorna lista de letras de unidade removíveis, ex: ['D:\\\\', 'E:\\\\']."""
    if not WINDOWS_DRIVE_DETECTION:
        return []
    removiveis = []
    try:
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split("\x00")[:-1]
        for device in drives:
            # DRIVE_REMOVABLE = 2
            if win32file.GetDriveType(device) == win32file.DRIVE_REMOVABLE:
                removiveis.append(device)
    except Exception:
        pass
    return removiveis


def obter_nome_volume(letra_unidade):
    """Retorna o rótulo (nome) do volume, ex: 'X9'."""
    try:
        nome = win32api.GetVolumeInformation(letra_unidade)[0]
        return nome if nome else "Sem nome"
    except Exception:
        return "Sem nome"


class MonitorUnidades:
    """Thread que verifica periodicamente as unidades removíveis."""

    def __init__(self, callback, intervalo=2.0):
        self.callback = callback
        self.intervalo = intervalo
        self.rodando = True
        self.ultimo_estado = None
        self.thread = None

    def iniciar(self):
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while self.rodando:
            try:
                atual = tuple(sorted(listar_unidades_removiveis()))
                if atual != self.ultimo_estado:
                    self.ultimo_estado = atual
                    self.callback(atual)
            except Exception:
                pass
            time.sleep(self.intervalo)

    def parar(self):
        self.rodando = False


# =============================================================
# Constantes
# =============================================================

FORMATOS = [
    ("mp3", "MP3 (compatível com tudo)"),
    ("m4a", "M4A (bom para celular)"),
    ("flac", "FLAC (sem perda)"),
    ("wav", "WAV (sem compressão)"),
    ("opus", "OPUS (menor tamanho)"),
    ("best", "Manter original (sem conversão)"),
]


# =============================================================
# App
# =============================================================

def main(page: ft.Page):
    page.title = "Baixador de Áudio"
    page.window_width = 820
    page.window_height = 720
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    cfg = load_config()
    file_picker = ft.FilePicker()

    # ---------- Campos ----------

    url_field = ft.TextField(
        label="URL do YouTube (vídeo ou playlist)",
        width=740,
        hint_text="https://www.youtube.com/watch?v=...",
    )

    pasta_field = ft.TextField(
        label="Pasta de destino",
        expand=True,
        read_only=True,
        value=cfg.get("pasta", ""),
    )

    formato_dropdown = ft.Dropdown(
        label="Formato de saída",
        width=280,
        value=cfg.get("formato", "mp3"),
        options=[ft.dropdown.Option(k, t) for k, t in FORMATOS],
    )

    unidade_dropdown = ft.Dropdown(
        label="Unidade removível (fone/pendrive)",
        width=300,
        hint_text="Conecte o dispositivo USB",
        value=cfg.get("unidade", ""),
        options=[],
    )

    # ---------- Aviso se pywin32 faltando ----------

    if not WINDOWS_DRIVE_DETECTION:
        unidade_dropdown.disabled = True
        unidade_dropdown.hint_text = "Instale pywin32 para usar esta função"

    # ---------- Progresso ----------

    progress_bar = ft.ProgressBar(
        value=0, width=740, color=ft.Colors.GREEN_400, bgcolor=ft.Colors.GREY_800
    )
    status_text = ft.Text("Aguardando...", size=13, color=ft.Colors.GREY_400)

    # ---------- Log ----------

    log_list = ft.ListView(expand=True, spacing=4, auto_scroll=True)

    # ---------- Funções ----------

    def log_msg(msg, cor=ft.Colors.WHITE):
        log_list.controls.append(ft.Text(msg, size=13, color=cor))
        try:
            page.update()
        except Exception:
            pass

    def atualizar_unidades(lista_atual=None):
        """Atualiza o dropdown de unidades removíveis."""
        if not WINDOWS_DRIVE_DETECTION:
            return

        if lista_atual is None:
            lista_atual = tuple(sorted(listar_unidades_removiveis()))

        opcoes = []
        for u in lista_atual:
            nome = obter_nome_volume(u)
            opcoes.append(ft.dropdown.Option(u, f"{u} ({nome})"))

        # Preserva seleção se ainda existir
        valor_atual = unidade_dropdown.value
        unidade_dropdown.options = opcoes

        letras_disponiveis = {u for u in lista_atual}
        if valor_atual and valor_atual in letras_disponiveis:
            unidade_dropdown.value = valor_atual
        elif len(lista_atual) == 1:
            unidade_dropdown.value = lista_atual[0]
        else:
            unidade_dropdown.value = None

        try:
            page.update()
        except Exception:
            pass

    def on_unidades_mudaram(lista_atual):
        """Callback chamado pela thread de monitoramento."""
        # Pequeno delay extra para o Windows montar o volume
        time.sleep(1)
        atualizar_unidades(lista_atual)
        if lista_atual:
            log_msg(
                f"🔌 Unidade(s) conectada(s): {', '.join(lista_atual)}",
                ft.Colors.CYAN_300,
            )
        else:
            log_msg("🔌 Unidade removível desconectada.", ft.Colors.GREY_500)

    async def escolher_pasta(e):
        path = await file_picker.get_directory_path(
            dialog_title="Escolha a pasta para salvar os áudios"
        )
        if path:
            pasta_field.value = path
            page.update()

    def usar_unidade(e):
        """Botão para definir a unidade selecionada como pasta de destino."""
        if unidade_dropdown.value:
            pasta_field.value = unidade_dropdown.value
            page.update()

    def progress_hook(d):
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total > 0:
                pct = downloaded / total
                progress_bar.value = pct
                status_text.value = (
                    f"Baixando... {pct * 100:.1f}% "
                    f"({downloaded / 1024 / 1024:.1f} MB / "
                    f"{total / 1024 / 1024:.1f} MB)"
                )
                try:
                    page.update()
                except Exception:
                    pass
        elif d["status"] == "finished":
            progress_bar.value = 1.0
            status_text.value = "Download concluído, processando..."
            try:
                page.update()
            except Exception:
                pass

    def baixar(e):
        url = (url_field.value or "").strip()
        pasta = (pasta_field.value or "").strip()
        formato = formato_dropdown.value or "mp3"
        unidade = unidade_dropdown.value or ""

        if not url:
            log_msg("⚠️ Cole uma URL válida!", ft.Colors.ORANGE)
            return
        if not pasta:
            log_msg("⚠️ Escolha uma pasta de destino!", ft.Colors.ORANGE)
            return

        save_config({
            "pasta": pasta,
            "formato": formato,
            "unidade": unidade,
        })

        btn_baixar.disabled = True
        progress_bar.value = 0
        status_text.value = "Iniciando..."
        page.update()

        threading.Thread(
            target=_executar_download,
            args=(url, pasta, formato),
            daemon=True,
        ).start()

    def _executar_download(url, pasta, formato):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "ignoreerrors": True,
            "quiet": True,
            "no_warnings": True,
        }

        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path
            log_msg(f"🎬 FFmpeg: {ffmpeg_path}", ft.Colors.GREY_500)
        else:
            log_msg(
                "⚠️ FFmpeg não encontrado na pasta do projeto. "
                "Coloque ffmpeg.exe na raiz.",
                ft.Colors.ORANGE,
            )

        if formato != "best":
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": formato,
                "preferredquality": "192",
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            log_msg(f"✅ Concluído! (formato: {formato.upper()})", ft.Colors.GREEN)
            status_text.value = "Pronto!"
        except Exception as ex:
            log_msg(f"❌ Erro: {ex}", ft.Colors.RED)
            status_text.value = "Erro no download"
        finally:
            btn_baixar.disabled = False
            try:
                page.update()
            except Exception:
                pass

    # ---------- Botões ----------

    btn_escolher = ft.Button(
        content="Escolher",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=escolher_pasta,
    )

    btn_usar_unidade = ft.Button(
        content="Usar unidade",
        icon=ft.Icons.USB,
        on_click=usar_unidade,
    )

    btn_baixar = ft.Button(
        content="Baixar",
        icon=ft.Icons.DOWNLOAD,
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
        height=45,
        on_click=baixar,
    )

    # ---------- Inicia monitor de unidades ----------

    monitor = MonitorUnidades(on_unidades_mudaram, intervalo=2.0)
    if WINDOWS_DRIVE_DETECTION:
        atualizar_unidades()  # Preenche uma vez na abertura
        monitor.iniciar()

    # ---------- Layout ----------

    page.add(
        ft.Text("🎧 Baixador de Áudio", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(),

        url_field,

        ft.Row([pasta_field, btn_escolher]),

        ft.Row([
            formato_dropdown,
            unidade_dropdown,
            btn_usar_unidade,
        ]),

        btn_baixar,
        ft.Divider(),
        progress_bar,
        status_text,

        ft.Text("Log:", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=log_list,
            height=200,
            border=ft.Border.all(1, ft.Colors.GREY_700),
            border_radius=8,
            padding=10,
        ),
    )


ft.run(main)