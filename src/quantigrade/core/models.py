"""Pydantic data models for the Quantigrade compliance engine.

All models use strict Pydantic v2 validation with full type annotations.
These are the canonical data contracts between all layers (API, core logic, tests).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class SeverityLevel(StrEnum):
    """DORA incident severity classification levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DORAIncidentInput(BaseModel):
    """Input data for DORA Article 18 major incident classification.

    Based on RTS EBA thresholds (Commission Delegated Regulation EU 2024/1774).
    All monetary values in EUR. All durations in hours.
    """

    model_config = {"frozen": True, "str_strip_whitespace": True}

    clients_affected: Annotated[int, Field(ge=0, description="Number of clients impacted")]
    downtime_hours: Annotated[
        float, Field(ge=0.0, description="Service unavailability duration in hours")
    ]
    economic_loss_eur: Annotated[int, Field(ge=0, description="Estimated economic impact in EUR")]
    eu_countries_affected: Annotated[
        int, Field(ge=1, le=27, description="Number of EU Member States impacted")
    ]
    affects_critical_service: Annotated[
        bool, Field(description="Does the incident affect a critical or essential function?")
    ]
    data_integrity_compromised: Annotated[
        bool,
        Field(description="Was data integrity or confidentiality impacted (potential breach)?"),
    ]
    transaction_value_eur: Annotated[
        int, Field(ge=0, default=0, description="Value of affected transactions in EUR")
    ]


class DORAClassificationResult(BaseModel):
    """Result of the DORA incident major/minor classification."""

    model_config = {"frozen": True}

    is_major_incident: bool
    severity_level: SeverityLevel
    notification_deadline_hours: int
    triggered_thresholds: list[str]
    regulatory_reference: str = "DORA Art.18 / RTS EBA (EU) 2024/1774"
    required_reports: list[str]

    @model_validator(mode="after")
    def validate_notification_deadline(self) -> DORAClassificationResult:
        """Ensure notification deadline aligns with severity."""
        if self.is_major_incident and self.notification_deadline_hours > 4:
            raise ValueError(
                "Major incidents require initial notification within 4 hours (DORA Art. 19)"
            )
        return self


class PQCVerificationInput(BaseModel):
    """Input for post-quantum cryptographic signature verification."""

    model_config = {"frozen": True}

    message: Annotated[str, Field(min_length=1, description="Message or log hash to verify")]
    signature_hex: Annotated[
        str, Field(min_length=64, description="ML-DSA signature in hexadecimal")
    ]
    public_key_hex: Annotated[
        str, Field(min_length=64, description="ML-DSA public key in hexadecimal")
    ]
    algorithm: Annotated[
        str,
        Field(
            default="ML-DSA-87",
            pattern=r"^ML-DSA-(44|65|87)$",
            description="FIPS 204 algorithm variant",
        ),
    ]


class PQCVerificationResult(BaseModel):
    """Result of post-quantum signature verification."""

    model_config = {"frozen": True}

    is_valid: bool
    algorithm: str
    standard: str = "FIPS 204 (ML-DSA)"
    detail: str
