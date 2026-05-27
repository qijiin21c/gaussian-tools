# Advanced TDDFT Topics in Gaussian

Advanced topics for TDDFT calculations: wavefunction analysis, PES crossings, conformer effects, negative excitation energies, and symmetry breaking. Based on Sobereva's article (sobereva.com/266).

## Excited-state wavefunction analysis

### The density keyword

By default, Gaussian's TDDFT calculation produces the **ground-state** density. All output properties (dipole moment, quadrupole moment, Mulliken charges) and wavefunction analysis (L601, NBO L607) refer to the ground state.

To analyze the **excited state**, add `density`:

```
#p PBE1PBE/TZVP TD(nstates=5,root=2) density
```

Now the output shows:
- Dipole moment of the 2nd excited state
- Quadrupole moment of the 2nd excited state
- Mulliken charges of the 2nd excited state

### Excited-state .wfn file

To generate a .wfn file containing excited-state natural orbitals:

```
#p PBE1PBE/TZVP TD(nstates=5,root=2) density out=wfn

[coordinates]

C:\path\to\output.wfn
```

The path to the .wfn file goes on a blank line after the molecular coordinates.

### Important: .chk file stores ground-state orbitals

Even with `density`, the .chk file still contains ground-state DFT orbitals. To work with excited-state natural orbitals:

**Option 1:** Generate from .fch in Multiwfn
- Use Multiwfn to generate excited-state natural orbitals from the .fch file containing the excited-state density matrix
- See sobereva.com/403 for detailed example

**Option 2:** Transfer to .chk
- See Multiwfn manual Chapter 4 opening section, or sobereva.com/379

**Option 3:** Use .fch directly
- Run `formchk` on the .chk to get .fch, then load into Multiwfn
- Multiwfn can read the excited-state density matrix from .fch

### NBO analysis of excited states

Simply add `pop=NBO` alongside `density`:
```
#p PBE1PBE/TZVP TD(nstates=5,root=2) density pop=NBO
```

## Symmetry breaking for excited-state optimization

### The problem

Excited states often have **lower symmetry** than the ground state. If you start an excited-state optimization from a symmetric ground-state structure, the optimization may preserve the symmetry and converge to a saddle point (with imaginary frequencies) rather than the true minimum.

**Example:** Formaldehyde (H₂CO)
- Ground state: Cₛ symmetry
- S₁ minimum: **not** Cₛ symmetry
- Starting S₁ optimization from Cₛ structure → converges to Cₛ saddle point with imaginary frequency

### The solution

**Before optimizing the excited state, slightly distort the structure to break symmetry:**
- Perturb a dihedral angle by a few degrees
- Displace one atom slightly off the symmetry plane
- Any small distortion that breaks the point group

Then optimize the excited state from this distorted structure. The optimization will find the true (lower-symmetry) minimum.

**General rule:** If the ground state has symmetry, always break it slightly before excited-state optimization.

## Conformer effects on spectra

### The problem

Flexible molecules have multiple conformers, each with different absorption spectra. This is especially critical for ECD (electronic circular dichroism) spectra, which are highly conformation-sensitive.

If you compute the spectrum from a non-global-minimum conformer, it may disagree significantly with experiment.

### The solution

1. **Conformer search:** Use Molclus (keinsci.com/research/molclus) — free and easy to use
2. **Boltzmann weighting:** If multiple conformers are close in energy and can interconvert at experimental temperature:
   - Compute spectra for each conformer
   - Weight-average the spectra by Boltzmann population
   - See sobereva.com/165 for Boltzmann population calculation
   - See sobereva.com/383 for plotting conformer-weighted spectra with Multiwfn

### When is conformer averaging needed?
- Multiple conformers within ~2-3 kcal/mol
- Low barriers between conformers (interconvert at experimental temperature)
- Significant spectral differences between conformers

## Negative excitation energies

### What it means

If one or more computed excitation energies are **negative**, the SCF reference wavefunction (HF or DFT) is **not the true ground state** at this geometry. The excitation energies are meaningless.

Running `stable` keyword on this structure would confirm wavefunction instability.

### Troubleshooting

**Step 1: Check spin multiplicity**
- Is the spin multiplicity setting consistent with the actual ground state?
- Example: The structure's true ground state is singlet but you set triplet → negative excitation energies

**Step 2: If multiplicity is correct, stabilize the wavefunction**
```
#p PBE1PBE/6-31G* stable=opt
```
Gaussian will automatically find the true stable ground-state wavefunction.

**Step 3: Use the stabilized wavefunction as guess for TD**
```
#p PBE1PBE/TZVP TD(nstates=20) guess=read
```

After this treatment, if all excitation energies are positive, the problem is resolved.

## Potential energy surface crossings and excited-state optimization

### The complexity

Excited-state potential energy surfaces are much more complex than ground-state surfaces:
- **Dense energy levels** — many states close in energy
- **Frequent crossings** — conical intersections and avoided crossings between states
- **Surface bifurcation** — PES may split or merge

### Common phenomena

1. **Different initial states converge to the same minimum**
   - Optimizing S₄ and S₅ may both end up at the same geometry
   - This happens when the states cross during optimization

2. **State ordering changes during optimization**
   - Start optimizing S₄, but at the final geometry, this state is not the 4th-lowest anymore
   - The state you were following crossed with other states

3. **"Root flipping" during optimization**
   - The character of root=i changes along the optimization path
   - What started as a π→π* state may become n→π* at the minimum

### Understanding these phenomena

See sobereva.com/468 for a comprehensive discussion of PES crossing effects on excited-state optimization. Key insights:
- State tracking is based on energy ordering, not character
- When states cross, the program follows the energy-ordered state, which may change character
- This is not a bug — it reflects the physical reality of crossing PESs
- To follow a specific character, monitor the orbital transition contributions at each step

## Transition dipole moment vs dipole moment difference

**Common confusion among beginners:**

The transition dipole moment `<i|-r|j>` between states |i⟩ and |j⟩ is **NOT** the same as the difference in dipole moments between the two states `<j|-r|j> - <i|-r|i>`.

These are completely different quantities with no direct relationship.

### Oscillator strength formula

```
f = (2/3) × ΔE × |<i|-r|j>|²
```

- f is dimensionless
- f > 1 is possible (strong absorbers can reach f ≈ 7-8)
- f < 0.01 is generally considered forbidden

### Lifetime from oscillator strength

```
τ = 1.5 / (f × ΔE²)
```

- τ in seconds
- ΔE in cm⁻¹
- 1/τ = spontaneous emission rate

## Phosphorescence and spin-orbit coupling

### Gaussian's limitation

Gaussian does **not** support spin-orbit coupling (SOC) at the TDDFT level. Therefore:
- Phosphorescence oscillator strength is always 0
- Cannot compute phosphorescence rate from Gaussian
- Cannot plot phosphorescence spectrum (only a single broadened peak)

### Programs that support SOC

| Program | Cost | Method |
|---------|------|--------|
| **ADF** | Very expensive | TDDFT+SOC (not recommended for cost) |
| **Dalton** | Free | TDDFT+SOC (recommended, see bbs.keinsci.com/thread-2455-1-1.html) |
| **Dirac** | Free (registration) | 2-/4-component relativistic TDDFT |
| **ORCA** | Free (registration) | TDDFT+SOC (see sobereva.com/462) |
| **Gaussian + PySOC** | Free | SOC matrix elements at TDDFT level (see sobereva.com/411) |

### Alternative: MCSCF/MRCI level

Many programs support SOC at MCSCF/MRCI levels, but these methods are not suitable for large systems.

## Multiwfn for excited-state analysis

Multiwfn (sobereva.com/multiwfn) is essential for deep excited-state analysis:

| Analysis | What it tells you |
|----------|------------------|
| **Electron-hole analysis** (sobereva.com/434) | Hole/electron distribution, CT character, overlap integral, centroid distance |
| **NTO analysis** (sobereva.com/377, sobereva.com/91) | Converts multi-orbital transition to single dominant NTO pair |
| **Transition density matrix** | Orbital contributions, fragment contributions |
| **Charge transfer analysis** | How much charge transfers between fragments |
| **Δr index** | CT distance metric |
| **Density difference plot** | Visual electron redistribution upon excitation |
| **Oscillator strength decomposition** | Which orbitals/atoms/basis functions contribute to intensity |
| **Transition dipole moment density** | Spatial distribution of transition dipole |

See sobereva.com/437 for a comprehensive list of excited-state analysis methods in Multiwfn.

## References

- sobereva.com/266 — This article (TDDFT in Gaussian)
- sobereva.com/468 — PES crossing effects on excited-state optimization
- sobereva.com/437 — Multiwfn excited-state analysis methods
- sobereva.com/434 — Electron-hole analysis
- sobereva.com/377 — NTO analysis
- sobereva.com/91 — NTO introduction
- sobereva.com/403 — Excited-state natural orbitals from .fch
- sobereva.com/379 — Input file format conversion
- sobereva.com/165 — Boltzmann population calculation
- sobereva.com/383 — Conformer-weighted spectra plotting
- sobereva.com/411 — Gaussian + PySOC for SOC matrix elements
- sobereva.com/462 — ORCA TDDFT+SOC
- keinsci.com/research/molclus — Molclus conformer search program
