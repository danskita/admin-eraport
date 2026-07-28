import streamlit as st
from datetime import date

def render(db):
    st.header("📅 Input Absensi Harian Santri")
    st.caption("Pencatatan Kehadiran Santri Harian oleh Wali Kelas")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Sesuai SOP, Kepala Madrasah tidak mengisi absensi harian. Silakan pantau kehadiran di menu **Pemantauan & Rekap**.")
        return

    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    if not db.data_master:
        st.warning("⚠️ Belum ada data santri di kelas ini. Silakan tambahkan santri terlebih dahulu di menu **Input Biodata**.")
        return

    st.markdown("---")
    
    col_tgl1, col_tgl2 = st.columns([1, 2])
    with col_tgl1:
        tanggal_absen = st.date_input("Pilih Tanggal Absensi:", value=date.today())
    with col_tgl2:
        st.info(f"📆 Mengisi absensi untuk **{len(db.data_master)} santri** pada tanggal **{tanggal_absen.strftime('%d %B %Y')}**")

    # Ambil data absensi lama jika pernah diinput di tanggal ini
    data_absen_lama = db.get_absensi_harian(tanggal_absen)
    
    st.markdown("---")
    
    with st.form("form_absensi_harian"):
        dict_status_baru = {}
        opsi_status = ["Hadir", "Sakit", "Izin", "Alpa"]
        
        st.subheader("📋 Daftar Kehadiran Santri")
        
        for i, santri in enumerate(db.data_master):
            s_id = santri['id']
            s_nama = santri['nama']
            s_no = santri.get('no_induk', '-')
            
            # Status default: "Hadir"
            status_default = data_absen_lama.get(s_id, "Hadir")
            idx_default = opsi_status.index(status_default) if status_default in opsi_status else 0
            
            col_s1, col_s2 = st.columns([2, 2])
            with col_s1:
                st.markdown(f"**{i+1}. {s_nama}** `(NIS: {s_no})`")
            with col_s2:
                dict_status_baru[s_id] = st.radio(
                    f"Status Kehadiran {s_nama}", 
                    opsi_status, 
                    index=idx_default, 
                    horizontal=True, 
                    key=f"absen_{s_id}_{tanggal_absen}",
                    label_visibility="collapsed"
                )
            st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)
            
        submit_absen = st.form_submit_button("💾 Simpan Absensi Harian")
        
        if submit_absen:
            sukses, pesan = db.simpan_absensi_harian(tanggal_absen, dict_status_baru)
            if sukses:
                st.success(f"✅ {pesan}")
                st.rerun()
            else:
                st.error(f"❌ {pesan}")