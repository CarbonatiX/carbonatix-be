from ..schemas import CompanyResponse, CompanyDetail, CompanyUpdate
from ..models import find_company_by_id, update_company


def get_company(db, company_id: str) -> CompanyResponse:
    company = find_company_by_id(db, company_id)
    if not company:
        raise ValueError("Company not found")
    return CompanyResponse(
        company=CompanyDetail(
            id=company["id"],
            name=company["name"],
            technology=company["technology"],
            period_cap_tco2e=company["period_cap_tco2e"],
            site_spec=company["site_spec"],
        )
    )


def update_company_profile(db, company_id: str, req: CompanyUpdate) -> CompanyResponse:
    updates = req.model_dump(exclude_none=True)
    if not updates:
        raise ValueError("No fields to update")
    updated = update_company(db, company_id, updates)
    if not updated:
        raise ValueError("Company not found")
    return get_company(db, company_id)
