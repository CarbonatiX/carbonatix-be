import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import get_pending_users, approve_user

st.set_page_config(page_title="Approval - CarbonatiX ERP", page_icon=":white_check_mark:", layout="centered")

st.title("Persetujuan User")

# Check if user is logged in and has permission
token = st.session_state.get("token")
user = st.session_state.get("user")

if not token:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

if user.get("role") not in ["admin", "superadmin", "operator"]:
    st.error("Tidak ada akses. Hanya admin/operator yang bisa menyetujui user.")
    st.stop()

try:
    result = get_pending_users()
    pending_users = result.get("items", [])

    if not pending_users:
        st.info("Tidak ada user yang menunggu persetujuan")
    else:
        st.write(f"**{len(pending_users)} user menunggu persetujuan:**")

        for u in pending_users:
            with st.expander(f"{u['username']} - {u.get('name', '')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Username:** {u['username']}")
                    st.write(f"**Nama:** {u.get('name', '-')}")
                    st.write(f"**Email:** {u.get('email', '-')}")
                    st.write(f"**Facility:** {u.get('facility_id', '-')}")
                with col2:
                    st.write(f"**Dibuat:** {u.get('created_at', '-')}")

                col_approve, col_reject = st.columns(2)
                with col_approve:
                    if st.button("Setujui", key=f"approve_{u['_id']}", type="primary"):
                        try:
                            approve_user(u["_id"], True)
                            st.success(f"User {u['username']} disetujui!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {str(e)}")
                with col_reject:
                    if st.button("Tolak", key=f"reject_{u['_id']}"):
                        try:
                            approve_user(u["_id"], False)
                            st.warning(f"User {u['username']} ditolak!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {str(e)}")

except Exception as e:
    st.error(f"Gagal memuat data: {str(e)}")
