import streamlit as st
from datetime import date, datetime

def render(db):
    st.header("👤 Profil & Biodata Diri")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    # Kepala Madrasah tidak butuh profil guru, karena ia memantau data madrasah
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.info("💡 Halaman ini dirancang khusus untuk Guru / Wali Kelas agar mereka bisa melengkapi biodata dan mengubah password mereka sendiri.")
        return

    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif.")
        return

    # 🔍 MENCARI DATA GURU YANG SEDANG LOGIN
    daftar_guru = db.get_semua_guru_lembaga()
    nama_guru_aktif = db.data_lembaga.get('_nama_guru')
    kelas_binaan_aktif = getattr(db, 'kelas_binaan', None)
    
    my_data = None
    for g in daftar_guru:
        # Mencocokkan data login dengan database guru
        if g.get('nama_guru') == nama_guru_aktif and g.get('kelas_binaan') == kelas_binaan_aktif:
            my_data = g
            break
            
    if not my_data:
        st.error("❌ Data profil Anda tidak ditemukan di sistem. Silakan hubungi Kepala Madrasah.")
        return

    st.markdown("---")
    
    # ==========================================
    # FORM PENGISIAN BIODATA GURU
    # ==========================================
    with st.form("form_profil_guru"):
        st.subheader("🔐 Informasi Akun (Dikunci)")
        st.caption("Data identitas dasar di bawah ini hanya bisa diubah oleh Kepala Madrasah.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nama Lengkap", value=my_data.get('nama_guru', ''), disabled=True)
            st.text_input("NIP / Username", value=my_data.get('username', ''), disabled=True)
        with c2:
            st.text_input("Hak Akses (Role)", value=str(my_data.get('role', '')).replace("_", " ").title(), disabled=True)
            st.text_input("Kelas Binaan", value=my_data.get('kelas_binaan', '-') or "-", disabled=True)
            
        st.markdown("---")
        st.subheader("💳 Lengkapi Biodata Diri Anda")
        st.caption("Pastikan data di bawah ini diisi sesuai dengan KTP Anda.")
        
        c3, c4 = st.columns(2)
        with c3:
            e_nik = st.text_input("NIK (Nomor Induk Kependudukan)", value=my_data.get('nik', '') or "")
            e_tempat = st.text_input("Tempat Lahir", value=my_data.get('tempat_lahir', '') or "")
            
            # Konversi Tanggal dengan rentang min_value & max_value agar terbuka lebar
            tgl_str = my_data.get('tanggal_lahir')
            try: 
                tgl_val = datetime.strptime(tgl_str, "%Y-%m-%d").date() if tgl_str else date(1990, 1, 1)
            except: 
                tgl_val = date(1990, 1, 1)
                
            e_tgl = st.date_input(
                "Tanggal Lahir", 
                value=tgl_val,
                min_value=date(1940, 1, 1),
                max_value=date.today()
            )
            
            # Dropdown Jenis Kelamin
            jks = ["Laki-laki", "Perempuan"]
            jk_val = my_data.get('jenis_kelamin', 'Laki-laki')
            idx_jk = jks.index(jk_val) if jk_val in jks else 0
            e_jk = st.selectbox("Jenis Kelamin", jks, index=idx_jk)
            
        with c4:
            e_hp = st.text_input("Nomor HP / WhatsApp Aktif", value=my_data.get('no_hp', '') or "")
            e_alamat = st.text_area("Alamat Lengkap", value=my_data.get('alamat', '') or "")
            
            # Fitur Ubah Password Mandiri
            st.markdown("<br>", unsafe_allow_html=True)
            e_password = st.text_input("🔑 Ubah Password (Opsional)", type="password", help="Isi bagian ini HANYA jika Anda ingin mengubah password yang diberikan oleh Kepala Madrasah. Kosongkan jika tidak ingin mengubah sandi.")
            
        submit_profil = st.form_submit_button("💾 Simpan Biodata Saya", use_container_width=True)
        
        if submit_profil:
            # Menyimpan data kembali ke database
            sukses, pesan = db.update_akun_guru(
                guru_id=my_data['id'],
                nama_guru=my_data['nama_guru'],      # Tetap pakai nama asli (locked)
                username=my_data['username'],        # Tetap pakai username asli (locked)
                password=e_password,                 # Password baru (jika diisi)
                role=my_data['role'],                # Role asli (locked)
                kelas_binaan=my_data['kelas_binaan'],# Kelas asli (locked)
                nik=e_nik,
                jk=e_jk,
                tempat_lahir=e_tempat,
                tgl_lahir=e_tgl,
                no_hp=e_hp,
                alamat=e_alamat
            )
            
            if sukses:
                st.toast("✅ Biodata Anda berhasil diperbarui!", icon="🎉")
                st.success("✅ Biodata Anda berhasil diperbarui di sistem!")
                st.rerun()
            else:
                st.toast("Gagal mengubah biodata!", icon="⚠️")
                st.error(pesan)