import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from db import init_connection, get_db
from auth import login, register, get_all_users, delete_user, verify_token

st.set_page_config(page_title="Internal App", page_icon=":office:", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None

if "db" not in st.session_state:
    st.session_state.db = None


def connect_db():
    uri = st.secrets["mongo"]["uri"]
    db_name = st.secrets["mongo"]["db_name"]
    client = init_connection(uri)
    if client:
        st.session_state.db = get_db(client, db_name)
        return True
    return False


if st.session_state.db is None:
    if not connect_db():
        st.error("Gagal koneksi ke MongoDB!")
        st.stop()


db = st.session_state.db


def is_logged_in() -> bool:
    token = st.session_state.get("token")
    if not token:
        return False
    payload = verify_token(token)
    return payload is not None


def get_current_user() -> dict | None:
    token = st.session_state.get("token")
    if not token:
        return None
    return verify_token(token)


def logout():
    del st.session_state["token"]


if not is_logged_in():
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                result = login(db, username, password)
                if result:
                    st.session_state.token = result["token"]
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

    with tab_register:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_user")
            new_name = st.text_input("Nama Lengkap", key="reg_name")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            reg_submitted = st.form_submit_button("Register")

            if reg_submitted:
                success, msg = register(db, new_username, new_name, new_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

else:
    user = get_current_user()

    with st.sidebar:
        st.write(f"**{user['username']}** ({user['role']})")
        if st.button("Logout"):
            logout()
            st.rerun()

    st.title("Internal App")

    tab_data, tab_admin = st.tabs(["Data", "Admin"])

    with tab_data:
        st.subheader("CRUD Data")

        collection = db["items"]

        with st.form("add_item"):
            st.write("Tambah Data")
            item_name = st.text_input("Nama Item")
            item_desc = st.text_area("Deskripsi")
            if st.form_submit_button("Tambah"):
                collection.insert_one({"name": item_name, "description": item_desc, "author": user["username"]})
                st.success("Berhasil ditambahkan!")
                st.rerun()

        st.write("---")
        st.write("Data saat ini:")
        items = list(collection.find({}, {"_id": 0}))
        for item in items:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{item['name']}** - {item['description']} (oleh {item['author']})")
            with col2:
                if st.button("Hapus", key=f"del_{item['name']}"):
                    collection.delete_one({"name": item["name"]})
                    st.rerun()

    with tab_admin:
        if user["role"] != "admin":
            st.warning("Hanya admin yang bisa mengakses halaman ini.")
        else:
            st.subheader("Kelola User")
            users = get_all_users(db)
            for u in users:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{u['username']}** - {u['name']} ({u['role']})")
                with col2:
                    if u["username"] != "admin":
                        if st.button("Hapus", key=f"del_user_{u['username']}"):
                            delete_user(db, u["username"])
                            st.rerun()
