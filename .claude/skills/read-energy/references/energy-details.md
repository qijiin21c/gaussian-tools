# Electronic Energy Details

Detailed explanation of electronic energy components, energy zero definition, thermodynamic quantities, and related topics, based on Sobereva's article (sobereva.com/339).

## Electronic energy components

The electronic energy E_elec is the sum of four terms:

1. **Electron kinetic energy** — kinetic energy of all electrons
2. **Electron-electron Coulomb repulsion** — repulsion between all electron pairs
3. **Nucleus-nucleus Coulomb repulsion** — repulsion between all nucleus pairs
4. **Electron-nucleus Coulomb attraction** — attraction between all electron-nucleus pairs

```
E_elec = T_e + V_ee + V_nn + V_en
```

All four terms are evaluated at a fixed nuclear geometry (Born-Oppenheimer approximation).

## Energy zero definition

The energy zero is defined as: **all nuclei and electrons at rest, infinitely separated from each other.**

This means:
- A bound molecule has a **negative** electronic energy
- The more negative the energy, the more stable the system (relative to separated particles)
- **Only energy differences are chemically meaningful** — reaction energies, ionization energies, binding energies, etc.
- Absolute electronic energy values have no physical meaning on their own

## Single-point vs optimization vs frequency energies

### Single-point energy calculation
- Computes electronic energy at a fixed geometry
- Output: one `SCF Done` (or method-specific energy line)
- Fastest calculation type

### Geometry optimization
- Iteratively adjusts geometry to find a minimum (or transition state)
- Outputs electronic energy at **each optimization step**
- The **last step's energy** corresponds to the optimized structure
- Archive section at end of output shows energies for the last step's structure

### Frequency calculation
- Computes second derivatives of energy with respect to nuclear displacements
- Also outputs the electronic energy at the current geometry
- If the geometry and method are identical to a single-point, the electronic energy will be the same
- Additionally produces thermodynamic quantities (see below)

**Key point:** The electronic energy itself is always computed the same way regardless of task type. If the geometry, method, basis set, and SCF convergence are identical, the electronic energy will be identical — it's just a byproduct.

## Thermodynamic quantities

Thermodynamic quantities include contributions from **nuclear motion** (vibration, rotation, translation) in addition to the electronic energy.

### Required calculation
A **frequency calculation** is required to compute thermodynamic quantities. Without frequencies, Gaussian cannot produce these values.

### Thermodynamic quantities output

After a frequency calculation, Gaussian outputs (under "Thermochemistry"):

| Quantity | Symbol | Components |
|----------|--------|------------|
| **Internal energy** | E | E_elec + E_ZPE + E_thermal(vib) + E_thermal(rot) + E_thermal(trans) |
| **Enthalpy** | H | E + RT |
| **Gibbs free energy** | G | H - T×S |
| **Entropy** | S | S(vib) + S(rot) + S(trans) |

### Zero Point Energy (ZPE)

ZPE is the energy difference between the electronic energy and the internal energy/enthalpy/free energy at 0 K:

```
ZPE = E(0 K) - E_elec
```

- ZPE arises from nuclear vibration — even at 0 K, nuclei vibrate due to quantum mechanics
- ZPE is always **positive** (it raises the energy above the electronic minimum)
- ZPE is computed from the harmonic oscillator approximation using vibrational frequencies
- ZPE can be scaled (common scaling factors: 0.98 for HF, 0.99 for DFT) to account for anharmonicity

### Relationship summary

```
E_elec (electronic energy)
  + ZPE
  = E(0 K) (internal energy at 0 K)
    + thermal corrections (vib + rot + trans at temperature T)
    = E(T) (internal energy at temperature T)
      + RT
      = H(T) (enthalpy at temperature T)
        - T×S(T)
        = G(T) (Gibbs free energy at temperature T)
```

### Temperature dependence

- Default temperature: 298.15 K
- Default pressure: 1 atm
- Can be changed via Gaussian route section: `temperature=X pressure=Y`
- Electronic energy does NOT depend on temperature — only thermodynamic quantities do

## Shermo program for thermodynamic data

Shermo (sobereva.com/shermo, sobereva.com/552) is a free program for computing more accurate thermodynamic quantities from Gaussian frequency calculation output.

### Why use Shermo?

- **Better vibrational treatment:** Low-frequency modes treated as free rotors instead of harmonic oscillators (Grimme's approach) — important for flexible molecules
- **Custom temperature/pressure:** Easy to compute thermodynamic quantities at any temperature and pressure
- **Multiple formats:** Supports Gaussian, ORCA, GAMESS, etc.
- **Rigid-rotor harmonic oscillator (RRHO) corrections:** Addresses the entropy divergence problem for low-frequency vibrations

### When is Shermo especially useful?

- Reactions involving large flexible molecules (many low-frequency modes)
- Gas-phase thermochemistry at non-standard temperatures
- When standard harmonic oscillator approximation gives unphysical entropy values

## Wavefunction initial guess effects on energy reproducibility

### The problem

In geometry optimization, Gaussian uses the **previous step's converged wavefunction** as the initial guess for the next step. In a single-point calculation, Gaussian generates a guess from scratch (usually Core or Hückel).

This means:
- **Same geometry + same method + same basis set** may give **slightly different energies** in optimization vs single-point
- The optimization result is typically more reliable because the wavefunction is "warm-started" from a converged solution
- A single-point calculation may converge to a different (higher-energy) SCF solution

### When does this matter?

- **Open-shell systems:** Different guesses can converge to different broken-symmetry solutions
- **Near-degenerate systems:** Small differences in guess can lead to different SCF minima
- **Transition metals:** d-electron configurations are sensitive to initial guess
- **Stretched bonds:** SCF may converge to different electronic states

### Best practice for reproducibility

If you need to reproduce an optimization's final energy:
1. Read the wavefunction from the optimization's .chk file: `guess=read`
2. Or use `stable=opt` to verify the wavefunction is at a true minimum

### `stable` keyword

```
#p B3LYP/6-31G* stable=opt
```

- Checks whether the SCF wavefunction is stable (at a minimum, not a saddle point)
- If unstable, Gaussian automatically finds a lower-energy stable wavefunction
- **Recommended** for single-point calculations on optimized geometries, especially for:
  - Open-shell systems
  - Transition metals
  - Systems with near-degenerate orbitals
  - Anions with diffuse functions

## Energy in composite methods

Composite methods (G4, G4(MP2), CBS-QB3, etc.) combine multiple calculations at different levels to approximate a high-level result.

### Two modes of composite methods

**Optimization + frequency mode:**
```
#p G4(MP2)
```
- Performs geometry optimization and frequency calculation internally
- Final energy includes ZPE and thermal corrections
- Read thermochemical quantities from the end of the output

**Single-point mode:**
```
#p G4(MP2)=SP
```
- Computes single-point energy at the provided geometry
- No optimization or frequency calculation
- Read: `G4MP2 Energy= -XXX.XXXXXX`

### Energy components in composite methods

Composite methods report multiple energy values:
- Individual method energies at each step (HF, MP2, MP4, etc.)
- Final composite energy
- ZPE (if frequency calculation was performed)
- Thermochemical quantities (if frequency calculation was performed)

The **final composite energy** is the one to use — not the intermediate values.

## Common misconceptions

| Misconception | Reality |
|---------------|---------|
| "More negative energy = better method" | Energy zero is arbitrary; only differences matter |
| "Electronic energy includes ZPE" | ZPE is nuclear motion; electronic energy is purely electronic |
| "Single-point and optimization give the same energy" | Different initial guesses may lead to different SCF solutions |
| "Higher-level methods always give more negative energies" | Not necessarily — depends on the system and reference |
| "Gaussian's thermochemistry is always accurate" | Harmonic oscillator approximation breaks down for low-frequency modes |
| "HF= in archive means Hartree-Fock" | Archive tag is always "HF=" regardless of method — it contains the final energy |

## References

- sobereva.com/339 — This article (reading electronic energy)
- sobereva.com/552 — Shermo program for thermodynamic data
- sobereva.com/397 — Wavefunction stability and initial guess effects
