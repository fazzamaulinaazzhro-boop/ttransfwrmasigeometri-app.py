import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Virtual Lab: Transformasi Geometri",
    page_icon="📐",
    layout="wide"
)

# --- Judul dan Intro ---
st.title("📐 Virtual Lab Matematika: Transformasi Geometri")
st.markdown("""
Selamat datang di laboratorium virtual! Di sini kamu bisa bereksperimen dengan 
**Translasi**, **Refleksi**, **Rotasi**, dan **Dilatasi** pada sebuah segitiga. 
Ubah parameter di sebelah kiri dan lihat apa yang terjadi pada grafik!
""")

# --- Sidebar (Kontrol) ---
st.sidebar.header("⚙️ Panel Kontrol")
jenis_transformasi = st.sidebar.selectbox(
    "Pilih Jenis Transformasi",
    ["Translasi (Pergeseran)", "Refleksi (Pencerminan)", "Rotasi (Perputaran)", "Dilatasi (Perkalian)"]
)

# --- Koordinat Awal (Segitiga ABC) ---
# Default points
p_awal = {
    'A': np.array([2, 5]),
    'B': np.array([5, 5]),
    'C': np.array([3, 8])
}

# Opsional: Izinkan user mengubah titik awal
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Koordinat Awal Segitiga")
ax = st.sidebar.number_input("Titik A (x)", value=2)
ay = st.sidebar.number_input("Titik A (y)", value=5)
bx = st.sidebar.number_input("Titik B (x)", value=5)
by = st.sidebar.number_input("Titik B (y)", value=5)
cx = st.sidebar.number_input("Titik C (x)", value=3)
cy = st.sidebar.number_input("Titik C (y)", value=8)

# Update points based on input
p_awal['A'] = np.array([ax, ay])
p_awal['B'] = np.array([bx, by])
p_awal['C'] = np.array([cx, cy])

# --- Logika Transformasi ---
def transform_point(point, matrix):
    # Menambahkan dimensi homogen untuk perkalian matriks jika perlu, 
    # tapi di sini kita pakai cara manual/langsung agar mudah dipahami siswa
    return point # Placeholder

p_akhir = {}
rumus_latex = ""
penjelasan = ""

# 1. TRANSLASI
if jenis_transformasi == "Translasi (Pergeseran)":
    st.sidebar.subheader("Parameter Translasi")
    tx = st.sidebar.slider("Geser X (Kanan/Kiri)", -10, 10, 3)
    ty = st.sidebar.slider("Geser Y (Atas/Bawah)", -10, 10, 2)
    
    rumus_latex = r"\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} x \\ y \end{pmatrix} + \begin{pmatrix} a \\ b \end{pmatrix}"
    penjelasan = f"Setiap titik digeser sejauh **{tx} satuan** sumbu-X dan **{ty} satuan** sumbu-Y."
    
    for key, val in p_awal.items():
        p_akhir[key] = val + np.array([tx, ty])

# 2. REFLEKSI
elif jenis_transformasi == "Refleksi (Pencerminan)":
    st.sidebar.subheader("Sumbu Cermin")
    mode_refleksi = st.sidebar.radio("Cerminkan terhadap:", 
                                     ["Sumbu X", "Sumbu Y", "Garis y = x", "Garis y = -x", "Titik Pusat (0,0)"])
    
    if mode_refleksi == "Sumbu X":
        rumus_latex = r"(x, y) \rightarrow (x, -y)"
        matriks = np.array([[1, 0], [0, -1]])
    elif mode_refleksi == "Sumbu Y":
        rumus_latex = r"(x, y) \rightarrow (-x, y)"
        matriks = np.array([[-1, 0], [0, 1]])
    elif mode_refleksi == "Garis y = x":
        rumus_latex = r"(x, y) \rightarrow (y, x)"
        matriks = np.array([[0, 1], [1, 0]])
    elif mode_refleksi == "Garis y = -x":
        rumus_latex = r"(x, y) \rightarrow (-y, -x)"
        matriks = np.array([[0, -1], [-1, 0]])
    else: # Titik Pusat
        rumus_latex = r"(x, y) \rightarrow (-x, -y)"
        matriks = np.array([[-1, 0], [0, -1]])

    penjelasan = f"Pencerminan dilakukan terhadap **{mode_refleksi}**."
    
    for key, val in p_awal.items():
        p_akhir[key] = np.dot(matriks, val)

# 3. ROTASI
elif jenis_transformasi == "Rotasi (Perputaran)":
    st.sidebar.subheader("Sudut Rotasi")
    theta_deg = st.sidebar.slider("Sudut (Derajat)", -360, 360, 90)
    theta_rad = np.radians(theta_deg)
    
    cos_t = np.cos(theta_rad)
    sin_t = np.sin(theta_rad)
    
    # Matriks Rotasi (berlawanan arah jarum jam)
    matriks = np.array([[cos_t, -sin_t], [sin_t, cos_t]])
    
    rumus_latex = r"\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} \cos \theta & -\sin \theta \\ \sin \theta & \cos \theta \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix}"
    penjelasan = f"Objek diputar sebesar **{theta_deg}°** berlawanan arah jarum jam dengan pusat (0,0)."
    
    for key, val in p_awal.items():
        p_akhir[key] = np.dot(matriks, val)

# 4. DILATASI
elif jenis_transformasi == "Dilatasi (Perkalian)":
    st.sidebar.subheader("Faktor Skala")
    k = st.sidebar.slider("Faktor Skala (k)", -3.0, 3.0, 2.0, 0.1)
    
    rumus_latex = r"\begin{pmatrix} x' \\ y' \end{pmatrix} = k \begin{pmatrix} x \\ y \end{pmatrix}"
    penjelasan = f"Objek diperbesar/diperkecil dengan faktor skala **k = {k}** dari pusat (0,0)."
    
    for key, val in p_awal.items():
        p_akhir[key] = val * k

# --- Visualisasi dengan Plotly ---

# Helper function untuk membuat list koordinat polygon (biar nyambung A-B-C-A)
def get_poly_coords(points_dict):
    coords = list(points_dict.values())
    coords.append(coords[0]) # Tutup jalur kembali ke A
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    return xs, ys

x_awal, y_awal = get_poly_coords(p_awal)
x_akhir, y_akhir = get_poly_coords(p_akhir)

fig = go.Figure()

# Plot Segitiga Awal
fig.add_trace(go.Scatter(
    x=x_awal, y=y_awal,
    mode='lines+markers+text',
    name='Awal (Asli)',
    line=dict(color='royalblue', width=2, dash='dash'),
    fill='toself',
    fillcolor='rgba(65, 105, 225, 0.2)', # Biru transparan
    text=["A", "B", "C", ""],
    textposition="top center"
))

# Plot Segitiga Akhir
fig.add_trace(go.Scatter(
    x=x_akhir, y=y_akhir,
    mode='lines+markers+text',
    name='Akhir (Bayangan)',
    line=dict(color='firebrick', width=3),
    fill='toself',
    fillcolor='rgba(178, 34, 34, 0.2)', # Merah transparan
    text=["A'", "B'", "C'", ""],
    textposition="top center"
))

# Dekorasi Layout Grafik
# Kita kunci range sumbu agar efek pergerakan terlihat jelas (tidak auto-zoom)
range_val = 15
fig.update_layout(
    title=f"Visualisasi {jenis_transformasi}",
    xaxis=dict(range=[-range_val, range_val], zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    yaxis=dict(range=[-range_val, range_val], zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    width=700,
    height=600,
    showlegend=True,
    grid=dict(rows=1, columns=1)
)

# --- Tampilan Layout Streamlit ---
col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📝 Teori & Rumus")
    st.info(penjelasan)
    st.latex(rumus_latex)
    
    st.markdown("---")
    st.subheader("📊 Perbandingan Koordinat")
    
    # Buat DataFrame untuk tabel
    data_coords = {
        "Titik": ["A", "B", "C"],
        "Awal (x,y)": [f"({p[0]:.1f}, {p[1]:.1f})" for p in p_awal.values()],
        "Bayangan (x',y')": [f"({p[0]:.1f}, {p[1]:.1f})" for p in p_akhir.values()]
    }
    df = pd.DataFrame(data_coords)
    st.table(df)

    st.success("Tips: Coba ubah 'Koordinat Awal' di sidebar untuk melihat bentuk segitiga yang berbeda!")
