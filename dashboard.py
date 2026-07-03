import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.dpi'] = 80   # DPI rendah = grafik tidak raksasa
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import os
import sqlite3
from datetime import datetime
import io
import hashlib
import base64 as _b64

try:
    from fpdf import FPDF
    pdf_tersedia = True
except ImportError:
    pdf_tersedia = False

conn = sqlite3.connect('database_kipk.db', check_same_thread=False)

st.set_page_config(
    page_title="KIP Kuliah UCA",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── SEMBUNYIKAN SIDEBAR SEPENUHNYA ──────────────────────────────────────────
st.markdown("""
<style>
/* Sembunyikan tombol hamburger dan sidebar sama sekali */
[data-testid="stSidebar"]          { display: none !important; }
[data-testid="collapsedControl"]   { display: none !important; }
#MainMenu                          { display: none !important; }
header                             { display: none !important; }
footer                             { display: none !important; }

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}
.block-container {
    padding: 0.75rem 0.75rem 3rem 0.75rem !important;
    max-width: 480px !important;   /* lebar maksimum seperti layar HP */
    margin: 0 auto !important;
}

/* ── FIX: Paksa background tetap putih walau HP pakai dark mode ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main,
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════════
   FIX 1 (DIPERBAIKI) — Paksa kolom tetap horizontal TANPA bikin
   overflow ke samping. Kuncinya: JANGAN pakai width:fit-content,
   itu yang kemarin bikin overflow.
   ══════════════════════════════════════════════════════════════ */
html, body {
    overflow-x: hidden !important;
}
[data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    width: 100% !important;
    gap: 0.5rem !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
}

/* ══════════════════════════════════════════════════════════════
   FIX 2 — Paksa background tetap putih/terang meskipun HP
   memakai dark mode. (Pelengkap dari .streamlit/config.toml)
   ══════════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
}
[data-testid="stAppViewContainer"], .main {
    background-color: #FFFFFF !important;
}

/* ── HEADER ── */
.mobile-header {
    background: linear-gradient(135deg,#1E40AF,#3B82F6);
    border-radius: 16px;
    padding: 18px 14px 14px 14px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(59,130,246,.3);
}
.mobile-header h1 { color:#fff; font-size:1.15rem; font-weight:800; margin:0 0 3px 0; line-height:1.3; }
.mobile-header p  { color:#BFDBFE; font-size:0.78rem; margin:0; }

/* ── NAVIGASI 4 TOMBOL ── */
.nav-wrap {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 5px;
    background: #1E3A8A;
    border-radius: 14px;
    padding: 6px;
    margin-bottom: 14px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 4px 12px rgba(0,0,0,.2);
}

/* ── TOMBOL STREAMLIT — ukuran sentuh nyaman ── */
.stButton > button {
    width: 100% !important;
    min-height: 48px !important;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    transition: all .15s ease !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg,#2563EB,#3B82F6) !important;
    color: #fff !important;
    box-shadow: 0 3px 10px rgba(37,99,235,.35) !important;
}
button[kind="secondary"] {
    background: rgba(255,255,255,.08) !important;
    color: #BFDBFE !important;
    border: 1.5px solid rgba(255,255,255,.15) !important;
}
button[kind="secondary"]:hover { background: rgba(255,255,255,.18) !important; color:#fff !important; }

/* Tombol di luar nav (konten biasa) */
.stDownloadButton > button, .main-btn {
    background: #2563EB !important;
    color: #fff !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    width: 100% !important;
}

/* ── AI BADGE ── */
.ai-badge {
    background: #ECFDF5; border: 1.5px solid #22C55E;
    border-radius: 12px; padding: 10px 14px;
    display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
}
.ai-badge .dot {
    width:9px;height:9px;background:#22C55E;border-radius:50%;flex-shrink:0;
    animation: pulse 1.5s infinite;
}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.4)}}
.ai-badge .text { color:#14532D; font-size:.82rem; }
.ai-badge .text b { font-size:.95rem; }

/* ── METRIC CARDS ── */
.metric-row { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; margin:10px 0; }
.metric-card { border-radius:12px; padding:12px 6px; text-align:center; }
.metric-card.blue  { background:#EFF6FF; border:1.5px solid #93C5FD; }
.metric-card.green { background:#ECFDF5; border:1.5px solid #6EE7B7; }
.metric-card.red   { background:#FEF2F2; border:1.5px solid #FCA5A5; }
.metric-card .num  { font-size:1.5rem; font-weight:800; }
.metric-card.blue  .num { color:#1D4ED8; }
.metric-card.green .num { color:#059669; }
.metric-card.red   .num { color:#DC2626; }
.metric-card .lbl  { font-size:.6rem; color:#64748B; font-weight:600; margin-top:2px; }

/* ── INPUT ── */
input, textarea, select { font-size:16px !important; border-radius:10px !important; min-height:46px !important; }

/* ── LABEL TABEL ── */
.label-layak {
    background:#DCFCE7; border-left:4px solid #22C55E;
    padding:9px 12px; border-radius:0 10px 10px 0;
    font-weight:700; color:#14532D; margin-bottom:6px; font-size:.82rem;
}
.label-tidak {
    background:#FEE2E2; border-left:4px solid #EF4444;
    padding:9px 12px; border-radius:0 10px 10px 0;
    font-weight:700; color:#7F1D1D; margin-bottom:6px; font-size:.82rem;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size:.95rem; font-weight:700; color:#1E293B;
    margin:16px 0 8px 0; display:flex; align-items:center; gap:7px;
}
.section-title::after {
    content:''; flex:1; height:2px;
    background:linear-gradient(90deg,#3B82F6,transparent); border-radius:2px;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    border:2px dashed #93C5FD !important; border-radius:14px !important;
    padding:16px !important; background:#F0F9FF !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] summary { padding:12px !important; font-size:.9rem !important; font-weight:600 !important; }

/* ── GRAFIK — paksa ukuran kecil ── */
.stPlotlyChart, .stPyplot { max-height: 220px !important; overflow: hidden; }

/* ── LOGIN ── */
.login-card {
    background:#fff; border-radius:20px; padding:28px 20px;
    box-shadow:0 10px 40px rgba(0,0,0,.12); max-width:360px; margin:50px auto 0 auto;
}
.login-logo { text-align:center; font-size:2.8rem; margin-bottom:6px; }
.login-title{ text-align:center; font-size:1.15rem; font-weight:800; color:#1E293B; margin-bottom:3px; }
.login-sub  { text-align:center; font-size:.75rem; color:#64748B; margin-bottom:20px; }

/* ── SEMBUNYIKAN OVERFLOW SCROLLBAR DI GRAFIK ── */
iframe { max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SISTEM LOGIN
# ══════════════════════════════════════════
LOGO_UCA_B64 = "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"

def init_login_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tb_admin(
        id_admin INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute("SELECT COUNT(*) FROM tb_admin")
    if c.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO tb_admin(username,password) VALUES(?,?)", ("admin", pw))
        conn.commit()

def cek_login(user, pw):
    c = conn.cursor()
    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    c.execute("SELECT * FROM tb_admin WHERE username=? AND password=?", (user, pw_hash))
    return c.fetchone() is not None

init_login_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown(f"""
    <div class="login-card">
        <div class="login-logo">
            <img src="data:image/png;base64,{LOGO_UCA_B64}" 
                 style="width:110px;height:110px;object-fit:contain;border-radius:50%;
                        background:#fff;padding:6px;
                        box-shadow:0 4px 14px rgba(0,0,0,.15);" />
        </div>
        <div class="login-title">KIP Kuliah UCA</div>
        <div class="login-sub">Universitas Cendekia Abditama<br>Sistem Klasifikasi Beasiswa</div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("form_login"):
        username = st.text_input("👤  Username", placeholder="Masukkan username")
        password = st.text_input("🔒  Password", type="password", placeholder="Masukkan password")
        if st.form_submit_button("🚀  Masuk ke Sistem", type="primary", use_container_width=True):
            if cek_login(username, password):
                st.session_state['logged_in'] = True; st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
    st.stop()

# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
for k,v in [('model_rf',None),('le_rumah',None),('akurasi',None),('df_train',None),
            ('df_baru',None),('df_hasil',None),('nama_file_baru',""),
            ('y_test',None),('y_pred',None),('kelas_ai',None),('menu_aktif',"EDA")]:
    if k not in st.session_state: st.session_state[k] = v

# ══════════════════════════════════════════
# AUTO-TRAIN
# ══════════════════════════════════════════
NAMA_FILE_LATIH = "data_latih.csv"
if st.session_state.df_train is None and os.path.exists(NAMA_FILE_LATIH):
    df_tr = pd.read_csv(NAMA_FILE_LATIH)
    st.session_state.df_train = df_tr
    try:
        dp = df_tr.copy()
        le = LabelEncoder()
        dp['Status_Rumah'] = le.fit_transform(dp['Status_Rumah'])
        st.session_state.le_rumah = le
        F = ['Penghasilan_Ortu','Tanggungan','Daya_Listrik','Status_Rumah','Nilai_Rapor']
        X, y = dp[F], dp['Status_Kelayakan']
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.2,random_state=42)
        mdl = RandomForestClassifier(n_estimators=100,random_state=42)
        mdl.fit(Xtr,ytr); yp = mdl.predict(Xte)
        st.session_state.update({'akurasi':accuracy_score(yte,yp),'model_rf':mdl,
                                  'y_test':yte,'y_pred':yp,'kelas_ai':mdl.classes_})
    except Exception as e:
        st.error(f"Gagal melatih model: {e}")

# ══════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════
st.markdown("""
<div class="mobile-header">
    <h1>🎓 KIP Kuliah — Sistem Klasifikasi</h1>
    <p>Universitas Cendekia Abditama</p>
</div>
""", unsafe_allow_html=True)

menu = st.session_state.menu_aktif

# ══════════════════════════════════════════
# BOTTOM NAVIGATION BAR
# Pakai st.columns biasa + CSS fixed positioning
# ══════════════════════════════════════════
MENUS = [("EDA","📊","Analisis"),("Seleksi","🎯","Seleksi"),
         ("Info","ℹ️","Info"),("Database","🗄️","Riwayat")]

# ══════════════════════════════════════════
# BOTTOM NAVIGATION BAR
# ══════════════════════════════════════════

st.markdown("""
<style>
/* ── Ruang bawah agar tidak tertutup nav ── */
.block-container { padding-bottom: 100px !important; }

/* ── WRAPPER: 4 kolom pertama = bottom nav ── */
section.main > div > div:nth-of-type(1) > div[data-testid="stHorizontalBlock"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 100% !important;
    max-width: 480px !important;
    z-index: 9999 !important;
    background: #1E3A8A !important;
    padding: 6px 6px 16px 6px !important;
    border-radius: 20px 20px 0 0 !important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.3) !important;
}

/* ── Semua tombol di nav ── */
section.main > div > div:nth-of-type(1) > div[data-testid="stHorizontalBlock"] button {
    background: transparent !important;
    border: none !important;
    color: #93C5FD !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    min-height: 58px !important;
    border-radius: 12px !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    line-height: 1.3 !important;
    padding: 4px 2px !important;
}

/* ── Tombol aktif ── */
section.main > div > div:nth-of-type(1) > div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-primary"] {
    background: rgba(59,130,246,0.35) !important;
    color: #FFFFFF !important;
}

/* ── Teks di dalam tombol (p tag) ── */
section.main > div > div:nth-of-type(1) > div[data-testid="stHorizontalBlock"] button p {
    font-size: 0.68rem !important;
    line-height: 1.3 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    text-align: center !important;
    margin: 0 !important;
}

/* ── Tombol Keluar merah ── */
.logout-btn button {
    background: linear-gradient(135deg,#DC2626,#EF4444) !important;
    color: white !important;
    border-radius: 14px !important;
    min-height: 52px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(220,38,38,0.35) !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# ── Render 4 tombol nav — ikon + label langsung di teks tombol ──
nav_cols = st.columns(4)
NAV_LABELS = {
    "EDA":      "📊\nAnalisis",
    "Seleksi":  "🎯\nSeleksi",
    "Info":     "ℹ️\nInfo",
    "Database": "🗄️\nRiwayat",
}
for i, (key, icon, label) in enumerate(MENUS):
    with nav_cols[i]:
        aktif = (menu == key)
        tipe  = "primary" if aktif else "secondary"
        if st.button(NAV_LABELS[key], key=f"nav_{key}",
                     use_container_width=True, type=tipe):
            st.session_state.menu_aktif = key
            st.rerun()

# ══════════════════════════════════════════
# HELPER — buat grafik kecil & rapi
# ══════════════════════════════════════════
def kecil_fig(w=3.2, h=2.2):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=7)
    return fig, ax

# ══════════════════════════════════════════
# MENU 1 — EDA
# ══════════════════════════════════════════
if menu == "EDA":
    st.markdown('<div class="section-title">📊 Analisis Data Acuan</div>', unsafe_allow_html=True)

    if st.session_state.akurasi is not None:
        pct = st.session_state.akurasi * 100
        st.markdown(f'<div class="ai-badge"><div class="dot"></div>'
                    f'<div class="text">AI Aktif &nbsp;·&nbsp; <b>Akurasi {pct:.2f}%</b></div></div>',
                    unsafe_allow_html=True)

    if st.session_state.df_train is not None:
        df_tr = st.session_state.df_train
        warna = {'Layak':'#3B82F6','Tidak Layak':'#EF4444'}

        with st.expander("🔬 Laporan Detail AI", expanded=False):
            if st.session_state.y_test is not None:
                cm  = confusion_matrix(st.session_state.y_test,st.session_state.y_pred,labels=st.session_state.kelas_ai)
                fig,ax = kecil_fig(3.5,2.5)
                sns.heatmap(cm,annot=True,fmt='d',cmap='Blues',
                            xticklabels=st.session_state.kelas_ai,
                            yticklabels=st.session_state.kelas_ai,ax=ax,annot_kws={"size":8})
                ax.set_ylabel('Aktual',fontsize=7); ax.set_xlabel('Prediksi',fontsize=7)
                st.pyplot(fig, use_container_width=True); plt.close(fig)

                rep = classification_report(st.session_state.y_test,st.session_state.y_pred,output_dict=True)
                st.dataframe(pd.DataFrame(rep).transpose().round(2),use_container_width=True)

        # 2 grafik → 1 kolom per grafik (kecil)
        c1,c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.caption("📈 Nilai Rapor")
                fig,ax = kecil_fig()
                sns.histplot(data=df_tr,x='Nilai_Rapor',kde=True,color='#93C5FD',ax=ax,linewidth=.5)
                ax.set_xlabel(''); ax.set_ylabel('')
                st.pyplot(fig,use_container_width=True); plt.close(fig)
        with c2:
            with st.container(border=True):
                st.caption("📈 Penghasilan")
                fig,ax = kecil_fig()
                sns.histplot(data=df_tr,x='Penghasilan_Ortu',kde=True,color='#86EFAC',ax=ax,linewidth=.5)
                ax.set_xlabel(''); ax.set_ylabel('')
                st.pyplot(fig,use_container_width=True); plt.close(fig)

        with st.container(border=True):
            st.caption("🟦 Jumlah per Kategori")
            fig,ax = kecil_fig(3.5,2.2)
            sns.countplot(data=df_tr,x='Status_Kelayakan',palette=warna,ax=ax)
            ax.set_xlabel(''); ax.set_ylabel('Jumlah',fontsize=7)
            st.pyplot(fig,use_container_width=True); plt.close(fig)

        c3,c4 = st.columns(2)
        with c3:
            with st.container(border=True):
                st.caption("Penghasilan vs Status")
                fig,ax = kecil_fig()
                sns.boxplot(data=df_tr,x='Status_Kelayakan',y='Penghasilan_Ortu',palette=warna,ax=ax)
                ax.set_xlabel(''); ax.set_ylabel(''); ax.tick_params(axis='x',labelsize=6)
                st.pyplot(fig,use_container_width=True); plt.close(fig)
        with c4:
            with st.container(border=True):
                st.caption("Nilai Rapor vs Status")
                fig,ax = kecil_fig()
                sns.boxplot(data=df_tr,x='Status_Kelayakan',y='Nilai_Rapor',palette=warna,ax=ax)
                ax.set_xlabel(''); ax.set_ylabel(''); ax.tick_params(axis='x',labelsize=6)
                st.pyplot(fig,use_container_width=True); plt.close(fig)
    else:
        st.warning(f"⚠️ File '{NAMA_FILE_LATIH}' tidak ditemukan.")

# ══════════════════════════════════════════
# MENU 2 — SELEKSI
# ══════════════════════════════════════════
elif menu == "Seleksi":
    st.markdown('<div class="section-title">🎯 Proses Seleksi Otomatis</div>', unsafe_allow_html=True)

    if st.session_state.model_rf is None:
        st.error(f"⚠️ Model belum siap. Pastikan '{NAMA_FILE_LATIH}' tersedia.")
    else:
        with st.container(border=True):
            st.markdown("**📂 Unggah Data Pendaftar (CSV)**")
            st.caption("File CSV tanpa kolom Kelayakan")
            file_baru = st.file_uploader("Pilih file", type=["csv"], label_visibility="collapsed")
            if file_baru and st.session_state.nama_file_baru != file_baru.name:
                st.session_state.df_baru = pd.read_csv(file_baru)
                st.session_state.df_hasil = None
                st.session_state.nama_file_baru = file_baru.name

        if st.session_state.df_baru is not None:
            df_baru = st.session_state.df_baru
            with st.expander(f"👀 Preview ({len(df_baru)} baris)", expanded=False):
                st.dataframe(df_baru.head(8), use_container_width=True)

            if st.session_state.df_hasil is None:
                st.markdown("")
                if st.button("✨  Jalankan Seleksi Otomatis", type="primary", use_container_width=True):
                    with st.spinner("AI sedang menganalisis..."):
                        dp = df_baru.copy()
                        try:
                            dp['Status_Rumah'] = st.session_state.le_rumah.transform(dp['Status_Rumah'])
                        except ValueError:
                            st.error("Kategori Status_Rumah tidak dikenali."); st.stop()
                        F = ['Penghasilan_Ortu','Tanggungan','Daya_Listrik','Status_Rumah','Nilai_Rapor']
                        hasil = st.session_state.model_rf.predict(dp[F])
                        df_out = df_baru.copy(); df_out['Keputusan_Akhir'] = hasil
                        st.session_state.df_hasil = df_out
                        try:
                            ds = df_out.copy()
                            ds['Waktu_Seleksi'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ds.to_sql('riwayat_seleksi',con=conn,if_exists='append',index=False)
                        except: pass
                        st.rerun()

            if st.session_state.df_hasil is not None:
                df_final = st.session_state.df_hasil
                total = len(df_final)
                layak = len(df_final[df_final['Keputusan_Akhir']=='Layak'])
                tidak = total - layak

                st.markdown('<div class="section-title">📊 Ringkasan Hasil</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric-card blue"><div class="num">{total}</div><div class="lbl">Total</div></div>
                  <div class="metric-card green"><div class="num">{layak}</div><div class="lbl">✅ Layak</div></div>
                  <div class="metric-card red"><div class="num">{tidak}</div><div class="lbl">❌ Tidak Layak</div></div>
                </div>""", unsafe_allow_html=True)

                warna_b = {'Layak':'#3B82F6','Tidak Layak':'#EF4444'}
                with st.container(border=True):
                    t1,t2 = st.tabs(["📊 Distribusi","🔍 Kelayakan"])
                    with t1:
                        c_a,c_b = st.columns(2)
                        with c_a:
                            fig,ax = kecil_fig()
                            sns.histplot(data=df_final,x='Nilai_Rapor',kde=True,color='#93C5FD',ax=ax,linewidth=.5)
                            ax.set_xlabel('Nilai',fontsize=7); ax.set_ylabel('')
                            st.pyplot(fig,use_container_width=True); plt.close(fig)
                        with c_b:
                            fig,ax = kecil_fig()
                            sns.histplot(data=df_final,x='Penghasilan_Ortu',kde=True,color='#86EFAC',ax=ax,linewidth=.5)
                            ax.set_xlabel('Penghasilan',fontsize=7); ax.set_ylabel('')
                            st.pyplot(fig,use_container_width=True); plt.close(fig)
                    with t2:
                        fig,ax = kecil_fig(3.5,2.2)
                        sns.countplot(data=df_final,x='Keputusan_Akhir',palette=warna_b,ax=ax)
                        ax.set_xlabel(''); ax.set_ylabel('Jumlah',fontsize=7)
                        st.pyplot(fig,use_container_width=True); plt.close(fig)

                with st.container(border=True):
                    st.markdown("**🧠 Faktor Penentu AI**")
                    F = ['Penghasilan_Ortu','Tanggungan','Daya_Listrik','Status_Rumah','Nilai_Rapor']
                    imp = st.session_state.model_rf.feature_importances_
                    df_imp = pd.DataFrame({'P':F,'V':imp}).sort_values('V')
                    fig,ax = kecil_fig(3.5,2.2)
                    ax.barh(df_imp['P'],df_imp['V'],color='#3B82F6',height=.5)
                    ax.set_xlabel('Pengaruh',fontsize=7)
                    st.pyplot(fig,use_container_width=True); plt.close(fig)

                st.markdown('<div class="section-title">📋 Daftar Mahasiswa</div>', unsafe_allow_html=True)
                df_l = df_final[df_final['Keputusan_Akhir']=='Layak']
                df_t = df_final[df_final['Keputusan_Akhir']=='Tidak Layak']
                st.markdown('<div class="label-layak">🟢 DIREKOMENDASIKAN — LAYAK</div>', unsafe_allow_html=True)
                st.dataframe(df_l,use_container_width=True,height=260)
                st.markdown('<div class="label-tidak">🔴 TIDAK DIREKOMENDASIKAN</div>', unsafe_allow_html=True)
                st.dataframe(df_t,use_container_width=True,height=260)

                st.markdown('<div class="section-title">📥 Unduh Berkas</div>', unsafe_allow_html=True)
                out = io.BytesIO()
                with pd.ExcelWriter(out,engine='openpyxl') as wr:
                    df_final.to_excel(wr,sheet_name='Semua',index=False)
                    df_l.to_excel(wr,sheet_name='Layak',index=False)
                    df_t.to_excel(wr,sheet_name='Tidak Layak',index=False)
                st.download_button("📥  Unduh Rekap Excel",data=out.getvalue(),
                    file_name='rekap_seleksi_kipk.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)

                if pdf_tersedia:
                    def buat_pdf(df):
                        pdf = FPDF(); pdf.add_page()
                        pdf.set_font("Arial",'B',13)
                        pdf.cell(190,9,"SURAT KEPUTUSAN SELEKSI KIP KULIAH",ln=True,align='C')
                        pdf.set_font("Arial",'B',9)
                        pdf.cell(190,7,"Universitas Cendekia Abditama",ln=True,align='C')
                        pdf.line(10,26,200,26); pdf.ln(6)
                        pdf.set_font("Arial",'B',7); pdf.set_fill_color(200,220,255)
                        for h,w in [('Nama',40),('Penghasilan',33),('Listrik',18),('Rumah',28),('Rapor',23),('Keputusan',28)]:
                            pdf.cell(w,8,h,border=1,fill=True,align='C')
                        pdf.ln(); pdf.set_font("Arial",'',7)
                        for _,row in df.iterrows():
                            nama = row.get('nama',row.get('Nama','-'))
                            pdf.cell(40,7,str(nama),border=1)
                            pdf.cell(33,7,f"Rp{row['Penghasilan_Ortu']}",border=1,align='C')
                            pdf.cell(18,7,f"{row['Daya_Listrik']}VA",border=1,align='C')
                            pdf.cell(28,7,str(row['Status_Rumah']),border=1,align='C')
                            pdf.cell(23,7,str(row['Nilai_Rapor']),border=1,align='C')
                            pdf.cell(28,7,str(row['Keputusan_Akhir']),border=1,align='C')
                            pdf.ln()
                        return pdf.output(dest='S').encode('latin-1')
                    st.download_button("📄  Cetak Surat PDF",data=buat_pdf(df_final),
                        file_name="SK_KIP_Kuliah_UCA.pdf",mime="application/pdf",use_container_width=True)

# ══════════════════════════════════════════
# MENU 3 — INFO
# ══════════════════════════════════════════
elif menu == "Info":
    st.markdown('<div class="section-title">ℹ️ Informasi KIP Kuliah</div>', unsafe_allow_html=True)

    # ── HERO BANNER ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E40AF,#3B82F6);border-radius:14px;
                padding:18px 16px;margin-bottom:14px;text-align:center;">
        <div style="font-size:2.2rem;">🎓</div>
        <div style="color:#fff;font-size:1.05rem;font-weight:800;margin:6px 0 4px 0;">
            Kartu Indonesia Pintar Kuliah
        </div>
        <div style="color:#BFDBFE;font-size:0.78rem;">
            Program Beasiswa Pemerintah Indonesia — Kemendikbudristek
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TAB NAVIGASI INFO ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 Tentang","📋 Persyaratan","📄 Dokumen","🏫 Komponen","❓ FAQ"])

    with tab1:
        st.markdown("""
        <div style="background:#EFF6FF;border-left:4px solid #3B82F6;border-radius:0 10px 10px 0;
                    padding:12px 14px;margin-bottom:10px;">
            <b style="color:#1E40AF;">Apa itu KIP Kuliah?</b><br>
            <span style="font-size:.88rem;color:#1E293B;">
            KIP Kuliah adalah bantuan biaya pendidikan dari Pemerintah Indonesia yang diberikan kepada
            mahasiswa berprestasi yang berasal dari keluarga kurang mampu secara ekonomi, dengan tujuan 
            agar mereka dapat menempuh pendidikan tinggi.
            </span>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("**🎯 Tujuan Program**")
            st.markdown("""
            - Meningkatkan akses pendidikan tinggi bagi siswa kurang mampu
            - Memperluas kesempatan bagi anak-anak dari keluarga prasejahtera
            - Mendorong pemerataan mutu pendidikan di seluruh Indonesia
            - Mencegah putus kuliah akibat keterbatasan biaya
            """)

        with st.container(border=True):
            st.markdown("**💰 Besaran Bantuan**")
            st.markdown("""
            | Jenis Biaya | Keterangan |
            |---|---|
            | Biaya Pendidikan (UKT) | Dibayar langsung ke PTN/PTS |
            | Biaya Hidup | Rp 800.000 – Rp 1.400.000 / bulan |
            | Durasi | Maksimal 8 semester (S1) / 6 semester (D3) / 4 semester (D2) / 2 semester (D1) |
            """)

        with st.container(border=True):
            st.markdown("**📅 Jadwal Pendaftaran (Estimasi)**")
            st.markdown("""
            - **Februari–Maret** → Pendaftaran akun & unggah dokumen
            - **Maret–April** → Seleksi berkas dan verifikasi
            - **Mei–Juni** → Pengumuman hasil seleksi
            - **Juli–Agustus** → Registrasi ulang penerima
            """)
            st.caption("⚠️ Jadwal dapat berubah. Pantau situs resmi: **kip-kuliah.kemdikbud.go.id**")

    with tab2:
        st.markdown("##### 📋 Persyaratan Penerima KIP Kuliah")

        with st.container(border=True):
            st.markdown("**1️⃣ Persyaratan Umum**")
            st.markdown("""
            - Warga Negara Indonesia (WNI)
            - Lulus SMA/SMK/MA atau sederajat pada tahun berjalan atau maksimal 2 tahun sebelumnya
            - Diterima di Perguruan Tinggi Negeri (PTN) atau Perguruan Tinggi Swasta (PTS) terakreditasi
            - Tidak sedang menerima beasiswa lain dari sumber APBN/APBD
            """)

        with st.container(border=True):
            st.markdown("**2️⃣ Persyaratan Ekonomi** 💰")
            st.markdown("""
            Memenuhi **salah satu** dari kriteria berikut:
            - Pemegang Kartu Indonesia Pintar (KIP) SMA/SMK
            - Terdaftar dalam Program Keluarga Harapan (PKH)
            - Pemegang Kartu Keluarga Sejahtera (KKS)
            - Orang tua/wali terdaftar dalam Data Terpadu Kesejahteraan Sosial (DTKS)
            - Penghasilan kotor gabungan orang tua **maksimal Rp 4.000.000/bulan** atau per kapita maksimal **Rp 750.000/bulan**
            """)

        with st.container(border=True):
            st.markdown("**3️⃣ Persyaratan Akademik** 🎓")
            st.markdown("""
            - Memiliki potensi akademik yang baik, dibuktikan dengan:
            - **Nilai rapor** semester 1–5 rata-rata minimal **70,00**
            - **Ranking** di kelas atau prestasi akademik lainnya
            - Lulus seleksi masuk PTN (SNBP, SNBT, atau Mandiri)
            - Diutamakan yang memiliki prestasi non-akademik (olahraga, seni, dll.)
            """)

        with st.container(border=True):
            st.markdown("**4️⃣ Indikator Kondisi Ekonomi** 🏠")
            st.markdown("""
            Diverifikasi melalui survei lapangan dengan melihat:
            - **Daya listrik rumah:** Subsidi 450 VA atau 900 VA bersubsidi
            - **Status kepemilikan rumah:** Sewa/Kontrak/Menumpang lebih diutamakan
            - **Kondisi fisik rumah:** Rumah sederhana / tidak permanen
            - **Aset keluarga:** Tidak memiliki kendaraan mewah, properti investasi, dll.
            - **Pekerjaan orang tua:** Buruh, petani, nelayan, atau pekerjaan informal
            """)

    with tab3:
        st.markdown("##### 📄 Dokumen yang Diperlukan")

        with st.container(border=True):
            st.markdown("**📁 Dokumen Wajib**")
            st.markdown("""
            ✅ Kartu Tanda Penduduk (KTP) calon mahasiswa  
            ✅ Kartu Keluarga (KK) yang masih berlaku  
            ✅ Rapor SMA/SMK/MA semester 1–5 (legalisir)  
            ✅ Ijazah atau Surat Keterangan Lulus (SKL)  
            ✅ Surat Keterangan Penghasilan Orang Tua (dari kelurahan/desa)  
            ✅ Bukti penerimaan di PTN/PTS (Surat Penerimaan Mahasiswa Baru)  
            ✅ Foto terbaru ukuran 3×4 (background merah)  
            ✅ Nomor Induk Mahasiswa (NIM) — jika sudah diterima
            """)

        with st.container(border=True):
            st.markdown("**📁 Dokumen Pendukung (jika ada)**")
            st.markdown("""
            📌 Kartu Indonesia Pintar (KIP) SMA/SMK  
            📌 Kartu Keluarga Sejahtera (KKS)  
            📌 Surat Keterangan Peserta PKH  
            📌 Surat Keterangan Tidak Mampu (SKTM) dari kelurahan/desa  
            📌 Bukti rekening listrik (untuk verifikasi daya listrik)  
            📌 Sertifikat prestasi akademik / non-akademik  
            📌 Surat pernyataan tidak menerima beasiswa lain (bermaterai)
            """)

        with st.container(border=True):
            st.markdown("**⚠️ Catatan Penting Dokumen**")
            st.markdown("""
            - Semua dokumen di-**scan/foto** dengan jelas dan tidak buram
            - Ukuran file per dokumen maksimal **2 MB** (format JPG/PDF)
            - Pastikan **nama** di semua dokumen **konsisten** (sesuai KTP)
            - Dokumen yang **tidak lengkap** akan otomatis **gugur** seleksi
            """)

    with tab4:
        st.markdown("##### 🏫 Komponen Bantuan KIP Kuliah")

        st.markdown("""
        <div style="background:#ECFDF5;border:1.5px solid #22C55E;border-radius:12px;
                    padding:14px;margin-bottom:10px;">
            <b style="color:#065F46;">✅ Biaya Pendidikan (UKT/SPP)</b><br>
            <span style="font-size:.85rem;color:#1E293B;">
            Dibayarkan langsung ke rekening perguruan tinggi sesuai besaran UKT/SPP yang ditetapkan.
            Untuk PTN maksimal sesuai golongan UKT, untuk PTS maksimal Rp 12.000.000/semester.
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#EFF6FF;border:1.5px solid #3B82F6;border-radius:12px;
                    padding:14px;margin-bottom:10px;">
            <b style="color:#1E40AF;">💵 Biaya Hidup Bulanan</b><br>
            <span style="font-size:.85rem;color:#1E293B;">
            Ditransfer ke rekening mahasiswa setiap bulan. Besaran berbeda per klaster wilayah:
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        | Klaster | Wilayah | Biaya Hidup/Bulan |
        |---|---|---|
        | Klaster 1 | Kota kecil / kabupaten | Rp 800.000 |
        | Klaster 2 | Kota sedang | Rp 950.000 |
        | Klaster 3 | Kota besar | Rp 1.100.000 |
        | Klaster 4 | Jakarta & kota mahal | Rp 1.400.000 |
        """)

        with st.container(border=True):
            st.markdown("**📅 Durasi Penerimaan Bantuan**")
            st.markdown("""
            | Program | Durasi Maksimal |
            |---|---|
            | Sarjana (S1) | 8 Semester |
            | Diploma 3 (D3) | 6 Semester |
            | Diploma 2 (D2) | 4 Semester |
            | Diploma 1 (D1) | 2 Semester |
            | Profesi (Dokter/Apoteker/dll.) | Sesuai kurikulum |
            """)

    with tab5:
        st.markdown("##### ❓ Pertanyaan yang Sering Ditanyakan")

        with st.expander("🔹 Apakah KIP Kuliah bisa digunakan di PTS?", expanded=False):
            st.markdown("""
            **Ya**, KIP Kuliah bisa digunakan di PTS yang terakreditasi BAN-PT minimal **B** (atau **Baik Sekali**).
            Namun, bantuan UKT di PTS dibatasi maksimal **Rp 12.000.000/semester**.
            """)

        with st.expander("🔹 Apakah mahasiswa yang sudah kuliah bisa daftar?", expanded=False):
            st.markdown("""
            **Tidak**. KIP Kuliah hanya untuk **mahasiswa baru** (semester 1) yang baru diterima di PTN/PTS.
            Mahasiswa lama atau pindahan tidak bisa mendaftar KIP Kuliah.
            """)

        with st.expander("🔹 Apakah nilai rapor buruk otomatis gugur?", expanded=False):
            st.markdown("""
            **Ya**, nilai rapor adalah **syarat mutlak**. Jika rata-rata nilai rapor di bawah ambang batas 
            (umumnya **70,00**), pendaftar akan otomatis dinyatakan **Tidak Layak** meskipun kondisi 
            ekonominya sangat kurang mampu.
            """)

        with st.expander("🔹 Apa yang terjadi jika IPK turun?", expanded=False):
            st.markdown("""
            Penerima KIP Kuliah wajib mempertahankan **IPK minimal 2,75** setiap semester.
            Jika IPK di bawah ketentuan selama 2 semester berturut-turut, bantuan dapat **dicabut**.
            """)

        with st.expander("🔹 Apakah bisa pindah jurusan/PTN?", expanded=False):
            st.markdown("""
            **Tidak diperkenankan** pindah program studi atau perguruan tinggi selama menerima KIP Kuliah,
            kecuali mendapat persetujuan khusus dari Kemendikbudristek. Jika pindah tanpa izin, 
            bantuan akan **dihentikan**.
            """)

        with st.expander("🔹 Di mana mendaftar KIP Kuliah?", expanded=False):
            st.markdown("""
            Pendaftaran dilakukan secara online melalui:
            - 🌐 **Website:** [kip-kuliah.kemdikbud.go.id](https://kip-kuliah.kemdikbud.go.id)
            - 📱 **Aplikasi:** KIP Kuliah Mobile (tersedia di Play Store & App Store)
            - Bisa juga melalui portal **SNPMB** saat pendaftaran SNBP/SNBT
            """)

        with st.expander("🔹 Bagaimana cara kerja sistem AI di aplikasi ini?", expanded=False):
            st.markdown("""
            Sistem ini menggunakan algoritma **Random Forest** — sejenis kecerdasan buatan yang 
            mempelajari pola dari data historis penerima KIP Kuliah sebelumnya. 
            
            AI mempertimbangkan **5 faktor utama:**
            1. 💰 Penghasilan Orang Tua
            2. 👨‍👩‍👧‍👦 Jumlah Tanggungan Keluarga  
            3. ⚡ Daya Listrik Rumah
            4. 🏠 Status Kepemilikan Rumah
            5. 📊 Nilai Rata-rata Rapor
            
            Keputusan AI bersifat **rekomendasi awal** — keputusan final tetap berada di tangan 
            panitia seleksi perguruan tinggi.
            """)

# ══════════════════════════════════════════
# MENU 4 — DATABASE
# ══════════════════════════════════════════
elif menu == "Database":
    st.markdown('<div class="section-title">🗄️ Riwayat Database Admin</div>', unsafe_allow_html=True)
    st.caption("Semua hasil seleksi tersimpan otomatis.")
    try:
        df_h = pd.read_sql('SELECT * FROM riwayat_seleksi ORDER BY Waktu_Seleksi DESC',con=conn)
        if len(df_h) > 0:
            fs = st.radio("Filter:",["Semua","Layak","Tidak Layak"],horizontal=True)
            df_t = df_h if fs=="Semua" else df_h[df_h['Keputusan_Akhir']==fs]
            tl = len(df_h[df_h['Keputusan_Akhir']=='Layak'])
            tt = len(df_h[df_h['Keputusan_Akhir']=='Tidak Layak'])
            st.markdown(f"""
            <div class="metric-row">
              <div class="metric-card blue"><div class="num">{len(df_t)}</div><div class="lbl">Tampil</div></div>
              <div class="metric-card green"><div class="num">{tl}</div><div class="lbl">✅ Layak</div></div>
              <div class="metric-card red"><div class="num">{tt}</div><div class="lbl">❌ Tidak Layak</div></div>
            </div>""", unsafe_allow_html=True)
            st.dataframe(df_t,use_container_width=True)
            st.markdown("")
            if st.button("🗑️  Kosongkan Database",type="primary",use_container_width=True):
                conn.cursor().execute("DROP TABLE riwayat_seleksi"); conn.commit()
                st.success("✅ Database dikosongkan!"); st.rerun()
        else:
            st.info("ℹ️ Database kosong. Jalankan seleksi dulu di menu Seleksi.")
    except:
        st.info("ℹ️ Database kosong. Jalankan seleksi dulu di menu Seleksi.")

# ══════════════════════════════════════════
# TOMBOL KELUAR — tampil di semua halaman, di bawah konten
# ══════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="border-top:1.5px solid #E2E8F0;margin:8px 0 16px 0;"></div>', unsafe_allow_html=True)
st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
if st.button("🚪  Keluar / Logout", key="btn_logout", use_container_width=True):
    st.session_state['logged_in'] = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
