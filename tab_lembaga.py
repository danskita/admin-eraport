import streamlit as st
import base64

def render(db):
    st.header("🏛️ Profil & Identitas Lembaga")

    # Tarik data profil lembaga dan pengaturan master (untuk melihat daftar kelas)
    dl_raw = db.data_lembaga
    profil = dl_raw.get("profil_lengkap", {})
    pengaturan = dl_raw.get("pengaturan_master", {})
    
    # Ambil daftar kelas dari Master Data (jika kosong, beri nilai default)
    list_kelas = pengaturan.get("kelas", ["Kelas 1"])

    with st.form("form_lembaga"):
        st.subheader("Data Madrasah")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Madrasah", value=dl_raw.get("nama_madrasah", ""))
            nsm = st.text_input("Nomor Statistik (NSM)", value=dl_raw.get("nsm", ""))
            
            # Tingkatan dikunci sesuai saat pendaftaran awal
            tingkatan = st.text_input("Tingkatan Lembaga", value=profil.get("tingkatan", "MDTU"), disabled=True)
            
            alamat = st.text_input("Alamat Jalan", value=profil.get("alamat", ""))
            desa = st.text_input("Desa/Kelurahan", value=profil.get("desa_kelurahan", ""))
        with col2:
            kecamatan = st.text_input("Kecamatan", value=profil.get("kecamatan", ""))
            kabupaten = st.text_input("Kabupaten/Kota", value=profil.get("kabupaten_kota", ""))
            provinsi = st.text_input("Provinsi", value=profil.get("provinsi", ""))
            tahun = st.text_input("Tahun Pelajaran", value=profil.get("tahun_pelajaran", ""))

        st.subheader("Pejabat & Pengesahan")
        col3, col4 = st.columns(2)
        with col3:
            kepala = st.text_input("Nama Kepala Madrasah", value=profil.get("kepala_madin", ""))
            tempat = st.text_input("Tempat Titimangsa (cth: Jakarta)", value=profil.get("tempat_raport", ""))
            tanggal = st.text_input("Tanggal Raport", value=profil.get("tanggal_raport", ""))
            
        with col4:
            st.write("**👨‍🏫 Daftar Wali Kelas**")
            st.caption("Isi nama wali kelas sesuai dengan tingkatan kelasnya.")
            
            # Menarik data wali kelas lama (mengantisipasi jika data lama masih berupa teks biasa)
            wali_kelas_dict = profil.get("wali_kelas", {})
            if not isinstance(wali_kelas_dict, dict): 
                wali_kelas_dict = {}

            # Membuat input nama Wali Kelas sebanyak jumlah kelas secara otomatis!
            input_wali = {}
            for k in list_kelas:
                val_awal = wali_kelas_dict.get(k, "")
                input_wali[k] = st.text_input(f"Wali {k}", value=val_awal)

        st.markdown("---")
        st.subheader("🖼️ Logo Madrasah")
        logo_file = st.file_uploader("Pilih Logo Madrasah (Format: PNG / JPG)", type=["png", "jpg", "jpeg"])
        
        logo_b64 = profil.get("logo", "")
        
        if logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
            st.image(logo_file, width=150, caption="Logo yang akan disimpan")
        elif logo_b64:
            try:
                st.image(base64.b64decode(logo_b64), width=150, caption="Logo tersimpan")
            except:
                st.write("Gagal memuat logo lama.")

        submitted = st.form_submit_button("💾 Simpan Perubahan")

        if submitted:
            data_baru = {
                "nama_madrasah": nama, 
                "nsm": nsm, 
                "profil_lengkap": {
                    "tingkatan": profil.get("tingkatan", "MDTU"),
                    "alamat": alamat, 
                    "desa_kelurahan": desa, 
                    "kecamatan": kecamatan, 
                    "kabupaten_kota": kabupaten,
                    "provinsi": provinsi, 
                    "tahun_pelajaran": tahun,
                    "kepala_madin": kepala, 
                    "wali_kelas": input_wali, # <--- SEKARANG MENYIMPAN DATA MULTI WALI KELAS
                    "tempat_raport": tempat,
                    "tanggal_raport": tanggal, 
                    "logo": logo_b64
                }
            }
            sukses, pesan = db.simpan_lembaga(data_baru)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)