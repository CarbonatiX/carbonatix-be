from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from server.models.twin import create_twin_model
from server.schemas import TwinNode
from server.services import twin_service


def _seed_twin(mock_db, company_id="company_123"):
    return create_twin_model(mock_db, company_id, "plant.glb", "gridfs_abc", [])


def _node(node_id="node_1", process_type="ORE_STOCKPILE"):
    return {
        "node_id": node_id,
        "label": f"Label {node_id}",
        "mesh_ref": f"mesh_{node_id}",
        "process_type": process_type,
    }


def test_add_node_service(mock_db):
    _seed_twin(mock_db)
    req = TwinNode(**_node())

    result = twin_service.add_node(mock_db, "company_123", req)

    assert result.twin_model_id.startswith("twin_")
    assert len(result.nodes) == 1
    assert result.nodes[0].node_id == "node_1"
    assert result.nodes[0].process_type == "ORE_STOCKPILE"


def test_add_node_duplicate_raises(mock_db):
    _seed_twin(mock_db)
    req = TwinNode(**_node())
    twin_service.add_node(mock_db, "company_123", req)

    with pytest.raises(ValueError, match="already exists"):
        twin_service.add_node(mock_db, "company_123", req)


def test_remove_node_service(mock_db):
    _seed_twin(mock_db)
    twin_service.add_node(mock_db, "company_123", TwinNode(**_node("node_1")))
    twin_service.add_node(mock_db, "company_123", TwinNode(**_node("node_2")))

    result = twin_service.remove_node(mock_db, "company_123", "node_1")

    assert len(result.nodes) == 1
    assert result.nodes[0].node_id == "node_2"


def test_remove_node_missing_raises(mock_db):
    _seed_twin(mock_db)

    with pytest.raises(ValueError, match="not found"):
        twin_service.remove_node(mock_db, "company_123", "missing")


def test_get_gaps_unbound_and_orphan(mock_db):
    _seed_twin(mock_db)
    twin_service.add_node(
        mock_db, "company_123", TwinNode(**_node("node_1", "ORE_STOCKPILE"))
    )
    mock_db.documents.insert_one(
        {
            "_id": "doc_1",
            "company_id": "company_123",
            "extraction": {
                "status": "processed",
                "candidates": [
                    {
                        "field_name": "dryer_thermal_efficiency",
                        "owning_process_type": "ROTARY_DRYER",
                        "value": 0.8,
                        "confidence": 0.9,
                    }
                ],
            },
        }
    )

    gaps = twin_service.get_gaps(mock_db, "company_123")

    assert "ROTARY_DRYER" in gaps.unbound_required_process_types
    assert "ELECTRIC_ARC_FURNACE" in gaps.unbound_required_process_types
    assert "ORE_STOCKPILE" not in gaps.unbound_required_process_types
    assert len(gaps.orphan_fields) == 1
    assert gaps.orphan_fields[0].field_name == "dryer_thermal_efficiency"
    assert gaps.orphan_fields[0].document_id == "doc_1"
    assert gaps.ambiguous_fields == []


def test_get_gaps_ambiguous(mock_db):
    _seed_twin(mock_db)
    twin_service.add_node(
        mock_db, "company_123", TwinNode(**_node("node_k1", "ROTARY_KILN"))
    )
    twin_service.add_node(
        mock_db, "company_123", TwinNode(**_node("node_k2", "ROTARY_KILN"))
    )
    mock_db.documents.insert_one(
        {
            "_id": "doc_1",
            "company_id": "company_123",
            "extraction": {
                "status": "processed",
                "candidates": [
                    {
                        "field_name": "reductant_biocoke_pct",
                        "owning_process_type": "ROTARY_KILN",
                        "value": 0.3,
                        "confidence": 0.9,
                    }
                ],
            },
        }
    )

    gaps = twin_service.get_gaps(mock_db, "company_123")

    assert "ROTARY_KILN" not in gaps.unbound_required_process_types
    assert gaps.orphan_fields == []
    assert len(gaps.ambiguous_fields) == 1
    assert set(gaps.ambiguous_fields[0].candidate_node_ids) == {"node_k1", "node_k2"}


def test_post_twin_nodes(client, auth_headers, mock_db):
    # Register seeds a bundled twin; add an extra node onto it.
    response = client.post(
        "/twin/nodes",
        headers=auth_headers,
        json=_node("node_ore_extra", "ORE_STOCKPILE"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["twin_model_id"].startswith("twin_")
    assert any(n["node_id"] == "node_ore_extra" for n in body["nodes"])


def test_delete_twin_nodes(client, auth_headers, mock_db):
    client.post(
        "/twin/nodes",
        headers=auth_headers,
        json=_node("node_temp", "EAF"),
    )

    response = client.delete("/twin/nodes/node_temp", headers=auth_headers)

    assert response.status_code == 200
    assert all(n["node_id"] != "node_temp" for n in response.json()["nodes"])


def test_upload_twin_model_persists_to_gridfs(client, auth_headers, mock_db, monkeypatch):
    from server.models.user import find_user_by_email

    user = find_user_by_email(mock_db, "user@example.com")
    # Register already seeds a bundled twin; clear it so upload can create one.
    mock_db.twin_models.delete_many({"company_id": user["company_id"]})

    fake_oid = ObjectId()
    fake_fs = MagicMock()
    fake_fs.put.return_value = fake_oid
    monkeypatch.setattr("router.gridfs.GridFS", lambda db: fake_fs)

    response = client.post(
        "/twin/model",
        headers=auth_headers,
        files={"file": ("plant.glb", b"glb-bytes-here", "model/gltf-binary")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["twin_model"]["file_id"] == "plant.glb"
    assert body["twin_model"]["id"].startswith("twin_")
    fake_fs.put.assert_called_once()
    assert fake_fs.put.call_args.args[0] == b"glb-bytes-here"

    twin = mock_db.twin_models.find_one({"company_id": user["company_id"]})
    assert twin["gridfs_id"] == str(fake_oid)


def test_commit_run_blocked_by_gaps(
    client, auth_headers, mock_db, sample_emission_request
):
    from server.models.user import find_user_by_email

    user = find_user_by_email(mock_db, "user@example.com")
    # Document field owned by a process type that is not on the twin catalog.
    mock_db.documents.insert_one(
        {
            "_id": "doc_gap",
            "company_id": user["company_id"],
            "extraction": {
                "status": "processed",
                "candidates": [
                    {
                        "field_name": "energy",
                        "owning_process_type": "UNKNOWN_UNIT",
                        "value": 100,
                        "confidence": 0.9,
                    }
                ],
            },
        }
    )

    response = client.post(
        "/runs",
        headers=auth_headers,
        json={"input_snapshot": sample_emission_request},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "UNKNOWN_UNIT" in detail["unbound_required_process_types"]
    assert detail["orphan_fields"][0]["field_name"] == "energy"


def test_commit_run_succeeds_without_gaps(
    client, auth_headers, mock_db, sample_emission_request
):
    # Register seeds bundled twin nodes — form path should commit cleanly.
    response = client.post(
        "/runs",
        headers=auth_headers,
        json={"input_snapshot": sample_emission_request},
    )

    assert response.status_code == 201
    assert "run" in response.json()
    assert response.json()["run"]["forecast_snapshot"]["carbon"]["limit_price_idr"] == 59102.0
    assert response.json()["run"]["forecast_snapshot"]["carbon"]["tax_rate_idr"] == 30000.0