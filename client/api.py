import httpx
import streamlit as st
from typing import Any

BASE_URL = "http://localhost:8000/api/v1"


def get_headers() -> dict[str, str]:
    token = st.session_state.get("token")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def login(username: str, password: str) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def register(username: str, name: str, password: str) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "name": name, "password": password},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def get_users(params: dict[str, Any] | None = None) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/api/v1/users/",
            headers=get_headers(),
            params=params or {},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def create_user(data: dict) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/api/v1/users/",
            headers=get_headers(),
            json=data,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def get_nodes(params: dict[str, Any] | None = None) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/api/v1/nodes/",
            headers=get_headers(),
            params=params or {},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def create_node(data: dict) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/api/v1/nodes/",
            headers=get_headers(),
            json=data,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def get_node_parameters(
    node_id: str, params: dict[str, Any] | None = None
) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/api/v1/nodes/{node_id}/parameters",
            headers=get_headers(),
            params=params or {},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def create_node_parameter(node_id: str, data: dict) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/api/v1/nodes/{node_id}/parameters",
            headers=get_headers(),
            json=data,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def get_documents(params: dict[str, Any] | None = None) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/api/v1/documents/",
            headers=get_headers(),
            params=params or {},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def upload_document(
    file: Any,
    document_type: str,
    facility_id: str,
    uploaded_by: str | None = None,
    tags: str | None = None,
) -> dict:
    with httpx.Client() as client:
        headers = get_headers()
        headers.pop("Content-Type", None)

        files = {"file": (getattr(file, "name", "file"), file)}
        params = {
            "document_type": document_type,
            "facility_id": facility_id,
        }
        if uploaded_by:
            params["uploaded_by"] = uploaded_by
        if tags:
            params["tags"] = tags

        resp = client.post(
            f"{BASE_URL}/api/v1/documents/",
            headers=headers,
            files=files,
            params=params,
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.json()


def get_scans(params: dict[str, Any] | None = None) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/api/v1/scans/",
            headers=get_headers(),
            params=params or {},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


def simulate(data: dict) -> dict:
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE_URL}/api/v1/models/simulate",
            headers=get_headers(),
            json=data,
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.json()
