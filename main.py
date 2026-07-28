# File: main.py
import tkinter as tk
from tkinter import ttk

from database import DataEngine
from tema import TemaAplikasi               # IMPORT FILE TEMA BARU

# Impor Modul Tab
from tab_lembaga import TabIdentitasLembaga
from tab_biodata import TabInputBiodata
from tab_output import TabDataInduk
from tab_nilai import TabInputNilai
from tab_pratinjau_utama import TabPratinjauUtama

class AplikasiUtama:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Raport MDTU - Modern UI")
        self.root.geometry("1200x850")

        self.db = DataEngine()
        
        # SUNTIKKAN TEMA MODERN KE SELURUH APLIKASI
        TemaAplikasi.terapkan(self.root)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # FRAME TAB UTAMA
        f_lembaga = ttk.Frame(self.notebook)
        f_biodata = ttk.Frame(self.notebook)
        f_output = ttk.Frame(self.notebook)
        f_nilai = ttk.Frame(self.notebook)
        f_pratinjau = ttk.Frame(self.notebook)

        # TAMBAHKAN TAB UTAMA
        self.notebook.add(f_lembaga, text=" 🏫 LEMBAGA ")
        self.notebook.add(f_biodata, text=" 📝 INPUT BIODATA ")
        self.notebook.add(f_output, text=" 📊 DATA INDUK ")
        self.notebook.add(f_nilai, text=" 🧮 INPUT NILAI ")
        self.notebook.add(f_pratinjau, text=" 🖨️ PRATINJAU RAPORT ")

        # PASANG MODUL
        self.tab_lembaga_obj = TabIdentitasLembaga(f_lembaga, self.db)
        self.tab_output_obj = TabDataInduk(f_output, self.db)
        self.tab_biodata_obj = TabInputBiodata(f_biodata, self.db, callback_sukses=self.pindah_ke_tab_output)
        self.tab_nilai_obj = TabInputNilai(f_nilai, self.db)
        self.tab_pratinjau_obj = TabPratinjauUtama(f_pratinjau, self.db)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # Catatan: Fungsi setup_styles() lama telah dihapus sepenuhnya karena digantikan tema.py

    def pindah_ke_tab_output(self):
        self.tab_output_obj.refresh_tabel()
        self.notebook.select(2)

    def on_tab_change(self, event):
        self.tab_nilai_obj.refresh_dropdown()
        self.tab_pratinjau_obj.refresh_semua_dropdown()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiUtama(root)
    root.mainloop()