from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.models.models import FairPriceShop, BeneficiaryProfile, StockRecord, Discrepancy, Complaint
from backend.app.schemas.schemas import (
    OverviewStatsResponse,
    StateAnalyticsResponse,
    TrendResponse,
    CommodityBreakdownResponse
)

router = APIRouter(prefix="/analytics", tags=["Public Analytics"])

@router.get("/overview", response_model=OverviewStatsResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    total_shops = db.query(FairPriceShop).count()
    total_beneficiaries = db.query(BeneficiaryProfile).count()
    total_records = db.query(StockRecord).count()

    total_received_kg = db.query(func.sum(StockRecord.received_quantity)).scalar() or 0.0
    total_distributed_kg = db.query(func.sum(StockRecord.distributed_quantity)).scalar() or 0.0

    open_discrepancies = db.query(Discrepancy).filter(Discrepancy.status != "RESOLVED").count()
    open_complaints = db.query(Complaint).filter(Complaint.status.in_(["SUBMITTED", "UNDER_REVIEW", "INVESTIGATION"])).count()

    # Reconciliation rate: (1 - (discrepancies / total_records)) * 100
    recon_rate = round(max(0.0, (1.0 - (open_discrepancies / max(1, total_records))) * 100), 1)

    return OverviewStatsResponse(
        total_shops=total_shops,
        total_beneficiaries=total_beneficiaries,
        total_records_ingested=total_records,
        total_allocated_mt=round(total_received_kg / 1000.0, 2),
        total_distributed_mt=round(total_distributed_kg / 1000.0, 2),
        reconciliation_rate_pct=recon_rate,
        open_discrepancies_count=open_discrepancies,
        open_complaints_count=open_complaints
    )

@router.get("/states", response_model=List[StateAnalyticsResponse])
def get_state_analytics(db: Session = Depends(get_db)):
    # Group by state
    states_query = db.query(FairPriceShop.state).distinct().all()
    results = []

    for (state_name,) in states_query:
        shops_in_state = db.query(FairPriceShop.id).filter(FairPriceShop.state == state_name).all()
        shop_ids = [s[0] for s in shops_in_state]

        allocated = db.query(func.sum(StockRecord.received_quantity)).filter(StockRecord.shop_id.in_(shop_ids)).scalar() or 0.0
        distributed = db.query(func.sum(StockRecord.distributed_quantity)).filter(StockRecord.shop_id.in_(shop_ids)).scalar() or 0.0
        discrepancies = db.query(Discrepancy).filter(Discrepancy.related_shop_id.in_(shop_ids), Discrepancy.status != "RESOLVED").count()
        total_records = db.query(StockRecord).filter(StockRecord.shop_id.in_(shop_ids)).count()

        compliance = round(max(0.0, (1.0 - (discrepancies / max(1, total_records))) * 100), 1)

        results.append(StateAnalyticsResponse(
            state=state_name,
            allocated_quantity=round(allocated, 2),
            distributed_quantity=round(distributed, 2),
            shops_count=len(shop_ids),
            discrepancy_count=discrepancies,
            compliance_rate_pct=compliance
        ))

    return results

@router.get("/trends", response_model=List[TrendResponse])
def get_monthly_trends(db: Session = Depends(get_db)):
    periods = db.query(StockRecord.reporting_period).distinct().order_by(StockRecord.reporting_period.asc()).all()
    results = []

    for (period,) in periods:
        allocated = db.query(func.sum(StockRecord.received_quantity)).filter(StockRecord.reporting_period == period).scalar() or 0.0
        distributed = db.query(func.sum(StockRecord.distributed_quantity)).filter(StockRecord.reporting_period == period).scalar() or 0.0
        discrepancies = db.query(Discrepancy).filter(Discrepancy.reporting_period == period).count()

        results.append(TrendResponse(
            period=period,
            allocated=round(allocated, 2),
            distributed=round(distributed, 2),
            discrepancy_count=discrepancies
        ))

    return results

@router.get("/commodities", response_model=List[CommodityBreakdownResponse])
def get_commodity_breakdown(db: Session = Depends(get_db)):
    commodities = db.query(StockRecord.commodity).distinct().all()
    results = []

    for (comm,) in commodities:
        allocated = db.query(func.sum(StockRecord.received_quantity)).filter(StockRecord.commodity == comm).scalar() or 0.0
        distributed = db.query(func.sum(StockRecord.distributed_quantity)).filter(StockRecord.commodity == comm).scalar() or 0.0
        variance = round(((distributed - allocated) / max(1.0, allocated)) * 100, 2)

        results.append(CommodityBreakdownResponse(
            commodity=comm,
            allocated=round(allocated, 2),
            distributed=round(distributed, 2),
            unit="kg",
            variance_pct=variance
        ))

    return results
