"""Unit tests for the DORA Article 18 incident classification engine.

Covers:
- All quantitative RTS EBA thresholds (Art. 3)
- All qualitative thresholds (Art. 4)
- Severity level mapping
- Notification deadline correctness
- Required reports generation
- Edge cases: exactly at threshold, below threshold, multi-criteria
"""

from __future__ import annotations

import pytest

from quantigrade.core.dora_severity import DORAIncidentClassifier
from quantigrade.core.models import DORAIncidentInput, SeverityLevel


@pytest.fixture
def classifier() -> DORAIncidentClassifier:
    return DORAIncidentClassifier()


def make_input(**kwargs: object) -> DORAIncidentInput:
    """Helper: create a baseline (non-major) incident and override fields."""
    defaults: dict[str, object] = {
        "clients_affected": 0,
        "downtime_hours": 0.0,
        "economic_loss_eur": 0,
        "eu_countries_affected": 1,
        "affects_critical_service": False,
        "data_integrity_compromised": False,
        "transaction_value_eur": 0,
    }
    defaults.update(kwargs)
    return DORAIncidentInput(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Non-Major Incident
# ---------------------------------------------------------------------------
class TestNonMajorIncident:
    def test_all_zeros_is_not_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input())
        assert not result.is_major_incident
        assert result.severity_level == SeverityLevel.LOW
        assert result.notification_deadline_hours == 0
        assert result.required_reports == []

    def test_just_below_all_thresholds_is_not_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(
            make_input(
                clients_affected=99_999,
                downtime_hours=1.9,
                economic_loss_eur=99_999,
                eu_countries_affected=1,
            )
        )
        assert not result.is_major_incident


# ---------------------------------------------------------------------------
# Quantitative Thresholds — RTS Art. 3
# ---------------------------------------------------------------------------
class TestQuantitativeThresholds:
    def test_clients_threshold_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(clients_affected=100_000))
        assert result.is_major_incident
        assert any("Clients affected" in t for t in result.triggered_thresholds)

    def test_downtime_threshold_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(downtime_hours=2.0))
        assert result.is_major_incident
        assert any("Downtime" in t for t in result.triggered_thresholds)

    def test_economic_loss_threshold_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(economic_loss_eur=100_000))
        assert result.is_major_incident
        assert any("Economic loss" in t for t in result.triggered_thresholds)

    def test_transaction_value_threshold_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(transaction_value_eur=5_000_000))
        assert result.is_major_incident
        assert any("Transaction value" in t for t in result.triggered_thresholds)

    def test_cross_border_threshold_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(eu_countries_affected=2))
        assert result.is_major_incident
        assert any("Cross-border" in t for t in result.triggered_thresholds)


# ---------------------------------------------------------------------------
# Qualitative Thresholds — RTS Art. 4
# ---------------------------------------------------------------------------
class TestQualitativeThresholds:
    def test_critical_service_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(affects_critical_service=True))
        assert result.is_major_incident
        assert any("critical" in t.lower() for t in result.triggered_thresholds)

    def test_data_integrity_triggers_major(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(data_integrity_compromised=True))
        assert result.is_major_incident
        assert any("integrity" in t.lower() for t in result.triggered_thresholds)


# ---------------------------------------------------------------------------
# Severity Level & Notification Deadlines
# ---------------------------------------------------------------------------
class TestSeverityAndDeadlines:
    def test_critical_incident_has_2h_deadline(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(
            make_input(
                clients_affected=600_000,
                downtime_hours=5.0,
                affects_critical_service=True,
                eu_countries_affected=3,
                data_integrity_compromised=True,
            )
        )
        assert result.severity_level == SeverityLevel.CRITICAL
        assert result.notification_deadline_hours == 2

    def test_high_severity_has_4h_deadline(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(
            make_input(
                clients_affected=100_000,
                affects_critical_service=True,
            )
        )
        assert result.severity_level == SeverityLevel.HIGH
        assert result.notification_deadline_hours == 4

    def test_critical_requires_three_reports(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(
            make_input(
                clients_affected=600_000,
                downtime_hours=5.0,
                affects_critical_service=True,
                eu_countries_affected=3,
            )
        )
        assert len(result.required_reports) == 3
        assert any("Initial" in r for r in result.required_reports)
        assert any("Intermediate" in r for r in result.required_reports)
        assert any("Final" in r for r in result.required_reports)

    def test_low_major_requires_two_reports(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(downtime_hours=2.0))
        assert result.is_major_incident
        # medium severity — should include initial + final but not intermediate
        assert len(result.required_reports) >= 2


# ---------------------------------------------------------------------------
# Regulatory Reference
# ---------------------------------------------------------------------------
class TestRegulatoryReference:
    def test_regulatory_reference_is_correct(
        self, classifier: DORAIncidentClassifier
    ) -> None:
        result = classifier.classify(make_input(clients_affected=100_000))
        assert "DORA" in result.regulatory_reference
        assert "RTS EBA" in result.regulatory_reference
