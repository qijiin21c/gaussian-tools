# Task Types in Computational Chemistry

Detailed description of every common task type in computational chemistry, based on Sobereva's article (sobereva.com/723).

## The potential energy surface (PES)

A non-linear system with N atoms has 3N-6 internal coordinates describing relative atomic positions. Under the Born-Oppenheimer approximation, the system's energy is a 3N-6 dimensional function of these coordinates — this is the **potential energy surface (PES)**.

Most computational chemistry tasks are PES-based: they require the ability to compute energy (and often derivatives) at any point on the PES.

## PES-based static tasks

### Geometry optimization (minimum)

**What:** Starting from an initial guess structure, find the exact position of the nearest PES minimum using a specific algorithm.

**Needs:** Energy + gradient (first derivative)

**Also known as:** Energy minimization (em) in MD programs like GROMACS

**Note:** In MD programs, "energy minimization" serves a different purpose — releasing excessive repulsive forces in manually constructed initial models before MD simulation. The algorithm is the same, but the goal is different.

**Output:** Optimized structure at a local minimum (all forces ≈ 0, all frequencies real).

### Transition state optimization

**What:** Starting from an initial guess structure, find the exact position of the nearest first-order saddle point on the PES.

**Needs:** Energy + gradient (first derivative)

**Significance:** The TS represents the most representative structure along a reaction path. The energy difference between TS and adjacent minima gives the reaction barrier, which is key to assessing reaction feasibility.

**Algorithm details:** See sobereva.com/44

**Output:** Optimized TS structure (all forces ≈ 0, exactly one imaginary frequency).

### IRC / reaction path generation

**What:** Generate the easiest transformation path between two adjacent PES minima corresponding to an elementary reaction.

**Needs:** Energy + gradient along the path

**Types:**
- **IRC (Intrinsic Reaction Coordinate):** Path generated in mass-weighted coordinates
- **MEP (Minimum Energy Path):** Path generated without mass weighting

**Significance:** The reaction path is the most representative path for the actual chemical reaction process. Can be used to:
- Verify that a TS connects the correct reactant and product
- Visualize structural changes along the reaction
- Perform wavefunction analysis at each point to study electronic structure evolution (e.g., bond order curves, ELF/LOL/RDG animations — see sobereva.com/200)

**Output:** Series of structures and energies along the reaction path, with TS at the highest energy point.

### PES scan

**What:** For specified geometric variable(s) (bond length, angle, dihedral), compute energy at each value as the variable changes, mapping out the PES or a subspace of it.

**Needs:** Energy (rigid scan) or energy + gradient (relaxed scan)

**Types:**
- **Rigid scan:** Only the scanned variable changes; all other coordinates are fixed
- **Relaxed scan:** At each step, all other coordinates are optimized while the scanned variable is constrained

**Examples:**
- Scan OH bond length from 0.4 Å to 3.0 Å in 0.1 Å steps → energy curve describing O-H bond stretching PES
- Scan two dihedrals, each with 10 steps → 10² = 100 energy points covering a 2D PES subspace

**Output:** Energy as a function of the scanned variable(s).

See sobereva.com/400 for IRC and scan details in Gaussian.

### Vibrational analysis (frequency)

**What:** Computed at stationary points (all atomic forces = 0) on the PES to obtain vibrational frequencies for the corresponding structure.

**Needs:** Energy + Hessian (second derivative matrix)

**Uses:**
- Compute thermodynamic quantities (see Shermo manual, sobereva.com/552)
- Obtain vibrational energy levels and wavefunctions
- Verify geometry optimization accuracy (check for imaginary frequencies)
- Plot vibrational spectra (IR, Raman, UV-Vis, ECD, VCD, ROA — see sobereva.com/224)

**Output:** Vibrational frequencies, IR intensities, Raman activities, thermodynamic quantities.

### Conformational search (global optimization)

**What:** The PES typically has many minima. The lowest-energy one is the global minimum (most stable conformation). Other minima correspond to metastable conformations. Geometry optimization only converges to the nearest minimum from the initial guess — this may not be the global minimum. Conformational search aims to find the global minimum or the lowest-energy set of conformations.

**Needs:** Energy + gradient (for optimizing each candidate)

**Methods:** Many approaches available. molclus (sobereva.com/research/molclus.html) is a commonly used free tool.

**Output:** Set of low-energy conformations, ideally including the global minimum.

## PES-based dynamic tasks

### Molecular dynamics (MD)

**What:** Unlike the static tasks above (which don't involve time), MD introduces the time dimension to simulate how the system state evolves over time. This is highly complementary to static tasks.

**Needs:** Energy + gradient (forces) at each timestep

**Implementation:** Most commonly BOMD (Born-Oppenheimer MD) — evolving atomic coordinates and velocities according to classical Newton's equations based on positions, velocities, and forces. When combined with quantum chemistry methods, also called CPMD, ADMP, etc.

**Note:** Despite the name "molecular" dynamics, the subject is not limited to molecules — inorganic solids, metal clusters, etc. can also be simulated.

**Special forms:** Langevin dynamics, dissipative particle dynamics, etc. (limited current use)

**Output:** Trajectory — positions and velocities of all atoms as a function of time.

### Monte Carlo (MC)

**What:** Another PES sampling method alongside MD. Applicable to fewer situations — mainly used for small molecule adsorption in porous materials, gas-liquid coexistence curves, etc.

**Needs:** Energy only (no forces or velocities needed)

**Limitations vs MD:**
- No explicit time concept
- Cannot study time-dependent evolution like MD

**Output:** Statistical ensemble of configurations.

## Wavefunction analysis

Quantum chemistry or first-principles calculations produce electronic wavefunctions. According to quantum mechanics, the wavefunction contains all information about the system. Wavefunction analysis opens this "black box" to extract rich, chemically meaningful information.

### What wavefunction analysis can study

| Area | Methods |
|------|---------|
| **Bonding** | AIM, NBO, bond order, Mayer/Wiberg, ELF, orbital interaction analysis |
| **Electronic structure** | HOMO/LUMO, DOS/OPDOS, charge analysis (Mulliken, SCPA, etc.), electrostatic potential |
| **Reactivity** | Fukui function, conceptual DFT (Fukui function, dual descriptor, softness/hardness, electronegativity, etc.), NICS, hole-electron analysis |
| **Noncovalent interactions** | RDG, IRI, IGMH, quantitative molecular surface analysis |
| **Energy decomposition** | sobEDA, etc. |

### Key program

Multiwfn (sobereva.com/multiwfn) is the most powerful program for wavefunction analysis. See Multiwfn FAQ (sobereva.com/452).

### Training

For comprehensive learning: 北京科音波函数分析与Multiwfn培训班 (sobereva.com/WFN)

## Task comparison summary

| Task | Static/Dynamic | Needs energy | Needs gradient | Needs Hessian | Time dimension |
|------|---------------|-------------|---------------|--------------|----------------|
| Opt minimum | Static | Yes | Yes | No (optional) | No |
| Opt TS | Static | Yes | Yes | No (optional) | No |
| IRC/MEP | Static | Yes | Yes | No | No |
| PES scan | Static | Yes | Yes (relaxed) | No | No |
| Frequency | Static | Yes | No | Yes | No |
| Conformational search | Static | Yes | Yes | No | No |
| MD | Dynamic | Yes | Yes | No | Yes |
| Monte Carlo | Dynamic | Yes | No | No | No (statistical) |
| Wavefunction analysis | N/A | From QC output | No | No | N/A |
