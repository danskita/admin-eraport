import streamlit as st
import pandas as pd

def render(db):
    st.header("📊 Rekapitulasi Nilai & Ranking")
    
    semester = st.radio("Pilih Semester untuk Rekap:", [1, 2], horizontal=True)
    st.markdown("---")
    
    data_nilai = db.get_semua_nilai(semester)
    if not data_nilai:
        st.info(f"Belum ada data nilai untuk Semester {semester}.")
        return
        
    map_santri = {s['id']: s['nama'] for s in db.data_master}
    
    # Mengurutkan data berdasarkan Jumlah (untuk menghitung ranking)
    data_nilai = sorted(data_nilai, key=lambda x: x['jumlah'], reverse=True)
    
    tabel_rekap = []
    rank = 1
    for dn in data_nilai:
        nama = map_santri.get(dn['santri_id'], "Santri Terhapus")
        
        # Ekstrak Status (Naik / Tinggal / Lulus)
        status = dn.get("status", "-")
        naik, tinggal = "", ""
        if "LULUS" in status:
            naik = "LULUS"
        elif "Naik" in status:
            naik = status.replace("Naik Kelas", "").strip()
        elif "Tinggal" in status:
            tinggal = status.replace("Tinggal di Kelas", "").strip()
            
        tabel_rekap.append({
            "Nama Santri": nama,
            "JUMLAH": dn['jumlah'],
            "RATA-RATA": round(dn['rata_rata'], 2),
            "RANKING": rank,
            "NAIK KE KELAS": naik,
            "TINGGAL DI KELAS": tinggal
        })
        rank += 1
        
    df = pd.DataFrame(tabel_rekap)
    
    # Gunakan fitur styling Pandas untuk mempercantik dengan parameter BARU (width='stretch')
    st.dataframe(
        df.style.set_properties(**{'background-color': '#f0fdf4', 'color': 'black'}, subset=['JUMLAH', 'RATA-RATA'])
          .set_properties(**{'background-color': '#fef08a', 'color': 'black', 'font-weight': 'bold'}, subset=['RANKING'])
          .format({'RATA-RATA': '{:.2f}'}),
        width='stretch', hide_index=True
    )