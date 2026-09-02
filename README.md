# 🛡️ Quantigrade Core

**Enterprise-grade Python package for automated regulatory compliance auditing.**

[![CI/CD Pipeline](https://github.com/Tardigrado-76/quantigrade-core/actions/workflows/ci.yml/badge.svg)](https://github.com/Tardigrado-76/quantigrade-core/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-green.svg)](./openapi.yaml)

---

## 🎯 Overview

`quantigrade-core` is a production-ready Python package that implements the **DORA Article 18 / RTS EBA major incident classification engine**, along with integrations for ENS Alta, NIS2, RGPD, CRA, and EU AI Act compliance frameworks.

Designed for **Principal DevSecOps Engineers and CISOs** who need auditable, testable, and API-First compliance tooling.

---

## 🏗️ Architecture

```
quantigrade-core/
├── src/quantigrade/            # Installable Python package (PEP 517)
│   ├── core/
│   │   ├── dora_severity.py    # DORA Art.18 RTS EBA severity engine
│   │   ├── models.py           # Pydantic data models (typed)
│   │   └── pqc_verifier.py     # FIPS 204 ML-DSA signature verifier
│   └── api/
│       ├── main.py             # FastAPI application entry point
│       └── routers/
│           ├── audit.py            # /api/v1/audit/* endpoints
│           └── pqc.py              # /api/v1/pqc/* endpoints
├── tests/                      # pytest suite (>80% coverage)
├── docs/adr/                   # Architecture Decision Records
├── .github/workflows/ci.yml   # DevSecOps CI/CD pipeline
├── docker-compose.yml          # Multi-container deployment
├── openapi.yaml                # OpenAPI 3.1 specification
└── pyproject.toml              # PEP 517 package configuration
```

---

## ⚡ Quick Start

### Install via pip
```bash
pip install quantigrade-core
```

### Run the API locally
```bash
docker-compose up --build
# API available at: http://localhost:8000
# Docs:            http://localhost:8000/docs
```

### Classify a DORA incident
```python
from quantigrade.core.dora_severity import DORAIncidentClassifier
from quantigrade.core.models import DORAIncidentInput

input_data = DORAIncidentInput(
    clients_affected=175_000,
    downtime_hours=4.5,
    economic_loss_eur=300_000,
    eu_countries_affected=3,
    affects_critical_service=True,
    data_integrity_compromised=True,
)

classifier = DORAIncidentClassifier()
result = classifier.classify(input_data)
print(result.is_major_incident)  # True
print(result.severity_level)     # "CRITICAL"
print(result.notification_deadline_hours)  # 2
```

---

## 🛡️ Normative Coverage

| Framework | Coverage | Automated Controls |
|---|---|---|
| **DORA** (Reg. EU 2022/2554) | ✅ Full | Incident classification RTS EBA, TLPT, ICT Third-Party Risk |
| **ENS Alta** (RD 311/2022) | ✅ Full | Access control (op.acc.1), Patch management (op.exp.4) |
| **NIS2** (Dir. EU 2022/2555) | ✅ Full | CSIRT notification 24h/72h, VEX supply chain |
| **RGPD / LOPDGDD** | ✅ Full | Breach assessment 72h, SAR extraction, pseudonymization |
| **CRA** (Cyber Resilience Act) | ✅ Full | SBOM CycloneDX 1.6, SLSA Level 3+ |
| **EU AI Act** | ✅ Full | High-risk AI risk matrix, human oversight |
| **OWASP LLM Top 10** | ✅ Full | RAG Guardrails, Prompt Injection, PII detection |

---

## 🔧 DevSecOps Pipeline

Every `push` to `main` triggers the CI/CD pipeline:

1. 🔍 **Static Analysis**: `ruff` (linting) + `mypy` (strict type checking)
2. 🚫 **SAST Security**: `bandit` (vulnerability scanner)
3. ✅ **Unit Tests**: `pytest` with `>80%` code coverage gate
4. 📦 **Package Build**: `pip build` + integrity verification

---

## 📄 Architecture Decision Records

- [ADR-0001: API-First Architecture (FastAPI)](./docs/adr/0001-record-architecture-decisions.md)
- [ADR-0002: Post-Quantum Cryptography Standard (FIPS 204 ML-DSA)](./docs/adr/0002-post-quantum-cryptography-standard.md)

---

## 📊 CISO / CTO Executive Report

See [COMPLIANCE_MANAGER Executive Report](https://github.com/Tardigrado-76/COMPLIANCE_MANAGER) for the full security posture assessment.

---

*© 2026 Tardigrado-76 / Quantigrade | Licensed under MIT*
