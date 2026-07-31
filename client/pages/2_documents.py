import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import get_documents, upload_document

st.set_page_config(page_title="Documents - CarbonatiX", page_icon=":page_facing_up:", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

st.title("Document Management")

st.sidebar.header("Filters")
facility_filter = st.sidebar.text_input("Facility ID", key="doc_facility_filter")
doc_type_filter = st.sidebar.selectbox(
    "Document Type",
    ["", "spe_grk", "srn_ppi", "lcam", "invoice", "permit", "other"],
    key="doc_type_filter",
)
status_filter = st.sidebar.selectbox("Status", ["", "pending", "processed", "failed"], key="doc_status_filter")
page = st.sidebar.number_input("Page", min_value=1, value=1, key="doc_page")

params = {"page": page, "page_size": 20}
if facility_filter:
    params["facility_id"] = facility_filter
if doc_type_filter:
    params["document_type"] = doc_type_filter
if status_filter:
    params["status"] = status_filter

try:
    docs_data = get_documents(params)
    docs = docs_data.get("items", [])
    total = docs_data.get("total", len(docs))
    st.write(f"**{total}** documents found")

    if docs:
        for doc in docs:
            with st.expander(f"{doc.get('filename', 'Unknown')} - {doc.get('document_type', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Document ID:** {doc.get('document_id', 'N/A')}")
                    st.write(f"**Facility:** {doc.get('facility_id', 'N/A')}")
                    st.write(f"**Type:** {doc.get('document_type', 'N/A')}")
                with col2:
                    st.write(f"**Status:** {doc.get('status', 'N/A')}")
                    st.write(f"**Uploaded At:** {doc.get('uploaded_at', 'N/A')}")
                    st.write(f"**Uploaded By:** {doc.get('uploaded_by', 'N/A')}")

                if doc.get("extracted_data"):
                    st.subheader("Extracted Data")
                    st.json(doc["extracted_data"])
    else:
        st.info("No documents found.")
except Exception as e:
    st.error(f"Failed to load documents: {str(e)}")

st.divider()

st.subheader("Upload Document")
with st.form("upload_doc_form"):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"])
    doc_type = st.selectbox(
        "Document Type",
        ["spe_grk", "srn_ppi", "lcam", "invoice", "permit", "other"],
        key="upload_doc_type",
    )
    facility_id = st.text_input("Facility ID", key="upload_facility_id")
    tags = st.text_input("Tags (comma separated)", key="upload_tags")

    if st.form_submit_button("Upload"):
        if uploaded_file and facility_id:
            try:
                result = upload_document(
                    file=uploaded_file,
                    document_type=doc_type,
                    facility_id=facility_id,
                    tags=tags if tags else None,
                )
                st.success(f"Document uploaded! ID: {result.get('document_id', 'N/A')}")
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {str(e)}")
        else:
            st.error("Please provide a file and facility ID.")
