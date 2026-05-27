# SMD-GIL Parameters and Usage

Complete SMD-GIL parameter tables, parameter computation for common ionic liquids, and usage strategies, based on Sobereva's article (sobereva.com/431) and the original JPCB paper (J. Phys. Chem. B, 116, 9122, 2012).

## SMD-GIL averaged parameters

The SMD-GIL (Generic Ionic Liquid) model uses averaged experimental parameters across many common ionic liquids. From JPCB, 116, 9122 (2012):

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Static dielectric constant (eps)** | 11.5 | Typical for many ILs (range ~10-15) |
| **Refractive index (n)** | 1.43 | → epsinf = n² = 2.0449 |
| **Abraham hydrogen bond acidity** | 0.229 | Average across tested ILs |
| **Abraham hydrogen bond basicity** | 0.265 | Average across tested ILs |
| **Surface tension at interface** | 61.24 cal/mol/Å² | Gas-liquid interface at 298K |

These parameters work as defaults for any ionic liquid when specific experimental data is unavailable.

## Computing CarbonAromaticity and ElectronegativeHalogenicity

These two parameters are specific to each ionic liquid and must be computed from the chemical formula.

### CarbonAromaticity

```
CarbonAromaticity = (number of aromatic carbon atoms) / (total number of heavy atoms)
```

Heavy atoms = all non-hydrogen atoms.

### ElectronegativeHalogenicity

```
ElectronegativeHalogenicity = (number of halogen atoms) / (total number of heavy atoms)
```

Halogens = F, Cl, Br, I.

## Examples

### [BMIM][NTf2] (1-butyl-3-methylimidazolium bis(trifluoromethylsulfonyl)imide)

**Formula:** C₁₀H₁₅F₆N₃O₄S₂

| Property | Value |
|----------|-------|
| Heavy atoms | 10 C + 6 F + 3 N + 4 O + 2 S = 25 |
| Aromatic carbons | 3 (imidazole ring) |
| Halogen atoms | 6 (F) |
| **CarbonAromaticity** | 3/25 = **0.12** |
| **ElectronegativeHalogenicity** | 6/25 = **0.24** |

### [BMIM][PF6] (1-butyl-3-methylimidazolium hexafluorophosphate)

**Formula:** C₈H₁₅F₆N₂P

| Property | Value |
|----------|-------|
| Heavy atoms | 8 C + 6 F + 2 N + 1 P = 17 |
| Aromatic carbons | 3 (imidazole ring) |
| Halogen atoms | 6 (F) |
| **CarbonAromaticity** | 3/17 ≈ **0.176** |
| **ElectronegativeHalogenicity** | 6/17 ≈ **0.353** |

### [EMIM][BF4] (1-ethyl-3-methylimidazolium tetrafluoroborate)

**Formula:** C₆H₁₁BF₄N₂

| Property | Value |
|----------|-------|
| Heavy atoms | 6 C + 1 B + 4 F + 2 N = 13 |
| Aromatic carbons | 3 (imidazole ring) |
| Halogen atoms | 4 (F) |
| **CarbonAromaticity** | 3/13 ≈ **0.231** |
| **ElectronegativeHalogenicity** | 4/13 ≈ **0.308** |

### [BMIM][BF4] (1-butyl-3-methylimidazolium tetrafluoroborate)

**Formula:** C₈H₁₅BF₄N₂

| Property | Value |
|----------|-------|
| Heavy atoms | 8 C + 1 B + 4 F + 2 N = 15 |
| Aromatic carbons | 3 (imidazole ring) |
| Halogen atoms | 4 (F) |
| **CarbonAromaticity** | 3/15 = **0.20** |
| **ElectronegativeHalogenicity** | 4/15 ≈ **0.267** |

## Common ionic liquid experimental parameters

From JPCB, 116, 9122 (2012), Tables 1 and 3. Representative values:

| IL | eps | n | H-bond acidity | H-bond basicity | Surface tension (cal/mol/Å²) |
|----|-----|---|---------------|----------------|----------------------------|
| [BMIM][BF4] | 11.9 | 1.422 | 0.331 | 0.395 | 50.3 |
| [BMIM][PF6] | 11.0 | 1.410 | 0.174 | 0.218 | 45.2 |
| [BMIM][NTf2] | 11.8 | 1.428 | 0.194 | 0.257 | 60.4 |
| [EMIM][BF4] | 12.2 | 1.420 | 0.356 | 0.402 | 55.1 |
| [EMIM][NTf2] | 12.5 | 1.430 | 0.180 | 0.240 | 59.8 |

Check the original paper for complete parameter tables. The MN-SDD database (comp.chem.umn.edu/solvation/mnsddb.pdf) may also have some values.

## Mixed parameter strategies

### Strategy 1: All SMD-GIL
Use all SMD-GIL averaged parameters + computed aromaticity/halogenicity.

**Pros:** Simple, no literature search needed.
**Cons:** May miss specific IL characteristics.

### Strategy 2: Experimental + SMD-GIL fill-in
Use available experimental parameters (eps, n, surface tension) and SMD-GIL averages for missing ones (usually Abraham acidity/basicity).

**Pros:** Best practical accuracy.
**Cons:** Requires literature search.

### Strategy 3: Closest built-in solvent
Use `scrf(read,SMD,solvent=AAA)` where AAA is the closest built-in solvent, with eps/epsinf set to the IL values.

**Pros:** Borrows non-polar parameters from a well-characterized solvent.
**Cons:** AAA may not be chemically similar to the IL.

## Input file templates

### Full SMD with IL-specific parameters

```
# M052X/6-31G* SCRF(SMD,read,solvent=generic)

B3LYP/TZVP optimized geometry

0 1
[coordinates]

eps=11.8
epsinf=2.0449
HBondAcidity=0.194
HBondBasicity=0.257
SurfaceTensionAtInterface=60.4
CarbonAromaticity=0.12
ElectronegativeHalogenicity=0.24
```

### SMD-GIL defaults + computed aromaticity/halogenicity

```
# M052X/6-31G* SCRF(SMD,read,solvent=generic)

B3LYP/TZVP optimized geometry

0 1
[coordinates]

eps=11.5
epsinf=2.0449
HBondAcidity=0.229
HBondBasicity=0.265
SurfaceTensionAtInterface=61.24
CarbonAromaticity=0.20
ElectronegativeHalogenicity=0.267
```

### Polar part only (qualitative)

```
# M052X/6-31G* SCRF(read)

B3LYP/TZVP optimized geometry

0 1
[coordinates]

eps=11.5
epsinf=2.0449
```

## References

- sobereva.com/431 — This article (ionic liquid SMD)
- sobereva.com/327 — Solvation free energy fundamentals
- J. Phys. Chem. B, 116, 9122 (2012) — SMD-GIL model and validation
- comp.chem.umn.edu/solvation/mnsddb.pdf — MN-SDD solvent descriptor database
