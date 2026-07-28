# File: tab_cover.py
import tkinter as tk
from tkinter import ttk, messagebox

class TabCoverPreview:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.lbl_dinamis = {}
        self.setup_ui()

    def setup_ui(self):
        # --- KONTROL ATAS ---
        frame_kontrol = ttk.Frame(self.parent)
        frame_kontrol.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(frame_kontrol, text="Pilih Santri (Cover):", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        self.combo_cetak = ttk.Combobox(frame_kontrol, width=40, state="readonly")
        self.combo_cetak.pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_kontrol, text="🔄 Refresh & Tampilkan", command=self.tampilkan_preview).pack(side=tk.LEFT)
        self.combo_cetak.bind("<<ComboboxSelected>>", lambda e: self.tampilkan_preview())

        # --- CANVAS KERTAS A4 ---
        canvas = tk.Canvas(self.parent, bg="#525659")
        scroll_y = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        
        # Frame "Kertas Putih"
        self.kertas = tk.Frame(canvas, bg="white", padx=80, pady=80)
        self.kertas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((50, 20), window=self.kertas, anchor="nw", width=800, height=1100) # Ukuran panjang A4
        canvas.configure(yscrollcommand=scroll_y.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.bangun_format_cover()

    def bangun_format_cover(self):
        # 1. KOTAK LOGO (Placeholder)
        frame_logo = tk.Frame(self.kertas, bg="white", highlightbackground="black", highlightthickness=1, width=150, height=150)
        frame_logo.pack(pady=(0, 30))
        frame_logo.pack_propagate(False)
        tk.Label(frame_logo, text="LOGO\nMADRASAH", bg="white", font=("Arial", 10, "bold")).pack(expand=True)

        # 2. JUDUL BESAR
        tk.Label(self.kertas, text="BUKU RAPORT", font=("Times New Roman", 28, "bold"), bg="white").pack(pady=(10, 5))
        tk.Label(self.kertas, text="MADRASAH DINIYAH TAKMILIYAH ULA", font=("Times New Roman", 20, "bold"), bg="white").pack(pady=(0, 60))

        # 3. IDENTITAS LEMBAGA (Tengah)
        frame_lembaga = tk.Frame(self.kertas, bg="white")
        frame_lembaga.pack(pady=20)
        
        kolom_lembaga = [
            ("NAMA MADRASAH", "NAMA MADRASAH"),
            ("NOMOR STATISTIK", "NOMOR STATISTIK"),
            ("ALAMAT", "ALAMAT"),
            ("DESA/KELURAHAN", "DESA/KELURAHAN"),
            ("KECAMATAN", "KECAMATAN"),
            ("KABUPATEN/KOTA", "KABUPATEN/KOTA"),
            ("PROVINSI", "PROVINSI")
        ]

        for i, (label_teks, key_db) in enumerate(kolom_lembaga):
            tk.Label(frame_lembaga, text=label_teks, font=("Arial", 14), bg="white", anchor="w", width=20).grid(row=i, column=0, pady=5, sticky="w")
            tk.Label(frame_lembaga, text=":", font=("Arial", 14), bg="white").grid(row=i, column=1, padx=10, pady=5)
            
            lbl_val = tk.Label(frame_lembaga, text="-", font=("Arial", 14), bg="white", anchor="w")
            lbl_val.grid(row=i, column=2, pady=5, sticky="w")
            self.lbl_dinamis[f'lembaga_{key_db}'] = lbl_val

        # 4. NAMA SANTRI (Bawah)
        frame_santri = tk.Frame(self.kertas, bg="white")
        frame_santri.pack(side=tk.BOTTOM, pady=(150, 50)) # Didorong ke bawah
        
        tk.Label(frame_santri, text="NAMA SANTRI", font=("Arial", 14, "bold"), bg="white").pack(pady=(0, 10))
        self.lbl_dinamis['nama_santri'] = tk.Label(frame_santri, text="NAMA SANTRI", font=("Arial", 22), bg="white")
        self.lbl_dinamis['nama_santri'].pack(pady=(0, 20))
        
        frame_nis = tk.Frame(frame_santri, bg="white")
        frame_nis.pack()
        tk.Label(frame_nis, text="Nomor Induk :", font=("Arial", 16, "bold"), bg="white").pack(side=tk.LEFT)
        self.lbl_dinamis['nis_santri'] = tk.Label(frame_nis, text="-", font=("Arial", 16, "bold"), bg="white")
        self.lbl_dinamis['nis_santri'].pack(side=tk.LEFT, padx=(5, 0))

    def refresh_dropdown(self):
        self.combo_cetak['values'] = self.db.get_daftar_nama()

    def tampilkan_preview(self):
        nama = self.combo_cetak.get()
        if not nama: return
        
        # 1. Update Data Santri
        idx_nama = self.db.kolom_lengkap.index("NAMA") if "NAMA" in self.db.kolom_lengkap else -1
        idx_induk = self.db.kolom_lengkap.index("NO. INDUK") if "NO. INDUK" in self.db.kolom_lengkap else -1
        
        data_santri = next((row for row in self.db.data_master if len(row) > idx_nama and row[idx_nama] == nama), None)
        no_induk = data_santri[idx_induk] if data_santri else "-"
        
        self.lbl_dinamis['nama_santri'].config(text=nama)
        self.lbl_dinamis['nis_santri'].config(text=str(no_induk).replace(".0", ""))

        # 2. Update Data Lembaga
        dl = self.db.data_lembaga
        for key in ["NAMA MADRASAH", "NOMOR STATISTIK", "ALAMAT", "DESA/KELURAHAN", "KECAMATAN", "KABUPATEN/KOTA", "PROVINSI"]:
            if f'lembaga_{key}' in self.lbl_dinamis:
                val = dl.get(key, "-")
                self.lbl_dinamis[f'lembaga_{key}'].config(text=val)