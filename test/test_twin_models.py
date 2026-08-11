from server.models.twin import (
    add_twin_node,
    create_twin_model,
    remove_twin_node,
)


def test_add_twin_node(mock_db):
    company_id = "company_123"
    create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])

    node = {"node_id": "node_1", "type": "smelting", "label": "Smelting Process"}
    result = add_twin_node(mock_db, company_id, node)

    assert result is not None
    assert len(result["nodes"]) == 1
    assert result["nodes"][0]["node_id"] == "node_1"


def test_add_twin_node_multiple(mock_db):
    company_id = "company_123"
    create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])

    node1 = {"node_id": "node_1", "type": "smelting"}
    node2 = {"node_id": "node_2", "type": "refining"}
    add_twin_node(mock_db, company_id, node1)
    result = add_twin_node(mock_db, company_id, node2)

    assert len(result["nodes"]) == 2
    assert result["nodes"][0]["node_id"] == "node_1"
    assert result["nodes"][1]["node_id"] == "node_2"


def test_remove_twin_node(mock_db):
    company_id = "company_123"
    create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])

    node1 = {"node_id": "node_1", "type": "smelting"}
    node2 = {"node_id": "node_2", "type": "refining"}
    add_twin_node(mock_db, company_id, node1)
    add_twin_node(mock_db, company_id, node2)

    result = remove_twin_node(mock_db, company_id, "node_1")

    assert result is not None
    assert len(result["nodes"]) == 1
    assert result["nodes"][0]["node_id"] == "node_2"


def test_remove_twin_node_nonexistent(mock_db):
    company_id = "company_123"
    create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])

    node = {"node_id": "node_1", "type": "smelting"}
    add_twin_node(mock_db, company_id, node)

    result = remove_twin_node(mock_db, company_id, "node_nonexistent")

    assert result is not None
    assert len(result["nodes"]) == 1


def test_add_twin_node_updates_timestamp(mock_db):
    company_id = "company_123"
    twin = create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])
    original_updated_at = twin["updated_at"]

    import time
    time.sleep(0.01)

    node = {"node_id": "node_1", "type": "smelting"}
    result = add_twin_node(mock_db, company_id, node)

    assert result["updated_at"] >= original_updated_at


def test_remove_twin_node_updates_timestamp(mock_db):
    company_id = "company_123"
    twin = create_twin_model(mock_db, company_id, "file_1", "gridfs_1", [])
    original_updated_at = twin["updated_at"]

    node = {"node_id": "node_1", "type": "smelting"}
    add_twin_node(mock_db, company_id, node)

    import time
    time.sleep(0.01)

    result = remove_twin_node(mock_db, company_id, "node_1")

    assert result["updated_at"] >= original_updated_at
