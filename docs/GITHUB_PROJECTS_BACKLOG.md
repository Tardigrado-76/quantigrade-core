# 📊 GitHub Projects — Quantigrade Kanban Board
## Epics & User Stories with Acceptance Criteria and Definition of Done

---

## 🟣 EPIC-01: DORA Compliance Engine — Automated Incident Classification

**Goal**: Deliver a production-ready, testable Python package that automates the full DORA Art.18 / RTS EBA major incident classification workflow.

**Acceptance Criteria (Epic-level)**:
- [ ] All 5 quantitative and 2 qualitative RTS EBA thresholds are implemented
- [ ] pytest suite achieves ≥80% code coverage
- [ ] API endpoint `/api/v1/audit/dora` returns correct classification for all test cases
- [ ] CI/CD pipeline gates on all checks passing

---

### 📌 US-01.1: Implement DORA Severity Classifier Core Logic

**As a** CISO Tooling Engineer,  
**I want** a Python class that classifies ICT incidents against all DORA Art.18 / RTS EBA thresholds,  
**So that** the classification is auditable, reproducible, and can be unit-tested independently of any UI.

**Acceptance Criteria**:
- [ ] `DORAIncidentClassifier.classify()` accepts a validated `DORAIncidentInput` Pydantic model
- [ ] All 5 quantitative thresholds (clients, downtime, economic loss, transaction value, cross-border) are evaluated
- [ ] Both qualitative thresholds (critical service, data integrity) are evaluated
- [ ] Result includes: `is_major_incident`, `severity_level`, `notification_deadline_hours`, `triggered_thresholds`, `required_reports`
- [ ] Structured JSON log emitted via `structlog` for every classification event

**Definition of Done**:
- [ ] Code passes `ruff`, `mypy --strict`, and `bandit` with zero HIGH/CRITICAL findings
- [ ] Minimum 5 unit tests covering: non-major, each individual threshold, critical multi-threshold, deadline validation
- [ ] Code reviewed and approved by 1 peer reviewer
- [ ] Merged to `main` with CI pipeline green

---

### 📌 US-01.2: Expose DORA Classifier via FastAPI REST Endpoint

**As a** Platform Integrations Engineer,  
**I want** a REST endpoint `POST /api/v1/audit/dora` that wraps the classifier,  
**So that** any system (Streamlit UI, SIEM, CI/CD pipeline) can consume it over HTTP without Python dependencies.

**Acceptance Criteria**:
- [ ] `POST /api/v1/audit/dora` accepts JSON body matching `DORAIncidentInput` schema
- [ ] Successful classification returns `200 OK` with `DORAClassificationResult` JSON
- [ ] Invalid input returns `422 Unprocessable Entity` with field-level error detail
- [ ] All requests require JWT Bearer authentication (401 if missing/invalid)
- [ ] Redis caches results for 5 minutes (key: SHA256 hash of input)
- [ ] OpenAPI schema at `/docs` reflects the endpoint accurately

**Definition of Done**:
- [ ] Integration test with `httpx.AsyncClient` covers: valid request, invalid request, cache hit
- [ ] Endpoint documented in `openapi.yaml`
- [ ] Latency p99 < 200ms for non-cached requests (measured with `locust` or `k6`)
- [ ] CI pipeline green on merge

---

## 🟣 EPIC-02: DevSecOps Pipeline — Shift-Left Security

**Goal**: Every code change triggers a fully automated DevSecOps pipeline that gates merges on code quality, security, and coverage standards.

**Acceptance Criteria (Epic-level)**:
- [ ] GitHub Actions workflow completes in under 5 minutes for a typical push
- [ ] No HIGH/CRITICAL `bandit` findings can be merged to `main`
- [ ] Code coverage gate enforced at 80% minimum
- [ ] Pipeline badge visible on README

---

### 📌 US-02.1: Implement Multi-Stage GitHub Actions CI/CD Pipeline

**As a** Principal DevSecOps Engineer,  
**I want** a GitHub Actions workflow that runs lint, type check, SAST, tests, and build on every push,  
**So that** no insecure or low-quality code reaches the `main` branch.

**Acceptance Criteria**:
- [ ] Workflow triggers on `push` to `main` and on all `pull_request` events
- [ ] Stage 1: `ruff check` and `ruff format --check` must pass with zero errors
- [ ] Stage 2: `mypy --strict` must pass with zero type errors
- [ ] Stage 3: `bandit -r src/` must pass with no HIGH or CRITICAL severity findings
- [ ] Stage 4: `pytest --cov-fail-under=80` must pass
- [ ] Stage 5: `python -m build` + `twine check` must succeed
- [ ] Final gate job fails the entire pipeline if any stage fails
- [ ] Test results and coverage reports uploaded as artifacts (retained 30 days)

**Definition of Done**:
- [ ] Workflow file at `.github/workflows/ci.yml` committed and active
- [ ] First successful pipeline run recorded (green badge)
- [ ] README badge links to pipeline status
- [ ] Reviewed by CISO or Security Lead

---

### 📌 US-02.2: Enforce Branch Protection Rules

**As a** Engineering Manager,  
**I want** `main` branch protected so that no code can be merged without a passing CI run and at least one peer review,  
**So that** the `main` branch always represents a deployable, compliant state.

**Acceptance Criteria**:
- [ ] Direct pushes to `main` are blocked for all contributors including repository owners
- [ ] All PRs require: CI pipeline passing + at least 1 approving review
- [ ] Status checks required: `lint-and-typecheck`, `security-sast`, `test-and-coverage`, `build-package`
- [ ] Stale PR reviews dismissed on new commits
- [ ] Signed commits required (`commit.gpgsign = true`)

**Definition of Done**:
- [ ] Branch protection rules configured in GitHub repository settings
- [ ] Verified: direct push attempt to `main` is rejected
- [ ] Verified: PR without passing CI cannot be merged

---

## 🟣 EPIC-03: Post-Quantum Cryptography (PQC) Integration

**Goal**: Integrate FIPS 204 (ML-DSA) post-quantum signatures for immutable audit log integrity, aligning with DORA Art.12, CRA Art.13, and ENS Alta CCN-STIC-807.

**Acceptance Criteria (Epic-level)**:
- [ ] ML-DSA-87 signature generation and verification functional
- [ ] Hybrid signature scheme (ECDSA P-384 + ML-DSA-87) operational
- [ ] `/api/v1/pqc/verify` endpoint live and documented
- [ ] Merkle tree log integrity verifier integrated with audit pipeline

---

### 📌 US-03.1: Implement ML-DSA (FIPS 204) Signature Verifier

**As a** Security Engineer,  
**I want** a Python module that verifies ML-DSA-87 signatures on audit logs and incident reports,  
**So that** the integrity of all regulatory artifacts can be proven to auditors using a quantum-safe algorithm.

**Acceptance Criteria**:
- [ ] `PQCVerifier.verify()` accepts `PQCVerificationInput` and returns `PQCVerificationResult`
- [ ] Supports ML-DSA-44, ML-DSA-65, and ML-DSA-87 variants
- [ ] Returns `is_valid: false` (not raises) for tampered messages or wrong keys
- [ ] All verification events logged with `structlog` (algorithm, validity, timestamp)
- [ ] REST endpoint `POST /api/v1/pqc/verify` wraps the verifier
- [ ] Endpoint documented in `openapi.yaml`

**Definition of Done**:
- [ ] Unit tests: valid signature, tampered message, wrong key, unsupported algorithm
- [ ] `mypy --strict` passes on `pqc_verifier.py`
- [ ] `bandit` scan clean
- [ ] ADR-0002 references this implementation
- [ ] Merged to `main` with CI green

---

### 📌 US-03.2: Merkle Tree Audit Log Integrity Verifier

**As a** Compliance Officer,  
**I want** a module that builds and verifies Merkle tree hashes over batches of audit log entries,  
**So that** any tampering with historical audit logs is mathematically detectable — satisfying DORA Art.12 data integrity requirements.

**Acceptance Criteria**:
- [ ] `MerkleVerifier.build_tree(log_entries)` returns root hash (SHA-256)
- [ ] `MerkleVerifier.verify_entry(entry, proof)` validates a single entry against root
- [ ] Root hash is ML-DSA-87 signed before storage
- [ ] Verification result includes: `is_valid`, `root_hash`, `verified_at` (UTC ISO 8601)
- [ ] Integration test: build tree → tamper one entry → verify → assert `is_valid = false`

**Definition of Done**:
- [ ] Code merged to `main` with CI green
- [ ] Benchmark: tree build < 100ms for 10,000 log entries (recorded in PR description)
- [ ] Evidence of tamper detection demonstrated in PR integration test output
