from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.models.models import User, FairPriceShop, StockRecord, Discrepancy, InvestigationEvent
from backend.app.schemas.schemas import (
    ShopResponse,
    StockRecordResponse,
    AuditQueryResponse,
    DealerExplanationRequest
)

router = APIRouter(prefix="/dealer", tags=["Dealer"])

def get_dealer_shop(user: User, db: Session) -> FairPriceShop:
    shop = db.query(FairPriceShop).filter(FairPriceShop.dealer_user_id == user.id).first()
    if not shop:
        # Fall back to first shop in demo mode if dealer unassigned
        shop = db.query(FairPriceShop).first()
        if not shop:
            raise HTTPException(status_code=404, detail="No shop found assigned to this dealer")
    return shop

@router.get("/shop", response_model=ShopResponse)
def get_shop(
    current_user: User = Depends(require_roles(["DEALER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    shop = get_dealer_shop(current_user, db)
    return ShopResponse(
        id=shop.id,
        shop_identifier=shop.shop_identifier,
        shop_name=shop.shop_name,
        state=shop.state,
        district=shop.district,
        address=shop.address,
        status=shop.status,
        dealer_id=shop.dealer_user_id
    )

@router.get("/stock", response_model=List[StockRecordResponse])
def get_dealer_stock(
    current_user: User = Depends(require_roles(["DEALER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    shop = get_dealer_shop(current_user, db)
    records = db.query(StockRecord).filter(StockRecord.shop_id == shop.id).order_by(StockRecord.reporting_period.desc()).all()

    results = []
    for r in records:
        expected = round(r.opening_stock + r.received_quantity - r.distributed_quantity - (r.documented_adjustments or 0.0), 2)
        diff = round(r.recorded_closing_stock - expected, 2)
        has_disc = abs(diff) > 0.01 or expected < 0 or r.recorded_closing_stock < 0

        results.append(StockRecordResponse(
            id=r.id,
            shop_id=r.shop_id,
            commodity=r.commodity,
            reporting_period=r.reporting_period,
            opening_stock=r.opening_stock,
            received_quantity=r.received_quantity,
            distributed_quantity=r.distributed_quantity,
            recorded_closing_stock=r.recorded_closing_stock,
            documented_adjustments=r.documented_adjustments or 0.0,
            expected_closing_stock=expected,
            difference=diff,
            has_discrepancy=has_disc,
            created_at=r.created_at
        ))
    return results

@router.get("/audit-queries", response_model=List[AuditQueryResponse])
def get_dealer_audit_queries(
    current_user: User = Depends(require_roles(["DEALER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    shop = get_dealer_shop(current_user, db)
    discrepancies = db.query(Discrepancy).filter(Discrepancy.related_shop_id == shop.id).order_by(Discrepancy.created_at.desc()).all()
    return discrepancies

@router.post("/audit-queries/{id}/response")
def submit_dealer_explanation(
    id: int,
    req: DealerExplanationRequest,
    current_user: User = Depends(require_roles(["DEALER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    shop = get_dealer_shop(current_user, db)
    discrepancy = db.query(Discrepancy).filter(
        Discrepancy.id == id,
        Discrepancy.related_shop_id == shop.id
    ).first()
    if not discrepancy:
        raise HTTPException(status_code=404, detail="Audit discrepancy not found for this shop")

    discrepancy.dealer_explanation = req.explanation
    discrepancy.status = "UNDER_REVIEW"
    discrepancy.reviewed_at = datetime.now(timezone.utc)

    # Add investigation event
    event = InvestigationEvent(
        discrepancy_id=discrepancy.id,
        actor_id=current_user.id,
        event_type="DEALER_RESPONSE",
        note=f"Dealer submitted clarification: {req.explanation}",
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()

    return {
        "message": "Explanation submitted successfully. Case is under official review.",
        "discrepancy_id": discrepancy.id,
        "status": discrepancy.status
    }
