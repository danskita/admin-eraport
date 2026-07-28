import streamlit as st
from database import DataEngine

# Import semua modul tab
import tab_master
import tab_profil_guru
import tab_biodata
import tab_absen
import tab_nilai
import tab_data
import tab_cetak
import tab_hafalan

# Konfigurasi Halaman Web
st.set_page_config(page_title="e-Raport Madrasah", page_icon="📚", layout="wide")

# ==========================================
# DEFINISI FUNGSI BANNER
# ==========================================
def tampilkan_banner():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #023047, #0d98ba, #219ebc);
        padding: 35px 20px;
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid #8ecae6;
    ">
        <h1 style="
            color: #ffffff; 
            margin-bottom: 5px; 
            font-size: 2.8rem; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        ">
            🕌 Portal e-Raport Diniyah & TKA/TPA
        </h1>
        <h3 style="
            color: #ffb703; 
            margin-top: 0px; 
            font-weight: 500;
            font-size: 1.3rem;
            letter-spacing: 1px;
        ">
            Sistem Evaluasi Akademik & Pantauan Hafalan Santri
        </h3>
        <p style="
            color: #e0e0e0; 
            font-size: 15px; 
            margin-top: 15px; 
            margin-bottom: 0px;
        ">
            Lembaga Pembinaan dan Pengembangan TK Al-Qur'an (LPPTKA) BKPRMI<br>
            <i>Efisien, Cepat, dan Tepat Berstandar Nasional</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# FUNGSI UTAMA (MAIN APP)
# ==========================================
def main():
    tampilkan_banner()
    
    if 'db' not in st.session_state:
        st.session_state.db = DataEngine()
    
    db = st.session_state.db

    # ------------------------------------------------
    # HALAMAN LOGIN & PENDAFTARAN LEMBAGA
    # ------------------------------------------------
    if not db.lembaga_id:
        tab_login, tab_daftar = st.tabs(["🔑 Login Akun", "📝 Daftar Lembaga Baru"])
        
        # --- TAB 1: LOGIN ---
        with tab_login:
            st.subheader("Masuk ke Sistem")
            with st.form("form_login"):
                identitas = st.text_input("Email (Kepala Madrasah) / Username NIP (Guru)")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Masuk / Login", use_container_width=True)
                
                if submit:
                    sukses, pesan = db.login(identitas, password)
                    if sukses:
                        st.success(pesan)
                        st.rerun()
                    else:
                        st.error(pesan)
        
        # --- TAB 2: PENDAFTARAN LEMBAGA BARU ---
        with tab_daftar:
            st.subheader("Pendaftaran Madrasah / Lembaga Baru")
            st.info("💡 Setelah mendaftar, akun Anda akan berstatus *Menunggu Verifikasi* oleh Super Admin sebelum bisa digunakan untuk login.")
            
            with st.form("form_daftar_lembaga"):
                reg_nama = st.text_input("Nama Madrasah / Lembaga *", placeholder="Contoh: MDTU Al-Ikhlas")
                reg_nsm = st.text_input("Nomor Statistik Madrasah (NSM) *")
                reg_tingkatan = st.selectbox("Tingkatan Lembaga *", ["TKA", "TPA", "MDTU", "MDTW"])
                reg_email = st.text_input("Email Kepala Madrasah (Untuk Login) *")
                reg_pass = st.text_input("Password Baru *", type="password")
                
                submit_reg = st.form_submit_button("Daftarkan Lembaga", use_container_width=True)
                
                if submit_reg:
                    if not reg_nama or not reg_nsm or not reg_email or not reg_pass:
                        st.error("❌ Semua kolom bertanda bintang (*) wajib diisi!")
                    else:
                        sukses, pesan = db.register_madrasah(reg_email, reg_pass, reg_nama, reg_nsm, reg_tingkatan)
                        if sukses:
                            st.success(pesan)
                        else:
                            st.error(pesan)
        return

    # ------------------------------------------------
    # JIKA SUDAH LOGIN (MENU UTAMA)
    # ------------------------------------------------
    nama_lembaga = db.data_lembaga.get('nama_madrasah', 'Madrasah')
    nama_pengguna = db.data_lembaga.get('_nama_guru') or db.data_lembaga.get('email', 'Admin')
    
    st.sidebar.title(f"🏫 {nama_lembaga}")
    st.sidebar.write(f"👤 **{nama_pengguna}**")
    
    # --- ROUTING CERDAS (SMART ROUTING) ---
    if db.role == 'kepala_madrasah':
        st.sidebar.caption("👔 Role: Kepala Madrasah")
        menu_options = ["Pemantauan & Rekap", "Master Data", "Profil Guru"]
    else:
        kelas = db.kelas_binaan if db.kelas_binaan else "Belum Atur Kelas"
        st.sidebar.caption(f"👨‍🏫 Role: Wali Kelas ({kelas})")
        
        # KELAS TKA / TPA MEMILIKI DUA MENU PENILAIAN: INPUT HAFALAN & INPUT NILAI AKADEMIK
        if "TKA" in str(kelas).upper() or "TPA" in str(kelas).upper():
            menu_options = ["Profil Guru", "Input Biodata", "Input Absensi", "Input Hafalan", "Input Nilai Akademik", "Pemantauan & Rekap", "Cetak Raport"]
        else:
            menu_options = ["Profil Guru", "Input Biodata", "Input Absensi", "Input Nilai Akademik", "Pemantauan & Rekap", "Cetak Raport"]
            
    st.sidebar.markdown("---")
    pilihan = st.sidebar.radio("Navigasi Menu", menu_options)
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout / Keluar", use_container_width=True, key="btn_logout_utama"):
        db.logout()
        st.rerun()

    # --- EKSEKUSI HALAMAN TAB ---
    if pilihan == "Master Data":
        tab_master.render(db)
    elif pilihan == "Profil Guru":
        tab_profil_guru.render(db)
    elif pilihan == "Pemantauan & Rekap":
        tab_data.render(db)
    elif pilihan == "Input Biodata":
        tab_biodata.render(db)
    elif pilihan == "Input Absensi":
        tab_absen.render(db)
    elif pilihan == "Input Hafalan":
        tab_hafalan.render(db)
    elif pilihan == "Input Nilai Akademik":
        tab_nilai.render(db)
    elif pilihan == "Cetak Raport":
        tab_cetak.render(db)

if __name__ == "__main__":
    main()