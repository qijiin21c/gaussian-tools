# DFT-D3 Theory and Damping Functions

Detailed explanation of DFT-D3 theory, damping functions, and parameter fitting, based on Sobereva's articles (sobereva.com/83).

## Why DFT-D is needed

Traditional exchange-correlation functionals fail to describe dispersion (London dispersion forces):
- **B3LYP**: Related potential has wrong long-range behavior — completely cannot describe dispersion
- **PBE, PW91**: Describe dispersion extremely poorly
- **Consequences**: Physical adsorption, large molecule conformations (long-chain alkanes), weak polar molecular clusters — results are qualitatively wrong

**Solution:** Add empirical dispersion correction term (DFT-D).

## DFT-D evolution

| Version | Reference | Status |
|---------|-----------|--------|
| DFT-D1 | JCC, 25, 1463 (2004) | Obsolete |
| DFT-D2 | JCC, 27, 1787 (2006) | Obsolete — limited elements, simpler model |
| **DFT-D3** | **JCP, 132, 154104 (2010)** | **Standard — rigorous, H-Pu support, all major functionals** |
| DFT-D4 | JCP, 147, 034112 (2017) | Emerging — considers electronic structure effect; complex; limited support |

## Zero-damping vs BJ-damping

### Zero-damping (D3(0))

Original DFT-D3 form. The damping function f(R_AB) gradually decays to 0 as interatomic distance R_AB decreases, making D3 correction exactly 0 at short range.

**Formula:**
```
E_disp = -Σ_{AB} Σ_{n=6,8} s_n × C_n^AB / R_AB^n × f_n(R_AB)
```

**Damping function:**
```
f_n(R_AB) = R_AB^n / (R_AB^n + (s_{r,n} × R0_AB)^n)
```

where R0_AB = √(C8_AB / C6_AB)

**Parameters per functional (4 total):**
- s6, s8, s_{r,6}, s_{r,8}
- For normal functionals: s6 = 1, s_{r,8} = 1 → only fit s8 and s_{r,6}
- For double-hybrids: s6 < 1, also needs fitting

### BJ-damping (D3(BJ))

**Reference:** JCC, 32, 1456 (2011)

Physically more meaningful damping. Medium/short-range correction is small but NOT near zero.

**Formula:**
```
E_disp = -Σ_{AB} Σ_{n=6,8} s_n × C_n^AB / (R_AB^n + (a1 × R0_AB + a2)^n)
```

**Parameters per functional (4 total):**
- a1, a2, s6, s8
- For normal functionals: s6 = 1 → only fit a1, a2, s8
- For double-hybrids: s6 also needs fitting

### Which damping to use?

| Functional type | Recommended damping | Reason |
|----------------|-------------------|--------|
| **B3LYP, BLYP, PBE, PBE0, etc.** | **BJ** | Slightly better overall accuracy; better for intramolecular dispersion |
| **M05/06/08 series (M06-2X, M06, M05-2X)** | **Zero only** | Already have medium-range correlation; BJ causes double-counting |
| **HF** | **BJ only** | HF has zero dispersion; zero-damping gives nothing at short range |
| **MN15** | Either | Newer Minnesota functional compatible with BJ |
| **Double-hybrids (B2PLYP, DSD-PBEP86)** | BJ | s6 < 1; both work |

## Three-body term

DFT-D3 is pairwise additive by default. Real dispersion has non-additive many-body (three-body and higher) contributions.

- **Default:** Three-body term NOT computed (negligible effect for most systems)
- **For very large systems:** Three-body term can provide non-negligible improvement
- **Computational cost:** Minimal when computed
- **Analytic derivatives:** Only first derivatives available for three-body term

## Dispersion as approximate dispersion interaction energy

For functionals like B3LYP that completely cannot describe dispersion, the DFT-D3 correction energy can be approximately viewed as the dispersion interaction energy. This allows direct computation of intermolecular dispersion energy magnitude.

**Caveat:** This differs from SAPT's dispersion term. The sobEDA/sobEDAw method (sobereva.com/685) provides a dispersion term based on DFT-D correction but with additional considerations for SAPT comparability.

**Alternative:** Multiwfn force-field-based energy decomposition (sobereva.com/442) provides dispersion energy decomposed into atomic pairs and arbitrary fragment contributions.

## DFT-D with well-dispersing functionals

Even for functionals that already describe dispersion reasonably:
- **M06-2X**: Adding D3(0) provides slight improvement
- **wB97XD**: Already has DFT-D2 built-in; switching to D3 provides improvement but requires custom functional definition
- **Double-hybrids**: Adding D3 provides slight improvement

## Other dispersion correction methods

DFT-D is the most popular, widely supported, and cheapest. Other methods include:
- **TS** (Tkatchenko-Scheffler)
- **XDM** (Exchange-Dipole Moment)
- **VV10** (van der Waals 2010)
- **vdW-DF** (van der Waals Density Functional)
- **MBD** (Many-Body Dispersion)

These are covered in the Beijing Keinsci Intermediate Quantum Chemistry Training course.

## Analytic derivatives

DFT-D has simple functional form, so first and second analytic derivatives are easily obtained. Whatever order of analytic derivatives the base DFT method supports, the DFT-D corrected version supports the same order.

## Naming convention

DFT functional + DFT-D3 is typically named as "Functional-D3":
- B3LYP + D3 → B3LYP-D3
- BLYP + D3(BJ) → BLYP-D3(BJ)
- PBE0 + D3(0) → PBE0-D3(0)

## Functionals with built-in dispersion

These functionals have dispersion built into their definition — do NOT add separate DFT-D:

| Functional | Built-in correction | Version |
|-----------|-------------------|---------|
| B97D | DFT-D2 | Original definition |
| wB97XD | DFT-D2 | Original definition |
| B2PLYPD | DFT-D2 | Original definition |
| B2PLYPD3 | DFT-D3(BJ) | Updated version |
| B97D3 | DFT-D3(BJ) | Updated version |
| mPW2PLYPD | DFT-D2 | Original definition |

## References

- sobereva.com/83 — This article (DFT-D overview)
- sobereva.com/413 — When DFT-D3 is needed
- sobereva.com/705 — Multiwfn atomic dispersion contribution analysis
- sobereva.com/709 — Atomic C6 dispersion coefficient calculation
- sobereva.com/685 — sobEDA energy decomposition
- sobereva.com/442 — Multiwfn force-field energy decomposition
- J. Chem. Phys., 132, 154104 (2010) — DFT-D3
- J. Comput. Chem., 32, 1456 (2011) — DFT-D3(BJ)
- J. Mol. Model., 19, 5387 (2013) — B3LYP vs B3LYP-D3 for H₂/N₂ dimers
- Phys. Chem. Chem. Phys., 19, 32184 (2017) — GMTKN55 benchmark database
