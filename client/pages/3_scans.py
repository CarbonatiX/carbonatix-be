import streamlit as st
import sys
import os
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import get_scans, get_headers, BASE_URL

st.set_page_config(page_title="3D Scans - CarbonatiX", page_icon=":camera:", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

st.title("3D Scan Management")

st.sidebar.header("Filters")
facility_filter = st.sidebar.text_input("Facility ID", key="scan_facility_filter")
node_filter = st.sidebar.text_input("Node ID", key="scan_node_filter")
page = st.sidebar.number_input("Page", min_value=1, value=1, key="scan_page")

params = {"page": page, "page_size": 20}
if facility_filter:
    params["facility_id"] = facility_filter
if node_filter:
    params["node_id"] = node_filter

try:
    scans_data = get_scans(params)
    scans = scans_data.get("items", [])
    total = scans_data.get("total", len(scans))
    st.write(f"**{total}** scans found")

    if scans:
        for scan in scans:
            with st.expander(f"{scan.get('scan_name', 'Unknown')} - {scan.get('file_format', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Scan ID:** {scan.get('scan_id', 'N/A')}")
                    st.write(f"**Facility:** {scan.get('facility_id', 'N/A')}")
                    st.write(f"**Node ID:** {scan.get('node_id', 'N/A')}")
                with col2:
                    st.write(f"**Format:** {scan.get('file_format', 'N/A')}")
                    st.write(f"**Size:** {scan.get('file_size', 'N/A')} bytes")
                    st.write(f"**Captured At:** {scan.get('captured_at', 'N/A')}")

                if st.button("Download", key=f"download_{scan.get('scan_id')}"):
                    try:
                        with httpx.Client() as client:
                            resp = client.get(
                                f"{BASE_URL}/api/v1/scans/{scan['scan_id']}/file",
                                headers=get_headers(),
                                timeout=60.0,
                            )
                            resp.raise_for_status()

                            st.download_button(
                                label="Download File",
                                data=resp.content,
                                file_name=f"{scan.get('scan_name', 'scan')}.{scan.get('file_format', 'glb')}",
                                mime="application/octet-stream",
                                key=f"dl_btn_{scan.get('scan_id')}",
                            )
                    except Exception as e:
                        st.error(f"Download failed: {str(e)}")
    else:
        st.info("No scans found.")
except Exception as e:
    st.error(f"Failed to load scans: {str(e)}")
