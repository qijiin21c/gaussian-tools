# Basis Set Extrapolation Theory

Detailed discussion of SCF and correlation energy extrapolation to the complete basis set (CBS) limit, based on Sobereva's article (sobereva.com/338).

## Why basis set extrapolation works

Basis set incompleteness is a major error source in quantum chemistry. As basis set size increases, computed properties (energy, geometry, dipole moment) converge toward the CBS limit. If the convergence trend follows a known mathematical form, results from smaller basis sets can be extrapolated to predict CBS-limit values.

### Prerequisites for extrapolation

The basis set sequence must be **systematically constructed**:
- Each successive level adds basis functions in a predictable pattern
- Error decreases smoothly and monotonically
- Clear convergence trend exists

**Suitable sequences:**
- Dunning correlation-consistent: cc-pVnZ, aug-cc-pVnZ, cc-pV(n+d)Z
- ANO (Atomic Natural Orbital)
- Jensen polarization-consistent: pc-n
- Ahlrichs def2: def2-SVP, def2-TZVP, def2-QZVP

**NOT suitable:**
- Pople series (3-21G*, 6-31G*, 6-311+G(2d,p))
  - Error decreases but not smoothly
  - No predictable convergence pattern for extrapolation

### The L parameter

L = highest angular momentum quantum number in the basis set for main-group heavy atoms:

| Basis | Heavy atom highest l | L value |
|-------|---------------------|---------|
| cc-pVDZ | d | 2 |
| cc-pVTZ | f | 3 |
| cc-pVQZ | g | 4 |
| cc-pV5Z | h | 5 |
| cc-pV6Z | i | 6 |

## SCF energy extrapolation

### Why SCF converges fast

HF and DFT are formally single-electron approximations. The basis set only needs to adequately describe single-electron properties, which doesn't require very high angular momentum:
- For main-group elements, angular momentum up to **f** is sufficient
- Adding g and higher contributes almost nothing
- Better to invest computational effort in adding more low-angular-momentum functions

SCF results are already good at 3ζ level and near CBS at 4ζ. **SCF extrapolation has limited practical value.**

### Exponential convergence form

For Dunning correlation-consistent basis sets (and ANO series), SCF energy converges as:

**Form 1:** `E_SCF(L) = E_SCF(∞) + A × exp(-α × L)`

**Form 2:** `E_SCF(L) = E_SCF(∞) + A × exp(-α × √L)`

Both forms give nearly identical results. Form 2 is more commonly used.

This formula has three unknowns: E_SCF(∞), A, and α. In principle, three basis set levels are needed (e.g., DZ + TZ + QZ). However, α has been pre-fitted for common basis sequences, so only two calculations are needed.

### Pre-fitted α parameters

From ORCA manual v2.9, section 6.1.3.4:

| Basis sequence | L pair | α |
|---------------|--------|---|
| **cc-pVnZ** | 2/3 (DZ/TZ) | 4.42 |
| **cc-pVnZ** | 3/4 (TZ/QZ) | 5.46 |
| **def2** | 2/3 (SVP/TZVP) | 10.39 |
| **def2** | 3/4 (TZVP/QZVP) | 7.88 |

### Two-point extrapolation formula

Given α is known, from:
```
E(N) = E(∞) + A × exp(-α√N)     ... (1)
E(M) = E(∞) + A × exp(-α√M)     ... (2)
```

From (2): `A = [E(M) - E(∞)] / exp(-α√M)`

Substitute into (1) and rearrange:
```
E(∞) = [E(M)×exp(-α√N) - E(N)×exp(-α√M)] / [exp(-α√N) - exp(-α√M)]
```

Where M > N are the L values of the two basis sets.

### aug-cc-pVnZ extrapolation

There are no pre-fitted α parameters specifically for aug-cc-pVnZ. As an approximation, use the corresponding cc-pVnZ α parameters for the same L values — the difference is not large.

Alternatively, skip SCF extrapolation for aug-cc-pVnZ and use the largest basis result (e.g., aug-cc-pVQZ) directly as the CBS SCF energy — the error is minimal at QZ level.

## Correlation energy extrapolation

### Why correlation converges slowly

Post-HF methods account for electron correlation (mainly Coulomb correlation) beyond the mean-field approximation. Properly describing the correlation cusp (the sharp feature when two electrons approach each other) is a **two-electron property** that requires much higher basis set quality than single-electron properties.

The product of single-electron basis functions is an inefficient way to describe the cusp. High-angular-momentum functions play a critical role. This is why correlation energy converges much more slowly than SCF energy.

**Without R12/F12 methods, large basis sets are essential for accurate correlation energy.**

### Different convergence for same-spin vs opposite-spin pairs

- **Same-spin (singlet pair) correlation:** converges as L^(-3)
- **Opposite-spin (triplet pair) correlation:** converges as L^(-5)

Opposite-spin correlation converges much faster. In practice, the L^(-3) form dominates the overall convergence, so the simpler single-formula approach is used.

### Klopper-Helgaker formula

The most widely used correlation energy extrapolation formula, with clear theoretical basis:

```
E_corr(L) = E_corr(∞) + A × L^(-3)
```

Two unknowns (E_corr(∞) and A) → only two basis sets needed:
```
E_corr(∞) = [E_corr(N)×N³ - E_corr(M)×M³] / (N³ - M³)
```

### Truhlar generalized formula

```
E_corr(L) = E_corr(∞) + A × L^(-β)
```

When β = 3, this reduces to Klopper-Helgaker. For better accuracy, different β values are fitted for different basis sequences:

| Basis sequence | L pair | β |
|---------------|--------|---|
| **cc-pVnZ** | 2/3 (DZ/TZ) | 2.46 |
| **cc-pVnZ** | 3/4 (TZ/QZ) | 3.05 |
| **def2** | 2/3 (SVP/TZVP) | 2.40 |
| **def2** | 3/4 (TZVP/QZVP) | 2.97 |

**Recommendation:**
- For L = 3/4 (TZ/QZ and higher): **use β = 3.00** — the fitted value is very close to 3, and β = 3 has stronger theoretical basis
- For L = 2/3 (DZ/TZ): **use the fitted β value** (2.46 for cc-pVnZ, 2.40 for def2)

### Which basis pair to use?

| Extrapolation pair | Expected accuracy | Notes |
|-------------------|------------------|-------|
| **DZ/TZ** | Between QZ and 5Z (closer to QZ) | DZ quality is too low; not recommended for high accuracy |
| **TZ/QZ** | ≈ 5Z quality | **Recommended** — reliable results |
| **QZ/5Z** | Near CBS | For highest accuracy |

**Key insight:** Extrapolation typically improves accuracy by about one zeta level beyond the largest basis used. TZ/QZ extrapolation gives ≈ 5Z quality.

**Correlation extrapolation is much more impactful than SCF extrapolation** — the error reduction is significantly larger.

## N₂ example: Convergence behavior

N₂ at bond length 1.100314 Å, computed with cc-pVDZ/TZ/QZ/5Z/6Z:

### HF energy convergence
| Basis | E_HF (hartree) | Δ from previous |
|-------|---------------|----------------|
| DZ | -108.953748406 | — |
| TZ | -108.982940693 | -0.02919 |
| QZ | -108.990532392 | -0.00759 |
| 5Z | -108.992208035 | -0.00168 |
| 6Z | -108.992531280 | -0.00032 |

### MP2 correlation energy convergence
| Basis | ΔE_MP2 (hartree) | Δ from previous |
|-------|-----------------|----------------|
| DZ | -0.307086 | — |
| TZ | -0.374397 | -0.06731 |
| QZ | -0.399443 | -0.02505 |
| 5Z | -0.409803 | -0.01036 |
| 6Z | -0.414509 | -0.00471 |

**Observation:** HF energy converges much faster than correlation energy. QZ-level HF is already very accurate, while correlation energy is still not fully converged at QZ.

### SCF extrapolation results
| Extrapolation | E_HF(CBS) | Δ from max basis used |
|--------------|-----------|----------------------|
| DZ/TZ → CBS | -108.9924345 | -0.01469 (from TZ) |
| TZ/QZ → CBS | -108.9928198 | -0.00229 (from QZ) |

DZ/TZ extrapolation is close to 6Z result. TZ/QZ extrapolation is more accurate than 6Z — essentially the CBS limit.

### Correlation energy extrapolation results
| Extrapolation | ΔE_MP2(CBS) | Δ from max basis used |
|--------------|------------|----------------------|
| DZ/TZ → CBS (Klopper-Helgaker) | -0.402738 | Between QZ and 5Z |
| DZ/TZ → CBS (Truhlar β=2.46) | **-0.413729** | Closer to high-level result |
| TZ/QZ → CBS (Klopper-Helgaker) | -0.417720 | Slightly better than 6Z |

**Key findings:**
1. Correlation extrapolation has a much larger impact on total energy than SCF extrapolation
2. Correlation extrapolation at DZ/TZ level cannot reach CBS as effectively as SCF extrapolation
3. Truhlar formula (β=2.46) for DZ/TZ is clearly better than Klopper-Helgaker (β=3)
4. For high accuracy, correlate at TZ/QZ or higher

### Total MP2/CBS energy
```
E_MP2/CBS(TZ/QZ) = E_HF(CBS, TZ/QZ) + ΔE_MP2(CBS, TZ/QZ)
                  = -108.9928198 + (-0.417720035)
                  = -109.4105398
```

## Relative energies

Chemistry cares about **relative energies**, not absolute total energies. Extrapolation effects largely cancel in energy differences.

**Critical rule:** Either extrapolate ALL systems (with the same basis pair) or extrapolate NONE. Mixing extrapolated and non-extrapolated systems causes massive errors.

## Alternative extrapolation methods

Varandas proposed an alternative method (JCP, 126, 244105, 2007). Results are similar to the methods described above, but the formula is more complex. Not discussed further here.

## References

- sobereva.com/338 — This article (basis set energy extrapolation)
- sobereva.com/46 — BSSE and counterpoise correction
- ORCA manual v2.9, section 6.1.3.4 — α and β parameters
- JCP, 126, 244105 (2007) — Varandas extrapolation method
