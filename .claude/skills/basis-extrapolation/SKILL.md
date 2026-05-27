---
name: basis-extrapolation
description: This skill should be used when the user asks to "basis set extrapolation", "基组外推", "CBS limit", "complete basis set", "extrapolate to CBS", "Klopper-Helgaker", "SCF extrapolation", "correlation energy extrapolation", "cc-pVDZ cc-pVTZ cc-pVQZ CBS", "def2 extrapolation", "Truhlar extrapolation", "BSSE extrapolation", "counterpoise CBS", "MP2/CBS", "CCSD(T)/CBS", "E_SCF(infinity)", "E_corr(infinity)", or mentions extrapolating quantum chemistry energies to the complete basis set limit.
version: 0.1.0
---

# Basis Set Extrapolation to CBS Limit

Guidance for extrapolating single-point energies to the complete basis set (CBS) limit, based on Sobereva's article (sobereva.com/338).

**Core principle:** Basis set incompleteness is a major error source in quantum chemistry. For systematically constructed basis set sequences (cc-pVnZ, def2, pc-n), results converge smoothly with increasing basis size. By computing at two or more basis levels, you can extrapolate to the CBS limit — the theoretical result with an infinite basis set.

## Prerequisites

### Systematically constructed basis set sequences (suitable for extrapolation)
| Sequence | Notes |
|----------|-------|
| **cc-pVnZ** (DZ, TZ, QZ, 5Z, 6Z) | Dunning correlation-consistent |
| **aug-cc-pVnZ** | Dunning with diffuse |
| **cc-pV(n+d)Z** | For 3rd-row elements |
| **def2-SVP, TZVP, QZVP** | Ahlrichs def2 series |
| **pc-n** (pc-0, pc-1, pc-2, pc-3, pc-4) | Jensen polarization-consistent |
| **ANO** | Atomic natural orbital |

### NOT suitable for extrapolation
- **Pople series** (3-21G*, 6-31G*, 6-311+G(2d,p), etc.) — error decreases but not smoothly; no predictable convergence trend

### L values for Dunning series
| Basis | L value | Highest angular momentum |
|-------|---------|------------------------|
| cc-pVDZ | 2 | d (l=2) |
| cc-pVTZ | 3 | f (l=3) |
| cc-pVQZ | 4 | g (l=4) |
| cc-pV5Z | 5 | h (l=5) |
| cc-pV6Z | 6 | i (l=6) |

## Quick reference: Two-step extrapolation protocol

For high-accuracy calculations, compute energy as:
```
E_total(CBS) = E_SCF(CBS) + E_corr(CBS)
```
SCF (HF/DFT) and correlation energy converge differently — **extrapolate separately**.

### SCF extrapolation (HF/DFT)
**Formula:** `E_SCF(L) = E_SCF(∞) + A × exp(-α × √L)`

| Sequence | L pair | α parameter |
|----------|--------|------------|
| **cc-pVnZ** | DZ/TZ (2/3) | 4.42 |
| **cc-pVnZ** | TZ/QZ (3/4) | 5.46 |
| **def2** | SVP/TZVP (2/3) | 10.39 |
| **def2** | TZVP/QZVP (3/4) | 7.88 |

Two-point formula:
```
E_SCF(∞) = [E(M)×exp(-α√N) - E(N)×exp(-α√M)] / [exp(-α√N) - exp(-α√M)]
```
where M > N are the L values of the two basis sets.

### Correlation energy extrapolation
**Klopper-Helgaker formula:** `E_corr(L) = E_corr(∞) + A × L^(-3)`

Two-point formula:
```
E_corr(∞) = [E_corr(N)×N³ - E_corr(M)×M³] / (N³ - M³)
```

| Sequence | L pair | β (Truhlar) | β (recommended) |
|----------|--------|------------|----------------|
| **cc-pVnZ** | DZ/TZ (2/3) | 2.46 | **Use 2.46** |
| **cc-pVnZ** | TZ/QZ (3/4) | 3.05 | **Use 3.00** (theoretical) |
| **def2** | SVP/TZVP (2/3) | 2.40 | **Use 2.40** |
| **def2** | TZVP/QZVP (3/4) | 2.97 | **Use 3.00** (theoretical) |

## When is extrapolation worth it?

| Energy type | Convergence speed | Extrapolation value |
|-------------|-------------------|---------------------|
| **SCF (HF/DFT)** | Fast — 3ζ already good, 4ζ near CBS | **Limited value** — SCF converges quickly |
| **Correlation** | Slow — even QZ not fully converged | **Essential** for high accuracy |

**SCF note:** For main-group elements, angular momentum up to f is sufficient. Adding g and higher contributes almost nothing — better to invest in more low-angular-momentum functions.

## Recommended extrapolation levels

| Target accuracy | SCF | Correlation | Expected result quality |
|----------------|-----|------------|----------------------|
| **Minimum** | DZ/TZ | DZ/TZ | Slightly better than TZ |
| **Standard** | TZ/QZ | TZ/QZ | ≈ 5Z quality |
| **High** | QZ/5Z | QZ/5Z | Near CBS |

**Recommendation:** Use TZ/QZ for correlation extrapolation. DZ/TZ gives results between QZ and 5Z (closer to QZ) — not truly near CBS.

## Approximate CCSD(T)/CBS trick

When CCSD(T) with large basis sets is too expensive:
```
E_corr(∞)_CCSD(T) ≈ E_corr(∞)_MP2 + [E_corr(small)_CCSD(T) - E_corr(small)_MP2]
```
1. Extrapolate MP2 correlation to CBS (cheap — MP2 scales as N⁵)
2. Compute CCSD(T) and MP2 correlation at a small basis (e.g., DZ or TZ)
3. Add the CCSD(T)-MP2 difference to the MP2/CBS result

**Validity:** Assumes the CCSD(T)-MP2 correlation difference is basis-set insensitive — usually a reasonable assumption.

## BSSE-aware extrapolation

For intermolecular interaction energies, BSSE must be considered at each basis level before extrapolation.

### Counterpoise-corrected energy at each basis level
```
E'_AB = E_AB + E_BSSE
E_BSSE = (E_A - E_A,bAB) + (E_B - E_B,bAB)
```

For post-HF, split BSSE into HF and correlation parts:
```
E'_AB_HF = E_AB_HF + E_BSSE_HF
E'_AB_corr = E_AB_corr + E_BSSE_corr
```

Then extrapolate E'_AB_HF and E'_AB_corr separately to CBS.

### Recommended: Manual ghost atom approach
Do NOT use Gaussian's `counterpoise` keyword for post-HF extrapolation:
- `counterpoise` disables symmetry for all calculations
- Hard to extract separate E_BSSE_HF and E_BSSE_corr
- Instead, manually compute: E_AB, E_A, E_B, E_A,bAB, E_B,bAB with ghost atoms (Bq suffix)

### Consistency rule
**All systems must be extrapolated (or none).** Mixing extrapolated and non-extrapolated energies in relative energy calculations causes massive errors.

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/extrapolation-theory.md`** — Detailed derivation of SCF and correlation extrapolation formulas, α and β parameter fitting, convergence behavior analysis (N₂ example), HF vs correlation convergence comparison, Truhlar vs Klopper-Helgaker comparison
- **`references/bsse-extrapolation.md`** — Counterpoise-corrected extrapolation: manual ghost atom workflow, H₂-N₂ dimer CCSD(T)/CBS example, BSSE magnitude at different basis levels, symmetry considerations
