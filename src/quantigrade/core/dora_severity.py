"""DORA Article 18 / RTS EBA Major Incident Classification Engine.

Implements the Commission Delegated Regulation (EU) 2024/1774 thresholds
for classifying ICT-related incidents as major under DORA.

Reference:
    - DORA Article 18: Classification of ICT-related incidents
    - RTS EBA: Draft RTS on major incident classification criteria
    - Commission Delegated Regulation (EU) 2024/1774
"""

from __future__ import annotations

import structlog

from quantigrade.core.models import (
    DORAClassificationResult,
    DORAIncidentInput,
    SeverityLevel,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# RTS EBA Thresholds (Commission Delegated Regulation EU 2024/1774)
# ---------------------------------------------------------------------------
_CLIENTS_THRESHOLD_MAJOR: int = 100_000
_DOWNTIME_THRESHOLD_HOURS: float = 2.0
_ECONOMIC_LOSS_THRESHOLD_EUR: int = 100_000
_TRANSACTION_VALUE_THRESHOLD_EUR: int = 5_000_000
_CROSS_BORDER_THRESHOLD_COUNTRIES: int = 2


class DORAIncidentClassifier:
    """Classify ICT incidents under DORA Article 18 / RTS EBA criteria.

    This engine evaluates all quantitative and qualitative thresholds
    defined in the RTS and produces a fully auditable classification result.

    Usage:
        classifier = DORAIncidentClassifier()
        result = classifier.classify(input_data)
    """

    def classify(self, data: DORAIncidentInput) -> DORAClassificationResult:
        """Run all DORA threshold checks and return the classification result.

        Args:
            data: Validated DORAIncidentInput with incident metrics.

        Returns:
            DORAClassificationResult with severity, deadlines and triggered thresholds.
        """
        log = logger.bind(classifier="DORAIncidentClassifier")
        triggered: list[str] = []

        # --- Quantitative thresholds (RTS EBA Art. 3) ---
        if data.clients_affected >= _CLIENTS_THRESHOLD_MAJOR:
            triggered.append(
                f"Clients affected ({data.clients_affected:,}) ≥ "
                f"threshold ({_CLIENTS_THRESHOLD_MAJOR:,}) [RTS Art.3(a)]"
            )

        if data.downtime_hours >= _DOWNTIME_THRESHOLD_HOURS:
            triggered.append(
                f"Downtime ({data.downtime_hours}h) ≥ "
                f"threshold ({_DOWNTIME_THRESHOLD_HOURS}h) [RTS Art.3(b)]"
            )

        if data.economic_loss_eur >= _ECONOMIC_LOSS_THRESHOLD_EUR:
            triggered.append(
                f"Economic loss (€{data.economic_loss_eur:,}) ≥ "
                f"threshold (€{_ECONOMIC_LOSS_THRESHOLD_EUR:,}) [RTS Art.3(c)]"
            )

        if data.transaction_value_eur >= _TRANSACTION_VALUE_THRESHOLD_EUR:
            triggered.append(
                f"Transaction value (€{data.transaction_value_eur:,}) ≥ "
                f"threshold (€{_TRANSACTION_VALUE_THRESHOLD_EUR:,}) [RTS Art.3(d)]"
            )

        if data.eu_countries_affected >= _CROSS_BORDER_THRESHOLD_COUNTRIES:
            triggered.append(
                f"Cross-border impact ({data.eu_countries_affected} EU countries) "
                f"≥ threshold ({_CROSS_BORDER_THRESHOLD_COUNTRIES}) [RTS Art.3(e)]"
            )

        # --- Qualitative thresholds (RTS EBA Art. 4) ---
        if data.affects_critical_service:
            triggered.append("Critical/essential function affected [RTS Art.4(a)]")

        if data.data_integrity_compromised:
            triggered.append("Data integrity or confidentiality compromised [RTS Art.4(b)]")

        is_major = len(triggered) > 0
        severity = self._compute_severity(data, triggered)
        deadline = self._notification_deadline(is_major, severity)
        reports = self._required_reports(is_major, severity)

        log.info(
            "incident_classified",
            is_major=is_major,
            severity=severity,
            thresholds_triggered=len(triggered),
            notification_deadline_hours=deadline,
        )

        return DORAClassificationResult(
            is_major_incident=is_major,
            severity_level=severity,
            notification_deadline_hours=deadline,
            triggered_thresholds=triggered,
            required_reports=reports,
        )

    @staticmethod
    def _compute_severity(
        data: DORAIncidentInput,
        triggered: list[str],
    ) -> SeverityLevel:
        """Map triggered thresholds to a severity level."""
        count = len(triggered)
        critical_flags = (
            data.data_integrity_compromised
            or data.affects_critical_service
            or data.eu_countries_affected >= 3
        )
        if count == 0:
            return SeverityLevel.LOW
        if critical_flags and (data.clients_affected >= 500_000 or data.downtime_hours >= 4):
            return SeverityLevel.CRITICAL
        if critical_flags or count >= 4:
            return SeverityLevel.HIGH
        if count >= 2:
            return SeverityLevel.MEDIUM
        return SeverityLevel.LOW

    @staticmethod
    def _notification_deadline(is_major: bool, severity: SeverityLevel) -> int:
        """Return the regulatory notification deadline in hours."""
        if not is_major:
            return 0
        return 2 if severity == SeverityLevel.CRITICAL else 4

    @staticmethod
    def _required_reports(is_major: bool, severity: SeverityLevel) -> list[str]:
        """Return the list of mandatory regulatory reports."""
        if not is_major:
            return []
        reports = ["Initial Notification (DORA Art.19 §2 — within 4h)"]
        if severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL):
            reports.append("Intermediate Report (DORA Art.19 §3 — within 24h)")
        reports.append("Final Report (DORA Art.19 §4 — within 1 month)")
        return reports
