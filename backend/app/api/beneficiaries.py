from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.models.models import User, BeneficiaryProfile, DistributionTransaction, FairPriceShop
from backend.app.schemas.schemas import (
    BeneficiaryMeResponse,
    BeneficiaryProfileResponse,
    TransactionResponse,
    EntitlementsResponse,
    EntitlementItem
)

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])

@router.get("/me", response_model=BeneficiaryMeResponse)
def get_beneficiary_me(
    current_user: User = Depends(require_roles(["BENEFICIARY", "ADMIN"])),
    db: Session = Depends(get_db)
):
    profile = db.query(BeneficiaryProfile).filter(BeneficiaryProfile.user_id == current_user.id).first()
    profile_resp = None
    if profile:
        shop = db.query(FairPriceShop).filter(FairPriceShop.id == profile.assigned_shop_id).first()
        profile_resp = BeneficiaryProfileResponse(
            id=profile.id,
            masked_beneficiary_identifier=profile.masked_beneficiary_identifier,
            state=profile.state,
            district=profile.district,
            ration_card_type=profile.ration_card_type,
            family_members=profile.family_members,
            assigned_shop_id=profile.assigned_shop_id,
            assigned_shop_name=shop.shop_name if shop else None,
            assigned_shop_identifier=shop.shop_identifier if shop else None
        )

    return BeneficiaryMeResponse(user=current_user, profile=profile_resp)

@router.get("/me/transactions", response_model=List[TransactionResponse])
def get_my_transactions(
    commodity: Optional[str] = None,
    reporting_period: Optional[str] = None,
    current_user: User = Depends(require_roles(["BENEFICIARY", "ADMIN"])),
    db: Session = Depends(get_db)
):
    profile = db.query(BeneficiaryProfile).filter(BeneficiaryProfile.user_id == current_user.id).first()
    masked_id = profile.masked_beneficiary_identifier if profile else None

    query = db.query(DistributionTransaction).join(FairPriceShop, DistributionTransaction.shop_id == FairPriceShop.id)
    if current_user.role == "BENEFICIARY":
        query = query.filter(
            (DistributionTransaction.beneficiary_id == current_user.id) |
            (DistributionTransaction.beneficiary_reference == masked_id)
        )
    if commodity:
        query = query.filter(DistributionTransaction.commodity.ilike(f"%{commodity}%"))
    if reporting_period:
        query = query.filter(DistributionTransaction.reporting_period == reporting_period)

    txs = query.order_by(DistributionTransaction.transaction_date.desc()).all()
    results = []
    for tx in txs:
        results.append(TransactionResponse(
            id=tx.id,
            beneficiary_reference=tx.beneficiary_reference,
            transaction_date=tx.transaction_date,
            reporting_period=tx.reporting_period,
            commodity=tx.commodity,
            recorded_quantity=tx.recorded_quantity,
            entitlement_quantity=tx.entitlement_quantity,
            unit=tx.unit,
            shop_id=tx.shop_id,
            shop_identifier=tx.shop.shop_identifier if tx.shop else "N/A",
            shop_name=tx.shop.shop_name if tx.shop else "N/A"
        ))
    return results

@router.get("/me/entitlements", response_model=EntitlementsResponse)
def get_my_entitlements(
    period: str = Query("2026-10", description="Reporting period (e.g. 2026-10)"),
    current_user: User = Depends(require_roles(["BENEFICIARY", "ADMIN"])),
    db: Session = Depends(get_db)
):
    profile = db.query(BeneficiaryProfile).filter(BeneficiaryProfile.user_id == current_user.id).first()
    family_members = profile.family_members if profile else 4
    card_type = profile.ration_card_type if profile else "PHH"

    # NFSA entitlement rules:
    # Priority Household (PHH): 5kg/person (Wheat 3kg, Rice 2kg)
    # Antyodaya Anna Yojana (AAY): 35kg/family (Wheat 20kg, Rice 15kg)
    if card_type == "AAY":
        standard_wheat = 20.0
        standard_rice = 15.0
    else:
        standard_wheat = family_members * 3.0
        standard_rice = family_members * 2.0

    # Query recorded transactions for the period
    txs = db.query(DistributionTransaction).filter(
        (DistributionTransaction.beneficiary_id == current_user.id) |
        (DistributionTransaction.beneficiary_reference == (profile.masked_beneficiary_identifier if profile else "")),
        DistributionTransaction.reporting_period == period
    ).all()

    wheat_tx = sum(t.recorded_quantity for t in txs if t.commodity.lower() == "wheat")
    rice_tx = sum(t.recorded_quantity for t in txs if t.commodity.lower() == "rice")

    items = []
    # Wheat
    wheat_var = round(wheat_tx - standard_wheat, 2)
    items.append(EntitlementItem(
        commodity="Wheat",
        entitlement_quantity=standard_wheat,
        recorded_quantity=wheat_tx,
        unit="kg",
        reporting_period=period,
        is_matched=abs(wheat_var) < 0.01,
        variance=wheat_var,
        status="MATCHED" if abs(wheat_var) < 0.01 else ("SHORTFALL" if wheat_var < 0 else "SURPLUS")
    ))

    # Rice
    rice_var = round(rice_tx - standard_rice, 2)
    items.append(EntitlementItem(
        commodity="Rice",
        entitlement_quantity=standard_rice,
        recorded_quantity=rice_tx,
        unit="kg",
        reporting_period=period,
        is_matched=abs(rice_var) < 0.01,
        variance=rice_var,
        status="MATCHED" if abs(rice_var) < 0.01 else ("SHORTFALL" if rice_var < 0 else "SURPLUS")
    ))

    return EntitlementsResponse(reporting_period=period, items=items)
