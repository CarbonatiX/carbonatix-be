import os
import sys
from pathlib import Path

import mongomock
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "carbonatix_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-ci-only-32b")

TEST_PASSWORD = "Secure1!"


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["carbonatix_test"]
    yield db
    client.close()


@pytest.fixture
def client(mock_db, monkeypatch):
    from server import main as main_module
    from deps import get_db

    app = main_module.app

    app.dependency_overrides[get_db] = lambda: mock_db
    monkeypatch.setattr(main_module, "get_db", lambda: mock_db)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 201
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_emission_request():
    return {
        "wet_ore_input_tons": 1000.0,
        "moisture_content_pct": 0.3,
        "nickel_grade_pct": 0.015,
        "reductant_biocoke_pct": 0.05,
        "sec_eaf_kwh_per_t_alloy": 3200.0,
        "power_mix_captive_coal": 0.8,
        "power_mix_hydro_grid": 0.2,
        "ef_captive_pltu": 0.98,
        "dryer_thermal_efficiency": 0.82,
    }
