#!/home/zigoat/proyek_cli/venv/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import os
import sys
import subprocess  # <-- Kunci utamanya
import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.tree import Tree
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

console = Console()

# --- Konstanta ---
SCRIPT_DIR = Path(__file__).resolve().parent
HISTORY_FILE = SCRIPT_DIR / '.cli_history'
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma:2b-instruct-q4_K_M"
JADWAL_FILE = SCRIPT_DIR / 'jadwal.json'

# --- PETA APLIKASI (KAMU BISA EDIT INI) ---
# "Nama Panggilan" -> "Perintah Terminal Sebenarnya"
# --- PETA APLIKASI (KAMU BISA EDIT INI) ---
# "Nama Panggilan" -> ["Perintah", "Terminal", "Sebenarnya"]
APP_MAP = {
    "brave": ["brave-browser"],
    "rhythmbox": ["rhythmbox"],
    "sober": ["flatpak", "run", "org.vinegarhq.Sober"], # <-- INI DIA!
    "files": ["nemo"],
    "kalkulator": ["gnome-calculator"],
    "office": ["libreoffice"],
    "writer": ["lowriter"],
    "excel": ["localc"],
    "presentasi": ["loimpress"],
}

chat_history = []

# ------------------------------------------------------------------
# FUNGSI MANAJEMEN JADWAL (TIDAK BERUBAH)
# ------------------------------------------------------------------
def muat_jadwal():
    # ... (kode muat_jadwal tetap sama) ...
    if not Path(JADWAL_FILE).exists(): return []
    try:
        with open(JADWAL_FILE, 'r') as f: return json.load(f)
    except json.JSONDecodeError: return []

def simpan_jadwal_list(jadwal_list):
    # ... (kode simpan_jadwal tetap sama) ...
    try:
        jadwal_list.sort(key=lambda x: x['waktu'])
        with open(JADWAL_FILE, 'w') as f: json.dump(jadwal_list, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[bold red]Error menyimpan jadwal: {e}[/bold red]")
        return False

def tambah_jadwal(deskripsi, waktu_str):
    # ... (kode tambah_jadwal tetap sama) ...
    try:
        waktu_obj = datetime.datetime.strptime(waktu_str, '%H:%M').time()
        waktu_final = waktu_obj.strftime('%H:%M')
    except ValueError:
        return "[bold red]Error: Format waktu salah. Gunakan HH:MM (contoh: 14:30)[/bold red]"
    jadwal_list = muat_jadwal()
    jadwal_list.append({"deskripsi": deskripsi, "waktu": waktu_final})
    if simpan_jadwal_list(jadwal_list):
        return f"[bold green]Jadwal disimpan: '{deskripsi}' jam {waktu_final}[/bold green]"
    else:
        return "[bold red]Gagal menyimpan jadwal.[/bold red]"

def lihat_jadwal_hari_ini():
    # ... (kode lihat_jadwal tetap sama) ...
    jadwal_list = muat_jadwal()
    if not jadwal_list:
        console.print(Panel("[yellow]Belum ada jadwal untuk hari ini.[/yellow]", padding=(0, 1)))
        return
    table = Table(title="Jadwal Hari Ini")
    table.add_column("Waktu", style="cyan", justify="center")
    table.add_column("Deskripsi", style="magenta")
    for jadwal in jadwal_list:
        table.add_row(jadwal['waktu'], jadwal['deskripsi'])
    console.print(table)
    return None

# ------------------------------------------------------------------
# FUNGSI INTERNAL (DIMODIFIKASI AGAR TIDAK MEM-BLOK)
# ------------------------------------------------------------------

def run_command_non_blocking(command_list):
    """Menjalankan perintah di background (non-blocking) TANPA LOG."""
    try:
        # Mengarahkan stdout dan stderr ke "black hole" (DEVNULL)
        # Ini mencegah log/error aplikasi (seperti rhythmbox)
        # muncul di terminal kita.
        subprocess.Popen(
            command_list,
            stdout=subprocess.DEVNULL, # <-- TAMBAHAN INI
            stderr=subprocess.DEVNULL  # <-- TAMBAHAN INI
        )
        return f"[bold green]Berhasil menjalankan: '{' '.join(command_list)}'[/bold green]"
    
    except FileNotFoundError:
        return f"[bold red]Error: Perintah '{command_list[0]}' tidak ditemukan.[/bold red]"
    except Exception as e:
        return f"[bold red]Error: {e}[/bold red]"

def handle_open_file(file_path_str):
    """Membuka file/direktori menggunakan aplikasi default sistem (xdg-open)."""
    path = Path(file_path_str).expanduser()
    if not path.exists():
        return f"[bold red]Error: Path '{file_path_str}' tidak ditemukan.[/bold red]"
    
    if sys.platform == "win32":
        command = ["start", str(path)]
    elif sys.platform == "darwin":
        command = ["open", str(path)]
    else:
        command = ["xdg-open", str(path)]
    
    return run_command_non_blocking(command)

def handle_list_directory(dir_path_str):
    """Menampilkan isi direktori sebagai tree."""
    # ... (Fungsi ini tidak berubah, karena 'list' harus mem-blok) ...
    try:
        path = Path(dir_path_str).expanduser()
        if not path.exists():
            return f"[bold red]Error: Path '{dir_path_str}' tidak ditemukan.[/bold red]"
        if not path.is_dir():
            return f"[bold red]Error: '{dir_path_str}' bukan sebuah direktori.[/bold red]"
        tree = Tree(f"[bold bright_blue]📁 {path.resolve()}[/bold bright_blue]", guide_style="bold bright_black")
        for item in sorted(path.iterdir()):
            if item.is_dir():
                tree.add(f"[bold blue]📁 {item.name}/[/bold blue]")
            else:
                tree.add(f"📄 {item.name}")
        console.print(tree)
        return None 
    except Exception as e:
        return f"[bold red]Error saat mendaftar direktori: {e}[/bold red]"

def handle_open_in_vscode(path_str):
    """Membuka path (file/folder) secara spesifik di VS Code."""
    path = Path(path_str).expanduser()
    if not path.exists():
        return f"[bold red]Error: Path '{path_str}' tidak ditemukan.[/bold red]"
    
    return run_command_non_blocking(["code", str(path)])

# ------------------------------------------------------------------
# FUNGSI BARU: Peluncur Aplikasi
# ------------------------------------------------------------------
def handle_run_app(app_name):
    """Mencari nama aplikasi di APP_MAP dan menjalankannya."""
    app_name_lower = app_name.lower()
    if app_name_lower not in APP_MAP:
        return f"[bold red]Error: Aplikasi '{app_name}' tidak dikenal.[/bold red]\nCoba: {', '.join(APP_MAP.keys())}"
    
    # Langsung ambil list perintahnya
    command_list = APP_MAP[app_name_lower] 
    
    # Kirim list itu ke Popen
    return run_command_non_blocking(command_list)

# ------------------------------------------------------------------
# FUNGSI AI (TIDAK BERUBAH)
# ------------------------------------------------------------------
def kirim_prompt_ke_ollama(history_messages):
    # ... (kode kirim_prompt_ke_ollama tetap sama) ...
    data = {"model": MODEL_NAME, "messages": history_messages, "stream": True}
    full_response = ""
    panel_title = "[bold cyan]My Istri Gweh!![/bold cyan]"
    panel_content = Markdown("...")
    ai_panel = Panel(panel_content, title=panel_title, border_style="green")
    try:
        with Live(ai_panel, console=console, refresh_per_second=10) as live:
            with requests.post(OLLAMA_CHAT_URL, json=data, stream=True) as resp:
                resp.raise_for_status()
                is_ingesting = True 
                for chunk in resp.iter_lines(decode_unicode=True):
                    if not chunk: continue
                    try:
                        json_chunk = json.loads(chunk)
                    except json.JSONDecodeError: continue
                    if json_chunk.get("done"): break
                    if is_ingesting:
                        full_response = ""
                        ai_panel.border_style = "green"
                        is_ingesting = False
                    text_piece = json_chunk.get("message", {}).get("content", "")
                    if text_piece:
                        full_response += text_piece
                        ai_panel.renderable = Markdown(full_response)
                        live.refresh()
        return full_response
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Error: koneksi ke Ollama gagal.[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Terjadi error: {e}[/bold red]")
        return None

# ------------------------------------------------------------------
# FUNGSI main_loop() (DIMODIFIKASI)
# ------------------------------------------------------------------
def main_loop():
    """Loop utama chatbot."""
    welcome = Panel(
        f"[bold green]Welcome to Your Wife CLI![/bold green]\nModel: [yellow]{MODEL_NAME}[/yellow]\n\n"
        "Perintah:\n"
        "  [cyan]jadwal [desc] jam [HH:MM][/cyan] - Buat jadwal baru\n"
        "  [cyan]lihat jadwal[/cyan]        - Tampilkan semua jadwal\n"
        "  [cyan]buka [path][/cyan]               - Membuka file/folder (default app)\n"
        "  [cyan]buka [app][/cyan]               - Membuka aplikasi (misal: buka brave)\n" # <-- BARU
        "  [cyan]code [path][/cyan]               - Membuka file/folder di VS Code\n"
        "  [cyan]list [path][/cyan]               - Menampilkan isi folder",
        title="My Istri Gweh!!",
        border_style="bold blue"
    )
    console.print(welcome)

    session = PromptSession(history=FileHistory(HISTORY_FILE))

    while True:
        try:
            user_input = session.prompt("Kamu: ")
        except (KeyboardInterrupt, EOFError):
            break
        
        clean_input = user_input.strip()
        user_lower = clean_input.lower()

        if user_lower == "exit":
            break

        # --- PILAH PERINTAH INTERNAL ---
        
        # PERINTAH: 'buka' (bisa App atau Path)
        if user_lower.startswith("buka "):
            target = clean_input[5:].strip()
            # Cek dulu apakah targetnya ada di APP_MAP
            if target.lower() in APP_MAP:
                result_msg = handle_run_app(target)
            else:
                # Jika tidak, anggap itu sebagai path
                result_msg = handle_open_file(target)
            console.print(Panel(result_msg, border_style="yellow", padding=(0, 1)))
            continue 

        # PERINTAH: 'list'
        elif user_lower.startswith("list "):
            path_to_list = clean_input[5:].strip()
            result_msg = handle_list_directory(path_to_list)
            if result_msg:
                console.print(Panel(result_msg, border_style="red", padding=(0, 1)))
            continue
            
        # PERINTAH: 'code'
        elif user_lower.startswith("code "):
            path_to_open = clean_input[5:].strip()
            result_msg = handle_open_in_vscode(path_to_open)
            console.print(Panel(result_msg, border_style="yellow", padding=(0, 1)))
            continue
            
        # PERINTAH: 'lihat jadwal'
        elif user_lower == "lihat jadwal" or user_lower == "apa jadwalku":
            lihat_jadwal_hari_ini()
            continue
            
        # PERINTAH: 'jadwal ... jam ...'
        elif "jam" in user_lower and (user_lower.startswith("jadwal ") or user_lower.startswith("ingatkan ")):
            try:
                parts = clean_input.split(" jam ")
                waktu_str = parts[-1].strip()
                deskripsi = parts[0].split(" ", 1)[-1].strip()
                result_msg = tambah_jadwal(deskripsi, waktu_str)
                console.print(Panel(result_msg, border_style="green", padding=(0, 1)))
            except Exception as e:
                console.print(Panel(f"[bold red]Error parsing perintah jadwal: {e}[/bold red]", border_style="red"))
            continue

        # --- JIKA BUKAN PERINTAH INTERNAL, MAKA INI ADALAH CHAT BIASA ---
        else:
            final_prompt = clean_input
            chat_history.append({"role": "user", "content": final_prompt})
            
            if len(chat_history) == 1:
                chat_history.insert(0, {
                    "role": "system",
                    "content": "Kamu adalah asisten personal yang ramah, suportif, dan siap mendengarkan curhat. Kamu dipanggil 'Istri' oleh pengguna. Jawablah dengan santai dan hangat."
                })
            
            assistant_response = kirim_prompt_ke_ollama(chat_history)

            if assistant_response:
                chat_history.append({"role": "assistant", "content": assistant_response})


if __name__ == "__main__":
    main_loop()