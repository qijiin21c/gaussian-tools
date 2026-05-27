---
name: large-system-weak-interaction
description: This skill should be used when the user asks to "large system weak interaction", "大体系弱相互作用", "hundreds of atoms DFT", "weak interaction cost", "RI density fitting Gaussian", "Gaussian large system slow", "how to speed up weak interaction calculation", "basis set for large weak interaction", "gCP Gaussian", "ONIOM weak interaction", "semi-empirical weak interaction Gaussian", or mentions calculating weak interactions for large molecular systems in Gaussian including density fitting, cost considerations, and method selection for systems of various sizes.
version: 0.1.0
---

# Large System Weak Interaction Calculations in Gaussian

Practical guidance for computing weak interactions in large systems using Gaussian, based on Sobereva's article (sobereva.com/214).

**Core reality:** Gaussian, even with DFT-D, struggles with large weak interaction systems. For 100+ atom systems without symmetry, Gaussian requires significantly higher computational cost compared to programs with advanced density fitting (like ORCA). Understanding Gaussian's capabilities and limitations is essential for choosing feasible calculation strategies.

## Gaussian's limitations for large weak interaction systems

| Aspect | Gaussian status | Impact |
|--------|----------------|--------|
| **Density fitting (RI)** | RI-J only; no RI-K, no RI-MP2, no COSX | Hybrid functionals not accelerated for exchange part |
| **Auxiliary basis sets** | Very limited built-in; mostly auto-generated | Auto-generated auxiliary bases are larger → slower |
| **gCP** | Not supported (as of G16) | Must use counterpoise for BSSE (3× cost) |
| **Symmetry** | Supported, but large weak interaction systems rarely have symmetry | Cannot rely on symmetry for speedup |
| **Semi-empirical** | Only PM6; no dispersion-corrected variants (PM6-D3H4, PM7, etc.) | Limited options for very large systems |

## Gaussian density fitting performance

Gaussian supports RI-J via built-in or auto-generated auxiliary basis sets:

| Method | Syntax | Acceleration | Error |
|--------|--------|-------------|-------|
| **Built-in TZVPfit** | `BLYP/TZVP/TZVPfit` | ~2.7× | 2.26 kcal/mol (unacceptable) |
| **Auto-generated** | `BLYP/TZVP/Auto` | ~2.0× | 0.90 kcal/mol (marginal) |

**Verdict:** Gaussian's RI acceleration is modest and introduces non-negligible error. The limited auxiliary basis set support means Gaussian's density fitting is far less effective than specialized implementations.

## Recommended approaches in Gaussian by system size

### >500 atoms: Semi-empirical (limited options)

Gaussian only supports PM6 without dispersion correction — inadequate for weak interactions.

**Recommendation:** Use external programs (MOPAC with PM6-D3H4, xtb with GFN-xTB) for initial structures and energy estimates, then use Gaussian for smaller fragment calculations.

### 100-500 atoms: GGA + DFT-D3 + minimal basis

```
# BLYP/6-31G* EmpiricalDispersion=GD3BJ
```

**Constraints:**
- Even at this level, 100+ atom calculations are challenging on typical hardware
- No symmetry → very long computation times
- 6-31G* is below the recommended minimum for weak interactions — BSSE will be significant
- Counterpoise correction is prohibitively expensive (3× single-point cost)

**If you can afford 6-31+G\*\*:**
```
# BLYP/6-31+G** EmpiricalDispersion=GD3BJ
```
This is the absolute minimum for credible weak interaction calculations.

### 50-100 atoms: GGA or hybrid + DFT-D3 + double-zeta

```
# BLYP-D3(BJ)/def2-SVP
# or:
# B3LYP-D3(BJ)/def2-SVP
```

- GGA (BLYP) is significantly faster than hybrid (B3LYP) in Gaussian — no RI-K acceleration for exchange
- def2-SVP lacks diffuse functions; BSSE will be significant
- Consider: is this system small enough to use a better program?

### 20-50 atoms: Standard DFT-D3 approach

```
# B3LYP-D3(BJ)/6-31+G**
# or for better accuracy:
# B3LYP-D3(BJ)/def2-TZVP
```

This is where Gaussian becomes practical. DFT-D3 handles dispersion; 6-31+G\*\* is the minimum credible basis.

### <20 atoms: High-level methods feasible

```
# DSDPBEP86/jul-cc-pVTZ em=GD3BJ    (G16)
# or:
# CCSD(T)/aug-cc-pVTZ counterpoise=2
```

## Why GGA over hybrid for large systems in Gaussian

For large systems in Gaussian, **GGA functionals (BLYP, PBE, revPBE) are preferred over hybrids (B3LYP, PBE0)** when cost is a concern:

| Factor | GGA | Hybrid |
|--------|-----|--------|
| HF exchange | None | Must compute 4-center integrals |
| RI acceleration | RI-J accelerates entire calculation | Only Coulomb part accelerated (RI-J); exchange not accelerated in Gaussian |
| Speed difference | 3-10× faster than hybrid for large systems | — |

**For weak interactions with DFT-D3:** GGA-D3 and hybrid-D3 performance differences are small. B3LYP-D3 is only slightly better than BLYP-D3 quantitatively, with no qualitative difference. The cost savings of GGA outweigh the marginal accuracy gain.

## BSSE considerations for large systems

| Basis set | BSSE severity | Correction option in Gaussian |
|-----------|--------------|-------------------------------|
| def2-QZVP | Negligible | Skip correction |
| aug-cc-pVTZ | Small | Skip or counterpoise |
| def2-TZVP | Moderate | Counterpoise (3× cost) |
| 6-311+G\*\* | Moderate | Counterpoise (3× cost) |
| def2-SVP / 6-31+G\*\* | Significant | Counterpoise (3× cost) |
| 6-31G\* | Severe | Counterpoise essential (3× cost) |

**gCP is NOT available in Gaussian.** gCP provides "free" BSSE correction (like DFT-D3 for dispersion) but is only supported in ORCA.

**Practical advice for large systems:**
- If BSSE correction is essential but counterpoise is too expensive, use the largest basis set you can afford and acknowledge the limitation
- For intermolecular interactions, adding diffuse functions reduces BSSE more effectively than increasing zeta level

## ONIOM and QM/MM: NOT recommended for large weak interactions

**ONIOM/QM/MM has limited utility for large system weak interaction studies:**

1. PM6 (Gaussian's best semi-empirical) doesn't handle weak interactions well — the low-level region will be poorly described
2. Partitioning boundaries are arbitrary and introduce errors potentially larger than the semi-empirical method's own errors
3. QM/MM requires force field parameterization — operationally complex
4. PM6-D3H4/PM7 with MOZYME (in MOPAC) can handle large systems directly, making hybridization unnecessary

**Alternative:** Extract a model system (active site + key interaction partners), cap edges with methyl groups, and compute at DFT-D3 level.

## Mixed basis set approach

For a large molecule binding a small molecule:
- Use larger basis (with diffuse) on the interaction region
- Use smaller basis on distant parts

This reduces cost while maintaining accuracy where it matters. Implementation is straightforward in Gaussian via element-specific basis set assignment.

## Model system simplification

Reduce the system to a model containing only key interaction regions:
- Keep the binding site and immediately surrounding residues
- Cap dangling bonds with methyl groups
- Optionally treat distant atoms as background point charges

This approach is simpler than QM/MM and often sufficient. Requires chemical intuition to avoid over-simplification.

## Practical Gaussian keywords for large systems

### Maximum cost savings

```
# BLYP/6-31G* EmpiricalDispersion=GD3BJ SCF=conver=6
```

- `SCF=conver=6`: Relaxed SCF convergence (default `tight` in G09+ is unnecessarily strict)
- Use `SCF=XQC` only if SCF fails to converge

### Moderate cost

```
# BLYP/6-31+G** EmpiricalDispersion=GD3BJ
```

### Best accuracy feasible in Gaussian

```
# B3LYP-D3(BJ)/def2-TZVP
```

## Gaussian vs other programs: realistic expectations

For large weak interaction systems, Gaussian's performance is significantly behind programs with advanced density fitting + COSX:

**Example (37-atom system, def2-TZVP, per-iteration time):**
| Program | BLYP | B3LYP |
|---------|------|-------|
| Gaussian | 3.0 min/iter | 9.3 min/iter |
| With RI | 0.25 min/iter (12×) | No RI-K support |

**Example (37-atom system, B3LYP/def2-TZVP total):**
- Gaussian: ~102 min
- Program with RIJK: ~12 min (8.5× faster)

**For large systems (>100 atoms):** Consider using specialized programs for the energy calculation, and Gaussian only if necessary.

## When Gaussian IS the right choice

Gaussian remains appropriate for:
- Systems <50 atoms with standard basis sets
- Calculations requiring features unique to Gaussian (e.g., specific solvent models, certain analysis methods)
- When results must be directly comparable to previous Gaussian-based studies
- When the user's expertise is primarily in Gaussian

## References

- sobereva.com/214 — This article (large system weak interactions)
- sobereva.com/210 — DFT-D usage
- sobereva.com/83 — DFT-D overview
- sobereva.com/46 — BSSE and counterpoise
- sobereva.com/615 — 18-carbon ring + graphene interaction (large system case study)
- sobereva.com/217 — PM7/PM6-DH+ base pair optimization issues
- sobereva.com/388 — Grimme's contributions including xtb
- sobereva.com/421 — Gaussian + xTB coupling
- J. Chem. Phys., 136, 154101 (2012) — gCP
- Chem. Eur. J., 18, 9955 (2012) — S12L benchmark
