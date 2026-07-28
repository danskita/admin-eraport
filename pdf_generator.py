import io
import base64
import calendar
from datetime import date, datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# DEFINISI KERTAS F4 INDONESIA
F4 = (21.5 * cm, 33.0 * cm)
F4_Landscape = (33.0 * cm, 21.5 * cm)

NAMA_BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# REFERENSI MATERI HAFALAN UNTUK PDF
MATERI_HAFALAN_PDF = {
    "IQRA 1": {
        "Bacaan Sholat": ["Do'a Iftitah", "Surah Al Fatihah", "Do'a Ruku & Sujud", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
        "Do'a Harian": ["Do'a dan Adab Belajar", "Do'a Mensyukuri Nikmat", "Do'a dan Adab Sebelum Makan", "Do'a dan Adab Sesudah Makan"],
        "Surah Pendek": ["QS An Naas", "QS Al Falaq", "QS Al Ikhlash", "QS Al Lahab"],
        "Hadist": ["Hadist Kebersihan", "Hadist Senyum", "Hadist Larangan Marah"]
    },
    "IQRA 2": {
        "Bacaan Sholat": ["Do'a I'tidal", "Do'a Duduk Diantara 2 Sujud", "Do'a Tasyahud", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
        "Do'a Harian": ["Do'a dan Adab Sebelum Tidur", "Do'a dan Adab Bangun Tidur", "Do'a dan Adab Masuk WC", "Do'a dan Adab Keluar WC"],
        "Surah Pendek": ["QS An Nashr", "QS Al Kautsar", "QS Al 'Ashr", "QS Al Kafirun"],
        "Hadist": ["Hadist Niat", "Hadist Mencintai Keindahan", "Hadist Menyebarkan Salam"]
    },
    "IQRA 3": {
        "Bacaan Sholat": ["Sholawat", "Do'a Sebelum Salam", "Salam", "Dzikir Setelah Sholat", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
        "Do'a Harian": ["Do'a dan Adab Masuk Rumah", "Do'a dan Adab Keluar Rumah", "Do'a dan Adab Berpakaian", "Do'a dan Adab Melepas Pakaian"],
        "Surah Pendek": ["QS Al Ma'un", "QS Quraisy", "QS Al Fil", "QS Al Humazah", "QS At Takatsur"],
        "Hadist": ["Hadist Menjaga Lisan", "Hadist Makan/Minum dengan Tangan Kanan", "Hadist Bersikap Lemah Lembut"]
    },
    "IQRA 4": {
        "Do'a Harian": ["Do'a Kebaikan Dunia dan Akhirat", "Do'a dan Adab Bercermin", "Senandung Do'a Al-Qur'an", "Do'a dan Adab Naik Kendaraan", "Do'a dan Adab Memperoleh Rahmat"],
        "Surah Pendek": ["QS Al Qari'ah", "QS Al 'Aadiyyat", "QS Al Zalzalah", "QS Al Bayyinah", "QS Al Qadr"],
        "Ayat Pilihan": ["QS Al Baqarah ayat 255 (Ayat Qursiy)", "QS Al Mu'minun Ayat 1-11", "QS Ar Rahman Ayat 1-15"],
        "Hadist": ["Hadist Sesama Muslim Bersaudara", "Hadist Tolonglah Saudaramu", "Hadist Larangan Mencela Makanan"]
    },
    "IQRA 5": {
        "Do'a Harian": ["Do'a Kedua Orang Tua", "Do'a dan Adab Akhir Pertemuan", "Do'a dan Adab Masuk Masjid", "Do'a dan Adab Keluar Masjid"],
        "Surah Pendek": ["QS Al Alaq", "QS At Tin", "QS Al Insyirah", "QS Ad Dhuha", "QS Al Lail"],
        "Ayat Pilihan": ["QS Al Baqarah ayat 284-286", "QS Al Jumu'ah Ayat 9-11", "QS Luqman Ayat 12-19"],
        "Hadist": ["Hadist Berbuat Baik", "Hadist Kasih Sayang", "Hadist Keutamaan Membaca Al-Qur'an"]
    },
    "IQRA 6": {
        "Do'a Harian": ["Do'a dan Adab Sesudah Mendengarkan Adzan", "Do'a Ketika Sakit", "Do'a Menjenguk Orang Sakit", "Do'a Memperoleh Kesehatan & Akhlak Baik", "Do'a Dzikir Pagi & Sore Hari"],
        "Surah Pendek": ["QS As Syams", "QS Al Balad", "QS Al Fajr", "QS Al Ghasyiah", "QS Al A'la"],
        "Ayat Pilihan": ["QS Al Fath Ayat 28 - 29", "QS Ali Imran Ayat 133-136", "QS An Nahl Ayat 65-69"],
        "Hadist": ["Hadist Larangan Minum Sambil Berdiri", "Hadist Perkataan Baik Adalah Sedekah", "Hadist Amal Paling Utama", "Hadist Berbakti Pada Orang Tua"]
    }
}

def terbilang(angka):
    angka = int(angka)
    huruf = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if angka < 12: return huruf[angka]
    elif angka < 20: return terbilang(angka - 10) + " belas"
    elif angka < 100: return terbilang(angka // 10) + " puluh " + terbilang(angka % 10)
    elif angka == 100: return "seratus"
    else: return str(angka)

class PDFGenerator:
    def __init__(self, db):
        self.db = db

    def _get_dl_flat(self):
        dl_raw = self.db.data_lembaga
        profil = dl_raw.get("profil_lengkap", {})
        pengaturan = dl_raw.get("pengaturan_master", {})
        
        dl_flat = {**dl_raw, **profil}
        dl_flat["nomor_statistik"] = dl_raw.get("nsm", "-")
        dl_flat["pengaturan_master"] = pengaturan
        return dl_flat

    def cetak_cover(self, nama_santri):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        dl = self._get_dl_flat()

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4

        # LOGO
        logo_b64 = dl.get("logo", "")
        if logo_b64:
            try:
                logo_data = base64.b64decode(logo_b64)
                logo_img = ImageReader(io.BytesIO(logo_data))
                c.drawImage(logo_img, lebar/2 - 2*cm, tinggi - 8*cm, 4*cm, 4*cm, mask='auto')
            except Exception:
                c.rect(lebar/2 - 2*cm, tinggi - 7*cm, 4*cm, 4*cm)
                c.drawCentredString(lebar/2, tinggi - 5*cm, "LOGO ERROR")
        else:
            c.rect(lebar/2 - 2*cm, tinggi - 7*cm, 4*cm, 4*cm)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(lebar/2, tinggi - 5*cm, "LOGO")
            c.drawCentredString(lebar/2, tinggi - 5.5*cm, "MADRASAH")

        # JUDUL
        tingkatan_teks = dl.get("tingkatan", "MDTU")
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(lebar/2, tinggi - 11*cm, "BUKU RAPORT")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(lebar/2, tinggi - 12.5*cm, f"LEMBAGA PENDIDIKAN {tingkatan_teks}")

        # IDENTITAS
        c.setFont("Helvetica", 12)
        y_lembaga = tinggi - 15*cm
        labels = [
            ("NAMA MADRASAH", dl.get("nama_madrasah", "-")),
            ("NOMOR STATISTIK", dl.get("nomor_statistik", "-")),
            ("ALAMAT", dl.get("alamat", "-")),
            ("DESA/KELURAHAN", dl.get("desa_kelurahan", "-")),
            ("KECAMATAN", dl.get("kecamatan", "-")),
            ("KABUPATEN/KOTA", dl.get("kabupaten_kota", "-")),
            ("PROVINSI", dl.get("provinsi", "-"))
        ]
        
        for i, (lbl, val) in enumerate(labels):
            y_pos = y_lembaga - (i * 0.8 * cm)
            c.drawString(4*cm, y_pos, lbl)
            c.drawString(9*cm, y_pos, f": {val}")

        # SANTRI
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 9*cm, "NAMA SANTRI")
        
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(lebar/2, 6.5*cm, nama_santri)

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 6*cm, f"Nomor Induk : {santri.get('no_induk', '-')}")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer


    # ========================================================
    # 3. CETAK LAPORAN HAFALAN BULANAN TKA/TPA (IQRA 1-6)
    # ========================================================
    def cetak_laporan_hafalan_bulanan(self, nama_santri, jilid, nama_bulan, tahun):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        
        riwayat = self.db.get_nilai(santri['id'], 99)
        komp_lama = riwayat.get("komponen_nilai", {}) if riwayat else {}
        data_jilid = komp_lama.get(jilid, {})
        catatan = komp_lama.get(f"catatan_{jilid}", "-")
        
        dl = self._get_dl_flat()
        data_lengkap = santri.get("data_lengkap", {})
        kelas_santri = data_lengkap.get("kelas_santri", data_lengkap.get("kelas", "-"))
        
        daftar_guru = self.db.get_semua_guru_lembaga()
        nama_wali = "........................"
        for g in daftar_guru:
            if g.get('role') == 'wali_kelas' and str(g.get('kelas_binaan')).upper().replace(" ","") == str(kelas_santri).upper().replace(" ",""):
                nama_wali = g.get('nama_guru', "........................")
                break

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2.5*cm, "LAPORAN BULANAN PERKEMBANGAN HAFALAN SANTRI")

        c.setFont("Helvetica", 10)
        y_kop = tinggi - 3.5*cm
        c.drawString(2*cm, y_kop, "Nama Madrasah")
        c.drawString(4.5*cm, y_kop, f": {dl.get('nama_madrasah', '-')}")
        c.drawString(2*cm, y_kop - 0.5*cm, "Nama Santri")
        c.drawString(4.5*cm, y_kop - 0.5*cm, f": {nama_santri}")
        c.drawString(2*cm, y_kop - 1.0*cm, "No. Induk")
        c.drawString(4.5*cm, y_kop - 1.0*cm, f": {santri.get('no_induk', '-')}")

        c.drawString(lebar - 8*cm, y_kop, "Kelas / Ruang")
        c.drawString(lebar - 5*cm, y_kop, f": {kelas_santri}")
        c.drawString(lebar - 8*cm, y_kop - 0.5*cm, "Periode Bulan")
        c.drawString(lebar - 5*cm, y_kop - 0.5*cm, f": {nama_bulan} {tahun}")

        data_tabel = [['No.', 'Kategori Hafalan', 'Materi yang Dihapalkan', 'Lancar (√)']]
        styles = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (3,1), (3,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]
        
        style_teks = ParagraphStyle(name='NormalTeks', fontName='Helvetica', fontSize=9, leading=12)
        style_bold = ParagraphStyle(name='BoldTeks', fontName='Helvetica-Bold', fontSize=9, leading=12)
        
        materi_dict = MATERI_HAFALAN_PDF.get(jilid, {})
        idx = 1
        
        for kategori, materi_list in materi_dict.items():
            for i, materi in enumerate(materi_list):
                kat_display = Paragraph(f"<b>{kategori.upper()}</b>", style_bold) if i == 0 else ""
                mat_p = Paragraph(materi, style_teks)
                
                is_lulus = data_jilid.get(kategori, {}).get(materi, False)
                mark = "√" if is_lulus else ""
                
                data_tabel.append([str(idx), kat_display, mat_p, mark])
                idx += 1
                
        tabel = Table(data_tabel, colWidths=[1*cm, 3.5*cm, 10.5*cm, 2.5*cm])
        tabel.setStyle(TableStyle(styles))
        
        w, h = tabel.wrap(lebar, tinggi)
        y_tabel = y_kop - 2.0*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)
        
        y_bawah = y_tabel - 1*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y_bawah, "Catatan Evaluasi Wali Kelas:")
        
        c.setFont("Helvetica", 10)
        catatan_p = Paragraph(f"<i>{catatan}</i>", style_teks)
        catatan_p.wrapOn(c, lebar - 4*cm, 2*cm)
        y_bawah -= catatan_p.height + 0.5*cm
        catatan_p.drawOn(c, 2*cm, y_bawah)
        
        y_ttd = y_bawah - 2*cm
        tgl_raport = date.today().strftime('%d %B %Y')
        c.drawString(2*cm, y_ttd, f"Diberikan di : {dl.get('kabupaten_kota', '-')}")
        c.drawString(2*cm, y_ttd - 0.5*cm, f"Tanggal      : {tgl_raport}")
        
        c.drawCentredString(lebar/2, y_ttd - 1.5*cm, "Mengetahui,")
        c.drawString(2.5*cm, y_ttd - 2*cm, "Kepala Madrasah")
        c.drawCentredString(lebar/2, y_ttd - 2*cm, "Orang Tua/Wali")
        c.drawString(lebar - 5.5*cm, y_ttd - 2*cm, "Wali Kelas")

        c.setFont("Helvetica-Bold", 10)
        nama_kepala = dl.get('nama_kepala', '........................')
        c.drawString(2.5*cm, y_ttd - 4.5*cm, nama_kepala)
        c.drawString(lebar - 5.5*cm, y_ttd - 4.5*cm, nama_wali)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # ========================================================
    # 4. CETAK RAPORT AKADEMIK (MDTU / ANGKA)
    # ========================================================
    def cetak_raport(self, nama_santri, semester):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        
        nilai = self.db.get_nilai(santri['id'], semester)
        if not nilai: return None

        dl = self._get_dl_flat()
        pengaturan = dl.get("pengaturan_master", {})
        
        data_lengkap = santri.get("data_lengkap", {})
        kelas_santri = data_lengkap.get("kelas_santri", data_lengkap.get("kelas", "-"))
        
        daftar_guru = self.db.get_semua_guru_lembaga()
        nama_wali = "........................"
        for g in daftar_guru:
            if g.get('role') == 'wali_kelas' and str(g.get('kelas_binaan')).upper().replace(" ","") == str(kelas_santri).upper().replace(" ",""):
                nama_wali = g.get('nama_guru', "........................")
                break
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2.5*cm, "DAFTAR CAPAIAN KOMPETENSI")

        c.setFont("Helvetica", 10)
        y_kop = tinggi - 3.5*cm
        tingkatan_teks = dl.get("tingkatan", "MDTU")
        c.drawString(2*cm, y_kop, f"Nama {tingkatan_teks}")
        c.drawString(4.5*cm, y_kop, f": {dl.get('nama_madrasah', '-')}")
        c.drawString(2*cm, y_kop - 0.5*cm, "Alamat")
        c.drawString(4.5*cm, y_kop - 0.5*cm, f": {dl.get('desa_kelurahan', '-')}")
        c.drawString(2*cm, y_kop - 1*cm, "Nama Santri")
        c.drawString(4.5*cm, y_kop - 1*cm, f": {nama_santri}")
        c.drawString(2*cm, y_kop - 1.5*cm, "No. Induk")
        c.drawString(4.5*cm, y_kop - 1.5*cm, f": {santri.get('no_induk', '-')}")

        sem_teks = "1 (SATU)" if semester == 1 else "2 (DUA)"
        x_kanan = lebar - 8*cm
        c.drawString(x_kanan, y_kop, "Kelas")
        c.drawString(x_kanan + 3*cm, y_kop, f": {kelas_santri}")
        c.drawString(x_kanan, y_kop - 0.5*cm, "Semester")
        c.drawString(x_kanan + 3*cm, y_kop - 0.5*cm, f": {sem_teks}")

        komp_nilai = nilai.get('komponen_nilai', {})
        n_akademik = komp_nilai.get('akademik', {})
        n_narasi = komp_nilai.get('narasi_akademik', {})
        
        data_tabel = [['No.', 'Mata Pelajaran', 'Nilai', 'Predikat', 'Deskripsi Kemampuan']]
        styles = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('ALIGN', (4,0), (4,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]

        kelas_mapel = pengaturan.get("kelas_mapel", {})
        mapel_list = []
        kelas_santri_bersih = str(kelas_santri).upper().replace(" ", "")
        
        for kls, mapels in kelas_mapel.items():
            if str(kls).upper().replace(" ", "") == kelas_santri_bersih:
                mapel_list = mapels
                break

        style_teks = ParagraphStyle(name='NormalTeks', fontName='Helvetica', fontSize=9, leading=12, alignment=0)

        for i, mapel in enumerate(mapel_list):
            skor = int(n_akademik.get(mapel, 0))
            data_mapel = n_narasi.get(mapel, {})
            predikat = data_mapel.get("predikat", "-")
            deskripsi = data_mapel.get("deskripsi", "-")
            
            mapel_p = Paragraph(mapel, style_teks)
            deskripsi_p = Paragraph(deskripsi, style_teks)
            data_tabel.append([str(i+1), mapel_p, str(skor), predikat, deskripsi_p])

        tabel = Table(data_tabel, colWidths=[1*cm, 4.5*cm, 1.5*cm, 1.8*cm, 8.5*cm])
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        y_tabel = y_kop - 2.5*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)

        y_bawah = y_tabel - 0.7*cm

        if semester == 2:
            status_akhir = komp_nilai.get('status', 'LULUS / NAIK KELAS')
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, y_bawah, "KEPUTUSAN:")
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y_bawah - 0.5*cm, "Berdasarkan hasil capaian di atas, santri yang bersangkutan dinyatakan:")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y_bawah - 1.2*cm, status_akhir.upper())
            y_bawah -= 2.2*cm 

        p = komp_nilai.get("kepribadian", {})
        a = komp_nilai.get("absen", {})
        
        def getTextP(val):
            if val == "A": return "Sangat Baik"
            if val == "B": return "Baik"
            if val == "C": return "Cukup"
            return "Kurang"

        kel_val = p.get('Kelakuan','B')
        ker_val = p.get('Kerajinan','B')
        keb_val = p.get('Kebersihan','B')

        kepribadian_kiri = Paragraph("1. Kelakuan<br/>2. Kerajinan<br/>3. Kebersihan", style_teks)
        kepribadian_kanan = Paragraph(f"{kel_val} ({getTextP(kel_val)})<br/>{ker_val} ({getTextP(ker_val)})<br/>{keb_val} ({getTextP(keb_val)})", style_teks)
        
        absen_kiri = Paragraph("1. Sakit<br/>2. Izin<br/>3. Alpa", style_teks)
        absen_kanan = Paragraph(f"{a.get('Sakit','0')} hari<br/>{a.get('Izin','0')} hari<br/>{a.get('Alpa','0')} hari", style_teks)
        catatan_p = Paragraph(f"<b>Catatan Wali Kelas:</b><br/>{komp_nilai.get('catatan', '-')}", style_teks)

        data_bawah = [
            ["Kepribadian & Sikap", kepribadian_kiri, kepribadian_kanan],
            ["Ketidakhadiran", absen_kiri, absen_kanan],
            [catatan_p, "", ""]
        ]
        
        tabel_bawah = Table(data_bawah, colWidths=[4.2*cm, 3.5*cm, 9.6*cm])
        tabel_bawah.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,-2), 'CENTER'),
            ('SPAN', (0,2), (2,2))
        ]))
        wb, hb = tabel_bawah.wrap(lebar, tinggi)
        y_bawah = y_bawah - hb - 0.5*cm
        tabel_bawah.drawOn(c, 2*cm, y_bawah)

        # TANDA TANGAN
        c.setFont("Helvetica", 10)
        y_ttd = y_bawah - 1.5*cm
        tgl_raport = date.today().strftime('%d %B %Y')
        c.drawString(2*cm, y_ttd, f"Diberikan di : {dl.get('kabupaten_kota', '-')}")
        c.drawString(2*cm, y_ttd - 0.5*cm, f"Tanggal      : {tgl_raport}")
        
        c.drawCentredString(lebar/2, y_ttd - 1.5*cm, "Mengetahui,")
        c.drawString(2.5*cm, y_ttd - 2*cm, "Kepala Madrasah")
        c.drawCentredString(lebar/2, y_ttd - 2*cm, "Orang Tua/Wali")
        c.drawString(lebar - 5.5*cm, y_ttd - 2*cm, "Wali Kelas")

        c.setFont("Helvetica-Bold", 10)
        nama_kepala = dl.get('nama_kepala', '........................')
        c.drawString(2.5*cm, y_ttd - 4.5*cm, nama_kepala)
        c.drawString(lebar - 5.5*cm, y_ttd - 4.5*cm, nama_wali)
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_rekap_santri_lengkap(self, kelas_terpilih):
        """Membuat PDF Rekapitulasi Biodata Santri Lengkap Standar KK/KTP (F4 Landscape)"""
        dl = self._get_dl_flat()
        buffer = io.BytesIO()
        
        c = canvas.Canvas(buffer, pagesize=F4_Landscape)
        lebar, tinggi = F4_Landscape
        
        # Header Kop Surat
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, tinggi - 1.5*cm, "REKAPITULASI DATA INDUK SANTRI LENGKAP (STANDAR KK/KTP)")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(lebar/2, tinggi - 2.1*cm, f"MADRASAH: {dl.get('nama_madrasah', '-').upper()} | KELAS: {kelas_terpilih}")
        
        santri_kelas = []
        for s in self.db.data_master:
            dl_santri = s.get("data_lengkap", {})
            kls = dl_santri.get("kelas_santri", dl_santri.get("kelas", ""))
            if kelas_terpilih == "Semua Kelas" or str(kls).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ",""):
                santri_kelas.append(s)

        header_row = ['No.', 'NIS / NIK Santri', 'Nama Santri', 'L/P', 'Tempat, Tgl Lahir', 'Alamat Sesuai KK', 'Data Ayah', 'Data Ibu', 'No. WA Ortu']
        data_tabel = [header_row]
        
        styles = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (2,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]

        style_teks = ParagraphStyle(name='RSTLText', fontName='Helvetica', fontSize=7.5, leading=9.5)

        for i, s in enumerate(santri_kelas):
            dl_s = s.get("data_lengkap", {})
            nis_nik = f"<b>NIS:</b> {s.get('no_induk', '-')}<br/><b>NIK:</b> {dl_s.get('nik_santri', '-')}"
            tgl_lhr = f"{dl_s.get('tempat_lahir', '-')},<br/>{dl_s.get('tanggal_lahir', '-')}"
            
            almt_str = f"{dl_s.get('alamat', '-')}<br/>RT/RW: {dl_s.get('rt_rw', '-')}<br/>Desa: {dl_s.get('desa', '-')}<br/>Kec: {dl_s.get('kecamatan', '-')}"
            
            ayah_str = f"<b>{dl_s.get('nama_ayah', '-')}</b><br/>NIK: {dl_s.get('nik_ayah', '-')}<br/>Kerja: {dl_s.get('pekerjaan_ayah', '-')}"
            ibu_str = f"<b>{dl_s.get('nama_ibu', '-')}</b><br/>NIK: {dl_s.get('nik_ibu', '-')}<br/>Kerja: {dl_s.get('pekerjaan_ibu', '-')}"
            
            data_tabel.append([
                str(i+1),
                Paragraph(nis_nik, style_teks),
                Paragraph(f"<b>{s.get('nama', '-')}</b>", style_teks),
                Paragraph(str(dl_s.get('jk', dl_s.get('jenis_kelamin', '-')))[:1], style_teks),
                Paragraph(tgl_lhr, style_teks),
                Paragraph(almt_str, style_teks),
                Paragraph(ayah_str, style_teks),
                Paragraph(ibu_str, style_teks),
                Paragraph(str(dl_s.get('no_hp', '-')), style_teks)
            ])

        col_widths = [0.8*cm, 3.2*cm, 3.8*cm, 0.8*cm, 3.2*cm, 5.2*cm, 4.5*cm, 4.5*cm, 2.5*cm]
        tabel = Table(data_tabel, colWidths=col_widths)
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 1.2*cm, tinggi - 2.8*cm - h)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_rekap_nilai(self, kelas_terpilih, semester):
        """Membuat PDF Rekapitulasi Nilai Akademik Seluruh Santri Per Kelas (F4 Landscape)"""
        dl = self._get_dl_flat()
        pengaturan = dl.get("pengaturan_master", {})
        
        mapel_list = []
        for kls, mapels in pengaturan.get("kelas_mapel", {}).items():
            if str(kls).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ",""):
                mapel_list = mapels
                break
                
        if not mapel_list: mapel_list = ["Al-Qur'an", "Aqidah", "Fiqih"]

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4_Landscape)
        lebar, tinggi = F4_Landscape

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, tinggi - 1.5*cm, "REKAPITULASI NILAI AKADEMIK SANTRI")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(lebar/2, tinggi - 2.1*cm, f"MADRASAH: {dl.get('nama_madrasah', '-').upper()} | KELAS: {kelas_terpilih} | SEMESTER: {semester}")

        header_row = ['No.', 'Nama Santri'] + mapel_list + ['Jumlah', 'Rata-rata', 'Status']
        data_tabel = [header_row]
        
        styles = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]

        style_teks = ParagraphStyle(name='RKText', fontName='Helvetica', fontSize=8, leading=10)

        santri_kelas = [s for s in self.db.data_master if str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ","")]

        for i, s in enumerate(santri_kelas):
            nilai_s = self.db.get_nilai(s['id'], semester)
            komp = nilai_s.get('komponen_nilai', {}) if nilai_s else {}
            n_akademik = komp.get('akademik', {})
            
            baris = [str(i+1), Paragraph(s['nama'], style_teks)]
            for m in mapel_list:
                baris.append(str(int(n_akademik.get(m, 0))))
                
            baris.append(f"{nilai_s.get('jumlah', 0):.0f}" if nilai_s else "0")
            baris.append(f"{nilai_s.get('rata_rata', 0):.1f}" if nilai_s else "0")
            baris.append(str(komp.get('status', '-')))
            
            data_tabel.append(baris)

        lebar_mapel = min(2.5*cm, 12*cm / max(len(mapel_list), 1))
        col_widths = [1*cm, 5.5*cm] + [lebar_mapel]*len(mapel_list) + [1.8*cm, 1.8*cm, 3.5*cm]

        tabel = Table(data_tabel, colWidths=col_widths)
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 1.5*cm, tinggi - 3.2*cm - h)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_rekap_absen_bulanan(self, kelas_terpilih, bulan, tahun):
        """Membuat PDF Rekapitulasi Presensi/Absensi Santri Bulanan Matriks 1-31 (F4 Landscape)"""
        dl = self._get_dl_flat()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4_Landscape)
        lebar, tinggi = F4_Landscape

        nama_bulan = NAMA_BULAN[bulan] if 1 <= bulan <= 12 else str(bulan)
        _, max_days = calendar.monthrange(int(tahun), int(bulan))

        # Header Kop Surat
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, tinggi - 1.5*cm, "REKAPITULASI PRESENSI / ABSENSI SANTRI BULANAN")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(lebar/2, tinggi - 2.1*cm, f"MADRASAH: {dl.get('nama_madrasah', '-').upper()} | KELAS: {kelas_terpilih} | BULAN: {nama_bulan.upper()} {tahun}")

        # Ambil data santri
        santri_kelas = [s for s in self.db.data_master if kelas_terpilih == "Semua Kelas" or str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ","")]

        # Ambil data absen dari DB
        raw_absen = self.db.get_absensi_bulanan(bulan, tahun)
        map_absen = {}
        for item in raw_absen:
            try:
                tgl_dt = datetime.strptime(item['tanggal'], "%Y-%m-%d")
                map_absen[(item['santri_id'], tgl_dt.day)] = item['status']
            except Exception:
                pass

        header_row = ['No.', 'NIS', 'Nama Santri', 'L/P'] + [str(d) for d in range(1, max_days + 1)] + ['H', 'S', 'I', 'A', '%']
        data_tabel = [header_row]

        styles = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (2,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
        ]

        style_teks = ParagraphStyle(name='RABText', fontName='Helvetica', fontSize=6.5, leading=8)

        for i, s in enumerate(santri_kelas):
            s_id = s['id']
            dl_s = s.get("data_lengkap", {})
            jk_char = str(dl_s.get('jk', dl_s.get('jenis_kelamin', '-')))[:1]
            
            baris = [str(i+1), Paragraph(str(s.get('no_induk', '-')), style_teks), Paragraph(f"<b>{s.get('nama', '-')}</b>", style_teks), jk_char]
            
            cnt_h, cnt_s, cnt_i, cnt_a = 0, 0, 0, 0
            for d in range(1, max_days + 1):
                st_day = map_absen.get((s_id, d), '')
                if st_day == 'Hadir':
                    code = 'H'
                    cnt_h += 1
                elif st_day == 'Sakit':
                    code = 'S'
                    cnt_s += 1
                elif st_day == 'Izin':
                    code = 'I'
                    cnt_i += 1
                elif st_day == 'Alpa':
                    code = 'A'
                    cnt_a += 1
                else:
                    code = '-'
                baris.append(code)

            total_tercatat = cnt_h + cnt_s + cnt_i + cnt_a
            persen = f"{(cnt_h / total_tercatat * 100):.0f}%" if total_tercatat > 0 else "0%"
            
            baris.extend([str(cnt_h), str(cnt_s), str(cnt_i), str(cnt_a), persen])
            data_tabel.append(baris)

        # Hitung lebar kolom otomatis agar presisi
        day_col_width = 16.5 * cm / max_days
        col_widths = [0.7*cm, 2.0*cm, 4.2*cm, 0.7*cm] + [day_col_width]*max_days + [0.7*cm, 0.7*cm, 0.7*cm, 0.7*cm, 1.2*cm]

        tabel = Table(data_tabel, colWidths=col_widths)
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 1.2*cm, tinggi - 2.8*cm - h)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer