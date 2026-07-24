import streamlit as st
import pandas as pd
from supabase import create_client

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Super Admin - app_eraportDiniyah", page_icon="👁️", layout="wide")

# --- INISIALISASI SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- SISTEM LOGIN SUPER ADMIN ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔐 Login Super Admin app_eraportDiniyah")
    st.markdown("Dasbor khusus pemantauan dan persetujuan akun madrasah oleh Admin: dasnkita.")
    
    with st.form("form_login_admin"):
        pin = st.text_input("Masukkan PIN Rahasia", type="password")
        submit = st.form_submit_button("Masuk Dasbor")
        
        if submit:
            if pin == "123456": # SILAKAN GANTI PIN RAHASIA INI NANTI
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ PIN Salah! Akses ditolak.")
    st.stop()

# --- HEADER DASBOR UTAMA ---
col_judul, col_logout = st.columns([8, 2])
with col_judul:
    st.title("👁️ Menara Pengawas app_eraportDiniyah")
    st.caption("Administrator: dasnkita | Email Sistem: tasikita@gmail.com")
with col_logout:
    if st.button("🚪 Keluar", width='stretch'):
        st.session_state.admin_logged_in = False
        st.rerun()

st.markdown("---")

# ==========================================
# --- SIDEBAR: PINTASAN INFRASTRUKTUR ---
# ==========================================
with st.sidebar:
    st.markdown("### 🔗 Pintasan Infrastruktur")
    st.write("Akses cepat ke pusat kendali server Anda:")
    st.link_button("🗄️ Dasbor Supabase", "https://supabase.com/dashboard/project/gxrhvxnubqrpzjngxpsr", use_container_width=True)
    st.link_button("🐙 Repositori GitHub", "https://github.com/danskita/admin-eraport", use_container_width=True)
    st.link_button("☁️ Streamlit Cloud", "https://share.streamlit.io/", use_container_width=True)
    st.divider()
    st.caption("⚠️ Tombol ini hanya muncul di dasbor Super Admin dan aman dari jangkauan madrasah.")
# ==========================================

# --- TARIK DATA DARI SUPABASE ---
try:
    response = supabase.table("lembaga").select("*").execute()
    data_lembaga = response.data if response.data else []
except Exception as e:
    st.error(f"Gagal mengambil data dari Supabase: {e}")
    data_lembaga = []

# Membongkar JSONB untuk dibaca
for d in data_lembaga:
    profil = d.get("profil_lengkap", {})
    d["kabupaten_kota"] = profil.get("kabupaten_kota", "-")
    d["provinsi"] = profil.get("provinsi", "-")

# --- MEMBUAT TAB MENU ---
tab_verifikasi, tab_manajemen, tab_statistik = st.tabs([
    "🚦 Antrean Verifikasi", "🛡️ Manajemen & Keamanan Akun", "📊 Statistik Global"
])

# ==========================================
# 1. TAB ANTREAN VERIFIKASI
# ==========================================
with tab_verifikasi:
    st.subheader("Madrasah Menunggu Persetujuan")
    st.info("Madrasah di bawah ini sudah mendaftar, tetapi belum bisa login sebelum Anda klik 'Setujui'.")
    
    belum_aktif = [d for d in data_lembaga if not d.get("is_active", False)]
    
    if not belum_aktif:
        st.success("🎉 Tidak ada antrean! Semua madrasah yang terdaftar sudah aktif.")
    else:
        for m in belum_aktif:
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**🏫 {m.get('nama_madrasah', 'Tanpa Nama')}** (NSM: {m.get('nsm', '-')})")
                    st.write(f"📧 Email Pendaftar: `{m.get('email', '-')}`")
                
                with c2:
                    if st.button(f"✅ Setujui", key=f"btn_setuju_{m['id']}", type="primary", use_container_width=True):
                        try:
                            supabase.table("lembaga").update({"is_active": True}).eq("id", m['id']).execute()
                            st.success(f"{m['nama_madrasah']} berhasil disetujui!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menyetujui: {e}")
                
                with c3:
                    # FITUR BARU: TOLAK & HAPUS PENDAFTAR
                    if st.button(f"❌ Tolak & Hapus", key=f"btn_tolak_{m['id']}", use_container_width=True):
                        try:
                            supabase.table("lembaga").delete().eq("id", m['id']).execute()
                            st.warning(f"Pendaftar {m['nama_madrasah']} telah ditolak dan dihapus!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menghapus: {e}")
            st.divider()

# ==========================================
# 2. TAB MANAJEMEN & KEAMANAN AKUN
# ==========================================
with tab_manajemen:
    st.subheader("Manajemen Hak Akses & Bantuan Sandi")
    st.write("Di sini Anda bisa memantau, memblokir, membantu mereset kata sandi, atau menghapus akun madrasah.")
    
    if data_lembaga:
        for m in data_lembaga:
            status_ikon = "Aktif ✅" if m.get("is_active") else "Ditangguhkan / Antre ⏳"
            with st.expander(f"🏫 {m.get('nama_madrasah', 'Tanpa Nama')} - {m.get('email', '-')} (Status: {status_ikon})"):
                
                c_info, c_aksi1, c_aksi2, c_aksi3 = st.columns([2, 1, 1, 1])
                
                with c_info:
                    st.write(f"**NSM:** {m.get('nsm', '-')}")
                    st.write(f"**Wilayah:** {m.get('kabupaten_kota', '-')}, {m.get('provinsi', '-')}")
                
                with c_aksi1:
                    # FITUR RESET PASSWORD
                    if st.button("🔑 Reset Sandi", key=f"btn_reset_{m['id']}", use_container_width=True):
                        try:
                            supabase.auth.reset_password_email(m.get('email'))
                            st.success(f"Link reset sandi dikirim ke {m.get('email')}")
                        except Exception as e:
                            st.error(f"Gagal mengirim email: {e}")
                            
                with c_aksi2:
                    # FITUR SUSPEND / BLOKIR
                    if m.get('is_active'):
                        if st.button("🚫 Blokir Akses", key=f"btn_blokir_{m['id']}", use_container_width=True):
                            try:
                                supabase.table("lembaga").update({"is_active": False}).eq("id", m['id']).execute()
                                st.warning(f"Akses {m.get('nama_madrasah')} ditangguhkan.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal memblokir: {e}")
                    else:
                        if st.button("✅ Aktifkan", key=f"btn_aktifkan_{m['id']}", use_container_width=True):
                            try:
                                supabase.table("lembaga").update({"is_active": True}).eq("id", m['id']).execute()
                                st.success(f"Akses {m.get('nama_madrasah')} dipulihkan.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal mengaktifkan: {e}")
                
                with c_aksi3:
                    # FITUR BARU: HAPUS PERMANEN
                    if st.button("🗑️ Hapus Akun", key=f"btn_hapus_{m['id']}", type="primary", use_container_width=True):
                        try:
                            # Menghapus dari database utama
                            supabase.table("lembaga").delete().eq("id", m['id']).execute()
                            st.success(f"Akun {m.get('nama_madrasah')} beserta seluruh datanya berhasil dihapus permanen!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menghapus akun: {e}")
    else:
        st.info("Belum ada data madrasah terdaftar di database.")

# ==========================================
# 3. TAB STATISTIK GLOBAL
# ==========================================
with tab_statistik:
    st.subheader("Statistik Nasional Platform")
    total_madrasah = len(data_lembaga)
    aktif = len([d for d in data_lembaga if d.get("is_active", False)])
    non_aktif = total_madrasah - aktif
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pendaftar", total_madrasah)
    c2.metric("Madrasah Aktif", aktif)
    c3.metric("Antrean / Ditangguhkan", non_aktif)