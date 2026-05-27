---
name: solvation-free-energy
description: This skill should be used when the user asks to "solvation free energy", "溶剂化自由能", "溶解自由能", "solvated free energy", "体系在溶剂下的自由能", "SCRF free energy", "SMD solvation", "PCM solvation", "solvation Gibbs", "standard state correction 1.89", "M05-2X/6-31G* SMD", "implicit solvent free energy", "custom solvent SMD", "mixed solvent", "externaliteration", "uESE solvent model", "single ion solvation", or mentions calculating solvation free energy or solution-phase free energy using implicit solvent models in Gaussian.
version: 0.1.0
---

# Solvation Free Energy and Solution-Phase Free Energy

Guide to calculating solvation free energy and system free energy under implicit solvent models in Gaussian, based on Sobereva's article (sobereva.com/327).

**Core formulas:**

| Quantity | Formula |
|----------|---------|
| **Solvation free energy (ΔG_solv)** | E_solvent - E_gas (both at same geometry, same level) |
| **Solution-phase free energy (G_soln)** | G_gas(1 atm) + ΔG_solv(1M→1M) + 1.89 kcal/mol |

The 1.89 kcal/mol correction converts gas-phase 1 atm standard state to 1 M standard state at 298.15 K.

## Quick reference: Solvent model selection

| Task | Recommended | Why |
|------|------------|-----|
| **Geometry optimization** | `scrf` (default IEFPCM) | Stable convergence, no spurious imaginary frequencies |
| **Frequency calculation** | `scrf` (default IEFPCM) | Same reason; non-polar part negligible for freq |
| **Solvation free energy** | `scrf(SMD,solvent=xxx)` | Best accuracy — SMD parameterized for ΔG_solv |
| **Single-point energy in solvent** | `scrf(SMD,solvent=xxx)` | Includes polar + non-polar contributions |
| **TDDFT in solvent** | `scrf(SMD,solvent=xxx)` | Best for excited-state solvent effects |

**Personal recommended workflow:** Use IEFPCM for opt/freq, SMD for single-point energy and solvation free energy. Results are nearly identical for these tasks since the polar part dominates.

## Pre-solvation checklist

- [ ] **Don't use CPCM in Gaussian** — It's a buggy approximation of PCM. IEFPCM (Gaussian's default) is the correct implementation of PCM. CPCM gives unreliable results for neutral systems (JCTC, 11, 4220, 2015).
- [ ] **Don't use COSMO** — It's a conductor approximation, less accurate than IEFPCM.
- [ ] **SMD for ΔG_solv, IEFPCM for opt/freq** — SMD can cause convergence issues and spurious imaginary frequencies for flexible systems during opt/freq.
- [ ] **Include non-polar part for SMD** — Automatic with `scrf(SMD,...)`. For IEFPCM, must add `scrf=read` + `Dis/Rep/Cav` at end of input.
- [ ] **Never use `externaliteration` for SCF methods** — It's only meaningful for post-HF and TDDFT. Using it for HF, DFT, semi-empirical, or MCSCF is nonsensical.

## Implicit solvent model basics

### What implicit solvent models do
Treat solvent as a polarizable continuum medium — no explicit solvent molecules. Captures average solvent effect without enumerating solvent configurations.

**Advantages:** Fast, captures mean-field solvent effect.
**Limitations:** Cannot model hydrogen bonding, specific solvent-solute interactions, solvent catalysis, or solute-solvent charge transfer in excited states. Ionic solutes have lower accuracy than neutrals.

### Polar vs non-polar contributions

| Part | What it represents | Models that define it |
|------|-------------------|----------------------|
| **Polar** | Solvent-solute electrostatic interaction, solute polarization | All models (PCM, CPCM, SMD, COSMO, etc.) |
| **Non-polar** | Cavity formation work, dispersion, exchange-repulsion, solvent entropy effects | SMD, SMx series (explicitly defined); PCM/COSMO (program-dependent) |

**For quantitative solvation free energy, non-polar part is essential.** SMD's non-polar treatment is the best available.

### Effect of solvent on molecular properties

| Properties affected significantly | Properties affected minimally |
|-----------------------------------|------------------------------|
| Excitation energies | Geometry (for neutral molecules) |
| HOMO-LUMO gap | NMR chemical shifts |
| Dipole moment | Vibrational frequencies |
| Atomic charges | |

**Exception:** Molecules with significant local charges (ions, zwitterions) — solvent dramatically affects geometry. **Always use solvent model for opt/freq when charges are present.**

### When to use solvent model during optimization

| Molecule type | Use solvent during opt/freq? |
|---------------|---------------------------|
| Neutral, no local charges | Optional — gas-phase is usually fine |
| Significant local charges | **Required** — gas-phase structure may be qualitatively wrong |
| Uncertain | **Always add it** — small cost, avoids wrong results |

Some reactions only have a TS in solvent (e.g., Menschutkin reaction — products are ionic, gas phase has no TS). When studying solution-phase reactions, always include implicit solvent.

## Solvation free energy calculation

### The formula
```
ΔG_solv = E_solvent - E_gas
```

Both calculations at the **same geometry** and **same theory level**.

### Critical: Use the parameterized level for SMD

SMD was parameterized at **M05-2X/6-31G*** for best solvation free energy accuracy.

| Do this | Don't do this |
|---------|--------------|
| `M05-2X/6-31G* scrf(SMD,solvent=ethanol)` | `CCSD(T)/aug-cc-pVTZ scrf(SMD,solvent=ethanol)` |
| Even for anions: use 6-31G*, NOT 6-31+G* | Adding diffuse functions makes it worse |
| For transition metal complexes: still M05-2X/6-31G* | Don't worry that M05-2X is poor for TM — ligands dominate solvation |

**M05-2X/6-31G* has essentially only one good use:** computing solvation free energy with SMD. For everything else, use a more appropriate level.

### Standard state correction

Chemical standard states differ:
- Gas phase: 1 atm (≈ 1/24.46 M at 298.15 K)
- Solution: 1 M

Implicit solvent models compute ΔG for 1M(gas) → 1M(solution). To compare with experimental values (1 atm → 1M), add:

```
ΔG_solv(corrected) = ΔG_solv(raw) + 1.89 kcal/mol   (at 298.15 K)
```

### Temperature dependence

Implicit solvent parameters are fit to 298.15 K experimental data. **You cannot reliably compute ΔG_solv or ΔH_solv at other temperatures** from implicit solvent models alone. The parameters simply aren't fitted for temperature dependence.

### Dissolution enthalpy and entropy

**Cannot be obtained** from implicit solvent models. The models are parameterized for free energy only — the developers didn't fit parameters for enthalpy or entropy of solvation.

### When to use which structure for ΔG_solv

| Situation | Use |
|-----------|-----|
| Neutral molecules, no local charges | Gas-phase optimized structure (SMD was parameterized this way) |
| Significant solvent effect on structure | Solvent-optimized structure |
| Uncertain | Always optimize in solvent — safe and cheap |

## Solution-phase free energy calculation

### The full formula
```
G_soln(298.15K, 1M) = G_gas(298.15K, 1atm) + ΔG_solv(1M→1M) + 1.89 kcal/mol
```

**Important:** G_gas and ΔG_solv are computed at independent theory levels — each should be as accurate as possible for the combined result to be accurate.

### Three accuracy levels for G_gas

**Level 1 (lazy):**
```
# B3LYP/6-31G* opt freq
```
Read `Sum of electronic and thermal Free Energies=` — cheap but inaccurate. Not publication-quality.

**Level 2 (practical):**
```
# B3LYP/6-31G* opt freq          → get thermal correction to Gibbs Free Energy
# B2PLYP-D3(BJ)/def2-TZVP sp     → get high-accuracy electronic energy
```
G_gas = E_high_precision + Thermal_correction_to_G

**Level 3 (rigorous):**
1. Optimize at B3LYP/6-31G*
2. High-accuracy single-point
3. Use Shermo (sobereva.com/552) with quasi-RRHO model (`ilowfreq=2`) for thermal correction
4. G_gas = E_high_precision + Shermo_G_correction

For flexible systems, Level 3 is **strongly recommended** — Gaussian's RRHO model poorly handles low-frequency modes.

### Composite method shortcut

For small systems where composite methods are feasible:
```
# G4
```
Read `G4 Free Energy=` — this is the gas-phase free energy at high accuracy.

Composite method accuracy ranking: W1 > CBS-APNO ≥ G4 > G4(MP2) > CBS-QB3 > G3(MP2B3). CBS-4M is outdated.

### Quick approximate approach

1. `opt freq` (with or without solvent) → get thermal correction to G or H
2. High-level single-point in solvent → get solvated electronic energy
3. Sum + 1.89 kcal/mol

This is faster but computes ΔG_solv at the high level rather than the SMD-parameterized level — lower accuracy for the solvation part.

## Solvent model settings in Gaussian

### Built-in solvents
```
scrf(SMD,solvent=ethanol)
scrf(SMD,solvent=DMSO)          ! shorthand for DiMethylSulfoxide
```

See Gaussian manual for supported solvents. Don't invent solvent names. See bbs.keinsci.com/thread-10624-1-1.html for equivalent names.

### Custom solvent (polar part only)
```
scrf=read
```
After coordinates (blank line):
```
eps=23.0
epsinf=3.3
```
- `eps`: static dielectric constant (most important parameter)
- `epsinf`: optical dielectric constant — needed for TDDFT, NMR, polarizability. Estimate as n² (refractive index squared). If unknown: non-polar solvent → epsinf = eps; polar solvent → epsinf ≈ 1.9.

### Custom solvent (full SMD)
```
scrf(read,SMD,solvent=generic)
```
After coordinates (blank line):
```
eps=11.5
epsinf=2.0449
HBondAcidity=0.229
HBondBasicity=0.265
SurfaceTensionAtInterface=61.24
CarbonAromaticity=0.12
ElectronegativeHalogenicity=0.24
```

**Problem:** HBondAcidity/Basicity are from Abraham parameters — unavailable for new solvents.

**Best workaround:** `scrf(read,SMD,solvent=AAA)` where AAA is the closest built-in solvent. Borrows non-polar parameters from AAA.

### Mixed solvents
Mix `eps` and `epsinf` by volume ratio. For full SMD, mix all parameters from MN-SDD database (comp.chem.umn.edu/solvation/mnsddb.pdf).

**Water mixtures:** Water has special SMD treatment. Recommended: compute ΔG_solv in pure water and in pure co-solvent separately, then weight-average by volume ratio.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using CPCM in Gaussian | Use default IEFPCM — it's better and correct |
| Using COSMO in Gaussian | It's just a PCM approximation — use IEFPCM |
| `externaliteration` with DFT/HF | Meaningless for SCF methods — only for post-HF and TDDFT |
| M05-2X/6-31G* for everything except solvation | This level is only good for SMD solvation — use better levels for other tasks |
| Adding diffuse functions for SMD solvation of anions | SMD was parameterized with 6-31G*, NOT 6-31+G* |
| Expecting ΔH_solv or ΔS_solv from implicit solvent | Not parameterized — only ΔG_solv is available |
| Computing ΔG_solv at a different temperature | Parameters are for 298.15 K — temperature dependence not modeled |
| Forgetting 1.89 kcal/mol standard state correction | Required to match experimental 1 atm → 1M definition |
| Adding translational/rotational entropy corrections for solvation | Proven to make results worse (JPCA, 122, 1392, 2018) |

## Single ion solvation

Small ions (H⁺, Li⁺, Mg²⁺) **cannot** be computed by simple SMD gas-vs-solvent energy difference. Charge density is too high — strong specific solvent interactions are not captured by continuum models.

- **Proton in water:** Use established value: -265.9 kcal/mol (Tissandier et al., JPCA, 102, 7787, 1998)
- **Other small ions:** Use explicit + implicit solvent model (cluster-continuum approach). See Dixon et al., JPCA, 105, 11534 (2001).
- **Minimum for proton:** At least include one explicit solvent molecule.
- **Transition metal ions:** Must include actual solvation coordination structure.

### uESE model for ions
For +1/-1 charged polyatomic ions, use uESE solvent model — much more accurate than SMD. See sobereva.com/593.

## Additional Resources

- **`references/solvation-theory.md`** — Detailed implicit solvent model theory: polar vs non-polar components, SMD vs PCM comparison, external iteration explanation, why CPCM/COSMO should be avoided, custom solvent parameterization, mixed solvent strategies
- **`references/free-energy-workflow.md`** — Complete worked example (ethylene oxide in ethanol): four-step calculation workflow, three accuracy levels for gas-phase free energy, Shermo quasi-RRHO workflow, composite method alternatives, temperature variation, template input files
