import streamlit as st
import pandas as pd
from datetime import date, datetime

def render(db):
    st.header("👥 Input & Kelola Biodata Santri")
    st.caption("Khusus Wali Kelas / Guru untuk menginput dan mengedit data santri di kelasnya")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Sesuai SOP, Kepala Madrasah tidak menginput data santri. Silakan pantau rekap data di menu **Pemantauan & Rekap**.")
        return

    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    kelas_default = getattr(db, 'kelas_binaan', '') or "TKA A"

    t_tambah, t_edit, t_daftar = st.tabs(["➕ Tambah Santri Baru", "✏️ Edit / Hapus Santri", "📋 Daftar Santri Kelas"])

    # --- Pilihan Standar Dropdown ---
    opsi_pendidikan = ["SD/MI", "SMP/MTs", "SMA/SMK/MA", "D1/D2/D3", "S1/D4", "S2", "S3", "Tidak/Belum Sekolah"]
    opsi_pekerjaan = ["Tidak Bekerja", "Ibu Rumah Tangga", "Wiraswasta/Pedagang", "Karyawan Swasta", "PNS/TNI/Polri", "Petani/Peternak", "Buruh", "Lainnya"]
    opsi_agama = ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu"]

    # ==========================================================
    # TAB 1: TAMBAH SANTRI BARU
    # ==========================================================
    with t_tambah:
        st.info("💡 **Standar KK & KTP:** Silakan isi data di bawah ini selengkap mungkin sesuai dengan dokumen Kartu Keluarga / Akta Kelahiran santri.")
        
        with st.form("form_tambah_santri", clear_on_submit=True):
            st.markdown("#### 👤 1. Identitas Diri Santri")
            c1, c2 = st.columns(2)
            with c1:
                no_induk = st.text_input("NIS / Nomor Induk Santri *", help="Nomor Induk Madrasah (Wajib)")
                nik_santri = st.text_input("NIK Santri (16 Digit)")
                nama = st.text_input("Nama Lengkap Santri *")
                jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                
                if getattr(db, 'role', '') == 'wali_kelas' and db.kelas_binaan:
                    kelas_santri = st.text_input("Kelas Santri", value=db.kelas_binaan, disabled=True)
                else:
                    kelas_santri = st.text_input("Kelas Santri *", value=kelas_default)
                    
            with c2:
                tempat_lahir = st.text_input("Tempat Lahir")
                tgl_lahir = st.date_input("Tanggal Lahir", value=date(2018, 1, 1), min_value=date(1990, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
                agama = st.selectbox("Agama", opsi_agama, index=0)
                anak_ke = st.number_input("Anak Ke-", min_value=1, step=1)
                jml_saudara = st.number_input("Dari Jumlah Saudara", min_value=1, step=1)

            st.markdown("---")
            st.markdown("#### 🏠 2. Alamat Sesuai KK")
            c3, c4 = st.columns(2)
            with c3:
                alamat = st.text_area("Alamat Lengkap / Jalan / Dusun")
                rt_rw = st.text_input("RT / RW", placeholder="Contoh: 001 / 002")
                desa = st.text_input("Desa / Kelurahan")
            with c4:
                kecamatan = st.text_input("Kecamatan")
                kabupaten = st.text_input("Kabupaten / Kota")
                kode_pos = st.text_input("Kode Pos")

            st.markdown("---")
            st.markdown("#### 👨‍👩‍👦 3. Data Orang Tua / Wali")
            c5, c6 = st.columns(2)
            with c5:
                st.markdown("**Data Ayah:**")
                nama_ayah = st.text_input("Nama Lengkap Ayah")
                nik_ayah = st.text_input("NIK Ayah (16 Digit)")
                pend_ayah = st.selectbox("Pendidikan Terakhir Ayah", opsi_pendidikan, index=2)
                kerja_ayah = st.selectbox("Pekerjaan Ayah", opsi_pekerjaan, index=2)
                
            with c6:
                st.markdown("**Data Ibu:**")
                nama_ibu = st.text_input("Nama Lengkap Ibu")
                nik_ibu = st.text_input("NIK Ibu (16 Digit)")
                pend_ibu = st.selectbox("Pendidikan Terakhir Ibu", opsi_pendidikan, index=2)
                kerja_ibu = st.selectbox("Pekerjaan Ibu", opsi_pekerjaan, index=1)
                
            no_hp = st.text_input("📱 Nomor Telepon / WhatsApp Orang Tua (Aktif) *", placeholder="Contoh: 081234567890")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_santri = st.form_submit_button("💾 Simpan Data Santri (Standar KK)", use_container_width=True)
            
            if submit_santri:
                if not no_induk or not nama:
                    st.error("❌ Tanda Bintang (*) wajib diisi: No. Induk dan Nama Lengkap tidak boleh kosong!")
                else:
                    data_lengkap = {
                        "kelas_santri": kelas_santri,
                        "nik_santri": nik_santri, "jk": jk, "tempat_lahir": tempat_lahir, "tanggal_lahir": str(tgl_lahir),
                        "agama": agama, "anak_ke": anak_ke, "jml_saudara": jml_saudara,
                        "alamat": alamat, "rt_rw": rt_rw, "desa": desa, "kecamatan": kecamatan, "kabupaten": kabupaten, "kode_pos": kode_pos,
                        "nama_ayah": nama_ayah, "nik_ayah": nik_ayah, "pendidikan_ayah": pend_ayah, "pekerjaan_ayah": kerja_ayah,
                        "nama_ibu": nama_ibu, "nik_ibu": nik_ibu, "pendidikan_ibu": pend_ibu, "pekerjaan_ibu": kerja_ibu,
                        "no_hp": no_hp
                    }
                    # Untuk backwards compatibility tabel, simpan duplikat kunci lama
                    data_lengkap["jenis_kelamin"] = jk 
                    
                    sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                    if sukses:
                        st.toast(f"🎉 Sukses: {nama} berhasil didaftarkan!", icon="✅")
                        st.success(f"✅ {pesan}")
                    else:
                        st.toast("Gagal menyimpan data!", icon="⚠️")
                        st.error(f"❌ {pesan}")

    # ==========================================================
    # TAB 2: EDIT / HAPUS SANTRI
    # ==========================================================
    with t_edit:
        if not db.data_master:
            st.warning("Belum ada santri terdaftar di kelas ini.")
        else:
            map_santri = {f"{s['nama']} (NIS: {s.get('no_induk', '-')})": s for s in db.data_master}
            pilih_santri_str = st.selectbox("🔍 Pilih Santri yang ingin diedit/dihapus:", list(map_santri.keys()))
            
            if pilih_santri_str:
                s_data = map_santri[pilih_santri_str]
                d_lengkap = s_data.get("data_lengkap", {})
                
                with st.form("form_edit_santri"):
                    st.markdown("#### 👤 1. Identitas Diri Santri")
                    c1, c2 = st.columns(2)
                    with c1:
                        e_no_induk = st.text_input("NIS / Nomor Induk Santri", value=s_data.get("no_induk", ""))
                        e_nik_santri = st.text_input("NIK Santri", value=d_lengkap.get("nik_santri", ""))
                        e_nama = st.text_input("Nama Lengkap", value=s_data.get("nama", ""))
                        
                        jk_val = d_lengkap.get("jk", d_lengkap.get("jenis_kelamin", "Laki-laki"))
                        e_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=0 if jk_val=="Laki-laki" else 1)
                        e_kelas = st.text_input("Kelas Santri", value=d_lengkap.get("kelas_santri", db.kelas_binaan or ""))
                        
                    with c2:
                        e_tempat = st.text_input("Tempat Lahir", value=d_lengkap.get("tempat_lahir", ""))
                        tgl_str = d_lengkap.get("tanggal_lahir")
                        try: tgl_val = datetime.strptime(tgl_str, "%Y-%m-%d").date() if tgl_str else date(2018, 1, 1)
                        except: tgl_val = date(2018, 1, 1)
                        e_tgl = st.date_input("Tanggal Lahir", value=tgl_val, min_value=date(1990, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
                        
                        ag_val = d_lengkap.get("agama", "Islam")
                        e_agama = st.selectbox("Agama", opsi_agama, index=opsi_agama.index(ag_val) if ag_val in opsi_agama else 0)
                        e_anak = st.number_input("Anak Ke-", min_value=1, step=1, value=int(d_lengkap.get("anak_ke", 1)))
                        e_sdr = st.number_input("Dari Jumlah Saudara", min_value=1, step=1, value=int(d_lengkap.get("jml_saudara", 1)))

                    st.markdown("---")
                    st.markdown("#### 🏠 2. Alamat Sesuai KK")
                    c3, c4 = st.columns(2)
                    with c3:
                        e_alamat = st.text_area("Alamat Lengkap / Jalan", value=d_lengkap.get("alamat", ""))
                        e_rt = st.text_input("RT / RW", value=d_lengkap.get("rt_rw", ""))
                        e_desa = st.text_input("Desa / Kelurahan", value=d_lengkap.get("desa", ""))
                    with c4:
                        e_kec = st.text_input("Kecamatan", value=d_lengkap.get("kecamatan", ""))
                        e_kab = st.text_input("Kabupaten / Kota", value=d_lengkap.get("kabupaten", ""))
                        e_pos = st.text_input("Kode Pos", value=d_lengkap.get("kode_pos", ""))

                    st.markdown("---")
                    st.markdown("#### 👨‍👩‍👦 3. Data Orang Tua")
                    c5, c6 = st.columns(2)
                    with c5:
                        st.markdown("**Data Ayah:**")
                        e_n_ayah = st.text_input("Nama Ayah", value=d_lengkap.get("nama_ayah", ""))
                        e_nik_ayah = st.text_input("NIK Ayah", value=d_lengkap.get("nik_ayah", ""))
                        pa_val = d_lengkap.get("pendidikan_ayah", "SMA/SMK/MA")
                        e_p_ayah = st.selectbox("Pend. Ayah", opsi_pendidikan, index=opsi_pendidikan.index(pa_val) if pa_val in opsi_pendidikan else 2)
                        ka_val = d_lengkap.get("pekerjaan_ayah", "Wiraswasta/Pedagang")
                        e_k_ayah = st.selectbox("Kerja Ayah", opsi_pekerjaan, index=opsi_pekerjaan.index(ka_val) if ka_val in opsi_pekerjaan else 2)
                        
                    with c6:
                        st.markdown("**Data Ibu:**")
                        e_n_ibu = st.text_input("Nama Ibu", value=d_lengkap.get("nama_ibu", ""))
                        e_nik_ibu = st.text_input("NIK Ibu", value=d_lengkap.get("nik_ibu", ""))
                        pi_val = d_lengkap.get("pendidikan_ibu", "SMA/SMK/MA")
                        e_p_ibu = st.selectbox("Pend. Ibu", opsi_pendidikan, index=opsi_pendidikan.index(pi_val) if pi_val in opsi_pendidikan else 2)
                        ki_val = d_lengkap.get("pekerjaan_ibu", "Ibu Rumah Tangga")
                        e_k_ibu = st.selectbox("Kerja Ibu", opsi_pekerjaan, index=opsi_pekerjaan.index(ki_val) if ki_val in opsi_pekerjaan else 1)

                    e_hp = st.text_input("📱 Nomor Telepon / WA Aktif", value=d_lengkap.get("no_hp", ""))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit_edit = st.form_submit_button("💾 Update Data Santri", use_container_width=True)
                    
                    if submit_edit:
                        data_update = {
                            "kelas_santri": e_kelas, "nik_santri": e_nik_santri, "jk": e_jk, "jenis_kelamin": e_jk, 
                            "tempat_lahir": e_tempat, "tanggal_lahir": str(e_tgl), "agama": e_agama, "anak_ke": e_anak, "jml_saudara": e_sdr,
                            "alamat": e_alamat, "rt_rw": e_rt, "desa": e_desa, "kecamatan": e_kec, "kabupaten": e_kab, "kode_pos": e_pos,
                            "nama_ayah": e_n_ayah, "nik_ayah": e_nik_ayah, "pendidikan_ayah": e_p_ayah, "pekerjaan_ayah": e_k_ayah,
                            "nama_ibu": e_n_ibu, "nik_ibu": e_nik_ibu, "pendidikan_ibu": e_p_ibu, "pekerjaan_ibu": e_k_ibu,
                            "no_hp": e_hp
                        }
                        sukses, pesan = db.simpan_biodata(e_no_induk, e_nama, data_update, santri_id=s_data['id'])
                        if sukses:
                            st.toast(f"🔄 Data {e_nama} diperbarui!", icon="✅")
                            st.rerun()
                        else:
                            st.toast("Gagal mengubah data!", icon="⚠️")
                            st.error(f"❌ {pesan}")
                            
                st.markdown("---")
                st.error("🚨 **ZONA BERBAHAYA (DANGER ZONE)** 🚨")
                konfirmasi = st.checkbox(f"Saya sadar dan yakin ingin menghapus santri **{s_data['nama']}**")
                if st.button("🗑️ Hapus Santri Ini Permanen"):
                    if konfirmasi:
                        sukses, pesan = db.hapus_biodata(s_data['id'])
                        if sukses:
                            st.toast(f"🗑️ Santri dihapus!", icon="✅")
                            st.rerun()
                        else: st.error(f"❌ {pesan}")
                    else:
                        st.warning("Silakan centang kotak konfirmasi merah di atas terlebih dahulu!")

    # ==========================================================
    # TAB 3: DAFTAR SANTRI KELAS
    # ==========================================================
    with t_daftar:
        st.subheader(f"📋 Daftar Santri Kelas {db.kelas_binaan if db.kelas_binaan else ''}")
        if not db.data_master:
            st.info("Belum ada santri terdaftar di kelas ini.")
        else:
            st.success(f"Terdapat total **{len(db.data_master)} santri** yang terdaftar di kelas Anda.")
            list_tampil = []
            for s in db.data_master:
                dl = s.get("data_lengkap", {})
                list_tampil.append({
                    "NIS": s.get("no_induk", "-"),
                    "NIK Santri": dl.get("nik_santri", "-"),
                    "Nama Santri": s.get("nama", "-"),
                    "L/P": dl.get("jk", dl.get("jenis_kelamin", "-"))[:1],
                    "TTL": f"{dl.get('tempat_lahir', '-')}, {dl.get('tanggal_lahir', '-')}",
                    "Nama Ayah": dl.get("nama_ayah", "-"),
                    "Nama Ibu": dl.get("nama_ibu", "-"),
                    "No. WhatsApp": dl.get("no_hp", "-")
                })
            df = pd.DataFrame(list_tampil)
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)