export type UserRole = 'BENEFICIARY' | 'DEALER' | 'OFFICIAL' | 'ADMIN';

export interface User {
  id: number;
  full_name: string;
  username: string;
  email: string;
  role: UserRole;
  preferred_language: string;
  status: string;
  created_at: string;
}

export interface BeneficiaryProfile {
  id: number;
  masked_beneficiary_identifier: string;
  state: string;
  district: string;
  ration_card_type: string;
  family_members: number;
  assigned_shop_id?: number | null;
  assigned_shop_name?: string | null;
  assigned_shop_identifier?: string | null;
}

export interface BeneficiaryMeResponse {
  user: User;
  profile?: BeneficiaryProfile | null;
}

export interface Transaction {
  id: number;
  beneficiary_reference: string;
  transaction_date: string;
  reporting_period: string;
  commodity: string;
  recorded_quantity: number;
  entitlement_quantity: number;
  unit: string;
  shop_id: number;
  shop_identifier: string;
  shop_name: string;
}

export interface EntitlementItem {
  commodity: string;
  entitlement_quantity: number;
  recorded_quantity: number;
  unit: string;
  reporting_period: string;
  is_matched: boolean;
  variance: number;
  status: 'MATCHED' | 'SHORTFALL' | 'SURPLUS' | string;
}

export interface EntitlementsResponse {
  reporting_period: string;
  items: EntitlementItem[];
}

export interface InvestigationEvent {
  id: number;
  event_type: string;
  note: string;
  actor_name: string;
  actor_role: string;
  created_at: string;
}

export interface Complaint {
  id: number;
  reference_number: string;
  beneficiary_id: number;
  beneficiary_name: string;
  beneficiary_masked_id?: string | null;
  shop_id: number;
  shop_identifier: string;
  shop_name: string;
  category: string;
  description: string;
  status: string;
  resolution_summary?: string | null;
  created_at: string;
  updated_at: string;
  events: InvestigationEvent[];
}

export interface Discrepancy {
  id: number;
  category: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  status: 'OPEN' | 'UNDER_REVIEW' | 'RESOLVED' | string;
  shop_id: number;
  shop_identifier: string;
  shop_name: string;
  state: string;
  district: string;
  commodity: string;
  reporting_period: string;
  expected_value: number;
  observed_value: number;
  difference: number;
  unit: string;
  rule_triggered: string;
  calculation_details?: string | null;
  reason: string;
  evidence_summary?: string | null;
  dealer_explanation?: string | null;
  investigation_outcome?: string | null;
  created_at: string;
  reviewed_at?: string | null;
}

export interface AuditSummary {
  total_records: number;
  validated_records: number;
  pending_reviews: number;
  open_discrepancies: number;
  critical_discrepancies: number;
  resolved_cases: number;
  rule_a_count: number;
  rule_b_count: number;
}

export interface OverviewStats {
  total_shops: number;
  total_beneficiaries: number;
  total_records_ingested: number;
  total_allocated_mt: number;
  total_distributed_mt: number;
  reconciliation_rate_pct: number;
  open_discrepancies_count: number;
  open_complaints_count: number;
}

export interface StateAnalytics {
  state: string;
  allocated_quantity: number;
  distributed_quantity: number;
  shops_count: number;
  discrepancy_count: number;
  compliance_rate_pct: number;
}

export interface Trend {
  period: string;
  allocated: number;
  distributed: number;
  discrepancy_count: number;
}

export interface CommodityBreakdown {
  commodity: string;
  allocated: number;
  distributed: number;
  unit: string;
  variance_pct: number;
}

export interface TinyFishStatus {
  configured: boolean;
  mode: string;
  base_url: string;
  approved_sources_count: number;
  total_jobs_count: number;
  last_extraction_at?: string | null;
}

export interface DataSource {
  id: number;
  name: string;
  source_url: string;
  jurisdiction: string;
  source_type: string;
  is_approved: boolean;
  is_enabled: boolean;
  last_checked_at?: string | null;
}

export interface ExtractionJob {
  id: number;
  source_id: number;
  source_name?: string | null;
  source_url?: string | null;
  job_status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | string;
  started_at: string;
  completed_at?: string | null;
  records_extracted: number;
  records_validated: number;
  error_summary?: string | null;
  mode: 'LIVE' | 'DEMO' | string;
}

export interface SourceRecord {
  id: number;
  source_id: number;
  extraction_job_id: number;
  region: string;
  commodity: string;
  metric_name: string;
  quantity: number;
  unit: string;
  reporting_period: string;
  evidence_reference: string;
  extracted_at: string;
  record_hash: string;
  validation_status: string;
}
