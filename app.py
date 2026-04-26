import streamlit as st
import pandas as pd
import os
import urllib.parse
import altair as alt

from utils.model import load_model
from utils.pdf_extractor import extract_text_from_pdf
from utils.parser import parse_cv_structured
from utils.similarity import compute_similarity
from utils.feedback import generate_feedback

# ======================
# LOAD
# ======================
model = load_model()
df = pd.read_csv("data/job.csv")

def build_job_components(row):
    return {
        "edu": f"{row['degree']} {row['major']}",
        "exp": f"{row['pengalaman']} {row['peran/tanggung_jawab']}",
        "skill": f"{row['kemampuan']} {row['bahasa']} {row['peran/tanggung_jawab']}",
        "all": f"{row['degree']} {row['major']} {row['pengalaman']} {row['kemampuan']} {row['peran/tanggung_jawab']}"
    }

job_parts = df.apply(build_job_components, axis=1).tolist()

# ======================
# SAVE FUNCTION
# ======================
def save_data(file_path, new_row, key_cols):

    new_df = pd.DataFrame([new_row])

    if not os.path.exists(file_path):
        new_df.to_csv(file_path, index=False)
        return

    df_save = pd.read_csv(file_path)

    for col in new_df.columns:
        if col not in df_save.columns:
            df_save[col] = None

    for col in df_save.columns:
        if col not in new_df.columns:
            new_df[col] = None

    new_df = new_df[df_save.columns]

    for col in key_cols:
        df_save[col] = df_save[col].astype(str)
        new_df[col] = new_df[col].astype(str)

    mask = pd.Series([True] * len(df_save))
    for col in key_cols:
        mask &= (df_save[col] == new_df.iloc[0][col])

    if mask.any():
        df_save.loc[mask, :] = new_df.iloc[0].values
    else:
        df_save = pd.concat([df_save, new_df], ignore_index=True)

    df_save.to_csv(file_path, index=False)

def style_header(df):
    return df.style.set_table_styles([
        # Header: Hijau Kalla, Putih, Tengah
        {'selector': 'th', 'props': [
            ('background-color', '#0B5334'), 
            ('color', 'white'),
            ('font-family', 'sans-serif'),
            ('text-align', 'center !important'),
            ('vertical-align', 'middle !important'),
            ('padding', '15px')
        ]},
        # Data: Tengah, Padding rapi
        {'selector': 'td', 'props': [
            ('font-family', 'sans-serif'),
            ('padding', '10px'),
            ('text-align', 'center !important'),
            ('vertical-align', 'middle !important')
        ]}
    ]).set_properties(**{
        'background-color': 'white',
        'color': '#333',
        'border-color': '#f0f0f0',
        'text-align': 'center !important'
    })
# ======================
# CONFIG
# ======================
st.set_page_config(layout="wide", page_title="Dashboard Penilaian CV")

# ======================
# CSS DESIGN
# ======================
st.markdown("""
<style>
.stApp { background-color: #F8F9FA; }

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E0E0E0;
}

.main-title {
    color: #0B5334;
    font-weight: 700;
    font-size: 24px;
}

.custom-card {
    background-color: #FFFFFF;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #F0F0F0;
    
    /* KUNCI UTAMA: Berikan tinggi minimal yang cukup */
    min-height: 220px; 
    
    /* Pakai Flexbox agar konten bisa diatur jaraknya */
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.custom-card1 {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #F0F0F0;
    margin-bottom: 20px;
}

.custom-progress {
    height: 10px;
    background-color: #E9ECEF;
    border-radius: 5px;
}

.progress-fill {
    height: 100%;
    background-color: #28A745;
    border-radius: 5px;
}

.badge-match {
    background-color: #28A745;
    color: white;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 14px;
    font-weight: bold;
}

.card-best-match {
    background-color: #FFF9E6;
    border: 1px solid #FFE082;
    padding: 15px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    margin-top:15px;
}

/* --- STYLE NAVIGASI TAB (GAMBAR 2) --- */
.tab-container {
    display: flex;
    justify-content: center;
    width: 100%;
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 25px;
}

.tab-button {
    flex: 1;
    padding: 12px;
    text-align: center;
    text-decoration: none;
    color: #0B5334;
    font-weight: 600;
    transition: 0.3s;
    border-right: 1px solid #E0E0E0;
    background: none;
    border-top: none;
    border-bottom: none;
    border-left: none;
    cursor: pointer;
}

.tab-button:last-child {
    border-right: none;
}

.tab-active {
    background-color: #0B5334 !important;
    color: white !important;
}
/* Menghapus warna primary bawaan dan mengganti ke hijau muda custom */
button[kind="primary"] {
    background-color: #bceba2 !important;
    color: #0B5334 !important; /* Tulisan diganti hijau gelap agar kontras */
    border: none !important;
    font-size: 25px !important;   /* Ukuran font lebih besar */
    font-weight: 800 !important;
}

/* Efek saat kursor menempel (Hover) */
button[kind="primary"]:hover {
    background-color: #a8d691 !important;
    border: none !important;
    font-size: 25px !important;   /* Ukuran font lebih besar */
    font-weight: 800 !important;
}

/* Merapikan label Selectbox di Sidebar */
[data-testid="stSidebar"] label {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #444 !important;
    margin-bottom: 8px !important;
}

/* Memberikan efek fokus hijau pada input sidebar */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border: 1px solid #E0E0E0 !important;
}
/* Merapikan inputan di sidebar agar garisnya jelas */
[data-testid="stSidebar"] input[type="text"] {
    border: 2px solid #E0E0E0 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: #0B5334 !important;
}
[data-testid="stSidebar"] .stTextInput {
    margin-bottom: -20px !important;
}
.block-container {
            padding-top: 1.5rem !important;            
</style>
""", unsafe_allow_html=True)

# ======================
# MENU
# ======================
# menu = st.radio("", ["Single CV", "Leaderboard"], horizontal=True)
st.markdown("""
    <div style="
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0B5334;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div>
            <h1 style="
                margin: 0;
                color: #0B5334;
                font-size: 30px;
                font-weight: 800;
            ">
                Dashboard Penilaian CV
            </h1>
            <p style="
                margin: 6px 0 0 0;
                color: #555;
                font-size: 15px;
            ">
                Sistem ini membantu proses seleksi kandidat dengan membandingkan isi CV 
                terhadap kebutuhan posisi di <span style="color: #0B5334; font-weight: 600;">Kalla Aspal</span> secara lebih terstruktur. 
                Hasil analisis ditampilkan dalam bentuk skor, ranking, dan Rekomendasi Job/Posisi yang paling terbaik 
                berbasis <i>Sentence-BERT</i>
            </p>
        </div>
        
    </div>
""", unsafe_allow_html=True)

# --- LOGIKA NAVIGASI TAB ---
if 'menu' not in st.session_state:
    st.session_state.menu = "Single CV"

# Membuat Tab Layout
cols = st.columns([1, 1, 1])

with cols[0]:
    active_class = "tab-active" if st.session_state.menu == "Single CV" else ""
    if st.button("Single CV", use_container_width=True, type="primary" if st.session_state.menu == "Single CV" else "secondary"):
        st.session_state.menu = "Single CV"
        st.rerun()

with cols[1]:
    if st.button("Leaderboard", use_container_width=True, type="primary" if st.session_state.menu == "Leaderboard" else "secondary"):
        st.session_state.menu = "Leaderboard"
        st.rerun()

with cols[2]:
    if st.button("Bulk CV", use_container_width=True, type="primary" if st.session_state.menu == "Bulk CV" else "secondary"):
        st.session_state.menu = "Bulk CV"
        st.rerun()

# Simpan variabel menu agar kode di bawahnya tetap jalan
menu = st.session_state.menu

# =========================================================
# SINGLE CV
# =========================================================
if menu == "Single CV":
    with st.sidebar:
        st.markdown('<p class="main-title">📥 Input Data Kandidat</p>', unsafe_allow_html=True)
        
        # --- SEKSI INFORMASI DASAR ---
        st.markdown("""
            <div style='background-color: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #0B5334; margin-bottom: 5px;'>
                <p style='margin:0; font-size: 12px; color: gray; font-weight: bold;'>👤 INFORMASI DASAR</p>
            </div>
        """, unsafe_allow_html=True)
        
        nama = st.text_input("Nama Lengkap", placeholder="Ketik nama pelamar...", label_visibility="collapsed")
        hp = st.text_input("Nomor WhatsApp", placeholder="Contoh: 62812...", label_visibility="collapsed")
        
        # Jeda antar seksi
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

        # --- SEKSI TARGET POSISI ---
        st.markdown("""
            <div style='background-color: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #0B5334; margin-bottom: -20px;'>
                <p style='margin:0; font-size: 12px; color: gray; font-weight: bold;'>🎯 TARGET POSISI</p>
            </div>
        """, unsafe_allow_html=True)
        selected_job = st.selectbox("", df['job_title'], key="single_job_select")
        
        # --- UPLOAD & TOMBOL ---
        file = st.file_uploader("Upload CV (PDF)", type=["pdf"])
        process_btn = st.button("🚀 Proses Screening", use_container_width=True, type="primary")

    # --- LOGIKA VALIDASI ---
    if process_btn and not file:
        st.warning("⚠️ Silakan upload file CV terlebih dahulu.")
        st.stop()

    if file and process_btn:
        if not nama:
            st.error("⚠️ Mohon isi Nama Lengkap pelamar.")
            st.stop()

        with st.spinner("⏳ Menganalisis CV..."):
            # Proses Backend
            text = extract_text_from_pdf(file)
            cv_extracted = parse_cv_structured(text)
            df_sim = compute_similarity(cv_extracted, job_parts, model, df)
            df_rank = df_sim.sort_values(by="score", ascending=False)

            # Data untuk Job yang dipilih
            selected_row = df_rank[df_rank['job_title'] == selected_job].iloc[0]
            score = selected_row['score'] * 100
            exp_score = selected_row['exp'] * 100
            edu_score = selected_row['edu'] * 100
            skill_score = selected_row['skill'] * 100
            
            # Data untuk Best Match (Global)
            best_global = df_rank.iloc[0]
            best_job_name = best_global['job_title']
            best_job_score = best_global['score'] * 100

        # --- TAMPILAN DASHBOARD UTAMA ---
        st.markdown(f"<p class='main-title' style='font-size: 40px; margin-bottom: 0px;'>Dashboard Penilaian CV: {nama}</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="custom-card">
                <p style="color: gray; font-weight: bold; text-align:center; margin-bottom: 0px;">Skor Kecocokan</p>
                <h1 style="color: #0B5334; font-size: 58px; margin-top: -10px; margin-bottom: 10px; text-align:center;">{score:.1f}%</h1>
                <div class="custom-progress"><div class="progress-fill" style="width:{score}%;"></div></div>
                <div style="flex-grow: 1; display: flex; align-items: flex-end; margin-top: 20px;">
                    <p style="background: #F1F3F4; padding: 12px; border-radius: 8px; width: 100%; text-align: center; font-size: 18px; margin: 0; color: #333;">
                        <b>JOB:</b> {selected_job}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="custom-card">
                <p style="color: gray; font-weight: bold; margin-bottom:20px;">Detail Penilaian</p>
                <p style="margin-bottom:4px; font-size:16px; color: #444;">🎓 Pendidikan <span style="float:right; font-weight:bold;">{edu_score:.1f}%</span></p>
                <div class="custom-progress" style="margin-bottom:15px;"><div class="progress-fill" style="width:{edu_score}%;"></div></div>
                <p style="margin-bottom:4px; font-size:16px; color: #444;">💼 Pengalaman <span style="float:right; font-weight:bold;">{exp_score:.1f}%</span></p>
                <div class="custom-progress" style="margin-bottom:15px;"><div class="progress-fill" style="width:{exp_score}%;"></div></div>
                <p style="margin-bottom:4px; font-size:16px; color: #444;">⭐ Kemampuan <span style="float:right; font-weight:bold;">{skill_score:.1f}%</span></p>
                <div class="custom-progress"><div class="progress-fill" style="width:{skill_score}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="custom-card">
                <p style="color: gray; font-weight: bold; margin-bottom: 20px;">Informasi Pendidikan</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #f1f1f1; padding-bottom: 8px;">
                    <p style="font-size: 16px; color: gray; margin: 0;">🎓 Tingkat</p>
                    <p style="font-size: 19px; font-weight: bold; margin: 0; color: #333;">{str(cv_extracted['degree']).upper()}</p>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <p style="font-size: 16px; color: gray; margin: 0;">📖 Program Studi</p>
                    <p style="font-size: 19px; font-weight: bold; margin: 0; color: #333; text-align: right;">{str(cv_extracted['major']).title()}</p>
                </div>
                <div style="flex-grow: 1;"></div>
            </div>
            """, unsafe_allow_html=True)

        # --- SEKSI BEST MATCH & WHATSAPP ---
        colA, colB = st.columns([2, 1])
        with colA:
            st.markdown(f"""
            <div class="card-best-match">
                <div style="font-size: 30px; margin-right: 15px;">🏆</div>
                <div>
                    <span style="color: #28A745; font-weight: bold; font-size: 24px;">Best Job Match</span>
                    <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                        <span style="font-weight: bold; font-size: 28px; color: #333;">{best_job_name}</span>
                        <span class="badge-match">{best_job_score:.1f}% Match</span>
                    </div>
                    <p style="font-size: 13px; color: gray; margin-bottom: 15px;">Ini adalah Best Job Untuk CV.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with colB:
            if hp:
                nomor_wa = hp.replace("+","").replace(" ","")
                pesan_wa = urllib.parse.quote(f"Halo {nama}, skor CV Anda {score:.2f}% untuk posisi {selected_job}.")
                st.markdown(f"""
                <div style="background: white; border: 1px solid #F0F0F0; padding: 15px; margin-top:15px; border-radius: 12px;">
                    <p style="font-weight: bold; color: #333; margin-bottom: 5px; font-size:22px;">Rekomendasi</p>
                    <p style="font-size: 13px; color: gray; margin-bottom: 15px;">Kirim hasil rekomendasi ini ke WhatsApp untuk ditinjau lebih lanjut.</p>
                    <a href="https://wa.me/{nomor_wa}?text={pesan_wa}" target="_blank" style="text-decoration: none;">
                        <button style="width: 100%; background-color: #28A745; color: white; padding: 10px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">📲 Kirim WhatsApp</button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
        
        
        # --- TABEL TOP 5 ---
        st.markdown("### 📊 Top 5 Job")
        top5 = df_rank.head(5).copy().reset_index(drop=True)
        top5["Rank"] = top5.index + 1
        top5["Score"] = top5["score"].apply(lambda x: f"{x*100:.2f}%")
        top5["Skill"] = top5["skill"].apply(lambda x: f"{x*100:.2f}%")
        top5["Experience"] = top5["exp"].apply(lambda x: f"{x*100:.2f}%")
        top5["Education"] = top5["edu"].apply(lambda x: f"{x*100:.2f}%")
        
        df_to_show = top5[["Rank", "job_title", "Score", "Skill", "Experience", "Education"]]
        st.table(style_header(df_to_show))

        # --- SAVE DATA SEMUA JOB KE DATABASE ---
        # Kita melakukan perulangan untuk setiap baris di df_rank 
        # (df_rank berisi skor pelamar ini untuk SELURUH posisi job yang ada di database)
        
        # --- SAVE DATA TOP 5 JOB KE DATABASE ---
        # Kita ambil hanya 5 posisi dengan skor tertinggi untuk pelamar ini
        df_top5_save = df_rank.head(5)

        with st.spinner(f"💾 Menyimpan Top 5 rekomendasi untuk {nama}..."):
            for index, row_job in df_top5_save.iterrows():
                data_to_save = {
                    "nama": nama,
                    "hp": hp,
                    "job": row_job['job_title'],      # Nama posisi dari Top 5
                    "rekomendasi_ai": best_job_name,   # Tetap catat Rank #1 aslinya apa
                    "score": round(row_job['score'] * 100, 2),
                    "skill": round(row_job['skill'] * 100, 2),
                    "exp": round(row_job['exp'] * 100, 2),
                    "edu": round(row_job['edu'] * 100, 2)
                }
                
                # Simpan ke leaderboard.csv
                # Kunci unik ["nama", "job"] memastikan tidak ada duplikat untuk orang & posisi yang sama
                save_data("leaderboard.csv", data_to_save, ["nama", "job"])
        
        st.success(f"✅ Berhasil menyimpan Top 5 posisi terbaik untuk {nama}!")

    elif not file:
    # --- Tampilan Welcome / Tutorial ---
        st.markdown("### 🚀 Selamat Datang di Dashboard Penilaian CV")
        st.write("Aplikasi ini membantu Anda menyeleksi kandidat terbaik menggunakan AI dengan cepat dan akurat. Berikut adalah panduan fitur utamanya:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background-color: #f0f7f4; padding: 20px; border-radius: 10px; border-left: 5px solid #0B5334; height: 100%;">
                <h4 style="color: #0B5334; margin-top:0;">📄 Single CV</h4>
                <p style="font-size: 14px; color: #444;">
                    <b>Single CV</b> digunakan untuk menganalisis <b>satu kandidat secara lebih detail</b>. 
                    Fitur ini menampilkan skor kecocokan CV dengan posisi yang dilamar, 
                    serta memberikan rekomendasi job yang lain. Cocok digunakan ketika ingin mengevaluasi satu kandidat secara lebih fokus.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background-color: #fdfaf0; padding: 20px; border-radius: 10px; border-left: 5px solid #f39c12; height: 100%;">
                <h4 style="color: #f39c12; margin-top:0;">🏆 Leaderboard</h4>
                <p style="font-size: 14px; color: #444;">
                    <b>Leaderboard</b> merupakan halaman <b>peringkat kandidat berdasarkan skor</b>. 
                    Semua CV yang sudah dianalisis akan ditampilkan secara terurut dari yang tertinggi, 
                    serta memudahkan HR dalam membandingkan performa masing-masing kandidat. 
                    Cocok digunakan untuk membantu proses seleksi secara lebih cepat.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; border-left: 5px solid #2980b9; height: 100%;">
                <h4 style="color: #2980b9; margin-top:0;">📁 Bulk CV</h4>
                <p style="font-size: 14px; color: #444;">
                    <b>Bulk CV</b> digunakan untuk menangani <b>banyak file CV sekaligus</b>. 
                    Anda dapat mengunggah beberapa file dalam satu waktu tanpa harus satu per satu, 
                    lalu sistem akan memproses dan menampilkan skor CV secara otomatis, serta memberikan Rekomendasi job yang paling Terbaik.
                    Cocok digunakan saat menghadapi jumlah pelamar yang cukup banyak.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(" ", unsafe_allow_html=True)

            
    st.info("👈 **Mulai Sekarang:** Silakan pilih posisi pekerjaan dan upload file CV Anda melalui sidebar di sebelah kiri.")
# LEADERBOARD
# =========================================================
elif menu == "Leaderboard":
    # --- FUNGSI STYLE ---
    def style_leaderboard_custom(df):
        return df.style.set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#0B5334'), ('color', 'white'),
                ('text-align', 'center !important'), ('padding', '15px')
            ]},
            {'selector': 'td', 'props': [
                ('text-align', 'center !important'), ('padding', '12px')
            ]}
        ]).set_properties(**{'background-color': 'white', 'color': '#333', 'text-align': 'center !important'})

    # 1. --- SIDEBAR FILTER ---
    with st.sidebar:
        st.markdown('<p class="main-title">🔍 Filter Leaderboard</p>', unsafe_allow_html=True)
        
        if "lb_mode" not in st.session_state:
            st.session_state.lb_mode = "Single CV"

        st.markdown("<p style='font-size:13px; font-weight:bold; margin-bottom:5px; color:#444;'>Pilih Sumber Data:</p>", unsafe_allow_html=True)
        col_lb1, col_lb2 = st.columns(2)
        
        with col_lb1:
            if st.button("Single CV", use_container_width=True, type="primary" if st.session_state.lb_mode == "Single CV" else "secondary"):
                st.session_state.lb_mode = "Single CV"
                st.rerun()
                
        with col_lb2:
            if st.button("Bulk CV", use_container_width=True, type="primary" if st.session_state.lb_mode == "Bulk CV" else "secondary"):
                st.session_state.lb_mode = "Bulk CV"
                st.rerun()

        lb_mode = st.session_state.lb_mode
        file_path = "leaderboard.csv" if lb_mode == "Single CV" else "leaderboardbulk.csv"
        
        if not os.path.exists(file_path):
            st.error(f"📂 Belum ada data {lb_mode}.")
            st.stop()
        
        df_lb = pd.read_csv(file_path)
        job_col = "job" if "job" in df_lb.columns else "job_input" if "job_input" in df_lb.columns else None
        name_col = "nama" if "nama" in df_lb.columns else "cv"

        # st.markdown("<br>", unsafe_allow_html=True)

        if job_col:
            st.markdown("<div style='background-color:#f8f9fa; padding:10px; border-radius:10px; border-left:5px solid #0B5334; margin-bottom:-20px;'><p style='margin:0; font-size:11px; color:gray; font-weight:bold;'>🎯 FILTER POSISI</p></div>", unsafe_allow_html=True)
            job_list = ["All"] + sorted(df_lb[job_col].dropna().unique().tolist())
            selected_job = st.selectbox("", job_list, key="lb_job_filter")
        else:
            selected_job = "All"

        st.markdown("<div style='background-color:#f8f9fa; padding:10px; border-radius:10px; border-left:5px solid #0B5334; margin-bottom:-20px; margin-top:10px;'><p style='margin:0; font-size:11px; color:gray; font-weight:bold;'>🏆 TAMPILKAN PERINGKAT</p></div>", unsafe_allow_html=True)
        top_n = st.selectbox("", [1,3, 5, 10, 20], index=1, key="lb_top_n")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

        # --- KARTU INFORMASI (Hanya yang relevan untuk Leaderboard) ---
        total_kandidat_unik = df_lb[name_col].nunique() 

        st.markdown(f"""
        <div class="sidebar-stats-card">
            <div style="display: flex; align-items: center; justify-content: flex-start; gap: 8px; margin-bottom: 0px;">
                <span style="color: #0B5334; font-weight: bold; font-size: 18px; ">Total Kandidat</span>
            </div>
            <h2 style="color: #0B5334; margin: 0px; padding: 0px; font-size: 28px; line-height: 1.2;">
                {total_kandidat_unik} <small style="font-size: 14px; color: gray; font-weight: normal;">Orang</small>
            </h2>
            <p style="color: gray; font-size: 10px; margin: 0px; padding: 0px; margin-top: -2px;">
                Terdeteksi dari total {len(df_lb)} entri posisi
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. --- LOGIKA FILTERING ---
    df_filtered = df_lb.copy()
    if job_col and selected_job != "All":
        df_filtered = df_filtered[df_filtered[job_col] == selected_job]
    
    if "score" in df_filtered.columns:
        df_filtered["score"] = pd.to_numeric(df_filtered["score"].astype(str).str.replace('%', ''), errors='coerce')
        df_filtered = df_filtered.sort_values(by="score", ascending=False)

    df_filtered = df_filtered.head(top_n).reset_index(drop=True)
    df_filtered["rank"] = df_filtered.index + 1

    # 3. --- TAMPILAN UTAMA ---
    st.markdown(f'<p class="main-title">🏆 Leaderboard CV – {lb_mode}</p>', unsafe_allow_html=True)
    st.info(f"📍 Menampilkan Top {len(df_filtered)} kandidat untuk lowongan: **{selected_job}**")

    # (Lanjutkan bagian grafik dan tabel di bawahnya seperti biasa)

    if not df_filtered.empty:
        # --- GRAFIK ---
        st.subheader("📈 Grafik Skor (%)")
        df_chart = df_filtered.copy()
        
        # Pastikan skor dalam skala 0-100
        if df_chart["score"].max() <= 1.0:
            df_chart["score"] = df_chart["score"] * 100

        chart = alt.Chart(df_chart).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, color='#28A745').encode(
            x=alt.X(f"{name_col}:N", sort='-y', title="Nama CV"),
            y=alt.Y("score:Q", title="Skor (%)"),
            tooltip=[name_col, "score"]
        ).properties(height=400)

        text = chart.mark_text(baseline='bottom', dy=-5, fontWeight='bold').encode(text=alt.Text('score:Q', format='.2f'))
        st.altair_chart(chart + text, use_container_width=True)


        # --- TABEL ---
        st.subheader("📋 Detail Tabel Peringkat")
        df_table = df_filtered.copy()

        # Format tampilan persen
        cols_format = ["score", "skill", "exp", "edu"]
        for col in cols_format:
            if col in df_table.columns:
                df_table[col] = df_table[col].apply(lambda x: f"{float(x):.2f}%" if pd.notnull(x) else "-")

        # Rename kolom untuk tabel
        df_table = df_table.rename(columns={
            "rank": "Rank", name_col: "Nama CV", job_col: "Job Title",
            "score": "Score", "skill": "Skill", "exp": "Exp", "edu": "Edu"
        })

        available_cols = ["Rank", "Nama CV", "Job Title", "Score", "Skill", "Exp", "Edu"]
        cols_to_show = [c for c in available_cols if c in df_table.columns]
        
        st.table(style_leaderboard_custom(df_table[cols_to_show]))
    else:
        st.warning("Tidak ada data untuk ditampilkan.")

    
# =========================================================
# BULK CV (FINAL + RESET FILE UPLOAD)
elif menu == "Bulk CV":
    # --- SIDEBAR BULK INPUT ---
    # --- SIDEBAR BULK INPUT (VERSI TOMBOL BIASA) ---
    with st.sidebar:
        st.markdown('<p class="main-title">📥 Upload CV Kandidat</p>', unsafe_allow_html=True)
        
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        if "bulk_mode" not in st.session_state:
            st.session_state.bulk_mode = "Auto"

        # --- TOMBOL MODE (Auto / Manual) ---
        st.markdown("<p style='font-size:13px; font-weight:bold; margin-bottom:5px; color:#444;'>Mode Analisis:</p>", unsafe_allow_html=True)
        col_mode1, col_mode2 = st.columns(2)
        
        with col_mode1:
            # Jika mode adalah Auto, tombol jadi warna hijau (primary)
            if st.button("Auto", use_container_width=True, type="primary" if st.session_state.bulk_mode == "Auto" else "secondary"):
                st.session_state.bulk_mode = "Auto"
                st.rerun()
                
        with col_mode2:
            # Jika mode adalah Manual, tombol jadi warna hijau (primary)
            if st.button("Manual", use_container_width=True, type="primary" if st.session_state.bulk_mode == "Manual" else "secondary"):
                st.session_state.bulk_mode = "Manual"
                st.rerun()

        # Ambil nilai mode dari session state
        mode = st.session_state.bulk_mode

        # Pilihan Job hanya muncul jika mode Manual
        # Pilihan Job hanya muncul jika mode Manual
        selected_job = None
        if mode == "Manual":
            # st.markdown("<br>", unsafe_allow_html=True) # Spasi tipis
            
            # Container visual untuk Dropdown
            st.markdown("""
                <div style='background-color: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #0B5334; margin-bottom: -20px;'>
                    <p style='margin:0; font-size: 12px; color: gray; font-weight: bold;'>🎯 TARGET POSISI</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Selectbox asli Streamlit
            selected_job = st.selectbox("", df['job_title'], key="job_manual")
            
        # File Uploader
        files = st.file_uploader(
            "Upload banyak file CV (PDF)",
            type="pdf",
            accept_multiple_files=True,
            key=st.session_state.uploader_key
        )

        # Tombol Proses
        process_btn = st.button("🚀 Proses Screening", use_container_width=True, type="primary")
        
        # Tombol Reset
        if st.button("🔄 Reset & Hapus File", use_container_width=True):
            st.session_state.uploader_key += 1
            st.session_state.bulk_mode = "Auto" # Kembalikan ke default jika mau
            st.rerun()

        # --- KARTU RINGKASAN ---
        if files:
            st.markdown(f"""
            <div class="sidebar-stats-card">
                <p style="color: #0B5334; font-weight: bold; margin-bottom: 5px;">Total CV diupload</p>
                <h2 style="color: #0B5334; margin-top: -20px;">{len(files)} <small style="font-size: 14px; color: gray;">File</small></h2>
            </div>
            """, unsafe_allow_html=True)

    # --- LOGIC PROSES ---
    # --- LOGIC PROSES ---
    if files and process_btn:
        results = []
        with st.spinner("⏳ Menganalisis semua CV..."):
            for f in files:
                text = extract_text_from_pdf(f)
                cv = parse_cv_structured(text)
                df_sim = compute_similarity(cv, job_parts, model, df)
                
                # Cari Rekomendasi Terbaik AI (Peringkat 1 Global) untuk tampilan di UI
                best_ai_row = df_sim.sort_values(by="score", ascending=False).iloc[0]
                
                if mode == "Auto":
                    # Di mode Auto, yang diproses dan disimpan adalah hasil deteksi AI terbaik
                    job_to_save = best_ai_row['job_title']
                    score_val = best_ai_row['score']
                    skill_val = best_ai_row['skill']
                    exp_val = best_ai_row['exp']
                    edu_val = best_ai_row['edu']
                else:
                    # Di mode Manual, yang diproses dan disimpan HANYA job yang dipilih user
                    row_target = df_sim[df_sim['job_title'] == selected_job].iloc[0]
                    job_to_save = selected_job
                    score_val = row_target['score']
                    skill_val = row_target['skill']
                    exp_val = row_target['exp']
                    edu_val = row_target['edu']

                # Data untuk kebutuhan visualisasi UI (tetap ada best_ai agar UI tidak error)
                res_ui = {
                    "cv": f.name, 
                    "job_target": job_to_save, 
                    "best_ai": best_ai_row['job_title'], 
                    "score": round(score_val * 100, 2),
                    "skill": round(skill_val * 100, 2), 
                    "exp": round(exp_val * 100, 2), 
                    "edu": round(edu_val * 100, 2)
                }
                results.append(res_ui)

                # --- SIMPAN KE DATABASE (leaderboardbulk.csv) ---
                # Hanya simpan data job_target (tanpa kolom best_ai) agar seragam dengan auto
                data_db = {
                    "cv": f.name,
                    "job": job_to_save, # Kolom ini disamakan namanya dengan database
                    "score": round(score_val * 100, 2),
                    "skill": round(skill_val * 100, 2),
                    "exp": round(exp_val * 100, 2),
                    "edu": round(edu_val * 100, 2)
                }
                
                # save_data akan mengecek duplikat berdasarkan Nama File (cv) dan Posisi (job)
                save_data("leaderboardbulk.csv", data_db, ["cv", "job"])
        
        df_res = pd.DataFrame(results).sort_values(by="score", ascending=False).reset_index(drop=True)
        df_res["rank"] = df_res.index + 1

        # --- HEADER & STATS CARDS ---
        st.markdown(f'<p class="main-title">📊 Hasil Bulk CV Screening ({mode} Mode)</p>', unsafe_allow_html=True)
        
        top_val = df_res.iloc[0]
        total_cv = len(df_res)

        # Logika pembagian kolom (5 untuk Manual, 4 untuk Auto)
        if mode == "Manual":
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        else:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #FFD700;">
                <p style="color: gray; font-weight: bold; margin-bottom:5px;">🏆 CV TERBAIK</p>
                <h4 style="margin:0; color:#333;">{top_val['cv'][:15]}</h4>
                <p style="color: gray; font-size: 11px; ">Kandidat skor tertinggi</p>
            </div>""", unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #0B5334;">
                <p style="color: gray; font-weight: bold; margin-bottom:5px;">🥇 SKOR TERTINGGI</p>
                <h1 style="color: #0B5334; margin:0px 0; font-size:35px;">{top_val['score']:.1f}%</h1>
                <span style="background: #FFF9E6; border-radius: 20px; font-size: 12px; border: 1px solid #FFE082; font-weight:bold; color:#856404; padding: 2px 10px;">RANK #1</span>
            </div>""", unsafe_allow_html=True)

        with col_m3:
            st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #333;">
                <p style="color: gray; font-weight: bold; margin-bottom:5px;">📄 TOTAL CV</p>
                <h1 style="color: #333; margin:0px 0; font-size:35px;">{total_cv}</h1>
                <p style="color: gray; font-size: 12px; margin:0;">File PDF diupload</p>
            </div>""", unsafe_allow_html=True)

        if mode == "Manual":
            with col_m4:
                st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #28A745;">
                    <p style="color: gray; font-weight: bold; margin-bottom:5px;">🎯 JOB TARGET</p>
                    <h4 style="margin:0; color:#333;">{top_val['job_target']}</h4>
                    <p style="color: gray; font-size: 11px; margin-top:10px;">Pilihan Anda</p>
                </div>""", unsafe_allow_html=True)
            with col_m5:
                st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #1E90FF;">
                    <p style="color: gray; font-weight: bold; margin-bottom:5px;">💡 REKOMENDASI</p>
                    <h4 style="margin:0; color:#1E90FF;">{top_val['best_ai']}</h4>
                    <p style="color: gray; font-size: 11px; margin-top:10px;">Paling Direkomendasikan</p>
                </div>""", unsafe_allow_html=True)
        else:
            with col_m4:
                st.markdown(f"""<div class="custom-card" style="text-align: center; border-top: 5px solid #28A745;">
                    <p style="color: gray; font-weight: bold; margin-bottom:5px;">💼 JOB TERBAIK</p>
                    <h4 style="margin:0; color:#333;">{top_val['job_target']}</h4>
                    <p style="color: gray; font-size: 11px; margin-top:10px;">Hasil Deteksi AI</p>
                </div>""", unsafe_allow_html=True)


        # --- GRAFIK DISTRIBUSI ---
        st.subheader("📈 Distribusi Skor Seluruh Kandidat")
        chart = alt.Chart(df_res).mark_bar(color='#28A745', cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X("cv:N", sort="-y", title="Nama File CV"),
            y=alt.Y("score:Q", title="Skor (%)"),
            tooltip=["cv", "job_target", "score"]
        ).properties(height=600)
        
        text = chart.mark_text(baseline='bottom', dy=-5, fontWeight='bold').encode(text='score:Q')
        st.altair_chart(chart + text, use_container_width=True)

        # --- TABEL HASIL GAYA HIJAU KALLA ---
        st.subheader("📋 Tabel Penilaian Keseluruhan")
        
        df_table = df_res.copy()
        for col in ["score", "skill", "exp", "edu"]:
            df_table[col] = df_table[col].apply(lambda x: f"{x:.2f}%")

        def style_bulk(df):
            return df.style.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0B5334'), ('color', 'white'), ('text-align', 'center !important'), ('padding', '15px')]},
                {'selector': 'td', 'props': [('text-align', 'center !important'), ('padding', '12px')]}
            ]).set_properties(**{'background-color': 'white', 'color': '#333', 'border-color': '#f0f0f0', 'text-align': 'center !important'})

        # Menentukan kolom tabel berdasarkan mode
        if mode == "Manual":
            final_cols = ["rank", "cv", "job_target", "best_ai", "score", "skill", "exp", "edu"]
            col_names = {"rank": "Rank", "cv": "Nama CV", "job_target": "Job Target", "best_ai": "Saran AI", "score": "Skor", "skill": "Kemampuan", "exp": "Pengalaman", "edu": "Pendidikan"}
        else:
            final_cols = ["rank", "cv", "job_target", "score", "skill", "exp", "edu"]
            col_names = {"rank": "Rank", "cv": "Nama CV", "job_target": "Best Job", "score": "Skor", "skill": "Kemampuan", "exp": "Pengalaman", "edu": "Pendidikan"}

        st.table(style_bulk(df_table[final_cols].rename(columns=col_names)))

        # --- RANGKUMAN DETEKSI JOB ---
        if mode == "Auto":
            st.markdown("---")
            st.subheader("📊 Sebaran Deteksi Posisi")
            job_counts = df_res['job_target'].value_counts()
            cols_job = st.columns(4)
            for idx, (j_name, count) in enumerate(job_counts.items()):
                with cols_job[idx % 4]:
                    st.markdown(f"""<div style="background:white; padding:15px; border-radius:10px; border:1px solid #eee; margin-bottom:10px; text-align:center;">
                        <p style="margin:0; font-size:12px; color:gray; font-weight:bold;">{j_name.upper()}</p>
                        <h3 style="margin:5px 0; color:#0B5334;">{count} <span style="font-size:12px; font-weight:normal;">CV</span></h3>
                    </div>""", unsafe_allow_html=True)

        st.success(f"✅ Berhasil memproses {len(df_res)} CV!")

    elif not files:
        st.info("👋 Silakan upload beberapa file CV di sidebar untuk memulai analisis Bulk.")