import streamlit as st
from pdf_generator import PDFGenerator

def render(db):
    st.header("🖨️ Cetak Raport Santri")
    st.caption("Menu khusus pencetakan Cover Raport dan Isi Raport Santri (Format Kertas F4)")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Kepala Madrasah dapat memantau dan mencetak rekapitulasi data dari menu **Pemantauan & Rekap**.")
        return

    if not db.data_master:
        st.warning("⚠️ Belum ada data santri di kelas ini.")
        return
        
    gen = PDFGenerator(db)
    
    # Filter Santri Khusus Kelas Binaan Wali Kelas yang sedang Login
    kelas_binaan_bersih = str(db.kelas_binaan).upper().replace(" ", "")
    santri_kelas = [s for s in db.data_master if str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ", "") == kelas_binaan_bersih]
    
    if not santri_kelas:
        st.warning(f"⚠️ Belum ada data santri terdaftar di kelas **{db.kelas_binaan}**.")
        return

    map_santri = {f"{s['nama']} (NIS: {s.get('no_induk', '-')})": s['nama'] for s in santri_kelas}
    pilih_santri_str = st.selectbox("🔍 Pilih Santri yang akan dicetak:", list(map_santri.keys()))
    
    if not pilih_santri_str: 
        return
    
    nama_santri = map_santri[pilih_santri_str]
    
    st.markdown("---")
    st.subheader(f"📄 Dokumen Raport: {nama_santri}")
    
    semester = st.radio(
        "Pilih Semester Penilaian:", 
        [1, 2], 
        horizontal=True, 
        format_func=lambda x: "Semester 1 (Ganjil)" if x == 1 else "Semester 2 (Genap)"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📘 1. Cover Raport")
        st.caption("Cetak Sampul / Cover Depan Raport Santri Format Kertas F4.")
        if st.button("🖨️ Buat Cover Raport", use_container_width=True, key="btn_cover"):
            with st.spinner("Membuat file Cover Raport..."):
                pdf_cover = gen.cetak_cover(nama_santri)
                if pdf_cover:
                    st.success("✅ Cover berhasil dibuat!")
                    st.download_button(
                        "⬇️ Download Cover Raport (PDF)", 
                        pdf_cover, 
                        f"Cover_Raport_{nama_santri}.pdf", 
                        "application/pdf", 
                        use_container_width=True
                    )
                else:
                    st.error("Gagal membuat cover raport.")

    with col2:
        st.markdown("#### 📖 2. Isi Raport Hasil Belajar")
        st.caption("Cetak Lembar Nilai Akademik, Sikap, Presensi & Catatan Wali Kelas.")
        if st.button("🖨️ Buat Isi Raport Akademik", use_container_width=True, key="btn_isi_raport"):
            with st.spinner("Membuat file Isi Raport..."):
                try:
                    pdf_raport = gen.cetak_raport(nama_santri, semester)
                    if pdf_raport:
                        sem_str = "Ganjil" if semester == 1 else "Genap"
                        st.success(f"✅ Raport Semester {semester} berhasil dibuat!")
                        st.download_button(
                            f"⬇️ Download Raport Sem {semester} (PDF)", 
                            pdf_raport, 
                            f"Raport_{sem_str}_{nama_santri}.pdf", 
                            "application/pdf", 
                            use_container_width=True
                        )
                    else:
                        st.error(f"⚠️ Belum ada data nilai tersimpan untuk {nama_santri} di Semester {semester}.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mencetak raport: {e}")