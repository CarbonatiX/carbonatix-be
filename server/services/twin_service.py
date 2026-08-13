from collections import Counter

from server.models import (
    add_twin_node,
    create_twin_model,
    find_twin_by_company,
    list_documents_by_company,
    remove_twin_node,
    upsert_twin_nodes,
)
from server.schemas import (
    AmbiguousField,
    OrphanField,
    TwinGapsResponse,
    TwinModelInner,
    TwinModelResponse,
    TwinNode,
    TwinNodesResponse,
    TwinNodesUpdate,
    TwinPart,
)
from server.services.bundled_twin import REQUIRED_PROCESS_TYPES


def upload_model(
    db, company_id: str, file_id: str, gridfs_id: str, parts: list[dict]
) -> TwinModelResponse:
    existing = find_twin_by_company(db, company_id)
    if existing:
        raise ValueError("Twin model already exists for this company")
    twin = create_twin_model(db, company_id, file_id, gridfs_id, parts)
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


def add_node(db, company_id: str, req: TwinNode) -> TwinNodesResponse:
    twin = find_twin_by_company(db, company_id)
    if not twin:
        raise ValueError("No twin model found")

    existing_nodes = twin.get("nodes", [])
    if any(n["node_id"] == req.node_id for n in existing_nodes):
        raise ValueError(f"Node with id '{req.node_id}' already exists")

    twin = add_twin_node(db, company_id, req.model_dump())
    return TwinNodesResponse(
        twin_model_id=twin["id"],
        nodes=[TwinNode(**n) for n in twin.get("nodes", [])],
    )


def remove_node(db, company_id: str, node_id: str) -> TwinNodesResponse:
    twin = find_twin_by_company(db, company_id)
    if not twin:
        raise ValueError("No twin model found")

    existing_nodes = twin.get("nodes", [])
    if not any(n["node_id"] == node_id for n in existing_nodes):
        raise ValueError(f"Node with id '{node_id}' not found")

    twin = remove_twin_node(db, company_id, node_id)
    return TwinNodesResponse(
        twin_model_id=twin["id"],
        nodes=[TwinNode(**n) for n in twin.get("nodes", [])],
    )


def get_gaps(db, company_id: str) -> TwinGapsResponse:
    docs = list_documents_by_company(db, company_id)

    doc_process_types = set()
    for doc in docs:
        candidates = doc.get("extraction", {}).get("candidates", [])
        for c in candidates:
            pt = c.get("owning_process_type")
            if pt:
                doc_process_types.add(pt)

    twin = find_twin_by_company(db, company_id)
    required = set(REQUIRED_PROCESS_TYPES)

    if not twin:
        orphan_fields = [
            OrphanField(
                field_name=c["field_name"],
                owning_process_type=c["owning_process_type"],
                document_id=doc["id"],
            )
            for doc in docs
            for c in doc.get("extraction", {}).get("candidates", [])
            if c.get("owning_process_type")
        ]
        # RFC-004: unbound = static catalog with no nodes, plus any doc-owned types.
        return TwinGapsResponse(
            unbound_required_process_types=sorted(required | doc_process_types),
            orphan_fields=orphan_fields,
            ambiguous_fields=[],
        )

    node_process_types = {n["process_type"] for n in twin.get("nodes", [])}
    unbound = (required - node_process_types) | (doc_process_types - node_process_types)

    orphan_fields = [
        OrphanField(
            field_name=c["field_name"],
            owning_process_type=c["owning_process_type"],
            document_id=doc["id"],
        )
        for doc in docs
        for c in doc.get("extraction", {}).get("candidates", [])
        if c.get("owning_process_type")
        and c["owning_process_type"] not in node_process_types
    ]

    pt_counts = Counter(n["process_type"] for n in twin.get("nodes", []))
    ambiguous_fields = [
        AmbiguousField(
            field_name=c["field_name"],
            owning_process_type=c["owning_process_type"],
            candidate_node_ids=[
                n["node_id"]
                for n in twin.get("nodes", [])
                if n["process_type"] == c["owning_process_type"]
            ],
        )
        for doc in docs
        for c in doc.get("extraction", {}).get("candidates", [])
        if c.get("owning_process_type")
        and pt_counts.get(c["owning_process_type"], 0) > 1
    ]

    return TwinGapsResponse(
        unbound_required_process_types=sorted(unbound),
        orphan_fields=orphan_fields,
        ambiguous_fields=ambiguous_fields,
    )
