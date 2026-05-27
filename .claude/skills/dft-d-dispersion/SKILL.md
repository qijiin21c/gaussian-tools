---
name: dft-d-dispersion
description: This skill should be used when the user asks to "add dispersion correction", "DFT-D3", "DFT-D3(BJ)", "DFT-D4", "EmpiricalDispersion", "色散校正", "GD3", "GD3BJ", "GD2", "dispersion correction Gaussian", "B3LYP-D3", "when to use DFT-D", "DFT-D parameters", "custom D3 parameters", "TPSSh-D3", "MN15-D3", "damping function", "zero-damping", "BJ damping", "Grimme dispersion", "D3(BJ) frequency imaginary", or mentions adding dispersion corrections to DFT calculations in Gaussian or other quantum chemistry programs.
version: 0.1.0
---

# DFT-D Dispersion Correction

Guide to using DFT-D dispersion corrections in Gaussian, based on Sobereva's articles (sobereva.com/83, sobereva.com/413).

**Core principle:** If your system has ANY dispersion-related interactions (weak interactions, large molecules, flexible chains), you MUST add DFT-D correction. It's free and improves accuracy universally.

## Quick reference: DFT-D versions

| Version | Status | Notes |
|---------|--------|-------|
| DFT-D1 | Obsolete | Do not use |
| DFT-D2 | Obsolete | Limited element coverage; only used by B97D, wB97XD, B2PLYPD (built-in) |
| **DFT-D3** | **Current standard** | H to Pu, all major functionals, zero computational overhead |
| DFT-D4 | Emerging | Considers electronic structure effect on dispersion; limited program support |

## DFT-D3 damping functions

| Damping | Gaussian keyword | When to use |
|---------|-----------------|-------------|
| **Zero-damping (D3(0))** | `EmpiricalDispersion=GD3` or `em=GD3` | Default choice. Required for M05/06/08 series (M06-2X etc.) |
| **BJ-damping (D3(BJ))** | `EmpiricalDispersion=GD3BJ` or `em=GD3BJ` | Slightly better overall; better for intramolecular dispersion. Use for B3LYP, PBE, BLYP, etc. |
| DFT-D2 | `EmpiricalDispersion=GD2` or `em=GD2` | Only for older Gaussian versions or specific needs |

## When DFT-D is essential

| System type | Without DFT-D | With DFT-D |
|-------------|--------------|------------|
| **Van der Waals complexes** (e.g., Ar₂) | No minimum at all — cannot even find dimer | Correct minimum position |
| **π-π stacking** (e.g., DNA base pairs) | Stacking distances completely wrong | Matches experiment |
| **Large molecule conformations** (e.g., remdesivir) | Wrong conformer ordering | Correct |
| **Long-chain alkanes** | Conformational energies qualitatively wrong | Reasonable |
| **Physical adsorption** | Binding energies near zero | Matches CCSD(T) qualitatively |
| **Electrostatic H-bonds** (e.g., water dimer) | Qualitatively OK | Quantitatively improved |

**Even for electrostatic-dominated interactions (H-bonds, halogen bonds):** DFT-D still provides significant quantitative improvement. Adding DFT-D is beneficial and harmless.

## When NOT to add DFT-D

| Situation | Reason |
|-----------|--------|
| **Built-in dispersion functional** (B97D, wB97XD, B2PLYPD) | Already have DFT-D2 built-in; don't double-correct |
| **M06-2X, M06, M05-2X** | Already have medium-range correlation; adding D3(BJ) causes double-counting. D3(0) gives slight improvement but optional |
| **Double-hybrid with built-in D** (B2PLYPD3) | Already includes dispersion |

**Note:** Even for M06-2X and wB97XD which already describe dispersion reasonably, adding DFT-D3 still provides slight improvement. But it's optional for these functionals.

## How to use in Gaussian

### Gaussian 16 / G09 D.01 and later (recommended)

```
# B3LYP/def2-SVP EmpiricalDispersion=GD3BJ opt
# or shorthand:
# B3LYP/def2-SVP em=GD3BJ opt
```

**Output confirmation:** When DFT-D is enabled, Gaussian prints:
```
R6Disp:  Grimme-D3(BJ) Dispersion energy=       -0.0018363766 Hartrees.
Nuclear repulsion after empirical dispersion term =       41.9082499513 Hartrees.
```

### Built-in dispersion-corrected functionals

These functionals work directly without `EmpiricalDispersion`:
- `B2PLYPD3`, `B97D3` — DFT-D3(BJ) built-in
- `B97D`, `wB97XD`, `B2PLYPD` — DFT-D2 built-in

### G09 A/B/C (before D.01)

No DFT-D3 support. Use functionals with built-in dispersion:
- `wB97XD` — good for most weak interactions
- `M062X` — slightly better than wB97XD for some systems
- `B2PLYPD` — double-hybrid, higher accuracy

Both wB97XD and M062X are significantly slower than B3LYP.

### G03

No DFT-D support at all. Use `M052X` (only in later G03 versions).

## Custom DFT-D3 parameters (Gaussian 16)

For functionals not built into Gaussian (TPSSh, MN15, MN15L, BHandHLYP, etc.), use IOp to define D3 parameters:

**IOp mapping (parameter × 1,000,000):**
| IOp | Parameter |
|-----|-----------|
| IOp(3/174) | S6 |
| IOp(3/175) | S8 |
| IOp(3/176) | SR6 (zero-damping) |
| IOp(3/177) | A1 (BJ-damping) |
| IOp(3/178) | A2 (BJ-damping) |

**Examples:**

```
! TPSSh-D3(BJ)
# TPSSh/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=2238200,3/177=452900,3/178=4655000)

! MN15L-D3(0)
# MN15L/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=0,3/176=3338800)

! MN15-D3(BJ)
# MN15/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=786200,3/177=2097100,3/178=7592300)

! BHandHLYP-D3(BJ)
# BHandHLYP/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=1035400,3/177=279300,3/178=4961500)

! BHandHLYP-D3(0)
# BHandHLYP/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=1442000,3/176=1370000)
```

**CRITICAL WARNING:** When Gaussian runs multi-step tasks (e.g., `opt freq`), **IOp settings only apply to the first step**. The freq step will NOT receive the custom D3 parameters, causing opt and freq to use different methods — a serious inconsistency. **Solution:** Run opt and freq as separate calculations.

## Common mistakes

| Mistake | Consequence | Fix |
|---------|------------|-----|
| `# B3LYP/def2-SVP opt freq em=GD3BJ` + IOp | freq uses wrong D3 parameters | Separate opt and freq into two jobs |
| B3LYP without D3 for weak interaction | Cannot find minimum; wrong energies | Always use `em=GD3BJ` |
| Adding D3 to wB97XD | Double-correction | wB97XD already has DFT-D2 built-in |
| M06-2X with D3(BJ) | Double-counting of medium-range correlation | Use D3(0) or nothing for M06-2X |
| G09 D.01 D3(BJ) frequency | Missing r⁻⁸ term → false imaginary frequencies | Use G09 E.01+, or use D3(0) for opt+freq in D.01 |

## Recommended functional + D3 combinations

| Study type | Recommended level |
|-----------|-------------------|
| **General weak interaction** | `B3LYP-D3(BJ)/def2-SVP` — fast, reliable, well-validated |
| **Higher accuracy** | `B3LYP-D3(BJ)/def2-TZVP` → `PWPB95-D3/def2-TZVP` SP |
| **Organic molecules (non-weak)** | `B3LYP-D3(BJ)/def2-SVP` — D3 adds universality |
| **Transition metal** | `TPSSh-D3(BJ)/def2-SVP` |
| **Conformational search** | `B3LYP-D3(BJ)` — final refinement level |
| **High-precision benchmark** | `wB97X-V` or `DSD-PBEP86-D3(BJ)` |

## DFT-D3 program (standalone)

Grimme's standalone DFT-D3 program computes dispersion energy and gradients for any structure. Useful for:
- Analyzing pairwise atomic dispersion contributions
- Computing intermolecular dispersion energy decomposition
- Fragment-based dispersion analysis

**Usage:**
```bash
./dftd3 test.xyz -func b3-lyp -bj          # D3(BJ) correction
./dftd3 test.xyz -func b-lyp -zero         # D3(0) correction
./dftd3 test.xyz -func b3-lyp -bj -anal    # pairwise contribution analysis
./dftd3 test.xyz -func b3-lyp -bj -grad    # gradients
./dftd3 test.xyz -func b3-lyp -bj -abc     # three-body term
```

**Functional name format:** Must follow Turbomole convention: `b3-lyp`, `pbe0`, `b-lyp`, `cam-b3lyp`, `m062x`, `b2-plyp`, etc.

**Fragment analysis:** Create a `fragment` file in the working directory:
```
2-4
1,6
```
This defines fragment 1 (atoms 2-4), fragment 2 (atoms 1,6), and fragment 3 (remaining atom 5). Output shows intra-fragment and inter-fragment dispersion energies.

## References

- sobereva.com/83 — DFT-D overview
- sobereva.com/413 — When DFT-D3 is needed
- sobereva.com/705 — Multiwfn atomic dispersion contribution analysis
- sobereva.com/709 — Atomic C6 dispersion coefficient calculation
- sobereva.com/685 — sobEDA energy decomposition with dispersion
- J. Chem. Phys., 132, 154104 (2010) — DFT-D3
- J. Comput. Chem., 32, 1456 (2011) — DFT-D3(BJ)
- Phys. Chem. Chem. Phys., 19, 32184 (2017) — GMTKN55 benchmark
- J. Mol. Model., 19, 5387 (2013) — B3LYP vs B3LYP-D3 for dimers
