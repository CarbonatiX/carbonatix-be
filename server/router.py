import gridfs
from deps import get_current_user, get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from schemas import (
    AuthResponse,
    CompanyResponse,
    CompanyUpdate,
    DocumentExtractionResponse,
    EmissionRequest,
    EmissionResponse,
    ForecastsResponse,
    LoginRequest,
    RegisterRequest,
    RunRequest,
    RunResponse,
    TwinGapsResponse,
    TwinModelResponse,
    TwinNode,
    TwinNodesResponse,
    TwinNodesUpdate,
)
from services import (
    auth_service,
    company_service,
    document_service,
    emission_service,
    forecast_service,
    recommendation_service,
    run_service,
    twin_service,
)

router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────


@router.get("/health")
def health():
    return {"status": "healthy"}


# ── Auth ──────────────────────────────────────────────────────────────


@router.post("/auth/register", response_model=AuthResponse, status_code=201)
def register(req: RegisterRequest, db=Depends(get_db)):
    return auth_service.register(db, req)


@router.post("/auth/login", response_model=AuthResponse)
def login(req: LoginRequest, db=Depends(get_db)):
    return auth_service.login(db, req)


# ── Company ───────────────────────────────────────────────────────────


@router.get("/company", response_model=CompanyResponse)
def get_company(user=Depends(get_current_user), db=Depends(get_db)):
    return company_service.get_company(db, user["company_id"])


@router.put("/company", response_model=CompanyResponse)
def update_company(
    req: CompanyUpdate, user=Depends(get_current_user), db=Depends(get_db)
):
    return company_service.update_company_profile(db, user["company_id"], req)


# ── Twin ──────────────────────────────────────────────────────────────


@router.post("/twin/model", response_model=TwinModelResponse, status_code=201)
async def upload_twin_model(
    file: UploadFile = File(...), user=Depends(get_current_user), db=Depends(get_db)
):
    file_data = await file.read()

    fs = gridfs.GridFS(db)
    gridfs_id = fs.put(
        file_data,
        filename=file.filename or "uploaded_model",
        content_type=file.content_type or "application/octet-stream",
    )

    parts = [{"mesh_ref": "mesh_default", "label": file.filename or "uploaded_model"}]
    return twin_service.upload_model(
        db,
        user["company_id"],
        file_id=file.filename or "unknown",
        gridfs_id=str(gridfs_id),
        parts=parts,
    )


@router.get("/twin/nodes", response_model=TwinNodesResponse)
def get_twin_nodes(user=Depends(get_current_user), db=Depends(get_db)):
    return twin_service.get_nodes(db, user["company_id"])


@router.post("/twin/nodes", response_model=TwinNodesResponse, status_code=201)
def add_twin_node(
    req: TwinNode, user=Depends(get_current_user), db=Depends(get_db)
):
    return twin_service.add_node(db, user["company_id"], req)


@router.put("/twin/nodes", response_model=TwinNodesResponse)
def update_twin_nodes(
    req: TwinNodesUpdate, user=Depends(get_current_user), db=Depends(get_db)
):
    return twin_service.update_nodes(db, user["company_id"], req)


@router.delete("/twin/nodes/{node_id}", response_model=TwinNodesResponse)
def delete_twin_node(
    node_id: str, user=Depends(get_current_user), db=Depends(get_db)
):
    return twin_service.remove_node(db, user["company_id"], node_id)


@router.get("/twin/gaps", response_model=TwinGapsResponse)
def get_twin_gaps(user=Depends(get_current_user), db=Depends(get_db)):
    return twin_service.get_gaps(db, user["company_id"])


# ── Documents ─────────────────────────────────────────────────────────


@router.post("/documents", response_model=DocumentExtractionResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    profile: str = Form(...),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    return await document_service.extract_document(
        db, user["company_id"], file, profile
    )


# ── Emissions ─────────────────────────────────────────────────────────


@router.post("/emissions", response_model=EmissionResponse)
def calculate_emissions(req: EmissionRequest, user=Depends(get_current_user)):
    return emission_service.calculate_emissions(req)


# ── Runs ──────────────────────────────────────────────────────────────


@router.post("/runs", response_model=RunResponse, status_code=201)
def commit_run(req: RunRequest, user=Depends(get_current_user), db=Depends(get_db)):
    return run_service.commit_run(db, user["company_id"], user["user_id"], req)


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    return run_service.get_run(db, user["company_id"], run_id)


# ── Forecasts ─────────────────────────────────────────────────────────


@router.get("/forecasts", response_model=ForecastsResponse)
def get_forecasts(
    horizon_days: int = Query(ge=7, le=30, default=14),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    return forecast_service.get_forecasts(db, horizon_days)


# ── Recommendations (SSE) ────────────────────────────────────────────


@router.get("/runs/{run_id}/recommendation")
async def get_recommendation(
    run_id: str, user=Depends(get_current_user), db=Depends(get_db)
):
    # Load before StreamingResponse so a missing run can still be a 404.
    try:
        run_resp = run_service.get_run(db, user["company_id"], run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StreamingResponse(
        recommendation_service.stream_recommendation(run_resp.run),
        media_type="text/event-stream",
    )
