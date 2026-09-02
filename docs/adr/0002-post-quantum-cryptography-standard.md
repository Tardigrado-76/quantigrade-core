# ADR-0002: Post-Quantum Cryptography Standard (FIPS 204 — ML-DSA)

| Field | Value |
|---|---|
| **ID** | ADR-0002 |
| **Date** | 2026-09-02 |
| **Status** | Accepted |
| **Deciders** | Principal DevSecOps Engineer, CISO, Enterprise Architect |
| **Ticket** | QUANT-042 |
| **Supersedes** | N/A (greenfield decision) |

---

## Context

The Quantigrade platform processes and stores **audit logs, incident notifications, and regulatory reports** that require long-term integrity guarantees. Current threats to this integrity include:

1. **Harvest Now, Decrypt Later (HNDL)**: Adversaries are capturing encrypted audit trails today, anticipating that future quantum computers will break RSA-2048 and ECDSA-P256, which currently protect our log signatures.
2. **DORA Art. 12 (Data Reporting)**: Requires that ICT-related incident reports maintain demonstrable integrity over multi-year retention periods.
3. **CRA Art. 13 (Vulnerability Reporting)**: Mandates tamper-evident delivery of security disclosures.
4. **NIST PQC Standardization (August 2024)**: NIST published FIPS 203, 204, and 205 as the first post-quantum cryptographic standards.
5. **ENS Alta (CCN-STIC-807)**: The Spanish CCNA has issued guidance recommending preparation for quantum-safe cryptography in high-security systems.

The question is: **which post-quantum algorithm standard should Quantigrade adopt for digital signatures?**

## Decision

We adopt **FIPS 204 (ML-DSA — Module-Lattice-Based Digital Signature Algorithm)** as the primary post-quantum signature algorithm for:

1. **Audit log integrity verification** (immutable Merkle-tree-based log signing)
2. **Git commit signing** for regulatory evidence trazability (SLSA Level 3+)
3. **Incident report authentication** before submission to NCAs/EBA

Specifically:
- We use the **ML-DSA-87** variant (highest security level ≈ AES-256 classical equivalent) for all regulatory artifacts.
- We adopt a **hybrid signature scheme** during the transition period: classical ECDSA-P384 + ML-DSA-87 signatures are applied simultaneously. Verifiers can trust the classical signature today and the PQC signature for the long term.
- The `quantigrade-core` package exposes the `/api/v1/pqc/verify` endpoint for on-demand signature verification.

## Algorithm Comparison

| Property | ML-DSA-87 (FIPS 204) | Dilithium5 | SLH-DSA-SHA2-256 (FIPS 205) | RSA-4096 |
|---|---|---|---|---|
| **NIST Status** | ✅ FIPS 204 (final) | Predecessor | ✅ FIPS 205 (final) | Classical |
| **Security Level** | ~256-bit (quantum) | ~256-bit | ~256-bit | 0 (quantum) |
| **Signature Size** | 4,627 bytes | 4,595 bytes | 29,792 bytes | 512 bytes |
| **Public Key Size** | 2,592 bytes | 2,592 bytes | 64 bytes | 512 bytes |
| **Sign Speed** | Fast (lattice) | Fast (lattice) | Slow (hash-based) | Slow |
| **Verify Speed** | Very fast | Very fast | Fast | Fast |
| **Standardization** | FIPS 204 (NIST) | Finalist (pre-std) | FIPS 205 (NIST) | FIPS 186 |

**Rationale for ML-DSA over SLH-DSA**: ML-DSA produces signatures 6x smaller than SLH-DSA, critical for high-throughput audit log signing in DORA-regulated environments. Lattice-based security assumptions (Module Learning With Errors — MLWE) are well-studied with ~25 years of cryptanalytic history.

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Stay with ECDSA P-384 | Vulnerable to Shor's algorithm on quantum computers; non-compliant with post-2030 guidance |
| SLH-DSA (FIPS 205) | Signature size (29KB) impractical for audit log trazability at scale |
| CRYSTALS-Dilithium | Superseded by the formal FIPS 204 standardization of ML-DSA |
| Wait for further standards | HNDL threat is active now; delayed adoption increases regulatory risk |

## Implementation Plan

```
Phase 1 (Now):     Hybrid signatures (ECDSA-P384 + ML-DSA-87) on all audit logs
Phase 2 (2026 Q4): Pure ML-DSA-87 for new artifacts; ECDSA kept for backward compatibility
Phase 3 (2027 Q1): Full migration; ECDSA deprecated; FIPS 203 (ML-KEM) for key encapsulation
```

## Consequences

### Positive
- ✅ Audit logs remain verifiable against quantum adversaries for 25+ year retention periods.
- ✅ Aligns with DORA Art. 12, CRA Art. 13, and ENS Alta (CCN-STIC-807) guidance.
- ✅ SLSA Level 3+ provenance for software artifacts (Git commit signing).
- ✅ Forward-compatible with emerging EU NIS2 technical guidance on PQC.
- ✅ Demonstrates cryptographic agility — the hybrid scheme allows rollback if MLWE assumptions are challenged.

### Negative / Mitigated
- ⚠️ **Signature size increase**: ML-DSA-87 signatures (~4.6KB) vs ECDSA (~72 bytes). Mitigated by log compression and storing only Merkle tree root hashes for bulk audit records.
- ⚠️ **Library maturity**: `liboqs` and its Python bindings (`liboqs-python`) are production-ready but newer than ECDSA libraries. Mitigated by the hybrid scheme and pinned dependency versions.
- ⚠️ **Performance overhead**: Signing ~5ms vs ECDSA ~0.3ms at ML-DSA-87 level. Acceptable for audit log signing (not on the hot API path).

## Compliance Mapping

| Framework | Article | Satisfied By |
|---|---|---|
| DORA | Art. 12 (Data Reporting) | ML-DSA signed reports maintain long-term integrity |
| CRA | Art. 13 (Vulnerability Reporting) | PQC-signed security disclosures |
| ENS Alta | CCN-STIC-807 | Post-quantum readiness for high-security systems |
| NIST | FIPS 204 | Direct compliance with the standard |

---

*Last updated: 2026-09-02 by Tardigrado-76*
