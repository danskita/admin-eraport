# File: tema.py
import tkinter as tk
from tkinter import ttk

class TemaAplikasi:
    # --- PALET WARNA MODERN ---
    BG_UTAMA = "#F4F6F9"        # Abu-abu sangat muda untuk latar belakang
    BG_PUTIH = "#FFFFFF"        # Putih bersih untuk area kerja
    TEKS_UTAMA = "#2C3E50"      # Biru gelap (hampir hitam) untuk teks agar tidak terlalu tajam
    WARNA_PRIMER = "#3498DB"    # Biru cerah untuk tombol dan aksen
    WARNA_SEKUNDER = "#2980B9"  # Biru lebih gelap saat tombol disorot (hover)
    GARIS_BATAS = "#D1D8E0"     # Abu-abu lembut untuk garis tabel/border

    # --- PENGATURAN HURUF (FONT) ---
    FONT_NORMAL = ('Segoe UI', 10)
    FONT_JUDUL = ('Segoe UI', 14, 'bold')
    FONT_TAB = ('Segoe UI', 10, 'bold')

    @classmethod
    def terapkan(cls, root):
        # Mengubah warna latar belakang jendela paling dasar
        root.configure(bg=cls.BG_UTAMA)
        
        style = ttk.Style()
        # Menggunakan tema dasar 'clam' karena paling ramah untuk dikustomisasi
        style.theme_use('clam')

        # ==========================================
        # KONFIGURASI GLOBAL SEMUA ELEMEN
        # ==========================================
        style.configure('.', 
                        font=cls.FONT_NORMAL, 
                        background=cls.BG_UTAMA, 
                        foreground=cls.TEKS_UTAMA)

        # ==========================================
        # 1. DESAIN TAB (NOTEBOOK)
        # ==========================================
        style.configure('TNotebook', background=cls.BG_UTAMA, borderwidth=0)
        style.configure('TNotebook.Tab', 
                        font=cls.FONT_TAB, 
                        padding=[20, 8], # Membuat tab lebih luas dan lega
                        background="#E0E6ED", 
                        foreground="#7F8C8D",
                        borderwidth=0)
        # Efek saat tab diklik / aktif
        style.map('TNotebook.Tab', 
                  background=[('selected', cls.BG_PUTIH)], 
                  foreground=[('selected', cls.WARNA_PRIMER)])

        # ==========================================
        # 2. DESAIN TOMBOL
        # ==========================================
        style.configure('TButton', 
                        font=('Segoe UI', 10, 'bold'), 
                        background=cls.WARNA_PRIMER, 
                        foreground=cls.BG_PUTIH, 
                        padding=8,
                        borderwidth=0)
        # Efek saat kursor berada di atas tombol
        style.map('TButton', 
                  background=[('active', cls.WARNA_SEKUNDER)])

        # ==========================================
        # 3. DESAIN TEKS (LABEL) & GRUP (LABELFRAME)
        # ==========================================
        style.configure('TLabel', background=cls.BG_UTAMA)
        style.configure('Header.TLabel', font=cls.FONT_JUDUL, foreground=cls.WARNA_PRIMER)
        
        style.configure('TLabelframe', background=cls.BG_UTAMA, bordercolor=cls.GARIS_BATAS, borderwidth=1)
        style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'), foreground=cls.WARNA_PRIMER, background=cls.BG_UTAMA)
        style.configure('Blue.TLabelframe.Label', font=('Segoe UI', 10, 'bold'), foreground=cls.WARNA_PRIMER, background=cls.BG_UTAMA)

        # ==========================================
        # 4. DESAIN TABEL (TREEVIEW)
        # ==========================================
        style.configure('Treeview', 
                        background=cls.BG_PUTIH, 
                        foreground=cls.TEKS_UTAMA, 
                        fieldbackground=cls.BG_PUTIH,
                        rowheight=28, # Baris tabel lebih longgar
                        borderwidth=0)
        style.configure('Treeview.Heading', 
                        font=('Segoe UI', 10, 'bold'), 
                        background=cls.GARIS_BATAS, 
                        foreground=cls.TEKS_UTAMA,
                        padding=5)
        # Warna baris tabel saat diklik
        style.map('Treeview', background=[('selected', cls.WARNA_PRIMER)])

        # ==========================================
        # 5. DESAIN KOTAK INPUT (ENTRY & COMBOBOX)
        # ==========================================
        style.configure('TEntry', fieldbackground=cls.BG_PUTIH, padding=5, borderwidth=1)
        style.configure('TCombobox', fieldbackground=cls.BG_PUTIH, padding=5)

        # ==========================================
        # 6. KHUSUS KERTAS PRATINJAU CETAK
        # ==========================================
        style.configure('Kertas.TFrame', background="white")
        style.configure('Kertas.TLabel', background="white", foreground="black", font=('Arial', 11))