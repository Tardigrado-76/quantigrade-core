# ADR-0001: API-First Architecture with FastAPI

| Field | Value |
|---|---|
| **ID** | ADR-0001 |
| **Date** | 2026-09-02 |
| **Status** | Accepted |
| **Deciders** | Principal DevSecOps Engineer, Enterprise Architect, CISO |
| **Ticket** | QUANT-001 |

---

## Context

The Quantigrade compliance platform started as a monolithic Streamlit application that tightly coupled the business logic (severity calculation, audit engines) with the presentation layer. As the platform evolved to cover 7 regulatory frameworks simultaneously (DORA, ENS, NIS2, RGPD, CRA, EU AI Act, OWASP LLM), the following pain points emerged:

1. **Testability**: Business logic could not be unit-tested independently from the Streamlit UI runtime.
2. **Reusability**: The severity engine could not be consumed by third-party systems (CI/CD pipelines, SIEM integrations, mobile clients) without importing the entire Streamlit context.
3. **Scalability**: The monolith could not be independently scaled; the full app had to be replicated even when only the audit engine was under load.
4. **Auditability**: Regulatory frameworks (DORA Art. 11, CRA Art. 27) increasingly require demonstrable separation of concerns and auditable API contracts.

## Decision

We adopt an **API-First architecture** using **FastAPI (Python 3.12+)** as the primary service layer, decoupled from any frontend concerns.

Specifically:
- All compliance logic is encapsulated in the `quantigrade-core` Python package, installable via `pip`.
- The package exposes a FastAPI application that serves a **versioned REST API** (`/api/v1/`).
- The OpenAPI 3.1 specification (`openapi.yaml`) is the **source of truth** for the API contract, generated from code annotations.
- The Streamlit UI and any other consumer communicate with the API exclusively via HTTP — no direct Python imports across service boundaries in production.
- **Redis** is used as a cache layer for audit results to avoid redundant computation and provide a time-bounded audit history.

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Keep Streamlit monolith | Poor testability, no external consumption, scaling constraints |
| Django REST Framework | Heavier footprint, slower iteration, less idiomatic for data-oriented APIs |
| gRPC | Harder to consume from browser-based tools and non-Python clients; OpenAPI ecosystem preferred |
| GraphQL | Compliance APIs have well-defined, non-exploratory query shapes; REST is more appropriate |

## Consequences

### Positive
- ✅ Core logic is fully unit-testable with `pytest` without UI dependencies.
- ✅ The OpenAPI spec enables automatic SDK generation for any consumer language.
- ✅ Enables a DevSecOps pipeline (`bandit`, `mypy`, `ruff`) at the package level.
- ✅ API versioning (`/v1/`) allows non-breaking evolution of the contract.
- ✅ Aligns with DORA Art. 11 (ICT resilience testing) by enabling independent load testing of the audit engine.
- ✅ Redis caching provides a time-stamped, immutable audit trail suitable for DORA Art. 12 (data reporting).

### Negative / Mitigated
- ⚠️ **Network latency**: The Streamlit UI now makes HTTP calls instead of direct function calls. Mitigated by deploying both on the same internal network (Docker Compose) and using Redis caching.
- ⚠️ **Authentication surface**: The API introduces a new authentication boundary. Mitigated by enforcing JWT Bearer tokens on all non-health endpoints.

## Compliance Mapping

| Framework | Article | Satisfied By |
|---|---|---|
| DORA | Art. 11 (Resilience Testing) | Independent API service can be load/chaos tested |
| DORA | Art. 12 (Data Reporting) | Redis provides time-stamped audit cache |
| CRA | Art. 27 (Vulnerability Reporting) | OpenAPI spec documents the attack surface |
| ENS Alta | mp.sw.1 (Application Security) | Typed API contracts enforced by Pydantic v2 |

---

*Last updated: 2026-09-02 by Tardigrado-76*
