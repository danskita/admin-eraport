import streamlit as st
import pandas as pd

def render(db):
    st.header("🗃️ Tabel Output Data Induk Santri")
    
    if not db.data_master:
        st.info("Belum ada data santri di database. Silakan isi lewat tab Input Biodata nanti.")
    else:
        # Merapikan struktur JSONB dari Supabase agar enak dibaca di tabel Pandas
        df_list = []
        for row in db.data_master:
            flat_row = {
                "ID": row.get("id"), 
                "No. Induk": row.get("no_induk", "-"), 
                "Nama": row.get("nama", "-")
            }
            # Gabungkan dengan data_lengkap (JSONB)
            if row.get("data_lengkap"):
                flat_row.update(row["data_lengkap"])
            df_list.append(flat_row)
            
        df = pd.DataFrame(df_list)
        
        # Tampilkan sebagai Dataframe Streamlit dengan parameter gaya BARU (width='stretch')
        st.dataframe(df, width='stretch')