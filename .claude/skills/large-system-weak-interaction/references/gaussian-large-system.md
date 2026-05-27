# Gaussian Large System Weak Interaction Calculations

Detailed analysis of Gaussian's capabilities and limitations for large system weak interaction calculations, based on Sobereva's article (sobereva.com/214).

## Gaussian's density fitting: detailed analysis

Gaussian supports RI-J (Resolution of Identity for the Coulomb term) but NOT RI-K (exchange), RI-MP2, or COSX (Chain-of-Spheres for exchange). This is a fundamental limitation that makes Gaussian's density fitting far less effective than programs like ORCA.

### Built-in auxiliary basis sets

Gaussian has very few built-in auxiliary basis sets for density fitting. The main one is `TZVPfit` for the TZVP orbital basis:

```
# BLYP/TZVP/TZVPfit
```

This gives ~2.7× speedup but introduces unacceptable error (2.26 kcal/mol in the article's test case).

### Auto-generated auxiliary basis sets

Gaussian can auto-generate auxiliary basis sets on-the-fly:

```
# BLYP/TZVP/Auto
```

This gives ~2.0× speedup with marginal error (0.90 kcal/mol in the test case). The auto-generated auxiliary bases are larger than hand-optimized ones, reducing the speedup advantage.

### Comparison with ORCA

For a 37-atom system with def2-TZVP:

| Program | BLYP per-iter | B3LYP per-iter | BLYP with RI | B3LYP with RI |
|---------|--------------|---------------|-------------|--------------|
| Gaussian | 3.0 min | 9.3 min | 0.25 min (12×) | No RI-K support |
| ORCA | 3.0 min | 9.3 min | 0.1 min (30×) | 0.2 min (47×) |

Total time for a 37-atom B3LYP/def2-TZVP calculation:
- Gaussian: ~102 min
- Program with RIJK+COSX: ~12 min (8.5× faster)

For large systems (>100 atoms), this gap becomes even more pronounced. Gaussian's 2-3× acceleration from RI-J is negligible compared to ORCA's 30× for Coulomb + exchange acceleration.

## Why GGA is preferred over hybrid in Gaussian for large systems

In Gaussian, hybrid functionals (B3LYP, PBE0) compute Hartree-Fock exchange via 4-center integrals that are NOT accelerated by density fitting. Only the Coulomb part benefits from RI-J.

| Factor | GGA (BLYP, PBE) | Hybrid (B3LYP, PBE0) |
|--------|-----------------|---------------------|
| HF exchange | None | Must compute 4-center integrals |
| RI acceleration | RI-J accelerates entire calculation | Only Coulomb part accelerated |
| Speed for large systems | 3-10× faster than hybrid | — |

For weak interactions with DFT-D3, GGA-D3 and hybrid-D3 performance differences are small. B3LYP-D3 is only slightly better than BLYP-D3 quantitatively, with no qualitative difference. The cost savings of GGA outweigh the marginal accuracy gain.

## BSSE correction without gCP

gCP (geometry-based Counterpoise correction) provides "free" BSSE correction and is available only in ORCA. Gaussian does not support gCP.

In Gaussian, BSSE must be corrected via the traditional counterpoise method, which requires 3 calculations (monomer A, monomer B, dimer AB) → 3× the cost of a single-point calculation. For large systems, this is often prohibitive.

**Practical advice for large systems:**
- If BSSE correction is essential but counterpoise is too expensive, use the largest basis set you can afford and acknowledge the limitation
- For intermolecular interactions, adding diffuse functions reduces BSSE more effectively than increasing zeta level
- For 100+ atom systems, def2-SVP or 6-31+G** is often the practical ceiling — BSSE will be significant, but counterpoise is too expensive

## ONIOM/QM/MM detailed limitations for weak interactions

ONIOM/QM/MM has limited utility for large system weak interaction studies in Gaussian:

1. **PM6 limitation:** Gaussian only supports PM6 (without dispersion correction) as its best semi-empirical method. PM6 handles weak interactions terribly, so the low-level region will be poorly described
2. **Partitioning boundary errors:** Arbitrary QM/MM boundaries introduce errors potentially larger than the semi-empirical method's own errors
3. **QM/MM complexity:** Requires force field parameterization — operationally complex and not always available
4. **Better alternatives exist:** PM6-D3H4/PM7 with MOZYME (in MOPAC) can handle large systems directly, making hybridization unnecessary

**Recommended alternative:** Extract a model system containing the active site and key interaction partners, cap edges with methyl groups, and compute at DFT-D3 level. This is simpler than QM/MM and often sufficient.

## Semi-empirical options and their limitations

Gaussian only supports PM6 without dispersion correction — inadequate for weak interactions. For very large systems (>500 atoms):

**Recommendation:** Use external programs for initial structures and energy estimates:
- MOPAC with PM6-D3H4
- xtb with GFN-xTB (sobereva.com/388)

Then use Gaussian for smaller fragment calculations or specific properties that require Gaussian's unique features.

## Gaussian keywords for large systems: detailed explanation

### Maximum cost savings

```
# BLYP/6-31G* EmpiricalDispersion=GD3BJ SCF=conver=6
```

- `SCF=conver=6`: Relaxed SCF convergence. Gaussian's default `tight` convergence in G09+ is unnecessarily strict for large systems
- `SCF=XQC`: Use only if SCF fails to converge (adds quadratically convergent SCF steps)
- 6-31G* is below the recommended minimum for weak interactions — BSSE will be severe

### Moderate cost

```
# BLYP/6-31+G** EmpiricalDispersion=GD3BJ
```

- 6-31+G** is the absolute minimum credible basis for weak interactions
- GGA (BLYP) is significantly faster than hybrid for large systems in Gaussian

### Best accuracy feasible in Gaussian

```
# B3LYP-D3(BJ)/def2-TZVP
```

- def2-TZVP is well-constructed and gives reasonable results for weak interactions
- This is the ceiling for practical Gaussian calculations on moderate-sized systems

### SCF convergence tips for large systems

For large systems with many basis functions, SCF convergence can be problematic:

```
# BLYP/6-31+G** EmpiricalDispersion=GD3BJ SCF=XQC
```

If SCF still fails:
```
# BLYP/6-31+G** EmpiricalDispersion=GD3BJ SCF=(XQC,maxcycle=512)
```

For very large systems, consider using `SCF=conver=6` to relax convergence criteria and speed up calculation.

## Mixed basis set approach

For a large molecule binding a small molecule, use different basis sets on different parts:

- Larger basis (with diffuse) on the interaction region
- Smaller basis on distant parts

Implementation in Gaussian via element-specific basis set assignment:

```
# BLYP/gen EmpiricalDispersion=GD3BJ

# ... geometry ...
O 0 0 0
H 0 0 1
C 5 0 0
H 5 1 0

6-31+G**
O H 0
6-31G*
C H 0
****
```

This reduces cost while maintaining accuracy where it matters.

## Model system simplification

Reduce the system to a model containing only key interaction regions:

1. Keep the binding site and immediately surrounding residues
2. Cap dangling bonds with methyl groups
3. Optionally treat distant atoms as background point charges (via `charge=fragment` or external point charge input)

This approach is simpler than QM/MM and often sufficient. Requires chemical intuition to avoid over-simplification.

## Practical performance expectations

| System size | Feasible level in Gaussian | Approximate time (typical workstation) |
|-------------|---------------------------|--------------------------------------|
| <20 atoms | CCSD(T)/aug-cc-pVTZ | Hours to days |
| 20-50 atoms | B3LYP-D3(BJ)/def2-TZVP | Hours |
| 50-100 atoms | BLYP-D3(BJ)/def2-SVP | Hours to days |
| 100-500 atoms | BLYP/6-31G* GD3BJ | Days to weeks |
| >500 atoms | Semi-empirical (external) | Gaussian not practical |

## When Gaussian IS the right choice

Gaussian remains appropriate for:
- Systems <50 atoms with standard basis sets
- Calculations requiring features unique to Gaussian (e.g., specific solvent models, certain analysis methods)
- When results must be directly comparable to previous Gaussian-based studies
- When the user's expertise is primarily in Gaussian
- When the system has symmetry that Gaussian can exploit (rare for large weak interaction systems)

For large systems (>100 atoms) where the primary goal is accurate weak interaction energies, specialized programs with advanced density fitting (ORCA with RIJK+COSX, or xtb for initial screening) are far more cost-effective.

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
