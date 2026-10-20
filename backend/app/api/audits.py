from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.models.models import User, Discrepancy, FairPriceShop, StockRecord, InvestigationEvent
from backend.app.schemas.schemas import (
    DiscrepancyResponse,
    AuditSummaryResponse,
    DiscrepancyReviewRequest,
    DiscrepancyResolveRequest
)
from backend.app.services.audit_service import run_full_database_audit

router = APIRouter(prefix="/audits", tags=["Audits"])

def format_discrepancy(d: Discrepancy) -> DiscrepancyResponse:
    return DiscrepancyResponse(
        id=d.id,
        category=d.category,
        severity=d.severity,
        status=d.status,
        shop_id=d.related_shop_id,
        shop_identifier=d.shop.shop_identifier if d.shop else "N/A",
        shop_name=d.shop.shop_name if d.shop else "N/A",
        state=d.shop.state if d.shop else "N/A",
        district=d.shop.district if d.shop else "N/A",
        commodity=d.commodity,
        reporting_period=d.reporting_period,
        expected_value=d.expected_value,
        observed_value=d.observed_value,
        difference=d.difference,
        unit=d.unit,
        rule_triggered=d.rule_triggered,
        calculation_details=d.calculation_details,
        reason=d.reason,
        evidence_summary=d.evidence_summary,
        dealer_explanation=d.dealer_explanation,
        investigation_outcome=d.investigation_outcome,
        created_at=d.created_at,
        reviewed_at=d.reviewed_at
    )

@router.get("/summary", response_model=AuditSummaryResponse)
def get_audit_summary(
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    total_stock_records = db.query(StockRecord).count()
    open_discrepancies = db.query(Discrepancy).filter(Discrepancy.status == "OPEN").count()
    under_review = db.query(Discrepancy).filter(Discrepancy.status == "UNDER_REVIEW").count()
    resolved_cases = db.query(Discrepancy).filter(Discrepancy.status == "RESOLVED").count()
    critical_discrepancies = db.query(Discrepancy).filter(
        Discrepancy.severity == "CRITICAL",
        Discrepancy.status != "RESOLVED"
    ).count()

    rule_a_count = db.query(Discrepancy).filter(Discrepancy.rule_triggered == "RULE_A_STOCK_RECONCILIATION").count()
    rule_b_count = db.query(Discrepancy).filter(Discrepancy.rule_triggered == "RULE_B_NEGATIVE_STOCK").count()

    return AuditSummaryResponse(
        total_records=total_stock_records,
        validated_records=max(0, total_stock_records - open_discrepancies),
        pending_reviews=under_review,
        open_discrepancies=open_discrepancies,
        critical_discrepancies=critical_discrepancies,
        resolved_cases=resolved_cases,
        rule_a_count=rule_a_count,
        rule_b_count=rule_b_count
    )

@router.get("/discrepancies", response_model=List[DiscrepancyResponse])
def get_discrepancies(
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    state: Optional[str] = None,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    query = db.query(Discrepancy).join(FairPriceShop, Discrepancy.related_shop_id == FairPriceShop.id)

    if status_filter:
        query = query.filter(Discrepancy.status == status_filter)
    if severity:
        query = query.filter(Discrepancy.severity == severity)
    if category:
        query = query.filter(Discrepancy.category == category)
    if state:
        query = query.filter(FairPriceShop.state == state)

    discrepancies = query.order_by(Discrepancy.created_at.desc()).all()
    return [format_discrepancy(d) for d in discrepancies]

@router.get("/discrepancies/{id}", response_model=DiscrepancyResponse)
def get_discrepancy(
    id: int,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    discrepancy = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not discrepancy:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    return format_discrepancy(discrepancy)

@router.post("/run")
def trigger_audit_run(
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    count = run_full_database_audit(db)
    return {
        "message": f"Audit engine execution complete. {count} new discrepancies flagged.",
        "flagged_count": count
    }

@router.post("/discrepancies/{id}/review", response_model=DiscrepancyResponse)
def review_discrepancy(
    id: int,
    req: DiscrepancyReviewRequest,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    discrepancy = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not discrepancy:
        raise HTTPException(status_code=404, detail="Discrepancy not found")

    discrepancy.status = "UNDER_REVIEW"
    discrepancy.reviewed_at = datetime.now(timezone.utc)

    event = InvestigationEvent(
        discrepancy_id=discrepancy.id,
        actor_id=current_user.id,
        event_type="NOTE_ADDED",
        note=f"Official Review Note: {req.get_notes()}",
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(discrepancy)
    return format_discrepancy(discrepancy)

@router.post("/discrepancies/{id}/resolve", response_model=DiscrepancyResponse)
def resolve_discrepancy(
    id: int,
    req: DiscrepancyResolveRequest,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    discrepancy = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not discrepancy:
        raise HTTPException(status_code=404, detail="Discrepancy not found")

    notes_text = req.get_notes()
    discrepancy.status = "RESOLVED"
    discrepancy.investigation_outcome = f"[{req.outcome.upper()}] {notes_text}"
    discrepancy.reviewed_at = datetime.now(timezone.utc)

    event = InvestigationEvent(
        discrepancy_id=discrepancy.id,
        actor_id=current_user.id,
        event_type="RESOLUTION_RECORDED",
        note=f"Discrepancy closed with verified outcome: {req.outcome}. Notes: {notes_text}",
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(discrepancy)
    return format_discrepancy(discrepancy)
