from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    username = Column(String(60), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)  # BENEFICIARY, DEALER, OFFICIAL, ADMIN
    preferred_language = Column(String(10), default="en")
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)

    beneficiary_profile = relationship("BeneficiaryProfile", back_populates="user", uselist=False)
    dealer_shop = relationship("FairPriceShop", back_populates="dealer", uselist=False)
    complaints = relationship("Complaint", back_populates="beneficiary")
    investigation_events = relationship("InvestigationEvent", back_populates="actor")


class FairPriceShop(Base):
    __tablename__ = "fair_price_shops"

    id = Column(Integer, primary_key=True, index=True)
    shop_identifier = Column(String(50), unique=True, index=True, nullable=False)
    shop_name = Column(String(150), nullable=False)
    dealer_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    state = Column(String(80), nullable=False, index=True)
    district = Column(String(80), nullable=False, index=True)
    address = Column(String(255), nullable=True)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)

    dealer = relationship("User", back_populates="dealer_shop")
    stock_records = relationship("StockRecord", back_populates="shop")
    transactions = relationship("DistributionTransaction", back_populates="shop")
    discrepancies = relationship("Discrepancy", back_populates="shop")
    complaints = relationship("Complaint", back_populates="shop")
    beneficiaries = relationship("BeneficiaryProfile", back_populates="assigned_shop")


class BeneficiaryProfile(Base):
    __tablename__ = "beneficiary_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    masked_beneficiary_identifier = Column(String(50), unique=True, index=True, nullable=False)
    state = Column(String(80), nullable=False)
    district = Column(String(80), nullable=False)
    ration_card_type = Column(String(30), default="PHH")  # PHH, AAY
    family_members = Column(Integer, default=4)
    assigned_shop_id = Column(Integer, ForeignKey("fair_price_shops.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="beneficiary_profile")
    assigned_shop = relationship("FairPriceShop", back_populates="beneficiaries")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    source_url = Column(String(255), nullable=False)
    jurisdiction = Column(String(80), nullable=False)
    source_type = Column(String(30), default="PORTAL")  # PORTAL, API, DEMO_FEED
    is_approved = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, default=utc_now)

    extraction_jobs = relationship("ExtractionJob", back_populates="source")
    source_records = relationship("SourceRecord", back_populates="source")


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    job_status = Column(String(30), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    records_extracted = Column(Integer, default=0)
    records_validated = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    mode = Column(String(20), default="DEMO")  # LIVE, DEMO

    source = relationship("DataSource", back_populates="extraction_jobs")
    records = relationship("SourceRecord", back_populates="extraction_job")


class SourceRecord(Base):
    __tablename__ = "source_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    extraction_job_id = Column(Integer, ForeignKey("extraction_jobs.id"), nullable=True)
    region = Column(String(80), nullable=False)
    commodity = Column(String(50), nullable=False)
    metric_name = Column(String(80), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    reporting_period = Column(String(30), nullable=False)
    evidence_reference = Column(String(255), nullable=True)
    extracted_at = Column(DateTime, default=utc_now)
    record_hash = Column(String(64), nullable=True)
    validation_status = Column(String(30), default="VALID")

    source = relationship("DataSource", back_populates="source_records")
    extraction_job = relationship("ExtractionJob", back_populates="records")


class StockRecord(Base):
    __tablename__ = "stock_records"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("fair_price_shops.id"), nullable=False)
    commodity = Column(String(50), nullable=False)
    reporting_period = Column(String(30), nullable=False, index=True)  # e.g. "2026-09"
    opening_stock = Column(Float, nullable=False, default=0.0)
    received_quantity = Column(Float, nullable=False, default=0.0)
    distributed_quantity = Column(Float, nullable=False, default=0.0)
    recorded_closing_stock = Column(Float, nullable=False, default=0.0)
    documented_adjustments = Column(Float, default=0.0)
    source_record_id = Column(Integer, ForeignKey("source_records.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    shop = relationship("FairPriceShop", back_populates="stock_records")
    discrepancies = relationship("Discrepancy", back_populates="stock_record")


class DistributionTransaction(Base):
    __tablename__ = "distribution_transactions"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_reference = Column(String(50), nullable=False, index=True)
    beneficiary_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shop_id = Column(Integer, ForeignKey("fair_price_shops.id"), nullable=False)
    transaction_date = Column(DateTime, default=utc_now)
    reporting_period = Column(String(30), nullable=False)
    commodity = Column(String(50), nullable=False)
    recorded_quantity = Column(Float, nullable=False)
    entitlement_quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    created_at = Column(DateTime, default=utc_now)

    shop = relationship("FairPriceShop", back_populates="transactions")
    complaints = relationship("Complaint", back_populates="related_transaction")


class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # STOCK_RECONCILIATION, NEGATIVE_STOCK, TRANSACTION_MISMATCH
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="OPEN")  # OPEN, UNDER_REVIEW, RESOLVED, CLOSED
    related_shop_id = Column(Integer, ForeignKey("fair_price_shops.id"), nullable=False)
    related_stock_record_id = Column(Integer, ForeignKey("stock_records.id"), nullable=True)
    related_transaction_id = Column(Integer, ForeignKey("distribution_transactions.id"), nullable=True)
    commodity = Column(String(50), nullable=False)
    reporting_period = Column(String(30), nullable=False)
    expected_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=False)
    difference = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    rule_triggered = Column(String(50), nullable=False)  # RULE_A_STOCK_RECONCILIATION, RULE_B_NEGATIVE_STOCK
    calculation_details = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=False)
    dealer_explanation = Column(Text, nullable=True)
    investigation_outcome = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    reviewed_at = Column(DateTime, nullable=True)

    shop = relationship("FairPriceShop", back_populates="discrepancies")
    stock_record = relationship("StockRecord", back_populates="discrepancies")
    events = relationship("InvestigationEvent", back_populates="discrepancy")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String(50), unique=True, index=True, nullable=False)
    beneficiary_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    related_shop_id = Column(Integer, ForeignKey("fair_price_shops.id"), nullable=False)
    related_transaction_id = Column(Integer, ForeignKey("distribution_transactions.id"), nullable=True)
    category = Column(String(50), nullable=False)  # UNDER_DISTRIBUTION, NON_RECEIPT, QUALITY_ISSUE, OVERCHARGING
    description = Column(Text, nullable=False)
    status = Column(String(40), default="SUBMITTED")  # SUBMITTED, UNDER_REVIEW, INFORMATION_REQUESTED, INVESTIGATION, RESOLVED, CLOSED, REJECTED_WITH_REASON
    resolution_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    beneficiary = relationship("User", back_populates="complaints")
    shop = relationship("FairPriceShop", back_populates="complaints")
    related_transaction = relationship("DistributionTransaction", back_populates="complaints")
    events = relationship("InvestigationEvent", back_populates="complaint", order_by="InvestigationEvent.created_at")


class InvestigationEvent(Base):
    __tablename__ = "investigation_events"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    discrepancy_id = Column(Integer, ForeignKey("discrepancies.id"), nullable=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(40), nullable=False)  # STATUS_CHANGE, NOTE_ADDED, INFO_REQUESTED, RESOLUTION_RECORDED, DEALER_RESPONSE
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    complaint = relationship("Complaint", back_populates="events")
    discrepancy = relationship("Discrepancy", back_populates="events")
    actor = relationship("User", back_populates="investigation_events")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(80), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    metadata_json = Column(Text, nullable=True)
