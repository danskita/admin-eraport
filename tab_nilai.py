import streamlit as st

def hitung_predikat_dan_deskripsi(nilai, nama_mapel):
    if nilai >= 86:
        predikat = "A"
        narasi = f"Sangat baik dan sangat menguasai seluruh indikator capaian pada mata pelajaran {nama_mapel}."
    elif nilai >= 71:
        predikat = "B"
        narasi = f"Baik dan menunjukkan penguasaan yang memadai pada sebagian besar indikator mata pelajaran {nama_mapel}."
    elif nilai >= 56:
        predikat = "C"
        narasi = f"Cukup menguasai indikator dasar pada {nama_mapel}, masih memerlukan bimbingan rutin."
    else:
        predikat = "D"
        narasi = f"Perlu bimbingan intensif dan perhatian khusus pada kompetensi dasar {nama_mapel}."
    return predikat, narasi

def hitung_keputusan_otomatis(rata_rata, mapel_dibawah_kkm, alpa, sikap_baik, kelas_sekarang):
    urutan_kelas = {
        "TKA A": "TKA B", "TKA B": "TPA A", "TPA A": "TPA B", "TPA B": "LULUS",
        "MDTU 1": "MDTU 2", "MDTU 2": "MDTU 3", "MDTU 3": "MDTU 4", "MDTU 4": "LULUS"
    }
    
    syarat_lulus = (rata_rata >= 60 and mapel_dibawah_kkm <= 2 and alpa <= 10 and sikap_baik)
    kelas_bersih = str(kelas_sekarang).upper().strip()
    kelas_tujuan = urutan_kelas.get(kelas_bersih, "LULUS")
    
    if syarat_lulus:
        if kelas_tujuan == "LULUS" or "MDTU 4" in kelas_bersih or "TPA B" in kelas_bersih:
            return "LULUS", "Sistem Menetapkan: LULUS (Memenuhi seluruh standar kriteria nilai nasional)"
        else:
            return f"Naik Kelas {kelas_tujuan}", f"Sistem Menetapkan: NAIK KELAS ke {kelas_tujuan}"
    else:
        alasan = []
        if rata_rata < 60: alasan.append(f"Rata-rata ({rata_rata:.1f}) < 60")
        if mapel_dibawah_kkm > 2: alasan.append(f"Mapel di bawah KKM ({mapel_dibawah_kkm}) > 2")
        if alpa > 10: alasan.append(f"Alpa ({alpa} hari) > 10 hari")
        if not sikap_baik: alasan.append("Nilai Sikap perlu pembinaan")
        
        detail_alasan = ", ".join(alasan)
        return f"Tinggal di Kelas {kelas_sekarang}", f"Sistem Menetapkan: TINGGAL DI KELAS ({detail_alasan})"

def render(db):
    st.header("📝 Input & Edit Nilai Santri")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Sesuai SOP, Kepala Madrasah tidak mengisi nilai santri. Silakan pantau rekap data di menu **Pemantauan & Rekap**.")
        return

    st.caption("Sistem Penilaian Standar Nasional dengan Narasi Deskripsi & Kenaikan Kelas Otomatis")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif.")
        return
        
    if not db.data_master:
        st.warning("⚠️ Belum ada data santri di kelas ini. Silakan tambahkan santri terlebih dahulu di menu **Input Biodata**.")
        return

    st.markdown("---")
    map_santri = {s['nama']: s for s in db.data_master}
    
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1: 
        pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2: 
        semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
    
    st.markdown("---")
    
    if pilih_nama:
        santri_aktif = map_santri[pilih_nama]
        santri_id = santri_aktif["id"]
        
        data_lengkap = santri_aktif.get("data_lengkap", {})
        kelas_santri = str(data_lengkap.get("kelas_santri", data_lengkap.get("kelas", ""))).strip()
        
        if not kelas_santri and getattr(db, 'kelas_binaan', None):
            kelas_santri = db.kelas_binaan
            
        st.info(f"👤 **Santri:** {pilih_nama} | **Kelas:** {kelas_santri}")
        
        pengaturan = db.data_lembaga.get("pengaturan_master") or {}
        kelas_mapel = pengaturan.get("kelas_mapel", {})
        
        mapel_list = []
        kelas_santri_bersih = kelas_santri.upper().replace(" ", "")
        
        for kls, mapels in kelas_mapel.items():
            if str(kls).upper().replace(" ", "") == kelas_santri_bersih:
                mapel_list = mapels
                break
        
        if not mapel_list:
            st.error(f"❌ Mata pelajaran untuk kelas **{kelas_santri}** belum diatur oleh Kepala Madrasah di Master Data!")
            return

        nilai_lama = db.get_nilai(santri_id, semester)
        komp_lama = nilai_lama.get('komponen_nilai', {}) if nilai_lama else {}
        
        def_akademik = komp_lama.get('akademik', {})
        def_pribadi = komp_lama.get('kepribadian', {})
        def_absen = komp_lama.get('absen', {})
        catatan_lama = komp_lama.get('catatan', '')
        
        with st.form("form_nilai"):
            st.subheader("📊 Nilai Akademik & Deskripsi Narasi Otomatis")
            
            nilai_akademik_input = {}
            narasi_akademik = {}
            
            for mapel in mapel_list:
                c_m1, c_m2 = st.columns([1, 2])
                with c_m1:
                    val_lama = int(def_akademik.get(mapel, 75))
                    val_input = st.number_input(f"Nilai {mapel}", min_value=0, max_value=100, value=val_lama, step=1)
                    nilai_akademik_input[mapel] = val_input
                with c_m2:
                    pred, desk = hitung_predikat_dan_deskripsi(val_input, mapel)
                    narasi_akademik[mapel] = {"predikat": pred, "deskripsi": desk}
                    st.markdown(f"**Predikat [{pred}]**: *{desk}*")
                st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
            
            col_bawah1, col_bawah2 = st.columns(2)
            
            with col_bawah1:
                st.subheader("🌱 Kepribadian & Sikap")
                c_p1, c_p2, c_p3 = st.columns(3)
                opsi_pribadi = ["A", "B", "C", "D"]
                get_idx = lambda val: opsi_pribadi.index(val) if val in opsi_pribadi else 1
                
                with c_p1: kelakuan = st.selectbox("Kelakuan", opsi_pribadi, index=get_idx(def_pribadi.get("Kelakuan", "B")))
                with c_p2: kerajinan = st.selectbox("Kerajinan", opsi_pribadi, index=get_idx(def_pribadi.get("Kerajinan", "B")))
                with c_p3: kebersihan = st.selectbox("Kebersihan", opsi_pribadi, index=get_idx(def_pribadi.get("Kebersihan", "B")))
                
            with col_bawah2:
                st.subheader("📅 Ketidakhadiran (Hari)")
                c_a1, c_a2, c_a3 = st.columns(3)
                with c_a1: sakit = st.number_input("Sakit", min_value=0, value=int(def_absen.get("Sakit", 0)), step=1)
                with c_a2: izin = st.number_input("Izin", min_value=0, value=int(def_absen.get("Izin", 0)), step=1)
                with c_a3: alpa = st.number_input("Alpa", min_value=0, value=int(def_absen.get("Alpa", 0)), step=1)

            st.subheader("📜 Catatan Wali Kelas")
            catatan = st.text_area("Catatan Perkembangan Santri", value=catatan_lama)

            jumlah = sum(nilai_akademik_input.values())
            rata_rata = jumlah / len(nilai_akademik_input) if nilai_akademik_input else 0
            mapel_dibawah_kkm = sum(1 for v in nilai_akademik_input.values() if v < 60)
            sikap_baik = kelakuan in ["A", "B"] and kerajinan in ["A", "B"]
            
            status_otomatis, ket_otomatis = hitung_keputusan_otomatis(
                rata_rata, mapel_dibawah_kkm, alpa, sikap_baik, kelas_santri
            )
            
            st.markdown("---")
            st.subheader("🤖 Keputusan Kenaikan Kelas (Dihitung Sistem Otomatis)")
            if "NAIK" in status_otomatis or "LULUS" in status_otomatis:
                st.success(f"🏆 **{status_otomatis}** — {ket_otomatis}")
            else:
                st.error(f"⚠️ **{status_otomatis}** — {ket_otomatis}")

            if st.form_submit_button("💾 Simpan Penilaian & Keputusan Sistem"):
                wadah_komponen = {
                    "akademik": nilai_akademik_input,
                    "narasi_akademik": narasi_akademik,
                    "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                    "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                    "catatan": catatan, 
                    "status": status_otomatis
                }

                data_simpan = {
                    "santri_id": santri_id, 
                    "semester": semester, 
                    "jumlah": jumlah, 
                    "rata_rata": rata_rata,
                    "komponen_nilai": wadah_komponen
                }
                
                id_nilai = nilai_lama['id'] if nilai_lama else None
                sukses, pesan = db.simpan_nilai(data_simpan, id_nilai)
                
                if sukses: 
                    st.success(f"✅ {pesan}")
                    st.rerun()
                else: 
                    st.error(f"❌ {pesan}")