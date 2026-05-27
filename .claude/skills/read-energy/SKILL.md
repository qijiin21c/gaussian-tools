---
name: read-energy
description: This skill should be used when the user asks to "read energy from Gaussian output", "Gaussian电子能量", "where to read energy", "SCF Done", "EUMP2", "CCSD(T)=", "HF= archive", "electronic energy", "single point energy", "GaussView Summary energy wrong", "B2PLYP energy", "dual-hybrid energy", "CASSCF energy", "TDDFT total energy", "semi-empirical energy", "molecular mechanics energy", "G4 energy", "CBS-QB3 energy", "ZPE electronic energy", "thermochemical energy", or mentions reading electronic energy values from Gaussian output files for various computational methods.
version: 0.1.0
---

# Reading Electronic Energy from Gaussian Output

Guide to finding the correct electronic energy value in Gaussian output files for different computational methods, based on Sobereva's article (sobereva.com/339).

**Core principle:** The electronic energy is the sum of: (1) electron kinetic energy, (2) electron-electron Coulomb repulsion, (3) nucleus-nucleus Coulomb repulsion, (4) electron-nucleus Coulomb attraction. The energy zero is when all nuclei and electrons are at rest and infinitely separated. **Only energy differences (reaction energies, ionization energies) are chemically meaningful.**

## Quick reference: Where to read energy by method

| Method | Read this label | Archive label | Notes |
|--------|----------------|---------------|-------|
| **HF** | `SCF Done` | `HF=` | Same value |
| **DFT (non-double-hybrid)** | `SCF Done` | `HF=` | Archive uses "HF=" tag but it IS the DFT result |
| **MP2** | `EUMP2 =` | `MP2=` | SCF Done is HF energy, NOT MP2 |
| **Double-hybrid (B2PLYP, etc.)** | `E(B2PLYP) =` | `MP2=` | SCF Done is DFT energy, NOT double-hybrid |
| **CCSD(T)** | `CCSD(T)=` | `CCSD(T)=` | Archive also shows MP2, MP4, CCSD energies |
| **CASSCF** | `EIGENVALUE` (under EIGENVALUES AND EIGENVECTORS OF CI MATRIX) | `HF=` | HF= is the highest-numbered state |
| **TDDFT** | `Total Energy, E(TD-HF/TD-DFT) =` (in excited state section) | Not in archive | Archive `HF=` is ground state only |
| **Semi-empirical (AM1, PM7)** | `SCF Done` | `HF=` | Energy = heat of formation (relative, not absolute) |
| **Molecular mechanics** | `Energy=` | `HF=` | Energy = force field energy (not electronic) |
| **Composite (G4, CBS-QB3)** | Depends — see below | Depends | See composite methods section |

## Important terminology

| Term | Meaning |
|------|---------|
| **Electronic energy** | Total electronic energy at fixed nuclear geometry. Also called "single-point energy" when the task is just computing energy. |
| **Thermodynamic energy (enthalpy, free energy, internal energy)** | Includes nuclear motion contributions (vibration, rotation, translation). Requires frequency calculation. |
| **ZPE (Zero Point Energy)** | Difference between electronic energy and internal energy/enthalpy/free energy at 0K. From nuclear vibration. |

**Key distinction:** Electronic energy does NOT include ZPE. Thermodynamic quantities require a frequency calculation.

## Method-by-method guide

### HF (Hartree-Fock)
- SCF iteration converges → `SCF Done: E(RHF) = -XXX.XXXXXX`
- This is the HF electronic energy
- Archive section: `HF=-XXX.XXXXXX` (same value)

**Note:** HF is completely obsolete. Do not use for publication-quality work.

### DFT (non-double-hybrid)
For B3LYP, M06-2X, PBE0, etc.:
- `SCF Done: E(RB3LYP) = -XXX.XXXXXX`
- This is the DFT electronic energy
- Archive section: `HF=-XXX.XXXXXX` (same value — **the "HF=" tag does NOT mean Hartree-Fock here**)

**Terminology warning:** Do NOT ask "should I use HF energy?" — this is ambiguous. Say "DFT energy at B3LYP level" instead.

### MP2
MP2 has two steps: (1) HF SCF iteration → (2) MP2 correlation correction
- `SCF Done: E(RHF) = -XXX.XXXXXX` → **HF energy, NOT MP2**
- `EUMP2 = -XXX.XXXXXX` → **MP2 energy (read this)**
- Archive: `MP2=-XXX.XXXXXX` (same as EUMP2)

### Double-hybrid functionals (B2PLYP, DSD-PBEP86, etc.)
Double-hybrids have two steps: (1) DFT SCF iteration → (2) MP2-like perturbation correction
- `SCF Done: E(RB2PLYP) = -XXX.XXXXXX` → **DFT energy, NOT double-hybrid**
- `E(B2PLYP) = -XXX.XXXXXX` → **Double-hybrid energy (read this)**
- Archive: `MP2=-XXX.XXXXXX` (same as E(B2PLYP))

**GaussView warning:** GaussView's Results → Summary shows `E(RB2PLYP)` which is the SCF Done value, NOT the actual double-hybrid energy. This is misleading in GaussView 5.0.9 and 6.0.16. **Always read from the output file directly.**

### CCSD(T)
CCSD(T) also has two steps: (1) HF SCF → (2) CCSD(T) correlation
- `SCF Done: E(RHF) = -XXX.XXXXXX` → **HF energy**
- `CCSD(T)= -XXX.XXXXXX` → **CCSD(T) energy (read this)**
- Archive: `CCSD(T)=-XXX.XXXXXX` (same value)
- Archive also contains intermediate energies: MP2, MP2D, MP4, CCSD

### CASSCF
CASSCF is an SCF process. After convergence, outputs energies for all computed states.
- Search for `EIGENVALUES AND EIGENVECTORS OF CI MATRIX`
- Each state's energy follows `EIGENVALUE` on the next line
- Archive: `HF=-XXX.XXXXXX` (energy of the highest-numbered state if multiple states computed)

### TDDFT
TDDFT computes excitation energies on top of a ground-state reference.
- Archive `HF=` → ground-state electronic energy
- In the excited state section for the target root:
  ```
  Total Energy, E(TD-HF/TD-DFT) =  -XXX.XXXXXX
  ```
  This is the excited-state electronic energy (ground-state energy + excitation energy)
- The excited-state energy is **NOT** in the archive section

### Semi-empirical methods (AM1, PM6, PM7, etc.)
- SCF iteration → `SCF Done: E(RAM1) = -XXX.XXXXXX`
- **Important:** Semi-empirical energies are **heats of formation** at standard conditions, NOT absolute electronic energies
- These are **relative energies** with much smaller magnitude than ab initio/DFT energies
- Archive: `HF=-XXX.XXXXXX` (same value)

**Terminology:** "Single-point energy" or simply "energy" is more appropriate than "electronic energy" for semi-empirical methods.

### Molecular mechanics (AMBER, UFF, etc.)
- Search for `Energy= -XXX.XXXXXX`
- This is the force field energy, NOT electronic energy
- Energy zero is when all geometric parameters are at the force field minimum
- Each atom is treated as a point particle — no separate electron/nucleus description
- Archive: `HF=-XXX.XXXXXX` (same value)

**Terminology:** "Energy" or "single-point energy" is more appropriate than "electronic energy."

### Composite thermochemistry methods (G4, G4(MP2), CBS-QB3)

These methods combine geometry optimization, frequency calculation, and high-level electronic energy computation to produce thermochemical quantities.

#### To get the electronic energy at the optimized minimum:
```
Electronic energy = E(0 K) - ZPE
```
Example from G4(MP2) output:
```
E(ZPE)=                     0.021064
G4MP2(0 K)=               -76.355852
Electronic energy = -76.355852 - 0.021064 = -76.376916 Hartree
```

#### To compute single-point energy at the current structure (no optimization, no frequency):
Add `=SP` to the keyword:
```
#p G4MP2=SP
```
Then read: `G4MP2 Energy= -XXX.XXXXXX` or archive `G4MP2=-XXX.XXXXXX`

Other composite methods follow the same pattern with different label names.

## Energy in geometry optimization

- The archive section at the end of the output file shows energies for the **last step's structure**
- The last optimization step's energy corresponds to the optimized geometry
- If you recompute a single-point at the optimized geometry with the **same method and settings**, the energy should match the last optimization step (but may differ if the SCF guess converges to a different wavefunction — optimization uses the previous step's converged wavefunction as guess)

## Energy in other tasks

Tasks like frequency analysis, NMR, and polarizability computations also output electronic energy. If all computational settings are identical to a single-point calculation, the energy will be the same — it's just a byproduct of the main calculation.

## Common mistakes

| Mistake | What happened | Correct approach |
|---------|--------------|-----------------|
| Reading `SCF Done` for MP2 | Got HF energy instead of MP2 | Read `EUMP2 =` |
| Reading `SCF Done` for B2PLYP | Got DFT energy, wasted double-hybrid cost | Read `E(B2PLYP) =` |
| Trusting GaussView Summary for double-hybrid | Summary shows SCF Done, not actual energy | Read from output file |
| Asking "should I use HF energy?" | Ambiguous — could mean HF method or archive `HF=` tag | Say "DFT energy" or "MP2 energy" explicitly |
| Comparing electronic energy to experimental enthalpy | Electronic energy has no ZPE or thermal corrections | Use thermodynamic quantities or add ZPE |
| Mixing semi-empirical with ab initio energies | Different energy zeros — incomparable | Never mix energy scales |

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/energy-details.md`** — Detailed explanation of electronic energy components, energy zero definition, single-point vs optimization vs frequency energy relationships, thermodynamic quantities (internal energy, enthalpy, free energy, ZPE), Shermo program for thermodynamic data, wavefunction guess effects on energy reproducibility
