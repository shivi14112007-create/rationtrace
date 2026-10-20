from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import random

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.models.models import User, Complaint, InvestigationEvent, FairPriceShop, BeneficiaryProfile
from backend.app.schemas.schemas import (
    ComplaintCreateRequest,
    ComplaintResponse,
    InvestigationEventResponse,
    ComplaintEventCreateRequest,
    ComplaintStatusUpdateRequest
)

router = APIRouter(prefix="/complaints", tags=["Complaints"])

def generate_reference_number() -> str:
    year = datetime.now(timezone.utc).year
    rand_id = random.randint(1000, 9999)
    return f"RT-{year}-COMP-{rand_id}"

def format_complaint_response(c: Complaint, db: Session) -> ComplaintResponse:
    events_resp = []
    for ev in c.events:
        events_resp.append(InvestigationEventResponse(
            id=ev.id,
            event_type=ev.event_type,
            note=ev.note,
            actor_name=ev.actor.full_name if ev.actor else "System",
            actor_role=ev.actor.role if ev.actor else "SYSTEM",
            created_at=ev.created_at
        ))

    profile = db.query(BeneficiaryProfile).filter(BeneficiaryProfile.user_id == c.beneficiary_id).first()

    return ComplaintResponse(
        id=c.id,
        reference_number=c.reference_number,
        beneficiary_id=c.beneficiary_id,
        beneficiary_name=c.beneficiary.full_name if c.beneficiary else "Unknown",
        beneficiary_masked_id=profile.masked_beneficiary_identifier if profile else None,
        shop_id=c.related_shop_id,
        shop_identifier=c.shop.shop_identifier if c.shop else "N/A",
        shop_name=c.shop.shop_name if c.shop else "N/A",
        category=c.category,
        description=c.description,
        status=c.status,
        resolution_summary=c.resolution_summary,
        created_at=c.created_at,
        updated_at=c.updated_at,
        events=events_resp
    )

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
    req: ComplaintCreateRequest,
    current_user: User = Depends(require_roles(["BENEFICIARY", "ADMIN"])),
    db: Session = Depends(get_db)
):
    shop = db.query(FairPriceShop).filter(FairPriceShop.id == req.related_shop_id).first()
    if not shop:
        raise HTTPException(status_code=400, detail="Invalid shop ID provided")

    ref_num = generate_reference_number()
    # Check uniqueness
    while db.query(Complaint).filter(Complaint.reference_number == ref_num).first():
        ref_num = generate_reference_number()

    complaint = Complaint(
        reference_number=ref_num,
        beneficiary_id=current_user.id,
        related_shop_id=req.related_shop_id,
        related_transaction_id=req.related_transaction_id,
        category=req.category,
        description=req.description,
        status="SUBMITTED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Initial event
    initial_event = InvestigationEvent(
        complaint_id=complaint.id,
        actor_id=current_user.id,
        event_type="STATUS_CHANGE",
        note=f"Grievance lodged with reference {ref_num} under category '{req.category}'.",
        created_at=datetime.now(timezone.utc)
    )
    db.add(initial_event)
    db.commit()
    db.refresh(complaint)

    return format_complaint_response(complaint, db)

@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if current_user.role == "BENEFICIARY":
        query = query.filter(Complaint.beneficiary_id == current_user.id)
    elif current_user.role == "DEALER":
        from backend.app.api.dealer import get_dealer_shop
        shop = get_dealer_shop(current_user, db)
        query = query.filter(Complaint.related_shop_id == shop.id)

    if status_filter:
        query = query.filter(Complaint.status == status_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return [format_complaint_response(c, db) for c in complaints]

@router.get("/{id}", response_model=ComplaintResponse)
def get_complaint(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Access control
    if current_user.role == "BENEFICIARY" and complaint.beneficiary_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this complaint")

    return format_complaint_response(complaint, db)

@router.post("/{id}/events", response_model=ComplaintResponse)
def add_complaint_event(
    id: int,
    req: ComplaintEventCreateRequest,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN", "BENEFICIARY"])),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role == "BENEFICIARY" and complaint.beneficiary_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this complaint")

    event = InvestigationEvent(
        complaint_id=complaint.id,
        actor_id=current_user.id,
        event_type=req.event_type,
        note=req.note,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    complaint.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(complaint)

    return format_complaint_response(complaint, db)

@router.patch("/{id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    id: int,
    req: ComplaintStatusUpdateRequest,
    current_user: User = Depends(require_roles(["OFFICIAL", "ADMIN"])),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = complaint.status
    complaint.status = req.status
    complaint.updated_at = datetime.now(timezone.utc)

    if req.resolution_summary:
        complaint.resolution_summary = req.resolution_summary

    note_text = req.note or f"Official status updated from {old_status} to {req.status}."
    if req.resolution_summary:
        note_text += f" Resolution Summary: {req.resolution_summary}"

    event = InvestigationEvent(
        complaint_id=complaint.id,
        actor_id=current_user.id,
        event_type="STATUS_CHANGE",
        note=note_text,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(complaint)

    return format_complaint_response(complaint, db)
