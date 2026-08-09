from models import create_twin_model, find_twin_by_company, upsert_twin_nodes
from schemas import (
    TwinGapsResponse,
    TwinModelInner,
    TwinModelResponse,
    TwinNode,
    TwinNodesResponse,
    TwinNodesUpdate,
    TwinPart,
)


def upload_model(
    db, company_id: str, file_id: str, parts: list[dict]
) -> TwinModelResponse:
    existing = find_twin_by_company(db, company_id)
    if existing:
        raise ValueError("Twin model already exists for this company")
    twin = create_twin_model(db, company_id, file_id, parts)
    return TwinModelResponse(
        twin_model=TwinModelInner(
            id=twin["id"],
            file_id=twin["file_id"],
            parts=[TwinPart(**p) for p in parts],
        )
    )


def get_nodes(db, company_id: str) -> TwinNodesResponse:
    twin = find_twin_by_company(db, company_id)
    if not twin:
        raise ValueError("No twin model found")
    return TwinNodesResponse(
        twin_model_id=twin["id"],
        nodes=[TwinNode(**n) for n in twin.get("nodes", [])],
    )


def update_nodes(db, company_id: str, req: TwinNodesUpdate) -> TwinNodesResponse:
    twin = upsert_twin_nodes(db, company_id, [n.model_dump() for n in req.nodes])
    return TwinNodesResponse(
        twin_model_id=twin["id"],
        nodes=[TwinNode(**n) for n in twin.get("nodes", [])],
    )


def get_gaps(db, company_id: str) -> TwinGapsResponse:
    # Placeholder: returns empty gaps
    return TwinGapsResponse(
        unbound_required_process_types=[],
        orphan_fields=[],
        ambiguous_fields=[],
    )
