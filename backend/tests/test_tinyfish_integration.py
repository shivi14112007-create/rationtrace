import pytest
import os
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx

from backend.app.core.database import Base
from backend.app.models.models import DataSource, ExtractionJob, SourceRecord
from backend.app.integrations.tinyfish_client import (
    TinyFishClient,
    validate_output_schema,
    is_source_approved,
    SourceNotApprovedError,
    SchemaValidationError,
    MissingApiKeyError,
    TinyFishApiError,
    TinyFishTimeoutError,
    NFSA_PUBLIC_ALLOCATION_URL,
    NFSA_ALLOCATION_OUTPUT_SCHEMA,
    DEMO_NFSA_ALLOCATION_FIXTURE,
)

# In-memory database fixture for job tracking tests
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 1. Schema Validation Tests
# ---------------------------------------------------------------------------

def test_schema_validation_valid():
    """Valid NFSA allocation schema should pass without error."""
    validate_output_schema(NFSA_ALLOCATION_OUTPUT_SCHEMA)


def test_schema_validation_top_level_must_be_object():
    """Non-object top level should be rejected."""
    with pytest.raises(SchemaValidationError, match="top-level schema must declare 'type': 'object'"):
        validate_output_schema({"type": "array", "items": {"type": "string"}})


def test_schema_validation_rejects_top_level_anyof():
    """Top-level anyOf is forbidden by TinyFish."""
    with pytest.raises(SchemaValidationError, match="top-level 'anyOf' is not supported"):
        validate_output_schema({"type": "object", "anyOf": [{"type": "string"}]})


def test_schema_validation_rejects_additional_properties():
    """additionalProperties is explicitly rejected per TinyFish docs."""
    schema = {
        "type": "object",
        "properties": {"title": {"type": "string"}},
        "additionalProperties": False,
    }
    with pytest.raises(SchemaValidationError, match="additionalProperties.*is not supported"):
        validate_output_schema(schema)


def test_schema_validation_rejects_oneof():
    """oneOf is rejected (TinyFish requires anyOf)."""
    schema = {
        "type": "object",
        "properties": {
            "val": {"oneOf": [{"type": "string"}, {"type": "number"}]}
        }
    }
    with pytest.raises(SchemaValidationError, match="oneOf.*is not supported"):
        validate_output_schema(schema)


def test_schema_validation_rejects_const():
    """const is rejected (TinyFish requires enum)."""
    schema = {
        "type": "object",
        "properties": {
            "status": {"const": "active"}
        }
    }
    with pytest.raises(SchemaValidationError, match="const.*is not supported"):
        validate_output_schema(schema)


def test_schema_validation_rejects_unknown_keywords():
    """Keywords outside the allowlist are rejected."""
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "custom_invented_keyword": 123
    }
    with pytest.raises(SchemaValidationError, match="unsupported keyword 'custom_invented_keyword'"):
        validate_output_schema(schema)


def test_schema_validation_depth_limit():
    """Schemas deeper than 10 levels must be rejected."""
    # Build deep nested object
    current = {"type": "string"}
    for i in range(12):
        current = {"type": "object", "properties": {f"level_{i}": current}}

    with pytest.raises(SchemaValidationError, match="exceeds maximum nesting depth"):
        validate_output_schema(current)


# ---------------------------------------------------------------------------
# 2. Admin-Approved Source Allowlist Tests
# ---------------------------------------------------------------------------

def test_source_allowlist_approved_domains():
    """Official portals must be approved."""
    assert is_source_approved("https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx") is True
    assert is_source_approved("https://epos.bihar.gov.in/reports") is True
    assert is_source_approved("https://nfs.delhi.gov.in/index.html") is True
    assert is_source_approved("https://subdomain.nfsa.gov.in/page") is True


def test_source_allowlist_unapproved_domain_rejected():
    """Non-whitelisted public domains must be rejected."""
    assert is_source_approved("https://unapproved-commercial-site.com/data") is False
    assert is_source_approved("https://malicious-actor.org/exploit") is False

    client = TinyFishClient(api_key="sk-test")
    with pytest.raises(SourceNotApprovedError, match="not in the admin-approved"):
        client.validate_source("https://unapproved-site.com")


def test_source_allowlist_dynamic_db_approval(db_session):
    """Sources dynamically registered in DataSource table must be approved if is_approved=True."""
    custom_url = "https://custom-state-pds-portal.gov.in/dashboard"

    # Initially not approved
    assert is_source_approved(custom_url, db=db_session) is False

    # Admin approves source in DB
    ds = DataSource(
        name="Custom State PDS",
        source_url=custom_url,
        jurisdiction="State",
        source_type="PORTAL",
        is_approved=True,
        is_enabled=True
    )
    db_session.add(ds)
    db_session.commit()

    # Now approved
    assert is_source_approved(custom_url, db=db_session) is True


# ---------------------------------------------------------------------------
# 3. Missing API Key & DEMO Fixture (Never Fake Live Success)
# ---------------------------------------------------------------------------

def test_missing_api_key_raises_error_in_live_mode():
    """In LIVE mode, missing API key must raise MissingApiKeyError; never fake a live success."""
    client = TinyFishClient(api_key="")
    with pytest.raises(MissingApiKeyError, match="Cannot perform live extraction in LIVE mode"):
        client.extract_nfsa_allocations(mode="LIVE")


def test_demo_mode_returns_clearly_labelled_fixture(db_session):
    """When mode='DEMO', returns clearly labelled demo fixture with mode='DEMO'."""
    client = TinyFishClient(api_key="")
    result = client.extract_nfsa_allocations(mode="DEMO", db=db_session)

    assert result.status == "COMPLETED"
    assert result.mode == "DEMO"
    assert result.is_demo is True
    assert result.provenance == "DEMO_FIXTURE_NFSA_ALLOCATION"
    assert result.records_extracted > 0
    assert result.records_validated == result.records_extracted
    assert any(r["state"] == "Delhi" for r in result.records)

    # Verify job tracking in DB reflects mode='DEMO'
    job = db_session.query(ExtractionJob).filter(ExtractionJob.id == result.job_id).first()
    assert job is not None
    assert job.mode == "DEMO"
    assert job.job_status == "COMPLETED"

    # Verify source records in DB
    records = db_session.query(SourceRecord).filter(SourceRecord.extraction_job_id == job.id).all()
    assert len(records) == result.records_extracted
    assert records[0].evidence_reference.startswith("DEMO_FIXTURE:")


def test_auto_mode_falls_back_to_demo_when_key_missing():
    """When mode='AUTO' and key is missing, uses labelled DEMO fixture."""
    client = TinyFishClient(api_key="")
    result = client.extract_nfsa_allocations(mode="AUTO")
    assert result.mode == "DEMO"
    assert result.is_demo is True
    assert result.provenance == "DEMO_FIXTURE_NFSA_ALLOCATION"


# ---------------------------------------------------------------------------
# 4. Payload Compliance & Endpoint Verification
# ---------------------------------------------------------------------------

def test_sync_automation_payload_no_invented_fields():
    """Verify that only real documented fields are sent in the payload."""
    client = TinyFishClient(api_key="sk-test-key")

    captured_request = {}

    def mock_request(method, url, headers, json):
        captured_request["method"] = method
        captured_request["url"] = url
        captured_request["headers"] = headers
        captured_request["json"] = json
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "run_id": "test-run-123",
            "status": "COMPLETED",
            "started_at": "2026-10-20T10:00:00Z",
            "finished_at": "2026-10-20T10:00:15Z",
            "num_of_steps": 4,
            "result": {"reporting_period": "2026-09", "state_allocations": []},
            "error": None
        }
        return resp

    mock_client = MagicMock()
    mock_client.request.side_effect = mock_request

    with patch("httpx.Client", return_value=mock_client):
        res = client.run_sync_automation(
            url="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx",
            goal="Extract allocation figures",
            output_schema=NFSA_ALLOCATION_OUTPUT_SCHEMA,
            browser_profile="lite",
            api_integration="rationtrace"
        )

    assert res["status"] == "COMPLETED"
    assert captured_request["url"] == "https://agent.tinyfish.ai/v1/automation/run"
    assert captured_request["headers"]["X-API-Key"] == "sk-test-key"

    # Verify NO invented fields exist in the payload
    payload = captured_request["json"]
    allowed_payload_keys = {
        "url", "goal", "output_schema", "browser_profile", "proxy_config",
        "agent_config", "webhook_url", "use_profile", "profile_id", "use_vault",
        "credential_item_ids", "capture_config", "api_integration"
    }
    for k in payload.keys():
        assert k in allowed_payload_keys, f"Found invented field in payload: {k}"


# ---------------------------------------------------------------------------
# 5. Retry & Timeout Handling
# ---------------------------------------------------------------------------

def test_retry_on_429_rate_limit():
    """Client should retry on 429 and succeed on subsequent attempt."""
    client = TinyFishClient(api_key="sk-test-key", max_retries=2, backoff_factor=0.01)

    call_count = 0

    def mock_req(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        if call_count == 1:
            resp.status_code = 429
            resp.headers = {"Retry-After": "0"}
            return resp
        resp.status_code = 200
        resp.json.return_value = {"run_id": "run-429", "status": "COMPLETED", "result": {}}
        return resp

    mock_http = MagicMock()
    mock_http.request.side_effect = mock_req

    with patch("httpx.Client", return_value=mock_http):
        res = client.run_sync_automation(
            url="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx",
            goal="Extract figures"
        )

    assert call_count == 2
    assert res["run_id"] == "run-429"


def test_retry_on_500_server_error():
    """Client should retry on 500 and succeed on subsequent attempt."""
    client = TinyFishClient(api_key="sk-test-key", max_retries=2, backoff_factor=0.01)

    call_count = 0

    def mock_req(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        if call_count == 1:
            resp.status_code = 500
            resp.text = "Internal Server Error"
            return resp
        resp.status_code = 200
        resp.json.return_value = {"run_id": "run-500", "status": "COMPLETED", "result": {}}
        return resp

    mock_http = MagicMock()
    mock_http.request.side_effect = mock_req

    with patch("httpx.Client", return_value=mock_http):
        res = client.run_sync_automation(
            url="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx",
            goal="Extract figures"
        )

    assert call_count == 2
    assert res["run_id"] == "run-500"


def test_no_retry_on_400_invalid_input():
    """Client must NOT retry on 400 Bad Request."""
    client = TinyFishClient(api_key="sk-test-key", max_retries=3)

    call_count = 0

    def mock_req(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        resp.status_code = 400
        resp.json.return_value = {"error": {"code": "INVALID_INPUT", "message": "Bad request"}}
        return resp

    mock_http = MagicMock()
    mock_http.request.side_effect = mock_req

    with patch("httpx.Client", return_value=mock_http):
        with pytest.raises(SchemaValidationError):
            client.run_sync_automation(
                url="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx",
                goal="Extract figures"
            )

    assert call_count == 1  # No retries on 400
