"""External integrations such as TinyFish Web Agent API."""

from backend.app.integrations.tinyfish_client import (
    TinyFishClient,
    tinyfish_client,
    ExtractionJobResult,
    StateAllocationRecord,
    validate_output_schema,
    is_source_approved,
    TinyFishError,
    MissingApiKeyError,
    SourceNotApprovedError,
    SchemaValidationError,
    TinyFishApiError,
    TinyFishTimeoutError,
    ADMIN_APPROVED_DOMAINS,
    NFSA_PUBLIC_ALLOCATION_URL,
    NFSA_ALLOCATION_OUTPUT_SCHEMA,
    DEMO_NFSA_ALLOCATION_FIXTURE,
)

__all__ = [
    "TinyFishClient",
    "tinyfish_client",
    "ExtractionJobResult",
    "StateAllocationRecord",
    "validate_output_schema",
    "is_source_approved",
    "TinyFishError",
    "MissingApiKeyError",
    "SourceNotApprovedError",
    "SchemaValidationError",
    "TinyFishApiError",
    "TinyFishTimeoutError",
    "ADMIN_APPROVED_DOMAINS",
    "NFSA_PUBLIC_ALLOCATION_URL",
    "NFSA_ALLOCATION_OUTPUT_SCHEMA",
    "DEMO_NFSA_ALLOCATION_FIXTURE",
]
