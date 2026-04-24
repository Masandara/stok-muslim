import hashlib
import streamlit as st
from koneksi import get_koneksi


# ─────────────────────────────────────────────
# 🔐 HASH FUNCTION
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────────
# 🔑 SESSION
# ─────────────────────────────────────────────
def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def login(username: str, password: str) -> bool:
    try:
        conn = get_koneksi()
        cursor = conn.cursor()

        hashed_password = hash_password(password)

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, hashed_password),
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state["logged_in"] = True
            st.session_state["admin_username"] = username
            return True

        return False

    except Exception as e:
        st.error(f"Error: {e}")
        return False


def logout():
    st.session_state.clear()


# ─────────────────────────────────────────────
# 🖥️ LOGIN UI
# ─────────────────────────────────────────────
def show_login_page():
    st.markdown("## 🕌 Grand Mode Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not username or not password:
            st.error("Semua field wajib diisi")
        elif login(username, password):
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username / Password salah")
