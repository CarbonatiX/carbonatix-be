import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from api import login, register

st.set_page_config(page_title="CarbonatiX ERP", page_icon=":office:", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


def is_logged_in() -> bool:
    return st.session_state.token is not None


def get_current_user() -> dict | None:
    return st.session_state.user


def logout():
    st.session_state.token = None
    st.session_state.user = None


if not is_logged_in():
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                try:
                    result = login(username, password)
                    st.session_state.token = result["access_token"]
                    st.session_state.user = result["user"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    with tab_register:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_user")
            new_name = st.text_input("Nama Lengkap", key="reg_name")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            facility_id = st.text_input("Facility ID", key="reg_facility")
            role = st.selectbox("Role", ["operator", "viewer"], key="reg_role")
            reg_submitted = st.form_submit_button("Register")

            if reg_submitted:
                try:
                    result = register(
                        username=new_username,
                        name=new_name,
                        password=new_password,
                        email=new_email,
                        facility_id=facility_id,
                        role=role,
                    )
                    st.success(result.get("message", "Registration successful!"))
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

else:
    user = get_current_user()

    with st.sidebar:
        st.write(f"**{user.get('username', 'User')}** ({user.get('role', 'unknown')})")
        if st.button("Logout"):
            logout()
            st.rerun()

    st.title("CarbonatiX ERP")
    st.write("Welcome to the CarbonatiX ERP Dashboard. Use the sidebar to navigate.")
    st.info("Navigate using the pages in the sidebar: Nodes, Documents, Scans, Models.")
