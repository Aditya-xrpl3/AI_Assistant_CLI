Asisten CLI Personal

Sebuah asisten CLI personal yang berjalan 100% offline. Dibuat dengan Python dan didukung oleh Ollama.

<img width="1907" height="987" alt="image" src="https://github.com/user-attachments/assets/49ea2bbe-e00e-4782-a4bd-b94549b002b9" />


## 💡 Tentang Proyek Ini

Proyek ini adalah eksperimen untuk membuat asisten CLI yang ringan, cepat, personal, dan 100% privat. Fokus utamanya adalah sebagai **asisten harian** yang membantumu mengelola jadwal, meluncurkan aplikasi, dan sebagai teman chat (curhat), semuanya tanpa perlu koneksi internet.

## ✨ Fitur Utama

* **100% Offline:** Semua chat dan pemrosesan dilakukan secara lokal menggunakan **Ollama**.
* **Chat Personal:** Mampu diajak chat biasa atau "curhat" dengan *system prompt* yang personal.
* **Manajemen Jadwal:** Simpan (`jadwal ... jam ...`) dan lihat (`lihat jadwal`) agendamu. Data disimpan di `jadwal.json`.
* **Peluncur Aplikasi:** Buka aplikasi favoritmu (seperti `brave`, `sober`, `rhythmbox`) langsung dari CLI.
* **Interaksi Sistem:** Buka file/folder (`buka [path]`), buka proyek di VS Code (`code [path]`), dan lihat isi folder (`list [path]`).
* **UI Cantik:** Dibangun dengan `rich` untuk menampilkan panel, tabel, dan *live streaming* respons AI yang modern.
* **Input Canggih:** Menggunakan `prompt_toolkit` yang menyimpan riwayat perintah (bisa diakses dengan panah atas).

## 🛠️ Teknologi yang Digunakan

* **Python 3**
* **Ollama** (sebagai backend LLM)
* **Rich** (untuk TUI, panel, tabel, live update)
* **prompt\_toolkit** (untuk input CLI dengan history)
* **requests** (untuk berkomunikasi dengan API Ollama)

---

## 🚀 Instalasi & Setup

Ikuti langkah-langkah ini untuk menjalankan asistenmu sendiri.

### 1. Prasyarat

* **Python 3.10+** dan `python3-venv` (biasanya sudah ada di Linux Mint).
* **Ollama** terinstal dan berjalan. [Cek di sini](https://ollama.com/).
* **VS Code** terinstal (untuk perintah `code`).

### 2. Instalasi Proyek

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/username-kamu/nama-repo-kamu.git](https://github.com/username-kamu/nama-repo-kamu.git)
    cd nama-repo-kamu
    ```

2.  **Buat file `requirements.txt`:**
    Buat file baru bernama `requirements.txt` dan isi dengan:
    ```
    requests
    rich
    prompt_toolkit
    ```

3.  **Buat Virtual Environment dan Instal Dependensi:**
    ```bash
    # Buat venv
    python3 -m venv venv
    
    # Aktifkan venv
    source venv/bin/activate
    
    # Instal library
    pip install -r requirements.txt
    ```

### 3. Setup Asisten

1.  **Download Model LLM:**
    Proyek ini ringan dan disarankan menggunakan model 1B-3B.
    ```bash
    # (Contoh)
    ollama pull gemma:2b-instruct-q4_K_M
    ```
    Pastikan nama model di `chat.py` (variabel `MODEL_NAME`) sesuai dengan yang kamu *pull*.

2.  **Kustomisasi Aplikasi (Opsional):**
    Buka `chat.py` dan edit `APP_MAP` untuk mendaftarkan aplikasi di laptopmu.
    ```python
    APP_MAP = {
        "brave": ["brave-browser"],
        "sober": ["flatpak", "run", "org.vinegarhq.Sober"],
        # ... tambahkan aplikasimu di sini
    }
    ```

3.  **Buat Perintah Global (Rekomendasi):**
    Agar kamu bisa memanggil asistenmu dari mana saja dengan nama `My_Istri`.

    * **Edit `chat.py`:**
        Tambahkan "shebang" di **baris paling pertama** file. Ganti `/home/namamu/...` dengan *path* absolut ke proyekmu.
        ```python
        #!/home/namamu/proyek_cli/venv/bin/python3
        # -*- coding: utf-8 -*-
        import requests
        # ...sisa kode...
        ```

    * **Beri Izin Eksekusi:**
        ```bash
        chmod +x chat.py
        ```

    * **Buat Symlink:**
        ```bash
        # Ganti /home/namamu/... dengan path absolut-mu
        sudo ln -s /home/namamu/proyek_cli/chat.py /usr/local/bin/My_Istri
        ```

4.  **Selesai!**
    Buka terminal baru dan jalankan asistenmu dari mana saja:
    ```bash
    My_Istri
    ```

---

## ⌨️ Daftar Perintah

| Perintah | Deskripsi |
| :--- | :--- |
| `(teks curhat apa saja)` | Memulai chat biasa dengan AI. |
| `jadwal [deskripsi] jam [HH:MM]` | Membuat jadwal baru (misal: `jadwal meeting jam 14:30`). |
| `lihat jadwal` | Menampilkan semua jadwal yang tersimpan dalam tabel. |
| `buka [nama aplikasi]` | Membuka aplikasi dari `APP_MAP` (misal: `buka brave`). |
| `buka [path]` | Membuka file atau folder dengan aplikasi *default* (misal: `buka file.pdf`). |
| `code [path]` | Membuka folder atau file di VS Code (misal: `code .`). |
| `list [path]` | Menampilkan isi folder dalam format *tree* (misal: `list .`). |
| `exit` | Keluar dari aplikasi. |

## ✍️ Author

Dibuat oleh **Zigoat**
