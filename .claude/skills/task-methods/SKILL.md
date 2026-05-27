---
name: task-methods
description: This skill should be used when the user asks to "what task type is this", "difference between MD and AIMD", "QM/MM vs ONIOM", "what theoretical method to use", "任务类型", "理论方法", "AIMD vs QM/MM", "DFT vs post-HF", "excited state dynamics", "ab initio MD", "first-principles", "wavefunction analysis", "when to use semi-empirical", "what is PES", "transition state vs minimum", or mentions distinguishing computational chemistry task types and theoretical methods.
version: 0.1.0
---

# Computational Chemistry Task Types and Methods Guide

Clarifies the relationship between task types (what you do) and theoretical methods (how you do it) in computational chemistry, based on Sobereva's authoritative article (sobereva.com/723).

**Core concept:** Task type and theoretical method are orthogonal. Any theoretical method can (in principle) be used for any task type. A program that supports a given theoretical method can perform all PES-dependent tasks using that method.

## Quick reference: The two axes

| Axis | Question it answers | Examples |
|------|---------------------|----------|
| **Task type** | "What are you doing?" | Optimize, TS search, IRC, scan, frequency, MD, conformational search, wavefunction analysis |
| **Theoretical method** | "How are you computing energy/forces?" | Force field, DFT, HF, MP2, CCSD(T), CASSCF, semi-empirical, QM/MM |

**Common beginner mistake:** Confusing terms from different axes. "MD, AIMD, and QM/MM" are not comparable — MD is a task type, AIMD is a task+method combination, QM/MM is a theoretical method.

## The potential energy surface (PES)

Under the Born-Oppenheimer approximation, a non-linear system with N atoms has 3N-6 internal coordinates, and the energy is a 3N-6 dimensional function of these coordinates — this is the **potential energy surface (PES)**.

Most task types are PES-based: given PES information (energy and its derivatives at any point), you can perform these tasks.

## Task types at a glance

### PES-based tasks (static)

| Task | What it does | Needs |
|------|-------------|-------|
| **Geometry optimization (minimum)** | Find nearest PES minimum from initial guess | Energy + gradient |
| **Transition state optimization** | Find nearest first-order saddle point | Energy + gradient |
| **Vibrational analysis (frequency)** | Compute vibrational frequencies at a stationary point | Energy + Hessian (2nd derivative) |
| **IRC / reaction path** | Generate minimum energy path between two minima via TS | Energy + gradient along path |
| **PES scan** | Compute energy at points along specified geometric variable(s) | Energy (rigid) or energy + gradient (relaxed) |
| **Conformational search** | Find global minimum and low-energy conformers among many minima | Energy + gradient (for optimization of each candidate) |

### PES-based tasks (dynamic)

| Task | What it does | Needs |
|------|-------------|-------|
| **Molecular dynamics (MD)** | Simulate time evolution of the system | Energy + gradient (forces) at each timestep |
| **Monte Carlo (MC)** | Sample PES statistically without time evolution | Energy only (no forces needed) |

### Wavefunction analysis

Quantum chemistry calculations produce electronic wavefunctions. Wavefunction analysis methods extract chemically meaningful information from wavefunctions:

- **Bonding:** AIM, NBO, bond order, Mayer/Wiberg, ELF, orbital interaction
- **Electronic structure:** HOMO/LUMO, DOS/OPDOS, charge analysis, electrostatic potential
- **Reactivity:** Fukui function, conceptual DFT, NICS, hole-electron analysis
- **Noncovalent interactions:** RDG, IRI, IGMH
- **Energy decomposition:** sobEDA, etc.

Multiwfn (sobereva.com/multiwfn) is the most powerful program for wavefunction analysis.

## Theoretical methods at a glance

### Non-quantum methods

| Method | Cost | Accuracy | Describes reactions? | Parameters? |
|--------|------|----------|---------------------|-------------|
| **Molecular force field (MM)** | Extremely low | System-dependent | No (bonds fixed) | Heavy empirical |
| **Machine learning potential** | Low-medium | Training-dependent | Usually no | ML-trained |
| **Reactive force field** | Medium | System-dependent | Yes | Heavy empirical |

### Quantum chemistry methods

| Method | Cost | Dynamic corr. | Static corr. | Ab initio? |
|--------|------|---------------|--------------|------------|
| **HF** | Medium | No | No | Yes |
| **DFT (KS-DFT)** | Medium | Approximate | No | Debated |
| **Post-HF (MP2, CCSD, etc.)** | High | Yes | No | Yes |
| **MCSCF / CASSCF** | High | No/limited | Yes | Yes |
| **Multireference (CASPT2, NEVPT2)** | Very high | Yes | Yes | Yes |
| **Semi-empirical (AM1, PM3, PM6)** | Very low | No | No | No (empirical) |
| **GFN-xTB (GFN1, GFN2)** | Very low | Approximate | No | No (empirical) |

**Cost ranking (lowest to highest):** Force field < ML potential ≈ semi-empirical ≈ GFN-xTB << HF ≈ DFT < post-HF (MP2) < MCSCF < post-HF (CCSD) < multireference (CASPT2, NEVPT2) < CCSD(T) < MRCI

### Composite methods

| Method | Description |
|--------|-------------|
| **QM/MM** | QM region (accurate, expensive) + MM region (fast, approximate). Must partition correctly — reaction center in QM, environment in MM. |
| **ONIOM** | Combines any two theoretical methods for different regions. ONIOM(QM:MM) is similar to QM/MM but implemented differently. |

**Important:** QM/MM and ONIOM are NOT the same thing. Do not confuse them.

### Excited state methods

Ground state methods (DFT, HF, post-HF, semi-empirical) can compute excited states via delta-SCF but this is not general-purpose.

**Dedicated excited state methods:**
- TDDFT — most common, good cost-performance
- CIS — obsolete, poor accuracy
- EOM-CCSD — high precision, very expensive

**Excited state dynamics:** Requires more than just excited state energy/forces. Often needs internal conversion, intersystem crossing rates, or nonadiabatic dynamics (surface hopping). Specialized programs: Newton-X, SHARC.

## Common terminology clarified

| Term | What it means | Components |
|------|--------------|------------|
| **MD** | Molecular dynamics (task type) | Usually means classical/force-field MD by default |
| **AIMD** | Ab initio molecular dynamics | Task: MD + Method: quantum chemistry (usually for isolated systems) |
| **FPMD** | First-principles molecular dynamics | Task: MD + Method: quantum chemistry (usually for periodic systems) |
| **QM/MM MD** | Molecular dynamics using QM/MM method | Task: MD + Method: QM/MM |
| **First-principles calculation** | Quantum chemistry for periodic systems | Includes DFT, not strictly ab initio |
| **Ab initio** | Methods with no empirical parameters | HF, post-HF, MCSCF, multireference |
| **WFT** | Wavefunction theory | HF + post-HF + MCSCF + multireference (excludes DFT) |
| **Quantum chemistry calculation** | Usually refers to isolated (non-periodic) systems | Molecular/cluster systems |
| **Quantum computing** | NOT the same as quantum chemistry | Uses quantum computers for algorithms |

## Naming conventions: "Quantum chemistry" vs "First-principles"

- **"Quantum chemistry calculation"** typically refers to isolated (non-periodic) systems — molecules, clusters
- **"First-principles calculation"** typically refers to periodic systems (crystals, surfaces)
- Programs: Gaussian, ORCA, GAMESS-US = quantum chemistry programs; CP2K, Quantum ESPRESSO = first-principles programs
- DFTB has many empirical parameters but is often counted as first-principles for periodic systems

## Basis functions and basis sets

All quantum theory-based methods (except force fields and ML potentials) use molecular orbitals, expanded as linear combinations of basis functions.

- **Gaussian-type orbitals (GTO):** Atom-centered, used by Gaussian, ORCA, etc. Basis sets: 6-31G*, def2-TZVP, cc-pVDZ
- **Plane waves:** Cover entire unit cell, used by most first-principles programs
- **Basis set quality:** Better basis set → more accurate results, but higher cost. Good method + bad basis set = bad results. Bad method + good basis set = bad results. Good method + good basis set = good results.
- **Semi-empirical / GFN-xTB:** Basis functions are built into the method — you do NOT and cannot specify basis sets for these.

## Task + Method combinations

Any theoretical method can be combined with any task type (if the program supports it):

| Combination | Example use case |
|-------------|-----------------|
| Force field + optimization | Energy minimization before MD in GROMACS |
| DFT + optimization | Most common computational chemistry workflow |
| DFT + frequency | Verify minimum (no imaginary frequencies) |
| DFT + TS optimization | Find transition state for reaction |
| DFT + IRC | Verify TS connects correct reactant/product |
| DFT + PES scan | Map reaction coordinate or conformational space |
| DFT + MD | AIMD / FPMD — expensive but accurate dynamics |
| QM/MM + optimization | Enzyme active site reaction |
| QM/MM + MD | Enzyme dynamics with QM accuracy at active site |
| TDDFT + optimization | Optimize excited state geometry |
| TDDFT + MD | Excited state dynamics (limited — needs nonadiabatic treatment for full rigor) |
| Semi-empirical + conformational search | Fast screening of many conformers |
| GFN-xTB + optimization | Quick pre-optimization before DFT |

## Practical workflow: How to choose

1. **Identify the task** — What do you want to know? Structure? Energy? Dynamics? Spectra? Reaction mechanism?
2. **Choose the theoretical method** — Based on system size, required accuracy, and available resources
3. **Choose the basis set** — Based on the method (DFT vs post-HF have different requirements — see basis-set skill)
4. **Combine** — Run the task with the chosen method and basis set

**Common workflows:**
- Small molecule, high accuracy: CCSD(T)/CBS or DFT with large basis set
- Medium molecule, good accuracy: DFT/def2-TZVP for single-point, DFT/def2-SVP for optimization
- Large system: QM/MM or semi-empirical/GFN-xTB
- Conformational search: MM or semi-empirical for screening → DFT for top candidates
- Dynamics: Force field for classical MD, DFT for AIMD (small systems), QM/MM for large systems with QM region of interest

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/task-types.md`** — Detailed description of every task type with use cases and requirements
- **`references/methods.md`** — Detailed description of every theoretical method with cost, accuracy, and applicability
