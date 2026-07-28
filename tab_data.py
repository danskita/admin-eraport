import streamlit as st
import pandas as pd
from datetime import datetime
from pdf_generator import PDFGenerator, NAMA_BULAN

def render(db):
    st.header("📊 Pemantauan & Rekap Data Madrasah")
    
    if not db.data_master:
        st.warning("Belum ada data santri yang terdaftar di sistem.")
        return

    is_kepala = getattr(db, 'role', '') == 'kepala_madrasah'
    gen = PDFGenerator(db)
    
    if is_kepala:
        st.success("👨‍💼 **Mode Kepala Madrasah:** Anda dapat memantau dan mencetak rekap data seluruh kelas.")
    else:
        st.info(f"👨‍🏫 **Mode Wali Kelas:** Menampilkan rekap data khusus untuk kelas {db.kelas_binaan}.")
        
    tab_santri, tab_nilai, tab_absen = st.tabs([
        "👥 Rekap Biodata Santri", 
        "📈 Rekap Nilai & Status Akhir", 
        "📅 Rekap Absensi Bulanan"
    ])
    
    # ========================================
    # TAB 1: REKAPITULASI DATA SANTRI
    # ========================================
    with tab_santri:
        st.subheader("Daftar Induk Santri")
        
        semua_kelas = list(set([s.get("data_lengkap", {}).get("kelas_santri", "Umum") for s in db.data_master]))
        pilih_kelas_rs = st.selectbox("Pilih Kelas untuk Cetak Rekap Biodata:", semua_kelas, key="sel_k_santri")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, _ = st.columns(2)
        
        with col_btn1:
            if st.button("🖨️ Cetak PDF Rekap Santri Lengkap (Landscape F4)", use_container_width=True):
                with st.spinner("Membuat dokumen PDF Landscape F4..."):
                    pdf_buf_l = gen.cetak_rekap_santri_lengkap(pilih_kelas_rs)
                    st.download_button(
                        label="⬇️ Download PDF Rekap Santri Lengkap",
                        data=pdf_buf_l,
                        file_name=f"Rekap_Lengkap_Santri_Kelas_{pilih_kelas_rs}_F4.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.toast("✅ Dokumen PDF Landscape F4 berhasil dibuat!", icon="📜")

        st.markdown("---")
        df_list = []
        for row in db.data_master:
            flat_row = {
                "NIS": row.get("no_induk", "-"), 
                "Nama Santri": row.get("nama", "-")
            }
            if row.get("data_lengkap"):
                dl = row["data_lengkap"]
                flat_row["NIK Santri"] = dl.get("nik_santri", "-")
                flat_row["Kelas"] = dl.get("kelas_santri", dl.get("kelas", "-"))
                flat_row["L/P"] = dl.get("jk", dl.get("jenis_kelamin", "-"))[:1]
                flat_row["TTL"] = f"{dl.get('tempat_lahir', '-')}, {dl.get('tanggal_lahir', '-')}"
                flat_row["Desa"] = dl.get("desa", "-")
                flat_row["Kecamatan"] = dl.get("kecamatan", "-")
                flat_row["Nama Ayah"] = dl.get("nama_ayah", "-")
                flat_row["Nama Ibu"] = dl.get("nama_ibu", "-")
                flat_row["No. WA"] = dl.get("no_hp", "-")
            df_list.append(flat_row)
            
        df_santri = pd.DataFrame(df_list)
        df_santri.index = df_santri.index + 1
        st.dataframe(df_santri, use_container_width=True)

    # ========================================
    # TAB 2: REKAPITULASI NILAI
    # ========================================
    with tab_nilai:
        st.subheader("Pantauan Nilai & Keputusan Akhir")
        
        c_sem, c_kls = st.columns(2)
        with c_sem:
            semester = st.radio("Pilih Semester Pantauan:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
        with c_kls:
            semua_kelas_n = list(set([s.get("data_lengkap", {}).get("kelas_santri", "Umum") for s in db.data_master]))
            pilih_kelas_rn = st.selectbox("Pilih Kelas untuk Cetak Rekap Nilai:", semua_kelas_n, key="sel_k_nilai")

        if st.button("🖨️ Cetak PDF Rekap Nilai Kelas (F4 Landscape)", use_container_width=True):
            with st.spinner("Membuat rekap nilai PDF..."):
                pdf_buf_n = gen.cetak_rekap_nilai(pilih_kelas_rn, semester)
                sem_str = "Ganjil" if semester == 1 else "Genap"
                st.download_button(
                    label="⬇️ Download PDF Rekap Nilai",
                    data=pdf_buf_n,
                    file_name=f"Rekap_Nilai_Semester_{sem_str}_Kelas_{pilih_kelas_rn}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.toast("✅ Dokumen PDF Rekap Nilai berhasil dibuat!", icon="📈")

        st.markdown("---")
        semua_nilai = db.get_semua_nilai(semester)
        
        if not semua_nilai:
            st.warning("Belum ada nilai yang diinput oleh wali kelas pada semester ini.")
        else:
            rekap_nilai = []
            map_santri = {s['id']: {"nama": s['nama'], "kelas": s.get("data_lengkap", {}).get("kelas_santri", "-")} for s in db.data_master}
            
            for n in semua_nilai:
                s_id = n['santri_id']
                if s_id in map_santri:
                    info = map_santri[s_id]
                    if not is_kepala and str(info["kelas"]).upper().replace(" ","") != str(db.kelas_binaan).upper().replace(" ",""):
                        continue
                        
                    komp = n.get('komponen_nilai', {})
                    rekap_nilai.append({
                        "Nama Santri": info["nama"],
                        "Kelas": info["kelas"],
                        "Rata-rata": round(n.get('rata_rata', 0), 2),
                        "Sakit": komp.get("absen", {}).get("Sakit", 0),
                        "Izin": komp.get("absen", {}).get("Izin", 0),
                        "Alpa": komp.get("absen", {}).get("Alpa", 0),
                        "Status Akhir": komp.get("status", "-")
                    })
                    
            if rekap_nilai:
                df_nilai = pd.DataFrame(rekap_nilai)
                df_nilai.index = df_nilai.index + 1
                st.dataframe(df_nilai, use_container_width=True)
            else:
                st.warning("Belum ada data nilai untuk kelas Anda di semester ini.")

    # ========================================
    # TAB 3: REKAPITULASI ABSENSI BULANAN
    # ========================================
    with tab_absen:
        st.subheader("📅 Rekap Kehadiran Santri Bulanan")
        
        c_k, c_b, c_t = st.columns([2, 2, 1])
        with c_k:
            semua_kelas_a = list(set([s.get("data_lengkap", {}).get("kelas_santri", "Umum") for s in db.data_master]))
            pilih_kelas_ra = st.selectbox("Pilih Kelas:", semua_kelas_a, key="sel_k_absen")
        with c_b:
            bln_sekarang = datetime.now().month
            pilih_bulan = st.selectbox(
                "Pilih Bulan:", 
                range(1, 13), 
                index=bln_sekarang-1, 
                format_func=lambda x: NAMA_BULAN[x],
                key="sel_b_absen"
            )
        with c_t:
            thn_sekarang = datetime.now().year
            pilih_tahun = st.number_input("Tahun:", min_value=2020, max_value=2035, value=thn_sekarang, step=1, key="sel_t_absen")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🖨️ Cetak PDF Rekap Absensi Bulanan (F4 Landscape)", use_container_width=True):
            with st.spinner("Membuat PDF rekap absensi bulanan..."):
                pdf_buf_a = gen.cetak_rekap_absen_bulanan(pilih_kelas_ra, pilih_bulan, pilih_tahun)
                nama_bln_str = NAMA_BULAN[pilih_bulan]
                st.download_button(
                    label=f"⬇️ Download PDF Rekap Absen {nama_bln_str} {pilih_tahun}",
                    data=pdf_buf_a,
                    file_name=f"Rekap_Absen_{nama_bln_str}_{pilih_tahun}_Kelas_{pilih_kelas_ra}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.toast(f"✅ Dokumen Rekap Absen Bulan {nama_bln_str} berhasil dibuat!", icon="📅")

        st.markdown("---")
        st.info(f"💡 Menampilkan ringkasan kehadiran kelas **{pilih_kelas_ra}** bulan **{NAMA_BULAN[pilih_bulan]} {pilih_tahun}**.")
        
        # Tampilkan preview tabel rekap di screen
        raw_absen = db.get_absensi_bulanan(pilih_bulan, pilih_tahun)
        santri_kelas_a = [s for s in db.data_master if pilih_kelas_ra == "Semua Kelas" or str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ","") == str(pilih_kelas_ra).upper().replace(" ","")]

        map_absen = {}
        for item in raw_absen:
            try:
                tgl_dt = datetime.strptime(item['tanggal'], "%Y-%m-%d")
                map_absen[(item['santri_id'], tgl_dt.day)] = item['status']
            except Exception:
                pass

        list_prev_absen = []
        for s in santri_kelas_a:
            s_id = s['id']
            cnt_h = sum(1 for d in range(1, 32) if map_absen.get((s_id, d)) == 'Hadir')
            cnt_s = sum(1 for d in range(1, 32) if map_absen.get((s_id, d)) == 'Sakit')
            cnt_i = sum(1 for d in range(1, 32) if map_absen.get((s_id, d)) == 'Izin')
            cnt_a = sum(1 for d in range(1, 32) if map_absen.get((s_id, d)) == 'Alpa')
            tot = cnt_h + cnt_s + cnt_i + cnt_a
            pct = f"{(cnt_h/tot*100):.0f}%" if tot > 0 else "0%"
            
            list_prev_absen.append({
                "NIS": s.get("no_induk", "-"),
                "Nama Santri": s.get("nama", "-"),
                "Hadir (H)": cnt_h,
                "Sakit (S)": cnt_s,
                "Izin (I)": cnt_i,
                "Alpa (A)": cnt_a,
                "% Kehadiran": pct
            })

        if list_prev_absen:
            df_absen_prev = pd.DataFrame(list_prev_absen)
            df_absen_prev.index = df_absen_prev.index + 1
            st.dataframe(df_absen_prev, use_container_width=True)
        else:
            st.warning("Belum ada santri terdaftar di kelas ini.")