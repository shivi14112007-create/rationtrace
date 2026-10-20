from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# ----------------- Auth Schemas -----------------

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    username: str
    email: str
    role: str
    preferred_language: str
    status: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----------------- Beneficiary Schemas -----------------

class BeneficiaryProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    masked_beneficiary_identifier: str
    state: str
    district: str
    ration_card_type: str
    family_members: int
    assigned_shop_id: Optional[int] = None
    assigned_shop_name: Optional[str] = None
    assigned_shop_identifier: Optional[str] = None

class BeneficiaryMeResponse(BaseModel):
    user: UserResponse
    profile: Optional[BeneficiaryProfileResponse] = None

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_reference: str
    transaction_date: datetime
    reporting_period: str
    commodity: str
    recorded_quantity: float
    entitlement_quantity: float
    unit: str
    shop_id: int
    shop_identifier: str
    shop_name: str

class EntitlementItem(BaseModel):
    commodity: str
    entitlement_quantity: float
    recorded_quantity: float
    unit: str
    reporting_period: str
    is_matched: bool
    variance: float
    status: str  # MATCHED, SHORTFALL, SURPLUS

class EntitlementsResponse(BaseModel):
    reporting_period: str
    items: List[EntitlementItem]


# ----------------- Dealer Schemas -----------------

class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shop_identifier: str
    shop_name: str
    state: str
    district: str
    address: Optional[str] = None
    status: str
    dealer_id: Optional[int] = None

class StockRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shop_id: int
    commodity: str
    reporting_period: str
    opening_stock: float
    received_quantity: float
    distributed_quantity: float
    recorded_closing_stock: float
    documented_adjustments: float
    expected_closing_stock: float
    difference: float
    has_discrepancy: bool
    created_at: datetime

class DealerExplanationRequest(BaseModel):
    explanation: str

class AuditQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    severity: str
    status: str
    commodity: str
    reporting_period: str
    expected_value: float
    observed_value: float
    difference: float
    unit: str
    rule_triggered: str
    calculation_details: str
    reason: str
    evidence_summary: str
    dealer_explanation: Optional[str] = None
    investigation_outcome: Optional[str] = None
    created_at: datetime


# ----------------- Audit & Discrepancy Schemas -----------------

class DiscrepancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    severity: str
    status: str
    shop_id: int
    shop_identifier: str
    shop_name: str
    state: str
    district: str
    commodity: str
    reporting_period: str
    expected_value: float
    observed_value: float
    difference: float
    unit: str
    rule_triggered: str
    calculation_details: str
    reason: str
    evidence_summary: str
    dealer_explanation: Optional[str] = None
    investigation_outcome: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

class AuditSummaryResponse(BaseModel):
    total_records: int
    validated_records: int
    pending_reviews: int
    open_discrepancies: int
    critical_discrepancies: int
    resolved_cases: int
    rule_a_count: int
    rule_b_count: int

class DiscrepancyReviewRequest(BaseModel):
    notes: Optional[str] = None
    note: Optional[str] = None

    def get_notes(self) -> str:
        return self.notes or self.note or ""

class DiscrepancyResolveRequest(BaseModel):
    outcome: str
    notes: Optional[str] = None
    note: Optional[str] = None

    def get_notes(self) -> str:
        return self.notes or self.note or ""



# ----------------- Complaint Schemas -----------------

class ComplaintCreateRequest(BaseModel):
    related_shop_id: int
    category: str
    description: str
    related_transaction_id: Optional[int] = None

class InvestigationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    note: str
    actor_name: str
    actor_role: str
    created_at: datetime

class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_number: str
    beneficiary_id: int
    beneficiary_name: str
    beneficiary_masked_id: Optional[str] = None
    shop_id: int
    shop_identifier: str
    shop_name: str
    category: str
    description: str
    status: str
    resolution_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    events: List[InvestigationEventResponse] = []

class ComplaintEventCreateRequest(BaseModel):
    event_type: str
    note: str

class ComplaintStatusUpdateRequest(BaseModel):
    status: str
    resolution_summary: Optional[str] = None
    note: Optional[str] = None


# ----------------- Analytics Schemas -----------------

class OverviewStatsResponse(BaseModel):
    total_shops: int
    total_beneficiaries: int
    total_records_ingested: int
    total_allocated_mt: float
    total_distributed_mt: float
    reconciliation_rate_pct: float
    open_discrepancies_count: int
    open_complaints_count: int

class StateAnalyticsResponse(BaseModel):
    state: str
    allocated_quantity: float
    distributed_quantity: float
    shops_count: int
    discrepancy_count: int
    compliance_rate_pct: float

class TrendResponse(BaseModel):
    period: str
    allocated: float
    distributed: float
    discrepancy_count: int

class CommodityBreakdownResponse(BaseModel):
    commodity: str
    allocated: float
    distributed: float
    unit: str
    variance_pct: float


# ----------------- TinyFish Intelligence Schemas -----------------

class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_url: str
    jurisdiction: str
    source_type: str
    is_approved: bool
    is_enabled: bool
    last_checked_at: Optional[datetime] = None

class DataSourceCreateRequest(BaseModel):
    name: str
    source_url: str
    jurisdiction: str
    source_type: str = "PORTAL"

class ExtractionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    job_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_extracted: int
    records_validated: int
    error_summary: Optional[str] = None
    mode: str

class ExtractionJobTriggerRequest(BaseModel):
    url: Optional[str] = None
    reporting_period: Optional[str] = None
    mode: str = "AUTO"  # AUTO, LIVE, DEMO

class SourceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    extraction_job_id: int
    region: str
    commodity: str
    metric_name: str
    quantity: float
    unit: str
    reporting_period: str
    evidence_reference: str
    extracted_at: datetime
    record_hash: str
    validation_status: str

class TinyFishStatusResponse(BaseModel):
    configured: bool
    mode: str
    base_url: str
    approved_sources_count: int
    total_jobs_count: int
    last_extraction_at: Optional[datetime] = None

