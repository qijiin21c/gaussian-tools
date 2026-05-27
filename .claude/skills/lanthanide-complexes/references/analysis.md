# Wavefunction Analysis for Lanthanide Complexes

Detailed guidance for wavefunction analysis of lanthanide/actinide complexes, based on Sobereva's article (sobereva.com/581).

## Prerequisites

- **Must use small-core ECP or all-electron calculation** — large-core ECPs remove too many electrons for meaningful analysis
- **Must use stable wavefunction** — run `stable=opt` before any wavefunction analysis
- Use Multiwfn (sobereva.com/multiwfn) for most analyses

## Mulliken population analysis

### What Mulliken tells you for lanthanide complexes

Mulliken population reveals the 4f electron localization on the lanthanide center.

**Example: Ho(III) with small-core ECP (SDD/MWB28):**

After `stable=opt`, the output shows:
```
 Mulliken charges and spin densities:
 Atom    Charge    Spin
  1 Ho   2.845     4.002
  2 O   -0.612     0.001
  3 O   -0.598     0.003
  ...
```

Key observations:
- Ho spin density ≈ 4.0 → 4 unpaired alpha electrons on Ho 4f orbitals
- This confirms Ho(III) with 10 4f electrons: 7α + 3β = 4 net unpaired
- Oxygen atoms carry negative charge (as expected for O-donor ligands)
- Spin is highly localized on Ho — minimal spin delocalization onto ligands

### Mulliken vs Hirshfeld vs ADCH charges

| Method | Ho charge | O charges | Notes |
|--------|-----------|-----------|-------|
| **Mulliken** | ~+2.8 | ~-0.6 | Basis set dependent, but shows spin density |
| **Hirshfeld** | ~+1.8 | ~-0.3 | Less basis set dependent, more physical |
| **ADCH** | ~+2.2 | ~-0.4 | Improved over Hirshfeld, good for charge analysis |

**Recommendation:** Use Hirshfeld or ADCH for charge analysis; Mulliken for spin density.

**Important:** If using large-core ECP, Mulliken population is meaningless for the lanthanide center — the 4f electrons are pseudopotential, not described in the wavefunction.

## Atomic charge and oxidation state

### LOBA (Localized Orbital Bonding Analysis)

LOBA identifies the oxidation state by analyzing localized orbitals.

**For Ho(III):**
1. Run Natural Bond Orbital (NBO) analysis or use Multiwfn's LOBA module
2. Ho should show +3 oxidation state
3. 4f orbitals should be clearly identified as localized on Ho

**Procedure in Multiwfn:**
```
Main function 15: Natural bond orbital (NBO) analysis
  → Subfunction for LOBA
  → Set occupation threshold (usually 1.5 for alpha, 0.5 for beta)
  → Output shows oxidation state per atom
```

**Expected result for Ho(III):**
- Ho oxidation state: +3
- Each coordinating O: -1 to -2 (depends on ligand type)
- Confirms the formal oxidation state assignment

## AIM (Atoms in Molecules) topology analysis

### AIM for Ho-O bonds

AIM topology analysis reveals the nature of metal-ligand interactions.

**Key AIM parameters for Ho-O interactions:**

| Parameter | Covalent bond | Ho-O (typical) | Interpretation |
|-----------|---------------|----------------|----------------|
| ρ(r) at BCP | > 0.2 a.u. | ~0.03-0.08 a.u. | Low electron density |
| ∇²ρ(r) at BCP | < 0 | > 0 | Positive Laplacian = closed-shell |
| H(r) at BCP | < 0 | > 0 or ≈ 0 | Non-covalent interaction |
| |ρ|/∇²ρ ratio | > 1 | < 1 = ionic/closed-shell |

**Interpretation:**
- Ho-O bonds are **closed-shell interactions** (ionic/coordination bonds)
- Not covalent — consistent with lanthanide chemistry understanding
- ρ(r) values are low, ∇²ρ(r) > 0
- This is the same interaction type as hydrogen bonds, just stronger

**Multiwfn AIM workflow:**
```
Main function 2: AIM analysis
  → Subfunction 1: Topology analysis
  → Select atoms of interest (Ho and coordinating O atoms)
  → Output: BCP positions, ρ(r), ∇²ρ(r), H(r), ellipticity
```

## RDG (Reduced Density Gradient) analysis

### Visualizing non-covalent interactions around Ho

RDG isosurface visualization shows the coordination environment and weak interactions.

**For Ho(III) complex:**
- Strong attractive interaction (blue isosurface): Ho-O coordination bonds
- Weak van der Waals (green isosurface): ligand-ligand interactions, solvent effects
- Steric repulsion (red isosurface): crowding in coordination sphere

**Multiwfn RDG workflow:**
```
Main function 20: RDG analysis
  → Calculate RDG on grid
  → Output .cube file for visualization
  → Load in VMD or Multiwfn's built-in viewer
  → Color by sign(λ₂)ρ: blue (attractive), green (vdW), red (repulsive)
```

**VMD visualization script:**
```tcl
mol load cube rdg.cube
Graphics → Representations
  Color → Color Scale → BGR (blue-green-red)
  Draw → Isosurface → Level 0.5
```

## Coordination number analysis

### Determining coordination number from wavefunction

The coordination number can be determined from:
1. **AIM bond paths** — count BCPs between Ho and ligand atoms
2. **Multiwfn coordination number module:**
   ```
   Main function: Bond order analysis
     → Coordination number calculation
     → Set distance cutoff (typically 3.0 Å for Ho-O)
   ```
3. **ICOHP (Integrated Crystal Orbital Hamilton Population):**
   - Use LOBSTER or similar tool
   - More rigorous than simple distance cutoff

**For Ho(III) 12-crown-4 pentahydrate:**
- 4 Ho-O bonds from crown ether
- 5 Ho-O bonds from water molecules
- Total coordination number: 9

## CDA (Charge Decomposition Analysis)

### Orbital interaction between Ho and ligands

CDA decomposes the metal-ligand interaction into:
- **Donation (d):** Ligand → metal electron donation
- **Back-donation (b):** Metal → ligand back-donation
- **Repulsion (r):** Pauli repulsion between occupied orbitals

**For Ho(III) complexes:**
- Donation dominates (O lone pair → Ho empty orbitals)
- Back-donation is minimal (Ho 4f orbitals are core-like, poor overlap)
- This is unlike transition metals where π-back-donation is significant

**Multiwfn CDA workflow:**
```
Main function: Charge decomposition analysis
  → Define fragment 1: Ho atom
  → Define fragment 2: ligands
  → Output: d, b, r values, orbital contributions
```

**Expected results for Ho(III):**
| Component | Value | Interpretation |
|-----------|-------|----------------|
| d (donation) | ~0.5-1.0 e | Significant O→Ho donation |
| b (back-donation) | ~0.0-0.1 e | Negligible Ho→O back-donation |
| r (repulsion) | ~0.2-0.5 e | Pauli repulsion |

## IR spectrum analysis

### Computing and plotting IR spectrum

After frequency calculation:

1. **Apply frequency scaling factor:**
   - PBE0/6-31G*: scaling factor ≈ 0.965
   - PBE0/6-311G*: scaling factor ≈ 0.968
   - See multiparallel.com/scale.html for up-to-date factors

2. **Extract IR intensities from Gaussian output:**
   ```
   Frequency and IR intensity pairs from the frequency output
   ```

3. **Plot with Gaussian broadening:**
   Use Multiwfn:
   ```
   Main function: IR spectrum simulation
     → Input frequency/intensity data
     → Set broadening method (Lorentzian, Gaussian, or Voigt)
     → Set FWHM (typically 10-20 cm⁻¹)
     → Output: simulated IR spectrum
   ```

4. **Ho-ligand vibrations:**
   - Ho-O stretching: typically 200-500 cm⁻¹ (far-IR region)
   - Ho-O bending: typically 100-300 cm⁻¹
   - These modes involve significant Ho motion and are sensitive to the coordination environment

**Note:** If frequency was calculated with large-core ECP, the Ho-O vibrational frequencies are reasonable but the intensity may be less accurate. Small-core ECP frequencies are more reliable for intensity analysis.

## Additional wavefunction analysis methods

### NBO (Natural Bond Orbital) analysis

- Use `pop=nbo6read` in Gaussian
- Reveals donor-acceptor interactions
- For Ho(III): shows O lone pair → Ho acceptor orbital interactions
- Second-order perturbation analysis gives stabilization energy

### EDA (Energy Decomposition Analysis)

- Decompose interaction energy into physical components
- Available in ADF, ORCA, or via Multiwfn
- Components: electrostatic, exchange, polarization, charge transfer

### ELF (Electron Localization Function)

- Visualize electron localization regions
- For lanthanides: 4f orbitals show as localized basins on the metal
- Useful for visualizing the shielding effect of 5s5p shells

### DOS/PDOS (Density of States)

- Total and partial density of states
- Shows 4f orbital energy levels
- Useful for understanding electronic transitions
- Plot with Multiwfn or external tools

## References

- sobereva.com/581 — This article (lanthanide complex calculation)
- sobereva.com/156 — Wavefunction analysis with pseudopotentials
- sobereva.com/714 — ADCH charge calculation
- sobereva.com/multiwfn — Multiwfn software
- sobereva.com/82 — Wavefunction stability analysis
- sobereva.com/60 — Gaussian mixed basis/ECP input
