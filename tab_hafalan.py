import streamlit as st
from pdf_generator import PDFGenerator
from datetime import datetime

NAMA_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ==========================================
# DATABASE KURIKULUM HAFALAN TKA/TPA (IQRA 1 - 6)
# ==========================================
MATERI_HAFALAN = {
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

def render(db):
    st.header("📖 Kelola Target Hafalan Santri (TKA / TPA)")
    st.caption("Ceklis setoran hafalan dan cetak laporan bulanan langsung dari halaman ini.")

    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas TKA / TPA.")
        return
        
    if not db.kelas_binaan:
        st.warning("⚠️ Anda belum memiliki kelas binaan.")
        return

    kelas_binaan_bersih = str(db.kelas_binaan).upper().replace(" ", "")
    santri_kelas = [s for s in db.data_master if str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ", "") == kelas_binaan_bersih]
    
    if not santri_kelas:
        st.info(f"Belum ada data santri di kelas {db.kelas_binaan}.")
        return

    map_santri = {f"{s['nama']} (NIS: {s.get('no_induk', '-')})": s for s in santri_kelas}
    
    # ==========================================
    # LOGIKA SMART FILTERING JILID BERDASARKAN KELAS
    # ==========================================
    opsi_jilid = list(MATERI_HAFALAN.keys()) # Default semua jilid
    
    if "TKAA" in kelas_binaan_bersih:
        opsi_jilid = ["IQRA 1", "IQRA 2"]
    elif "TKAB" in kelas_binaan_bersih:
        opsi_jilid = ["IQRA 2", "IQRA 3"]
    elif "TPAA" in kelas_binaan_bersih:
        opsi_jilid = ["IQRA 3", "IQRA 4"]
    elif "TPAB" in kelas_binaan_bersih:
        opsi_jilid = ["IQRA 5", "IQRA 6"]
    
    col1, col2 = st.columns(2)
    with col1:
        pilih_nama = st.selectbox("🔍 Pilih Nama Santri:", list(map_santri.keys()))
    with col2:
        jilid_aktif = st.selectbox(f"📚 Pilih Jilid (Khusus Kelas {db.kelas_binaan}):", opsi_jilid)
        
    st.markdown("---")
    
    if pilih_nama:
        santri_id = map_santri[pilih_nama]['id']
        nama_santri = map_santri[pilih_nama]['nama']
        
        riwayat = db.get_nilai(santri_id, 99)
        komp_lama = riwayat.get("komponen_nilai", {}) if riwayat else {}
        jilid_tersimpan = komp_lama.get(jilid_aktif, {})

        # MEMBUAT 2 TAB
        tab_input, tab_cetak = st.tabs(["📝 Input & Ceklis Setoran", "🖨️ Cetak Laporan Bulanan"])

        # ==========================================
        # TAB 1: INPUT HAFALAN
        # ==========================================
        with tab_input:
            st.subheader(f"Ceklis Setoran Hafalan - {jilid_aktif}")
            st.info("💡 Materi yang sudah dihafal (dicentang) akan **terkunci otomatis** agar tidak terklik dua kali.")
            
            with st.form("form_hafalan"):
                materi_jilid = MATERI_HAFALAN[jilid_aktif]
                hasil_ceklis = {}
                
                for kategori, daftar_materi in materi_jilid.items():
                    st.markdown(f"**{kategori.upper()}**")
                    hasil_ceklis[kategori] = {}
                    
                    cols = st.columns(2)
                    for i, materi in enumerate(daftar_materi):
                        with cols[i % 2]:
                            status_awal = jilid_tersimpan.get(kategori, {}).get(materi, False)
                            
                            if status_awal:
                                st.checkbox(f"{materi} ✅", value=True, disabled=True, key=f"{jilid_aktif}_{kategori}_{i}")
                                hasil_ceklis[kategori][materi] = True 
                            else:
                                is_checked = st.checkbox(materi, value=False, key=f"{jilid_aktif}_{kategori}_{i}")
                                hasil_ceklis[kategori][materi] = is_checked
                    
                    st.markdown("<hr style='margin: 10px 0; border: 1px dashed #ddd;'>", unsafe_allow_html=True)
                    
                st.markdown("📝 **Catatan / Evaluasi Perkembangan Jilid Ini:**")
                catatan_lama = komp_lama.get("catatan_" + jilid_aktif, "")
                catatan_guru = st.text_area("Opsional", value=catatan_lama, placeholder="Contoh: Bacaan tajwid sudah bagus, hafalan hadist perlu lebih diulang...")

                submit_hafalan = st.form_submit_button("💾 Simpan Ceklis Hafalan", use_container_width=True)
                
                if submit_hafalan:
                    komp_lama[jilid_aktif] = hasil_ceklis
                    komp_lama["catatan_" + jilid_aktif] = catatan_guru
                    
                    data_simpan = {
                        "santri_id": santri_id,
                        "semester": 99, 
                        "jumlah": 0,
                        "rata_rata": 0,
                        "komponen_nilai": komp_lama
                    }
                    
                    id_nilai = riwayat['id'] if riwayat else None
                    sukses, pesan = db.simpan_nilai(data_simpan, id_nilai)
                    
                    if sukses:
                        st.toast("✅ Ceklis hafalan berhasil diperbarui!", icon="🎉")
                        st.success("Berhasil menyimpan perkembangan hafalan santri.")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal menyimpan: {pesan}")

        # ==========================================
        # TAB 2: CETAK LAPORAN
        # ==========================================
        with tab_cetak:
            st.subheader("📅 Cetak Laporan Hafalan Bulanan")
            gen = PDFGenerator(db)
            
            c_bln, c_thn = st.columns(2)
            with c_bln:
                bln_skrg = datetime.now().month
                pilih_bulan = st.selectbox("Laporan Bulan:", NAMA_BULAN, index=bln_skrg-1)
            with c_thn:
                thn_skrg = datetime.now().year
                pilih_tahun = st.selectbox("Tahun:", [thn_skrg, thn_skrg+1, thn_skrg+2])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🖨️ Buat & Download Laporan PDF (Kertas F4)", use_container_width=True):
                with st.spinner(f"Menyiapkan laporan {nama_santri} bulan {pilih_bulan}..."):
                    pdf_laporan = gen.cetak_laporan_hafalan_bulanan(nama_santri, jilid_aktif, pilih_bulan, str(pilih_tahun))
                    if pdf_laporan:
                        st.success("✅ Dokumen berhasil dibuat! Silakan klik tombol di bawah untuk mengunduh.")
                        st.download_button(
                            "⬇️ Klik Disini Untuk Menyimpan PDF", 
                            pdf_laporan, 
                            f"Hafalan_{pilih_bulan}_{pilih_tahun}_{nama_santri}.pdf", 
                            "application/pdf", 
                            use_container_width=True
                        )
                    else:
                        st.error(f"Terjadi kesalahan saat memuat dokumen {nama_santri}.")