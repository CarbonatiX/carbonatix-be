"""Ensure every company has the five RFC-004 process bindings for the bundled demo GLB.

The FE form path never calls /twin/nodes. Without these nodes, get_gaps reports
all required process types as unbound and POST /runs returns 422.
"""

from server.models import create_twin_model, find_twin_by_company, upsert_twin_nodes

REQUIRED_PROCESS_TYPES: tuple[str, ...] = (
    "ORE_STOCKPILE",
    "ROTARY_DRYER",
    "ROTARY_KILN",
    "ELECTRIC_ARC_FURNACE",
    "CAPTIVE_POWER",
)

_BUNDLED_NODES: list[dict] = [
    {
        "node_id": "node_ore",
        "label": "Ore Stockpile",
        "mesh_ref": "mesh_default",
        "process_type": "ORE_STOCKPILE",
    },
    {
        "node_id": "node_dryer",
        "label": "Rotary Dryer",
        "mesh_ref": "mesh_default",
        "process_type": "ROTARY_DRYER",
    },
    {
        "node_id": "node_kiln",
        "label": "Rotary Kiln",
        "mesh_ref": "mesh_default",
        "process_type": "ROTARY_KILN",
    },
    {
        "node_id": "node_eaf",
        "label": "Electric Arc Furnace",
        "mesh_ref": "mesh_default",
        "process_type": "ELECTRIC_ARC_FURNACE",
    },
    {
        "node_id": "node_power",
        "label": "Captive Power",
        "mesh_ref": "mesh_default",
        "process_type": "CAPTIVE_POWER",
    },
]


def ensure_bundled_twin(db, company_id: str) -> None:
    """Create or complete the bundled twin so form-path commits are not blocked."""
    twin = find_twin_by_company(db, company_id)
    if twin is None:
        create_twin_model(
            db,
            company_id,
            file_id="bundled_demo.glb",
            gridfs_id="bundled",
            parts=[{"part_id": "mesh_default", "name": "Plant"}],
        )
        upsert_twin_nodes(db, company_id, list(_BUNDLED_NODES))
        return

    existing = {n.get("process_type") for n in twin.get("nodes", [])}
    missing = [n for n in _BUNDLED_NODES if n["process_type"] not in existing]
    if missing:
        upsert_twin_nodes(db, company_id, list(twin.get("nodes", [])) + missing)
