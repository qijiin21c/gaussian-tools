# Implicit Solvent Model Theory

Detailed discussion of implicit solvent models, their components, and proper usage in Gaussian, based on Sobereva's article (sobereva.com/327).

## What are implicit solvent models?

Implicit (continuum) solvent models treat the solvent as a polarizable continuous medium rather than explicit individual solvent molecules. The solute sits in a cavity within this continuum, and the continuum responds to the solute's charge distribution.

### Advantages over explicit solvent
- Captures average solvent effect without enumerating solvent configurations
- Computationally cheap — minimal overhead compared to gas-phase calculation
- Widely used in both quantum chemistry and molecular simulation

### Limitations
- Cannot model **hydrogen bonding** (specific directional interactions)
- Cannot model **solvent catalysis** (solvent molecules participating in reaction)
- Cannot model **solute-solvent charge transfer** in electronic excitation
- Lower accuracy for **ionic solutes** than neutral molecules

### Common implicit solvent models

| Model | Full name | Quality |
|-------|-----------|---------|
| **IEFPCM** | Integral Equation Formalism PCM | Best PCM variant — Gaussian's default |
| **PCM** | Polarizable Continuum Model | General framework |
| **CPCM** | Conductor-like PCM | Approximation — **avoid in Gaussian** |
| **COSMO** | Conductor-like Screening MOdel | Approximation — implemented as CPCM in Gaussian |
| **Onsager** | Reaction field model | Simple, outdated |
| **IPCM** | Iterative PCM | Self-consistent cavity |
| **SCIPCM** | Self-consistent IPCM | Full self-consistency |
| **SMD** | Solvation Model based on Density | **Best overall** — recommended |
| **SMx** | Solvation Model x (SM12, etc.) | Good, Truhlar group |
| **uESE** | Universal Electrostatic Solvation Energy | Best for charged polyatomic ions |

## Polar vs non-polar contributions

### Polar part
The dominant contribution. Describes:
- Solvent-solute electrostatic interaction
- Polarization of solute electron distribution by solvent

All implicit solvent models define the polar part. Getting this wrong leads to **qualitatively incorrect** results.

### Non-polar part
Secondary but essential for quantitative accuracy. Includes:
- **Cavity formation work**: energy to create the solute cavity in solvent
- **Solvent entropy effects**: how solute affects solvent molecule entropy
- **Exchange-repulsion**: solute-solvent Pauli repulsion
- **Dispersion attraction**: solute-solvent van der Waals attraction

**Only SMD and SMx series explicitly define the non-polar part.** For PCM/CPCM/COSMO, the non-polar treatment is program-dependent and less rigorously parameterized.

### How different models handle non-polar part

| Model | Non-polar treatment |
|-------|-------------------|
| **SMD** | Explicitly defined, parameterized at multiple theory levels |
| **SMx (SM12, etc.)** | Explicitly defined, parameterized |
| **PCM/CPCM/COSMO** | Not explicitly defined — Gaussian computes it via `Dis/Rep/Cav` keywords |
| **Onsager** | Not defined |

For PCM/CPCM in Gaussian, add after a blank line following coordinates:
```
Dis
Rep
Cav
```
This computes dispersion, repulsion, and cavity terms and adds them to the output energy.

## Why SMD is the best choice

SMD (Solvation Model based on Density, J. Phys. Chem. A, 113, 6378, 2009) is superior because:
1. **Best non-polar functional form** — more physically motivated than earlier models
2. **Careful parameterization** — fitted at multiple theory levels against experimental solvation free energies
3. **Best accuracy** — top-ranked for solvation free energy among all continuum models

For tasks where only the polar part matters (geometry optimization, frequency), SMD and IEFPCM give nearly identical results. SMD's advantage comes from its superior non-polar treatment, which only matters for energy calculations.

## Why NOT to use CPCM or COSMO in Gaussian

**COSMO** is an approximation of PCM that assumes the solvent is a perfect conductor (infinite dielectric constant), then approximates back to the actual dielectric constant. This simplification was implemented because it's computationally cheaper and easier to code.

**CPCM** is Gaussian's name for COSMO. It's NOT a better model — it's a worse approximation. Programs like DMol3 only support COSMO not because it's better, but because the developers didn't implement the full PCM formalism.

**IEFPCM** (Gaussian's default `scrf`) is the best implementation of PCM. There's no reason to use the inferior CPCM.

Additionally, CPCM in Gaussian uses **wrong parameters for neutral systems** (J. Chem. Theory Comput., 11, 4220, 2015). Results are partially unreliable.

**Bottom line: Never write `scrf=CPCM` in Gaussian. The default IEFPCM is better.**

## How implicit solvent affects molecular properties

Since the solvent modifies the potential energy surface, everything derived from the PES changes:

| Property | Solvent effect magnitude |
|----------|------------------------|
| Electronic energy | Significant |
| Excitation energies | Large |
| HOMO-LUMO gap | Large |
| Dipole moment | Large |
| Atomic charges | Large |
| Bond orders | Moderate |
| Geometry | Small (for neutrals), large (for ions) |
| Vibrational frequencies | Small |
| NMR chemical shifts | Small |
| Conformer populations | Can be significant |

**Rule of thumb:** The more polar the solute and solvent, the stronger the solvent effect.

### Geometry: when solvent matters

For most neutral molecules without local charges:
- Gas-phase and solvent-optimized structures are visually indistinguishable
- Vibration frequencies are barely affected
- SMD was parameterized using gas-phase geometries

For molecules with significant local charges (ions, zwitterions, strongly polar functional groups):
- Gas-phase structures may be **qualitatively wrong**
- Solvent optimization is **essential**

**When in doubt, always include solvent during opt/freq.** The cost increase is small for DFT, and it avoids the risk of qualitatively wrong results and reviewer criticism.

### Reaction pathways

Some reactions have completely different PES in solvent vs gas phase:

**Menschutkin reaction:** Reactants are neutral, products are ionic. In gas phase, no TS exists. In solvent, the ionic products are significantly stabilized, creating a well-defined TS.

When studying solution-phase reactions, always include implicit solvent for all calculations. Add explicit solvent molecules when necessary.

## External iteration (externaliteration)

### What it is

For post-HF methods (MP2, CCSD, etc.), the calculation proceeds in two steps:
1. SCF → converged HF wavefunction (density)
2. Post-HF → correlation energy on top of HF

In implicit solvent, the solvent response field is constructed from the HF density. But the post-HF density is different from the HF density. **External iteration** rebuilds the solvent response field based on the post-HF density and iterates until self-consistency.

### When it matters

| Method | Needs externaliteration? |
|--------|------------------------|
| Semi-empirical | No — SCF method, already self-consistent |
| HF | No — SCF method, already self-consistent |
| DFT | No — SCF method, already self-consistent |
| MCSCF | No — SCF method, already self-consistent |
| MP2, CCSD, CCSD(T) | Yes — improves accuracy |
| TDDFT | Yes — analogous to post-HF |

### Misuse

Many users blindly add `externaliteration` to DFT or HF calculations. This is **completely meaningless** — the reaction field is already self-consistent with the SCF density. There's nothing to iterate.

## Custom solvent parameterization

### Built-in solvents
```
scrf(SMD,solvent=ethanol)
```
Supported solvents listed in Gaussian manual under `scrf`. Don't invent names. See bbs.keinsci.com/thread-10624-1-1.html for equivalent names.

### Custom solvent (polar only)
```
scrf(read)
```
After coordinates:
```
eps=23.0
epsinf=3.3
```

These two parameters are the most important. The polar part depends ONLY on these.

- `eps`: Static dielectric constant — easily found in literature
- `epsinf`: Optical (high-frequency) dielectric constant — estimate as n² (refractive index squared)

**When is epsinf needed?**
- TDDFT: required
- Frequency-dependent (hyper)polarizability: required
- Frequency calculation: required but value doesn't matter
- NMR: required but value doesn't matter

**If refractive index unknown:**
- Non-polar solvent: epsinf = eps
- Polar solvent: epsinf ≈ 1.9 (typical for most polar solvents)

### Custom solvent (full SMD)
```
scrf(read,SMD,solvent=generic)
```
After coordinates:
```
eps=11.5
epsinf=2.0449
HBondAcidity=0.229
HBondBasicity=0.265
SurfaceTensionAtInterface=61.24     ! cal/mol/Å²
CarbonAromaticity=0.12              ! fraction of aromatic carbons
ElectronegativeHalogenicity=0.24    ! fraction of halogen atoms
```

**The problem:** HBondAcidity and HBondBasicity come from Abraham parameters — unavailable for new solvents.

**Best workaround:** Use `scrf(read,SMD,solvent=AAA)` where AAA is the closest built-in solvent. Non-polar parameters are borrowed from AAA.

### Mixed solvents
Mix all parameters by volume ratio. SMD parameters for built-in solvents are in the MN-SDD database: comp.chem.umn.edu/solvation/mnsddb.pdf

### Water mixtures
Water has special SMD treatment without direct non-polar parameter correspondence. No perfect solution exists.

**Recommended approach:**
1. Compute ΔG_solv in pure water
2. Compute ΔG_solv in pure co-solvent
3. Weight-average by volume ratio

## Cavity definition in Gaussian

Gaussian 09/16 default cavity construction:
- Overlapping atomic spheres
- Atomic radii = UFF van der Waals radii × 1.1
- **Independent of solvent radius definition**

Defining solvent radii in the input (as seen in some old tutorials) is **completely unnecessary** for G09/16 unless you explicitly request solvent-accessible surface cavity definition.

## References

- sobereva.com/327 — This article (solvation free energy)
- sobereva.com/42 — Implicit solvent models in molecular simulation
- sobereva.com/297 — Symmetry and nosymm keyword
- sobereva.com/373 — Pseudopotential basis set selection
- sobereva.com/431 — SMD model for ionic liquid solvents
- sobereva.com/593 — uESE solvent model for ions
- sobereva.com/314 — TDDFT with solvent models in Gaussian
- sobereva.com/469 — SAPT energy decomposition
- J. Phys. Chem. A, 114, 13442 (2010) — Correct use of continuum solvent models
- J. Phys. Chem. A, 113, 6378 (2009) — SMD model
- J. Chem. Theory Comput., 11, 4220 (2015) — CPCM parameter error
- J. Phys. Chem. A, 122, 1392 (2018) — Translational/rotational entropy corrections unnecessary
- J. Phys. Chem. B, 115, 14556 (2011) — Response to COSMO comment
- J. Phys. Chem. A, 102, 7787 (1998) — Proton solvation free energy
- J. Phys. Chem. B, 110, 16066 (2006) — Verification of proton solvation data
- comp.chem.umn.edu/solvation/mnsddb.pdf — MN-SDD solvent descriptor database
