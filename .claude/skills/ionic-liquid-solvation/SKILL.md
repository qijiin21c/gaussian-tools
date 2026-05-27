---
name: ionic-liquid-solvation
description: This skill should be used when the user asks to "ionic liquid solvent", "离子液体溶剂", "SMD-GIL", "ionic liquid solvation", "SMD ionic liquid", "[BMIM]", "[EMIM]", "[NTf2]", "[PF6]", "ionic liquid SMD parameters", "Abraham acidity alkalinity ionic liquid", "generic ionic liquid solvent model", or mentions modeling ionic liquid solvent environments in quantum chemistry calculations using the SMD solvation model.
version: 0.1.0
---

# Ionic Liquid Solvent Environment via SMD

Guide to describing ionic liquid solvent environments using the SMD solvation model in Gaussian, based on Sobereva's article (sobereva.com/431).

**Prerequisite:** Read the `solvation-free-energy` skill first (sobereva.com/327) for foundational knowledge on implicit solvent models and solvation free energy calculation.

## Key insight

Ionic liquids are **not special** from the SMD model's perspective. SMD only needs the solvent's macroscopic parameters — if you provide them, SMD handles ionic liquids the same way it handles ordinary molecular solvents.

The SMD-GIL (Generic Ionic Liquid) model validates this approach (J. Phys. Chem. B, 116, 9122, 2012). Accuracy for ionic liquids is comparable to ordinary solvents, though some (e.g., [EMIM][PF6]) show larger errors.

## Required SMD parameters

| Parameter | Symbol | How to obtain |
|-----------|--------|--------------|
| Static dielectric constant (298K) | `eps` | Literature, experimental |
| Optical dielectric constant | `epsinf` | n² (refractive index squared) |
| Abraham hydrogen bond acidity | — | Abraham papers, or SMD-GIL average |
| Abraham hydrogen bond basicity | — | Abraham papers, or SMD-GIL average |
| Surface tension at gas-liquid interface (298K) | — | cal/mol/Å², literature |
| Carbon aromaticity | — | Aromatic carbons / total heavy atoms |
| Electronegative halogenicity | — | Halogen atoms / total heavy atoms |

**The problem:** Most ionic liquids lack complete experimental parameter sets. Surface tension is often available, but Abraham hydrogen bond acidity/basicity are rarely reported.

## SMD-GIL average parameters

When individual parameters are unavailable, use the SMD-GIL (Generic Ionic Liquid) averaged parameters from JPCB, 116, 9122 (2012):

| Parameter | SMD-GIL value |
|-----------|--------------|
| **eps** | 11.5 |
| **epsinf** | 2.0449 (n = 1.43) |
| **HBondAcidity** | 0.229 |
| **HBondBasicity** | 0.265 |
| **SurfaceTensionAtInterface** | 61.24 cal/mol/Å² |

**You still need to compute manually:**
- **CarbonAromaticity** = aromatic carbons / total heavy (non-hydrogen) atoms
- **ElectronegativeHalogenicity** = halogen atoms / total heavy atoms

## Accuracy

| Approach | Accuracy |
|----------|----------|
| Full experimental parameters | Good — validated in JPCB paper |
| Mixed: experimental + SMD-GIL for missing | Comparable to full experimental |
| All SMD-GIL parameters | Good — accuracy "half a catty vs eight taels" (equivalent) to experimental |

**Recommendation:** Use experimental values when available, SMD-GIL averages for missing parameters. If you can't be bothered to look up experimental values, all SMD-GIL parameters work fine.

## Quick reference: Custom ionic liquid solvent setup

### Full SMD parameters (all available)

```
# M052X/6-31G* SCRF(SMD,read,solvent=generic)

Title

0 1
[coordinates]

eps=11.5
epsinf=2.0449
HBondAcidity=0.229
HBondBasicity=0.265
SurfaceTensionAtInterface=61.24
CarbonAromaticity=0.12
ElectronegativeHalogenicity=0.24
```

### Partial parameters (polar part only)

If you only care about the polar part and don't need non-polar contributions:

```
# M052X/6-31G* SCRF(read)

Title

0 1
[coordinates]

eps=11.5
epsinf=2.0449
```

This skips non-polar contributions — acceptable for qualitative studies but not for quantitative solvation free energy.

## Worked example: Ethanol in [BMIM][NTf2]

### Solute: ethanol
Optimized at B3LYP/TZVP. Compute solvation free energy as:
```
ΔG_solv = E_solvent(M05-2X/6-31G*/SMD) - E_gas(M05-2X/6-31G*)
```

### Ionic liquid: [BMIM][NTf2]
Formula: C₁₀H₁₅F₆N₃O₄S₂
- Heavy atoms (non-H): 25
- Aromatic carbons (imidazole ring): 3
- Halogen atoms (F): 6

**Compute parameters:**
- CarbonAromaticity = 3/25 = 0.12
- ElectronegativeHalogenicity = 6/25 = 0.24
- Other parameters from SMD-GIL averages

### Results
| Calculation | Energy (Hartree) |
|-------------|-----------------|
| Gas-phase SP | -154.9998251 |
| Solvent SP (SMD-GIL) | -155.0061949 |
| ΔG_solv | -3.997 kcal/mol |
| Experiment | -3.76 kcal/mol |

Agreement with experiment is good (error ~0.24 kcal/mol).

## Common ionic liquid SMD parameters

From JPCB, 116, 9122 (2012), Tables 1 and 3. Some representative values:

| Ionic liquid | eps | n | Surface tension |
|-------------|-----|---|----------------|
| [BMIM][BF4] | ~12 | ~1.42 | ~50 cal/mol/Å² |
| [BMIM][PF6] | ~11 | ~1.41 | ~45 cal/mol/Å² |
| [BMIM][NTf2] | ~12 | ~1.43 | ~60 cal/mol/Å² |
| [EMIM][BF4] | ~12 | ~1.42 | ~55 cal/mol/Å² |

Check the original paper for complete parameter tables.

## Workflow for ionic liquid solvation studies

1. **Geometry optimization:** Use any reasonable level (B3LYP/TZVP, etc.) — level doesn't significantly affect ΔG_solv
2. **Gas-phase single-point:** `# M052X/6-31G*`
3. **Solvent single-point:** `# M052X/6-31G* SCRF(SMD,read,solvent=generic)` with ionic liquid parameters
4. **ΔG_solv:** E_solvent - E_gas (both 1M standard state)
5. **Standard state correction:** Add 1.89 kcal/mol if comparing to experimental 1 atm → 1M values

See the `solvation-free-energy` skill for complete free energy computation workflow.

## Limitations

- Implicit solvent cannot capture specific ion pairing or local coordination structures
- Strong directional interactions (e.g., hydrogen bonding between solute and specific ions) are not modeled
- Some ionic liquids (e.g., [EMIM][PF6]) show larger errors — be cautious
- For transition metal ions in ionic liquids, consider explicit coordination structure + implicit solvent (cluster-continuum approach)

## Additional Resources

- **`references/smd-gil-parameters.md`** — Complete SMD-GIL parameter table from JPCB paper, detailed parameter computation for common ionic liquids, aromaticity and halogenicity calculation examples, mixed experimental + SMD-GIL parameter strategies
- **`references/validation-and-accuracy.md`** — JPCB paper validation results, comparison of SMD-GIL vs full experimental parameters, error analysis across different ionic liquids, case studies (ethanol, organic molecules in various ionic liquids)
