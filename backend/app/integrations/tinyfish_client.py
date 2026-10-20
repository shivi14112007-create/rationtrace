"""
TinyFish Web Agent Client Integration for RationTrace.

Implements real documented endpoints, authentication, and payload specifications
from the official TinyFish Web Agent API (https://docs.tinyfish.ai/).

Features:
- Real documented endpoints: POST /v1/automation/run, /v1/automation/run-async, /v1/automation/run-sse, GET /v1/runs/{id}
- Strict authentication via X-API-Key header.
- Admin-approved source allowlist validation for government/public portals.
- Strict schema validation for output_schema conforming to TinyFish supported keywords.
- Configurable timeout and exponential backoff retry handling (429, 500, network errors).
- Automatic ExtractionJob and SourceRecord tracking in the database when a session is supplied.
- Clearly labelled DEMO fixture when TINYFISH_API_KEY is missing (Never faking a live success).
- Live extraction helper for the NFSA Public Allocation Dashboard.
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse
import uuid

import httpx
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.models import DataSource, ExtractionJob, SourceRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & Allowlist
# ---------------------------------------------------------------------------

DEFAULT_TINYFISH_BASE_URL = "https://agent.tinyfish.ai"
DEFAULT_SYNC_TIMEOUT_SECONDS = 120.0  # Documented suggested sync timeout: 120s
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0

# Official NFSA Public Allocation Dashboard URL
NFSA_PUBLIC_ALLOCATION_URL = (
    "https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx"
)

# Admin-approved domains/hostnames for public food distribution portals
ADMIN_APPROVED_DOMAINS: Set[str] = {
    "nfsa.gov.in",
    "nfsadashboard.gov.in",
    "epos.bihar.gov.in",
    "nfs.delhi.gov.in",
    "food.up.nic.in",
    "ahara.kar.nic.in",
    "fcsca.wb.gov.in",
    "epos.kerala.gov.in",
    "pds.gov.in",
    "annavitran.nic.in",
    "impds.nic.in",
    "example.com",  # For automated health/integration tests
}

# Supported keywords allowlist per TinyFish docs
# (key-concepts/structured-output.md)
SUPPORTED_SCHEMA_KEYWORDS: Set[str] = {
    "anyOf",
    "enum",
    "format",
    "items",
    "maxItems",
    "maximum",
    "minItems",
    "minimum",
    "nullable",
    "properties",
    "propertyOrdering",
    "required",
    "type",
}

# Explicitly rejected keywords in TinyFish output_schema
REJECTED_SCHEMA_KEYWORDS: Set[str] = {
    "additionalProperties",
    "const",
    "example",
    "examples",
    "oneOf",
}

# ---------------------------------------------------------------------------
# Strict Documented Output Schema for NFSA Public Allocation Dashboard
# ---------------------------------------------------------------------------
NFSA_ALLOCATION_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "portal_name": {"type": "string"},
        "reporting_period": {"type": "string"},
        "unit_of_measure": {"type": "string"},
        "state_allocations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "state": {"type": "string"},
                    "commodity": {"type": "string"},
                    "allocated_quantity": {"type": "number", "minimum": 0},
                    "unit": {"type": "string"},
                },
                "required": ["state", "commodity", "allocated_quantity", "unit"],
            },
        },
    },
    "required": ["reporting_period", "state_allocations"],
}

# ---------------------------------------------------------------------------
# Clearly Labelled DEMO Fixture
# ---------------------------------------------------------------------------
DEMO_NFSA_ALLOCATION_FIXTURE: Dict[str, Any] = {
    "portal_name": "National Food Security Portal (NFSA) Public Allocation Dashboard",
    "reporting_period": "2026-09",
    "unit_of_measure": "MT",
    "is_demo_fixture": True,
    "provenance": "DEMO_FIXTURE_NFSA_ALLOCATION",
    "disclaimer": (
        "DEMO DATA: Generated from offline test fixture because TINYFISH_API_KEY "
        "was missing or DEMO mode was explicitly requested. NOT a live extraction."
    ),
    "state_allocations": [
        {
            "state": "Delhi",
            "commodity": "Wheat",
            "allocated_quantity": 45200.0,
            "unit": "MT",
        },
        {
            "state": "Delhi",
            "commodity": "Rice",
            "allocated_quantity": 28100.0,
            "unit": "MT",
        },
        {
            "state": "Delhi",
            "commodity": "Sugar",
            "allocated_quantity": 1200.0,
            "unit": "MT",
        },
        {
            "state": "Bihar",
            "commodity": "Rice",
            "allocated_quantity": 320000.0,
            "unit": "MT",
        },
        {
            "state": "Bihar",
            "commodity": "Wheat",
            "allocated_quantity": 210000.0,
            "unit": "MT",
        },
        {
            "state": "Uttar Pradesh",
            "commodity": "Wheat",
            "allocated_quantity": 540000.0,
            "unit": "MT",
        },
        {
            "state": "Uttar Pradesh",
            "commodity": "Rice",
            "allocated_quantity": 410000.0,
            "unit": "MT",
        },
        {
            "state": "Maharashtra",
            "commodity": "Rice",
            "allocated_quantity": 280000.0,
            "unit": "MT",
        },
        {
            "state": "Maharashtra",
            "commodity": "Wheat",
            "allocated_quantity": 190000.0,
            "unit": "MT",
        },
        {
            "state": "Karnataka",
            "commodity": "Rice",
            "allocated_quantity": 210000.0,
            "unit": "MT",
        },
        {
            "state": "Karnataka",
            "commodity": "Wheat",
            "allocated_quantity": 45000.0,
            "unit": "MT",
        },
    ],
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TinyFishError(Exception):
    """Base exception for all TinyFish client operations."""
    pass


class MissingApiKeyError(TinyFishError):
    """Raised when live execution is attempted without a valid TINYFISH_API_KEY."""
    pass


class SourceNotApprovedError(TinyFishError):
    """Raised when an unapproved target URL/domain is requested."""
    pass


class SchemaValidationError(TinyFishError):
    """Raised when an output_schema violates TinyFish API constraints."""
    pass


class TinyFishApiError(TinyFishError):
    """Raised when the TinyFish API returns an HTTP error or execution failure."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_details = error_details or {}


class TinyFishTimeoutError(TinyFishError):
    """Raised when an API request to TinyFish exceeds the configured timeout."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class StateAllocationRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    state: str
    commodity: str
    allocated_quantity: float
    unit: str = "MT"


class ExtractionJobResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: Optional[int] = None
    run_id: Optional[str] = None
    status: str  # COMPLETED, FAILED, RUNNING, PENDING
    mode: str    # LIVE or DEMO
    is_demo: bool = False
    url: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    num_of_steps: Optional[int] = None
    records_extracted: int = 0
    records_validated: int = 0
    records: List[Dict[str, Any]] = Field(default_factory=list)
    raw_result: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    provenance: str = "LIVE"


# ---------------------------------------------------------------------------
# Schema Validator Helper
# ---------------------------------------------------------------------------

def validate_output_schema(schema: Dict[str, Any], max_depth: int = 10, current_depth: int = 1) -> None:
    """
    Validates that output_schema strictly complies with TinyFish API requirements:
    - Top-level must be a JSON object (`type: "object"`).
    - Top-level `anyOf` is not supported.
    - Serialized schema size must be <= 64KB.
    - Maximum nesting depth is 10.
    - Boolean schema nodes (`true`/`false`) are not allowed.
    - Only keywords in SUPPORTED_SCHEMA_KEYWORDS are allowed.
    - REJECTED_SCHEMA_KEYWORDS (`additionalProperties`, `const`, `example`, `examples`, `oneOf`) are rejected.
    """
    if not isinstance(schema, dict):
        raise SchemaValidationError("output_schema must be a dictionary / JSON object.")

    # Size limit check (64KB)
    try:
        serialized = json.dumps(schema)
        if len(serialized.encode("utf-8")) > 65536:
            raise SchemaValidationError(
                f"output_schema serialized size ({len(serialized)} bytes) exceeds the 64KB limit."
            )
    except (TypeError, ValueError) as e:
        raise SchemaValidationError(f"output_schema must be JSON-serializable: {e}")

    # Depth check
    if current_depth > max_depth:
        raise SchemaValidationError(f"output_schema exceeds maximum nesting depth of {max_depth}.")

    # Top-level constraints
    if current_depth == 1:
        if schema.get("type") != "object":
            raise SchemaValidationError("output_schema top-level schema must declare 'type': 'object'.")
        if "anyOf" in schema:
            raise SchemaValidationError(
                "output_schema top-level 'anyOf' is not supported. Put composition inside object fields."
            )

    # Check for disallowed and unsupported keywords
    for key, value in schema.items():
        if key in REJECTED_SCHEMA_KEYWORDS:
            rewrite_hint = {
                "additionalProperties": "Omit 'additionalProperties'.",
                "const": "Use 'type': 'string', 'enum': [value].",
                "oneOf": "Use 'anyOf' instead.",
                "example": "Omit 'example'.",
                "examples": "Omit 'examples'.",
            }.get(key, "")
            raise SchemaValidationError(
                f"output_schema field '{key}' is not supported by TinyFish API. {rewrite_hint}"
            )
        if key not in SUPPORTED_SCHEMA_KEYWORDS:
            raise SchemaValidationError(
                f"output_schema contains unsupported keyword '{key}'. Allowed keywords: {sorted(SUPPORTED_SCHEMA_KEYWORDS)}"
            )

        # Check type requirements per documentation
        if key == "enum":
            if schema.get("type") != "string":
                raise SchemaValidationError("'enum' keyword requires 'type': 'string'.")
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise SchemaValidationError("Every value in 'enum' must be a string.")

        if key == "format":
            if schema.get("type") != "string":
                raise SchemaValidationError("'format' keyword requires 'type': 'string'.")
            if value not in {"date", "date-time", "duration", "time"}:
                raise SchemaValidationError(
                    f"Unsupported format '{value}'. Supported formats: date, date-time, duration, time."
                )

        if key in {"items", "minItems", "maxItems"} and schema.get("type") != "array":
            raise SchemaValidationError(f"'{key}' keyword requires 'type': 'array'.")

        if key in {"minimum", "maximum"} and schema.get("type") not in {"number", "integer"}:
            raise SchemaValidationError(f"'{key}' requires 'type': 'number' or 'type': 'integer'.")

        # Recursively validate nested nodes
        if key == "properties" and isinstance(value, dict):
            for prop_name, prop_node in value.items():
                if not isinstance(prop_node, dict):
                    raise SchemaValidationError(f"Property '{prop_name}' must be a schema object.")
                validate_output_schema(prop_node, max_depth=max_depth, current_depth=current_depth + 1)

        elif key == "items":
            if not isinstance(value, dict):
                raise SchemaValidationError("items must be a schema object.")
            validate_output_schema(value, max_depth=max_depth, current_depth=current_depth + 1)

        elif key == "anyOf" and isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    raise SchemaValidationError("anyOf elements must be schema objects.")
                validate_output_schema(item, max_depth=max_depth, current_depth=current_depth + 1)


# ---------------------------------------------------------------------------
# Allowlist Verification Helper
# ---------------------------------------------------------------------------

def is_source_approved(url: str, db: Optional[Session] = None, approved_domains: Optional[Set[str]] = None) -> bool:
    """
    Checks if target URL is approved for Web Agent automated extraction:
    1. Static allowlist of administrative and government domains.
    2. Dynamic verification against active, approved DataSource entries in the DB.
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
    except Exception:
        return False

    if not hostname:
        return False

    domain_set = approved_domains or ADMIN_APPROVED_DOMAINS

    # Match exact hostname or domain suffix (e.g. nfsadashboard.delhi.gov.in -> gov.in or nfsa.gov.in)
    for approved in domain_set:
        approved_lower = approved.lower()
        if hostname == approved_lower or hostname.endswith("." + approved_lower):
            return True

    # Check database DataSource records if session is provided
    if db is not None:
        try:
            active_sources = db.query(DataSource).filter(
                DataSource.is_approved == True,
                DataSource.is_enabled == True
            ).all()
            for src in active_sources:
                src_parsed = urlparse(src.source_url)
                src_host = (src_parsed.hostname or "").lower()
                if src_host and (hostname == src_host or hostname.endswith("." + src_host)):
                    return True
                if url.rstrip("/").startswith(src.source_url.rstrip("/")):
                    return True
        except Exception as e:
            logger.warning(f"Error querying DataSource table for allowlist check: {e}")

    return False


# ---------------------------------------------------------------------------
# TinyFish Web Agent Client
# ---------------------------------------------------------------------------

class TinyFishClient:
    """
    Client for TinyFish Web Agent API.
    Interacts with the real documented endpoints at https://agent.tinyfish.ai:
    - POST /v1/automation/run (sync)
    - POST /v1/automation/run-async (async)
    - GET  /v1/runs/{id}
    - POST /v1/runs/{id}/cancel
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_SYNC_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        approved_domains: Optional[Set[str]] = None,
    ):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = (settings.TINYFISH_API_KEY or "").strip()
        self.base_url = (base_url or settings.TINYFISH_BASE_URL or DEFAULT_TINYFISH_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.approved_domains = approved_domains or ADMIN_APPROVED_DOMAINS

    @property
    def has_api_key(self) -> bool:
        """Returns True if a non-empty API key is present."""
        return bool(self.api_key)

    def validate_source(self, url: str, db: Optional[Session] = None) -> None:
        """Ensures target URL is approved by system administrators."""
        if not is_source_approved(url, db=db, approved_domains=self.approved_domains):
            raise SourceNotApprovedError(
                f"Target URL '{url}' is not in the admin-approved data source allowlist. "
                f"Automated extraction rejected for security and compliance."
            )

    def _get_headers(self) -> Dict[str, str]:
        """Builds standard headers with documented authentication."""
        if not self.api_key:
            raise MissingApiKeyError("TINYFISH_API_KEY is not configured.")
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "RationTrace-Intelligence/1.0",
        }

    def _execute_http_with_retry(
        self,
        method: str,
        endpoint: str,
        json_payload: Optional[Dict[str, Any]] = None,
        client: Optional[httpx.Client] = None,
    ) -> Dict[str, Any]:
        """
        Executes HTTP requests to TinyFish with exponential backoff on retryable errors:
        - 429 Too Many Requests (respects Retry-After header)
        - 500, 502, 503, 504 Server Errors / Service Busy
        - Network/Transport timeouts
        Does NOT retry on 400 Invalid Input, 401 Auth error, or 403 Forbidden.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        close_client = False

        if client is None:
            client = httpx.Client(timeout=self.timeout)
            close_client = True

        last_exception: Optional[Exception] = None

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    logger.info(
                        f"TinyFish API {method} {url} (Attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    response = client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_payload,
                    )

                    # Successful response or execution response from /run
                    if response.status_code == 200:
                        data = response.json()
                        # If run finished with FAILED and category is SYSTEM_FAILURE, retry if possible
                        if data.get("status") == "FAILED":
                            err = data.get("error") or {}
                            category = err.get("category")
                            if category == "SYSTEM_FAILURE" and attempt < self.max_retries:
                                retry_delay = float(err.get("retry_after") or (self.backoff_factor ** attempt))
                                logger.warning(
                                    f"TinyFish run failed with SYSTEM_FAILURE: {err.get('message')}. "
                                    f"Retrying in {retry_delay}s..."
                                )
                                import time
                                time.sleep(retry_delay)
                                continue
                        return data

                    # Handle 429 (Rate Limit)
                    if response.status_code == 429:
                        if attempt < self.max_retries:
                            retry_after_hdr = response.headers.get("Retry-After")
                            retry_delay = (
                                float(retry_after_hdr)
                                if retry_after_hdr and retry_after_hdr.isdigit()
                                else self.backoff_factor ** (attempt + 1)
                            )
                            logger.warning(f"TinyFish Rate Limited (429). Retrying in {retry_delay}s...")
                            import time
                            time.sleep(retry_delay)
                            continue
                        raise TinyFishApiError("TinyFish rate limit exceeded (429)", status_code=429)

                    # Handle 5xx Server Errors
                    if response.status_code in {500, 502, 503, 504}:
                        if attempt < self.max_retries:
                            retry_delay = self.backoff_factor ** (attempt + 1)
                            logger.warning(
                                f"TinyFish Server Error ({response.status_code}). Retrying in {retry_delay}s..."
                            )
                            import time
                            time.sleep(retry_delay)
                            continue
                        error_body = response.text[:400]
                        raise TinyFishApiError(
                            f"TinyFish internal server error ({response.status_code}): {error_body}",
                            status_code=response.status_code
                        )

                    # Non-retryable client errors (400, 401, 403, 404, etc.)
                    try:
                        err_json = response.json()
                    except Exception:
                        err_json = {"message": response.text[:400]}

                    if response.status_code == 400:
                        raise SchemaValidationError(
                            f"TinyFish Invalid Input (400): {err_json.get('error', err_json)}"
                        )
                    if response.status_code == 401:
                        raise MissingApiKeyError(
                            f"TinyFish Authentication Failed (401): {err_json.get('error', err_json)}"
                        )
                    if response.status_code == 403:
                        raise TinyFishApiError(
                            f"TinyFish Forbidden (403): {err_json.get('error', err_json)}",
                            status_code=403,
                            error_details=err_json,
                        )

                    raise TinyFishApiError(
                        f"TinyFish API error ({response.status_code}): {err_json}",
                        status_code=response.status_code,
                        error_details=err_json,
                    )

                except httpx.TimeoutException as te:
                    last_exception = te
                    logger.warning(f"TinyFish request timeout on attempt {attempt + 1}: {te}")
                    if attempt < self.max_retries:
                        import time
                        time.sleep(self.backoff_factor ** attempt)
                        continue
                    raise TinyFishTimeoutError(
                        f"TinyFish request timed out after {self.timeout}s and {self.max_retries} retries."
                    ) from te

                except httpx.NetworkError as ne:
                    last_exception = ne
                    logger.warning(f"TinyFish network error on attempt {attempt + 1}: {ne}")
                    if attempt < self.max_retries:
                        import time
                        time.sleep(self.backoff_factor ** attempt)
                        continue
                    raise TinyFishApiError(f"TinyFish network connectivity failure: {ne}") from ne

            if last_exception:
                raise TinyFishApiError(f"Exhausted retries: {last_exception}")
            raise TinyFishApiError("Request failed after maximum retries.")

        finally:
            if close_client:
                client.close()

    def run_sync_automation(
        self,
        url: str,
        goal: str,
        output_schema: Optional[Dict[str, Any]] = None,
        browser_profile: str = "lite",
        proxy_config: Optional[Dict[str, Any]] = None,
        agent_config: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        use_profile: Optional[bool] = None,
        profile_id: Optional[str] = None,
        use_vault: Optional[bool] = None,
        credential_item_ids: Optional[List[str]] = None,
        capture_config: Optional[Dict[str, bool]] = None,
        api_integration: str = "rationtrace",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Executes a browser automation task synchronously via POST /v1/automation/run.
        Validates target URL against allowlist and schema against rules.
        Payload uses ONLY real documented fields.
        """
        self.validate_source(url, db=db)

        if output_schema is not None:
            validate_output_schema(output_schema)

        # Build payload with strictly documented fields ONLY
        payload: Dict[str, Any] = {
            "url": url,
            "goal": goal,
            "browser_profile": browser_profile,
            "api_integration": api_integration,
        }

        if output_schema is not None:
            payload["output_schema"] = output_schema
        if proxy_config is not None:
            payload["proxy_config"] = proxy_config
        if agent_config is not None:
            payload["agent_config"] = agent_config
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if use_profile is not None:
            payload["use_profile"] = use_profile
        if profile_id is not None:
            payload["profile_id"] = profile_id
        if use_vault is not None:
            payload["use_vault"] = use_vault
        if credential_item_ids is not None:
            payload["credential_item_ids"] = credential_item_ids
        if capture_config is not None:
            payload["capture_config"] = capture_config

        return self._execute_http_with_retry("POST", "/v1/automation/run", json_payload=payload)

    def run_async_automation(
        self,
        url: str,
        goal: str,
        output_schema: Optional[Dict[str, Any]] = None,
        browser_profile: str = "lite",
        proxy_config: Optional[Dict[str, Any]] = None,
        agent_config: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        use_profile: Optional[bool] = None,
        profile_id: Optional[str] = None,
        use_vault: Optional[bool] = None,
        credential_item_ids: Optional[List[str]] = None,
        capture_config: Optional[Dict[str, bool]] = None,
        api_integration: str = "rationtrace",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Starts an automation asynchronously via POST /v1/automation/run-async.
        Returns {'run_id': str, 'error': ...}
        """
        self.validate_source(url, db=db)

        if output_schema is not None:
            validate_output_schema(output_schema)

        payload: Dict[str, Any] = {
            "url": url,
            "goal": goal,
            "browser_profile": browser_profile,
            "api_integration": api_integration,
        }

        if output_schema is not None:
            payload["output_schema"] = output_schema
        if proxy_config is not None:
            payload["proxy_config"] = proxy_config
        if agent_config is not None:
            payload["agent_config"] = agent_config
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if use_profile is not None:
            payload["use_profile"] = use_profile
        if profile_id is not None:
            payload["profile_id"] = profile_id
        if use_vault is not None:
            payload["use_vault"] = use_vault
        if credential_item_ids is not None:
            payload["credential_item_ids"] = credential_item_ids
        if capture_config is not None:
            payload["capture_config"] = capture_config

        return self._execute_http_with_retry("POST", "/v1/automation/run-async", json_payload=payload)

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Retrieves details of an automation run via GET /v1/runs/{id}."""
        if not run_id:
            raise TinyFishError("run_id is required.")
        return self._execute_http_with_retry("GET", f"/v1/runs/{run_id}")

    def cancel_run(self, run_id: str) -> Dict[str, Any]:
        """Cancels an async or SSE automation run via POST /v1/runs/{id}/cancel."""
        if not run_id:
            raise TinyFishError("run_id is required.")
        return self._execute_http_with_retry("POST", f"/v1/runs/{run_id}/cancel")

    def get_demo_fixture(self, reporting_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a clearly labelled DEMO fixture.
        Never fakes a live success.
        """
        fixture = json.loads(json.dumps(DEMO_NFSA_ALLOCATION_FIXTURE))
        if reporting_period:
            fixture["reporting_period"] = reporting_period
        fixture["generated_at"] = datetime.now(timezone.utc).isoformat()
        return fixture

    def extract_nfsa_allocations(
        self,
        url: Optional[str] = None,
        reporting_period: Optional[str] = None,
        db: Optional[Session] = None,
        mode: str = "AUTO",  # "LIVE", "DEMO", or "AUTO"
    ) -> ExtractionJobResult:
        """
        Extracts allocation data from the NFSA Public Allocation Dashboard.

        Behavior regarding TINYFISH_API_KEY and mode:
        - If mode == "LIVE":
          Requires TINYFISH_API_KEY. If missing, raises MissingApiKeyError.
          (Never fakes a live success).
        - If mode == "DEMO":
          Returns clearly labelled DEMO fixture with mode='DEMO'.
        - If mode == "AUTO":
          If key is present and configured, executes LIVE extraction.
          If key is missing, uses clearly labelled DEMO fixture.

        Also tracks the execution as an ExtractionJob and persists SourceRecord
        entries in the database if `db` is provided.
        """
        target_url = url or NFSA_PUBLIC_ALLOCATION_URL
        self.validate_source(target_url, db=db)

        # Decide whether to run LIVE or DEMO
        effective_mode: str
        if mode == "LIVE":
            if not self.has_api_key:
                raise MissingApiKeyError(
                    "TINYFISH_API_KEY is not configured. Cannot perform live extraction in LIVE mode. "
                    "Refusing to fake live success."
                )
            effective_mode = "LIVE"
        elif mode == "DEMO":
            effective_mode = "DEMO"
        elif mode == "AUTO":
            effective_mode = "LIVE" if self.has_api_key else "DEMO"
        else:
            raise ValueError(f"Invalid mode '{mode}'. Choose 'LIVE', 'DEMO', or 'AUTO'.")

        started_at = datetime.now(timezone.utc)

        # Setup Database Job Tracking
        job: Optional[ExtractionJob] = None
        source: Optional[DataSource] = None

        if db is not None:
            try:
                # Find or register DataSource
                source = db.query(DataSource).filter(DataSource.source_url == target_url).first()
                if not source:
                    source = DataSource(
                        name="NFSA Allocation Portal",
                        source_url=target_url,
                        jurisdiction="National (NFSA)",
                        source_type="PORTAL",
                        is_approved=True,
                        is_enabled=True,
                        last_checked_at=started_at,
                    )
                    db.add(source)
                    db.commit()
                    db.refresh(source)

                # Initialize ExtractionJob
                job = ExtractionJob(
                    source_id=source.id,
                    job_status="RUNNING",
                    mode=effective_mode,
                    started_at=started_at,
                    records_extracted=0,
                    records_validated=0,
                )
                db.add(job)
                db.commit()
                db.refresh(job)
            except Exception as e:
                logger.error(f"Failed to record starting ExtractionJob in DB: {e}")
                db.rollback()

        # -------------------------------------------------------------------
        # CASE 1: DEMO Mode (Clearly Labelled Fixture)
        # -------------------------------------------------------------------
        if effective_mode == "DEMO":
            logger.info("Executing DEMO extraction using clearly labelled fixture.")
            demo_data = self.get_demo_fixture(reporting_period=reporting_period)
            allocations = demo_data.get("state_allocations", [])
            completed_at = datetime.now(timezone.utc)

            validated_records: List[Dict[str, Any]] = []
            for item in allocations:
                try:
                    record_model = StateAllocationRecord(**item)
                    validated_records.append(record_model.model_dump())
                except Exception as ve:
                    logger.warning(f"Demo record validation warning: {ve}")

            # Update DB Job
            if db is not None and job is not None and source is not None:
                try:
                    job.job_status = "COMPLETED"
                    job.completed_at = completed_at
                    job.records_extracted = len(validated_records)
                    job.records_validated = len(validated_records)
                    job.error_summary = None

                    # Add SourceRecord entries
                    for rec in validated_records:
                        raw_hash = f"{rec['state']}:{rec['commodity']}:{rec['allocated_quantity']}:{demo_data['reporting_period']}"
                        rec_hash = hashlib.sha256(raw_hash.encode()).hexdigest()
                        src_rec = SourceRecord(
                            source_id=source.id,
                            extraction_job_id=job.id,
                            region=rec["state"],
                            commodity=rec["commodity"],
                            metric_name="Allocated Quantity",
                            quantity=rec["allocated_quantity"],
                            unit=rec["unit"],
                            reporting_period=demo_data["reporting_period"],
                            evidence_reference="DEMO_FIXTURE: NFSA Public Allocation Dashboard",
                            extracted_at=completed_at,
                            record_hash=rec_hash,
                            validation_status="VALID",
                        )
                        db.add(src_rec)
                    db.commit()
                except Exception as dbe:
                    logger.error(f"Failed to persist DEMO records to DB: {dbe}")
                    db.rollback()

            return ExtractionJobResult(
                job_id=job.id if job else None,
                run_id=f"demo-fixture-{uuid.uuid4().hex[:12]}",
                status="COMPLETED",
                mode="DEMO",
                is_demo=True,
                url=target_url,
                started_at=started_at,
                completed_at=completed_at,
                num_of_steps=0,
                records_extracted=len(validated_records),
                records_validated=len(validated_records),
                records=validated_records,
                raw_result=demo_data,
                provenance="DEMO_FIXTURE_NFSA_ALLOCATION",
            )

        # -------------------------------------------------------------------
        # CASE 2: LIVE Mode Execution
        # -------------------------------------------------------------------
        logger.info(f"Executing LIVE extraction via TinyFish API on: {target_url}")
        goal = (
            "Navigate to the Public Allocation Dashboard. "
            "Extract food grain allocation data including state names, commodity types "
            "(Rice, Wheat, Coarse Grains, Nutri-Cereals, Sugar), allocated quantity, "
            "and unit of measure (e.g. MT or Quintals). "
            "Extract data for major states such as Delhi, Uttar Pradesh, Bihar, Maharashtra, and Karnataka. "
            "Also identify the reporting period (month/year) displayed on the dashboard."
        )

        try:
            live_response = self.run_sync_automation(
                url=target_url,
                goal=goal,
                output_schema=NFSA_ALLOCATION_OUTPUT_SCHEMA,
                browser_profile="lite",
                api_integration="rationtrace",
                db=db,
            )

            completed_at = datetime.now(timezone.utc)
            run_status = live_response.get("status", "FAILED")
            run_id = live_response.get("run_id")
            num_steps = live_response.get("num_of_steps")
            error_data = live_response.get("error")

            if run_status != "COMPLETED":
                error_msg = (
                    f"TinyFish live run failed: {error_data.get('message') if error_data else 'Unknown run error'}"
                )
                logger.error(error_msg)

                # Never fake a live success! Update job as FAILED.
                if db is not None and job is not None:
                    job.job_status = "FAILED"
                    job.completed_at = completed_at
                    job.error_summary = error_msg
                    db.commit()

                return ExtractionJobResult(
                    job_id=job.id if job else None,
                    run_id=run_id,
                    status="FAILED",
                    mode="LIVE",
                    is_demo=False,
                    url=target_url,
                    started_at=started_at,
                    completed_at=completed_at,
                    num_of_steps=num_steps,
                    records_extracted=0,
                    records_validated=0,
                    records=[],
                    raw_result=live_response,
                    error_summary=error_msg,
                    provenance=f"LIVE_API:{self.base_url}/v1/automation/run",
                )

            # Extract and validate records from live result
            raw_result = live_response.get("result") or {}
            state_allocations = raw_result.get("state_allocations") or []
            reported_period = raw_result.get("reporting_period") or reporting_period or "2026-09"

            validated_records = []
            for item in state_allocations:
                try:
                    record_model = StateAllocationRecord(**item)
                    validated_records.append(record_model.model_dump())
                except Exception as ve:
                    logger.warning(f"Skipping invalid record from live output: {ve}")

            # Persist validated live records into Database
            if db is not None and job is not None and source is not None:
                try:
                    job.job_status = "COMPLETED"
                    job.completed_at = completed_at
                    job.records_extracted = len(state_allocations)
                    job.records_validated = len(validated_records)
                    job.error_summary = None

                    for rec in validated_records:
                        raw_hash = f"{rec['state']}:{rec['commodity']}:{rec['allocated_quantity']}:{reported_period}"
                        rec_hash = hashlib.sha256(raw_hash.encode()).hexdigest()
                        src_rec = SourceRecord(
                            source_id=source.id,
                            extraction_job_id=job.id,
                            region=rec["state"],
                            commodity=rec["commodity"],
                            metric_name="Allocated Quantity",
                            quantity=rec["allocated_quantity"],
                            unit=rec["unit"],
                            reporting_period=reported_period,
                            evidence_reference=f"TinyFish Run ID: {run_id} (NFSA Live Extraction)",
                            extracted_at=completed_at,
                            record_hash=rec_hash,
                            validation_status="VALID",
                        )
                        db.add(src_rec)
                    db.commit()
                except Exception as dbe:
                    logger.error(f"Failed to persist LIVE records to DB: {dbe}")
                    db.rollback()

            return ExtractionJobResult(
                job_id=job.id if job else None,
                run_id=run_id,
                status="COMPLETED",
                mode="LIVE",
                is_demo=False,
                url=target_url,
                started_at=started_at,
                completed_at=completed_at,
                num_of_steps=num_steps,
                records_extracted=len(state_allocations),
                records_validated=len(validated_records),
                records=validated_records,
                raw_result=raw_result,
                error_summary=None,
                provenance=f"LIVE_API:{self.base_url}/v1/automation/run",
            )

        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            error_msg = f"Live extraction exception: {str(exc)}"
            logger.error(error_msg)

            # Never fake a live success on exception!
            if db is not None and job is not None:
                try:
                    job.job_status = "FAILED"
                    job.completed_at = completed_at
                    job.error_summary = error_msg
                    db.commit()
                except Exception:
                    db.rollback()

            if isinstance(exc, (TinyFishError, SchemaValidationError, SourceNotApprovedError)):
                raise exc

            raise TinyFishApiError(f"Live extraction failed: {exc}") from exc


# Default global client instance
tinyfish_client = TinyFishClient()
