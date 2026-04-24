import streamlit as st
from auth import is_logged_in, show_login_page, logout
from koneksi import get_koneksi
import pandas as pd
import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ─────────────────────────────────────────────────────────────
# Konfigurasi halaman
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grand Mode | Stok Muslim Pria",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Global
st.markdown(
    """
    <style>
    /* Warna tema hijau islami */
    :root {
        --primary: #1a6b3c;
        --primary-light: #e8f5ee;
        --accent: #f0a500;
        --danger: #dc3545;
        --card-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    /* Card produk */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.product-card) {
        border-radius: 12px !important;
    }
    /* Badge kategori */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-koko  { background: #dbeafe; color: #1d4ed8; }
    .badge-kurta { background: #fef3c7; color: #92400e; }
    .badge-jubah { background: #f3e8ff; color: #6b21a8; }
    /* Stok warning */
    .stok-rendah { color: #dc3545; font-weight: 700; }
    .stok-aman   { color: #1a6b3c; font-weight: 600; }
    /* Header stat card */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: var(--card-shadow);
        text-align: center;
        border-left: 4px solid var(--primary);
    }
    .stat-number { font-size: 2rem; font-weight: 800; color: var(--primary); }
    .stat-label  { color: #6b7280; font-size: 0.85rem; margin-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Guard: wajib login
# ─────────────────────────────────────────────────────────────
if not is_logged_in():
    show_login_page()
    st.stop()

# ─────────────────────────────────────────────────────────────
# Inisialisasi session state
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "hapus_id" not in st.session_state:
    st.session_state.hapus_id = None
if "notif" not in st.session_state:
    st.session_state.notif = None

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding:1rem 0 0.5rem'>
            <div style='font-size:2.5rem'>🕌</div>
            <div style='font-weight:800; font-size:1.1rem; color:#1a6b3c'>Grand Mode</div>
            <div style='font-size:0.8rem; color:#6b7280'>Stok Muslim Pria</div>
        </div>
        <hr style='margin:0.8rem 0'>
        """,
        unsafe_allow_html=True,
    )

    menu_items = [
        ("🏠", "Dashboard"),  # Ringkasan data
        ("📦", "Stok Produk"),  # Lihat, edit, hapus produk
        ("➕", "Tambah Produk"),  # Input produk baru
        ("📊", "Laporan"),  # Analisis & rekap data
    ]

    for icon, label in menu_items:
        is_active = st.session_state.page == label
        style = (
            "background:#e8f5ee; color:#1a6b3c; font-weight:700;" if is_active else ""
        )
        if st.button(
            f"{icon}  {label}",
            use_container_width=True,
            key=f"menu_{label}",
        ):
            st.session_state.page = label
            st.session_state.edit_id = None
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.8rem; color:#6b7280; padding:0 0.5rem'>"
        f"Login sebagai: <b>{st.session_state.get('admin_username','admin')}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────
# ===============================
# EXPORT EXCEL
# ===============================
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Laporan")
    return output.getvalue()


# ===============================
# EXPORT PDF
# ===============================
def export_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )

    elements = [table]
    doc.build(elements)

    return buffer.getvalue()


IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)


def get_conn():
    return get_koneksi()


def fetch_all_products():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM produk ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    cols = [
        "id",
        "nama_produk",
        "bahan",
        "motif",
        "warna",
        "ukuran",
        "kategori",
        "harga",
        "stok",
        "gambar",
        "created_at",
        "updated_at",
    ]
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)


def badge_html(kategori):
    cls = {"Koko Pria": "koko", "Kurta Pria": "kurta", "Jubah Pria": "jubah"}.get(
        kategori, "koko"
    )
    return f"<span class='badge badge-{cls}'>{kategori}</span>"


def stok_html(stok):
    cls = "stok-rendah" if stok < 10 else "stok-aman"
    icon = "⚠️" if stok < 10 else "✅"
    return f"<span class='{cls}'>{icon} {stok}</span>"


def show_notif():
    if st.session_state.notif:
        t, msg = st.session_state.notif
        if t == "success":
            st.success(msg)
        elif t == "error":
            st.error(msg)
        st.session_state.notif = None


# ═══════════════════════════════════════════════════════════
# HALAMAN: DASHBOARD
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "Dashboard":
    show_notif()

    st.markdown("## 🏠 Dashboard")
    st.caption("Ringkasan stok & nilai barang toko")
    st.markdown("---")

    df = fetch_all_products()

    # ===============================
    # PERHITUNGAN DATA UTAMA
    # ===============================
    total_produk = len(df)
    total_stok = int(df["stok"].sum()) if not df.empty else 0
    stok_rendah = int((df["stok"] < 10).sum()) if not df.empty else 0

    # 👉 TOTAL NILAI = harga × stok (nilai semua barang kalau dijual)
    total_nilai = int((df["harga"] * df["stok"]).sum()) if not df.empty else 0

    # ===============================
    # CARD STATISTIK
    # ===============================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
        <div class='stat-card'>
            <div class='stat-number'>{total_produk}</div>
            <div class='stat-label'>Jumlah Produk</div>
        </div>""",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
        <div class='stat-card'>
            <div class='stat-number'>{total_stok:,}</div>
            <div class='stat-label'>Total Stok (pcs)</div>
        </div>""",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
        <div class='stat-card' style='border-left-color:#dc3545'>
            <div class='stat-number' style='color:#dc3545'>{stok_rendah}</div>
            <div class='stat-label'>Produk Stok Rendah</div>
        </div>""",
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
        <div class='stat-card' style='border-left-color:#f0a500'>
            <div class='stat-number' style='color:#f0a500'>
                Rp {total_nilai:,}
            </div>
            <div class='stat-label'>Total Nilai Barang</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("### 📊 Analisis Stok")

    # ===============================
    # TABEL FULL WIDTH (FIX SCROLL)
    # ===============================
    st.markdown("#### 📦 Stok per Kategori")

    if not df.empty:
        summary = (
            df.groupby("kategori")
            .agg(
                Jumlah_Produk=("id", "count"),
                Total_Stok=("stok", "sum"),
                Harga_Min=("harga", "min"),
                Harga_Max=("harga", "max"),
            )
            .reset_index()
        )

        summary.columns = [
            "Kategori",
            "Jumlah Produk",
            "Total Stok",
            "Harga Min",
            "Harga Max",
        ]

        st.dataframe(summary, use_container_width=True, hide_index=True)

    # ===============================
    # STOK RENDAH
    # ===============================
    st.markdown("#### ⚠️ Produk Stok Rendah")

    if not df.empty:
        rendah = df[df["stok"] < 10][
            ["nama_produk", "kategori", "ukuran", "stok"]
        ].sort_values("stok")

        if rendah.empty:
            st.success("Semua stok aman ✅")
        else:
            st.dataframe(
                rendah.rename(
                    columns={
                        "nama_produk": "Produk",
                        "kategori": "Kategori",
                        "ukuran": "Ukuran",
                        "stok": "Stok",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

# ═══════════════════════════════════════════════════════════
# HALAMAN: STOK PRODUK (READ + EDIT + HAPUS)
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "Stok Produk":
    show_notif()

    # ── Mode EDIT ──
    if st.session_state.edit_id is not None:
        st.markdown("## ✏️ Edit Produk")

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM produk WHERE id=%s", (st.session_state.edit_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            st.error("Produk tidak ditemukan.")
            st.session_state.edit_id = None
            st.rerun()

        (pid, nama, bahan, motif, warna, ukuran, kat, harga, stok, gambar, *_) = row

        col1, col2 = st.columns([1, 2])
        with col1:
            img_path = os.path.join(IMAGE_DIR, gambar) if gambar else None
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.info("Tidak ada gambar")

        with col2:
            with st.form("form_edit"):
                nama_new = st.text_input("Nama Produk", nama)
                bahan_new = st.text_input("Bahan", bahan)
                motif_new = st.text_input("Motif", motif)
                warna_new = st.text_input("Warna", warna)
                ukuran_new = st.selectbox(
                    "Ukuran",
                    ["S", "M", "L", "XL", "XXL"],
                    index=(
                        ["S", "M", "L", "XL", "XXL"].index(ukuran)
                        if ukuran in ["S", "M", "L", "XL", "XXL"]
                        else 2
                    ),
                )
                kat_list = ["Koko Pria", "Kurta Pria", "Jubah Pria"]
                kat_new = st.selectbox(
                    "Kategori",
                    kat_list,
                    index=kat_list.index(kat) if kat in kat_list else 0,
                )
                harga_new = st.number_input(
                    "Harga (Rp)", min_value=0, value=int(harga), step=5000
                )
                stok_new = st.number_input(
                    "Stok (pcs)", min_value=0, value=int(stok), step=1
                )
                file_gambar = st.file_uploader(
                    "Ganti Gambar (opsional)", type=["jpg", "jpeg", "png"]
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button(
                        "💾 Simpan Perubahan", use_container_width=True
                    )
                with col_b:
                    cancel = st.form_submit_button("⬅ Batal", use_container_width=True)

        if cancel:
            st.session_state.edit_id = None
            st.rerun()

        if submitted:
            nama_file = gambar
            if file_gambar:
                nama_file = f"{nama_new.replace(' ','_')}_{file_gambar.name}"
                with open(os.path.join(IMAGE_DIR, nama_file), "wb") as f:
                    f.write(file_gambar.getbuffer())

            conn = get_conn()
            c = conn.cursor()
            c.execute(
                """
                UPDATE produk SET nama_produk=%s,bahan=%s,motif=%s,warna=%s,
                ukuran=%s,kategori=%s,harga=%s,stok=%s,gambar=%s
                WHERE id=%s
            """,
                (
                    nama_new,
                    bahan_new,
                    motif_new,
                    warna_new,
                    ukuran_new,
                    kat_new,
                    harga_new,
                    stok_new,
                    nama_file,
                    pid,
                ),
            )
            conn.commit()
            conn.close()

            st.session_state.notif = (
                "success",
                f"✅ Produk '{nama_new}' berhasil diperbarui!",
            )
            st.session_state.edit_id = None
            st.rerun()

    # ── Mode LIST ──
    else:
        st.markdown("## 📦 Stok Produk")

        df = fetch_all_products()

        # Filter
        with st.expander("🔍 Filter & Pencarian", expanded=True):
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                f_search = st.text_input(
                    "Cari nama produk", placeholder="ketik kata kunci..."
                )
            with fc2:
                f_kat = st.selectbox(
                    "Kategori",
                    (
                        ["Semua"] + sorted(df["kategori"].unique().tolist())
                        if not df.empty
                        else ["Semua"]
                    ),
                )
            with fc3:
                f_ukuran = st.selectbox(
                    "Ukuran",
                    (
                        ["Semua"] + sorted(df["ukuran"].unique().tolist())
                        if not df.empty
                        else ["Semua"]
                    ),
                )
            with fc4:
                f_stok = st.selectbox(
                    "Stok", ["Semua", "Stok Rendah (<10)", "Stok Aman (≥10)"]
                )

        df_f = df.copy()
        if f_search:
            df_f = df_f[
                df_f["nama_produk"].str.contains(f_search, case=False, na=False)
            ]
        if f_kat != "Semua":
            df_f = df_f[df_f["kategori"] == f_kat]
        if f_ukuran != "Semua":
            df_f = df_f[df_f["ukuran"] == f_ukuran]
        if f_stok == "Stok Rendah (<10)":
            df_f = df_f[df_f["stok"] < 10]
        elif f_stok == "Stok Aman (≥10)":
            df_f = df_f[df_f["stok"] >= 10]

        st.caption(f"Menampilkan **{len(df_f)}** dari **{len(df)}** produk")

        # Tabel
        if df_f.empty:
            st.info("Tidak ada produk yang sesuai filter.")
        else:
            # Header tabel
            h0, h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
                [0.5, 3, 2, 2, 2, 1.5, 2, 1.5, 2]
            )
            for h, label in zip(
                [h0, h1, h2, h3, h4, h5, h6, h7, h8],
                [
                    "#",
                    "Nama Produk",
                    "Kategori",
                    "Bahan",
                    "Warna",
                    "Ukuran",
                    "Harga",
                    "Stok",
                    "Aksi",
                ],
            ):
                h.markdown(f"**{label}**")
            st.markdown("<hr style='margin:4px 0'>", unsafe_allow_html=True)

            for i, row in df_f.iterrows():
                c0, c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                    [0.5, 3, 2, 2, 2, 1.5, 2, 1.5, 2]
                )
                c0.write(row["id"])
                c1.write(row["nama_produk"])
                c2.markdown(badge_html(row["kategori"]), unsafe_allow_html=True)
                c3.write(row["bahan"])
                c4.write(row["warna"])
                c5.write(row["ukuran"])
                c6.write(f"Rp {int(row['harga']):,}")
                c7.markdown(stok_html(int(row["stok"])), unsafe_allow_html=True)

                col_edit, col_del = c8.columns(2)
                if col_edit.button("✏️", key=f"edit_{row['id']}", help="Edit produk"):
                    st.session_state.edit_id = row["id"]
                    st.rerun()

                if col_del.button("🗑️", key=f"del_{row['id']}", help="Hapus produk"):
                    st.session_state.hapus_id = row["id"]
                    st.session_state.hapus_nama = row["nama_produk"]

        # Konfirmasi hapus
        if st.session_state.get("hapus_id"):
            pid = st.session_state.hapus_id
            nama = st.session_state.hapus_nama
            with st.container():
                st.warning(f"⚠️ Yakin ingin menghapus produk **'{nama}'** (ID: {pid})?")
                col_ya, col_batal = st.columns(2)
                if col_ya.button("✅ Ya, Hapus", use_container_width=True):
                    conn = get_conn()
                    cc = conn.cursor()
                    cc.execute("DELETE FROM produk WHERE id=%s", (pid,))
                    conn.commit()
                    conn.close()
                    st.session_state.notif = (
                        "success",
                        f"✅ Produk '{nama}' berhasil dihapus.",
                    )
                    st.session_state.hapus_id = None
                    st.session_state.hapus_nama = None
                    st.rerun()
                if col_batal.button("❌ Batal", use_container_width=True):
                    st.session_state.hapus_id = None
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# HALAMAN: TAMBAH PRODUK (CREATE)
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "Tambah Produk":
    show_notif()
    st.markdown("## ➕ Tambah Produk Baru")

    col_form, col_prev = st.columns([2, 1])

    with col_form:
        with st.form("form_tambah", clear_on_submit=True):
            st.markdown("#### 📝 Informasi Produk")
            nama = st.text_input(
                "Nama Produk *", placeholder="contoh: Koko Lengan Panjang Bordir"
            )

            r1c1, r1c2 = st.columns(2)
            bahan = r1c1.text_input("Bahan *", placeholder="Katun Rayon, Dobby, ...")
            motif = r1c2.text_input(
                "Motif *", placeholder="Polos, Bordir, Tekstur, ..."
            )

            r2c1, r2c2 = st.columns(2)
            warna = r2c1.text_input("Warna *", placeholder="Putih, Navy, ...")
            ukuran = r2c2.selectbox("Ukuran *", ["S", "M", "L", "XL", "XXL"])

            kat = st.selectbox("Kategori *", ["Koko Pria", "Kurta Pria", "Jubah Pria"])

            r3c1, r3c2 = st.columns(2)
            harga = r3c1.number_input(
                "Harga (Rp) *", min_value=0, step=5000, value=150000
            )
            stok = r3c2.number_input("Stok (pcs) *", min_value=0, step=1, value=10)

            gambar = st.file_uploader("📷 Upload Gambar", type=["jpg", "jpeg", "png"])

            submit = st.form_submit_button("💾 Simpan Produk", use_container_width=True)

    with col_prev:
        st.markdown("#### 🖼️ Preview Gambar")

        if gambar is not None:
            st.image(gambar, caption="Preview Gambar", use_container_width=True)
        else:
            st.markdown(
                "<div style='border:2px dashed #ccc;border-radius:10px;"
                "height:200px;display:flex;align-items:center;justify-content:center;"
                "color:#9ca3af'>📷 Belum ada gambar</div>",
                unsafe_allow_html=True,
            )

    if submit:
        if not nama or not bahan or not motif or not warna:
            st.error("Lengkapi semua field yang wajib diisi (*).")
        else:
            nama_file = None
            if gambar:
                nama_file = f"{nama.replace(' ','_')}_{gambar.name}"
                with open(os.path.join(IMAGE_DIR, nama_file), "wb") as f:
                    f.write(gambar.getbuffer())

            conn = get_conn()
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO produk (nama_produk,bahan,motif,warna,ukuran,kategori,harga,stok,gambar)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
                (nama, bahan, motif, warna, ukuran, kat, harga, stok, nama_file),
            )
            conn.commit()
            conn.close()

            st.session_state.notif = (
                "success",
                f"✅ Produk '{nama}' berhasil ditambahkan!",
            )
            st.session_state.page = "Stok Produk"
            st.rerun()


# ═══════════════════════════════════════════════════════════
# HALAMAN: LAPORAN
# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# HALAMAN: LAPORAN (# Rekap + Export Data)
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "Laporan":
    st.markdown("## 📊 Laporan Stok")

    df = fetch_all_products()

    if df.empty:
        st.info("Belum ada data produk.")
    else:

        # ===============================
        # EXPORT BUTTON
        # ===============================
        st.markdown("### 📥 Export Laporan")

        export_df = df[
            ["nama_produk", "kategori", "bahan", "warna", "ukuran", "harga", "stok"]
        ].copy()

        export_df.columns = [
            "Nama Produk",
            "Kategori",
            "Bahan",
            "Warna",
            "Ukuran",
            "Harga",
            "Stok",
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📊 Download Excel",
                data=export_excel(export_df),
                file_name="laporan_stok.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col2:
            st.download_button(
                label="📄 Download PDF",
                data=export_pdf(export_df),
                file_name="laporan_stok.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.markdown("---")

        # ===============================
        # TABS LAPORAN
        # ===============================
        tab1, tab2, tab3 = st.tabs(
            ["📈 Ringkasan", "📋 Detail Lengkap", "⚠️ Stok Rendah"]
        )

        # ===============================
        # TAB 1: RINGKASAN
        # ===============================
        with tab1:
            st.markdown("#### Stok & Nilai per Kategori")

            df["total_nilai"] = df["harga"] * df["stok"]

            summary = (
                df.groupby("kategori")
                .agg(
                    Jumlah_SKU=("id", "count"),
                    Total_Stok=("stok", "sum"),
                    Total_Nilai=("total_nilai", "sum"),
                    Harga_Min=("harga", "min"),
                    Harga_Max=("harga", "max"),
                )
                .reset_index()
            )

            summary["Total_Nilai"] = summary["Total_Nilai"].apply(
                lambda x: f"Rp {int(x):,}"
            )
            summary["Harga_Min"] = summary["Harga_Min"].apply(
                lambda x: f"Rp {int(x):,}"
            )
            summary["Harga_Max"] = summary["Harga_Max"].apply(
                lambda x: f"Rp {int(x):,}"
            )

            summary.columns = [
                "Kategori",
                "Jumlah SKU",
                "Total Stok",
                "Total Nilai",
                "Harga Terkecil",
                "Harga Terbesar",
            ]

            st.dataframe(summary, use_container_width=True, hide_index=True)

            st.markdown("#### Distribusi per Ukuran")

            ukuran_summary = df.groupby("ukuran")["stok"].sum().reset_index()
            ukuran_summary.columns = ["Ukuran", "Total Stok"]

            st.bar_chart(ukuran_summary.set_index("Ukuran"))

        # ===============================
        # TAB 2: DETAIL
        # ===============================
        with tab2:
            show_df = df[
                [
                    "id",
                    "nama_produk",
                    "kategori",
                    "bahan",
                    "warna",
                    "ukuran",
                    "harga",
                    "stok",
                ]
            ].copy()

            show_df["harga"] = show_df["harga"].apply(lambda x: f"Rp {int(x):,}")

            show_df.columns = [
                "ID",
                "Nama Produk",
                "Kategori",
                "Bahan",
                "Warna",
                "Ukuran",
                "Harga",
                "Stok",
            ]

            st.dataframe(show_df, use_container_width=True, hide_index=True)

        # ===============================
        # TAB 3: STOK RENDAH
        # ===============================
        with tab3:
            rendah = df[df["stok"] < 10][
                ["nama_produk", "kategori", "ukuran", "warna", "stok", "harga"]
            ].sort_values("stok")

            if rendah.empty:
                st.success("🎉 Semua produk memiliki stok cukup!")
            else:
                st.warning(f"⚠️ {len(rendah)} produk memiliki stok rendah!")

                rendah["harga"] = rendah["harga"].apply(lambda x: f"Rp {int(x):,}")

                rendah.columns = [
                    "Nama Produk",
                    "Kategori",
                    "Ukuran",
                    "Warna",
                    "Stok",
                    "Harga",
                ]

                st.dataframe(rendah, use_container_width=True, hide_index=True)
