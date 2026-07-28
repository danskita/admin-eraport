# File: tab_pratinjau_utama.py
import tkinter as tk
from tkinter import ttk

# Mengimpor ketiga modul layout cetak
from tab_cover import TabCoverPreview       # MODUL BARU KITA
from tab_cetak import TabCetakPreview       
from tab_raport_genap import TabRaportGenap

class TabPratinjauUtama:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        # Membuat Notebook (Sistem Tab) Internal
        self.sub_notebook = ttk.Notebook(self.parent)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 1. Siapkan Frame untuk masing-masing Sub-Tab
        self.sub_f_cover = ttk.Frame(self.sub_notebook)
        self.sub_f_ganjil = ttk.Frame(self.sub_notebook)
        self.sub_f_genap = ttk.Frame(self.sub_notebook)

        # 2. Tambahkan ke Notebook Internal (Sesuai Urutan Buku)
        self.sub_notebook.add(self.sub_f_cover, text=" 📔 Cover Raport ")
        self.sub_notebook.add(self.sub_f_ganjil, text=" 📘 Semester 1 (Ganjil) ")
        self.sub_notebook.add(self.sub_f_genap, text=" 📗 Semester 2 (Genap) ")

        # 3. Pasang masing-masing modul raport ke dalam sub-frame
        self.cover_obj = TabCoverPreview(self.sub_f_cover, self.db)
        self.ganjil_obj = TabCetakPreview(self.sub_f_ganjil, self.db)
        self.genap_obj = TabRaportGenap(self.sub_f_genap, self.db)

    def refresh_semua_dropdown(self):
        # Segarkan daftar nama di semua sub-tab pratinjau sekaligus
        self.cover_obj.refresh_dropdown()
        self.ganjil_obj.refresh_dropdown()
        self.genap_obj.refresh_dropdown()