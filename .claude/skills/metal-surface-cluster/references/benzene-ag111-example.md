# Benzene on Ag(111) — Step-by-Step Example

Detailed walkthrough of calculating benzene physisorption energy on Ag(111) surface using a cluster model, based on Sobereva's article (sobereva.com/540).

## System overview

Benzene molecule physisorbed on Ag(111) surface. This system was studied in the DFT-D3 paper (J. Chem. Phys., 132, 154104, 2010), which reported:
- Experimental adsorption enthalpy: **-13 kcal/mol**
- DFT-D3 rigid scan minimum: ~3 Å benzene-surface distance

Our goal: reproduce this result using a cluster model approach.

## Step 1: Build the Ag₅₈ cluster

### Construction
1. Obtain Ag crystal structure from ICSD
2. Cut (111) surface facet using VESTA, GaussView, or Avogadro
3. Extend to a sufficiently large slab, at least 3 layers thick
4. Trim atoms to form a roughly circular cluster shape (matching benzene's circular projection)
5. Use a "wide top, narrow bottom" shape to save atoms while maintaining adequate surface area

### Ag₅₈ cluster structure
- 58 silver atoms arranged in 3+ layers
- Surface shape approximately circular (matching benzene geometry)
- Total system with benzene: C₃v symmetry

### Verify cluster size
- **Too small?** → boundary effects dominate, results inaccurate
- **Too large?** → computational cost prohibitive
- Ag₅₈ is a good balance for benzene adsorption

## Step 2: Build the complex initial structure

### Place benzene on the cluster
1. Position benzene molecule above the cluster center
2. Set benzene-surface distance to **~3 Å** (close to expected equilibrium)
   - Too far → optimization takes many steps
   - Too close (e.g., 2.7 Å) → SCF convergence much harder for transition metal clusters

### Atom freezing strategy
**Critical:** Boundary atoms must be frozen to prevent unphysical relaxation.

**Frozen atoms (edge/bottom Ag):** 1-11, 14, 17, 19-23, 26, 29, 32, 34-38, 41, 44, 46-50, 52, 54-58

**Free atoms (surface Ag + benzene):** The central Ag atoms in direct contact with benzene, plus all benzene atoms. These are allowed to relax during optimization to naturally respond to the adsorption interaction.

### Ensure closed-shell system
- Benzene: closed-shell
- Ag₅₈: even number of Ag atoms (58) → closed-shell
- Total system: closed-shell ✓
- If using Ag₅₇ or Ag₅₉ → open-shell → significantly harder SCF

## Step 3: Geometry optimization

### ORCA optimization input
```
! PBE0 D3BJ def2-SV(P) def2/J RIJCOSX tightSCF

[atomic coordinates]

%geom
  Constraints
    {C 1 F}
    {C 2 F}
    {C 3 F}
    ... [all frozen atom indices]
  end
end
```

### Why this computational level?

| Choice | Reason |
|--------|--------|
| **PBE0** (not PBE) | Pure functionals like PBE have much worse SCF convergence for transition metal clusters; PBE0 describes metals reliably (JCP 127, 024103, 2007) |
| **PBE0** (not B3LYP) | B3LYP performs poorly for metals (JCP 127, 024103, 2007); PBE0 is reliable for Ag surfaces (J. Phys. Chem. C, 117, 5075, 2013) |
| **D3(BJ)** | Physisorption is dominated by dispersion; PBE0 alone completely fails to describe dispersion (see sobereva.com/413) |
| **def2-SV(P)** | 2-zeta is sufficient for geometry (sobereva.com/387); has standard auxiliary basis sets for RIJCOSX; removes f-polarization on Ag (saves cost with minimal geometry impact) |
| **RIJCOSX** | Dramatically reduces cost for large clusters; much faster than Gaussian for this type of calculation |

### Expected optimization behavior
- ~10 hours on 36-core dual Xeon E5-2696 v3
- Converges smoothly if initial structure is reasonable
- Benzene position adjusts slightly; Ag atoms barely move
- Use OfakeG tool (sobereva.com/498) to convert ORCA output to fake Gaussian output for GaussView visualization

### Alternative: Gaussian optimization
```
#p PBE1PBE/def2svp empirical=dispersion opt=modredundant

[coordinates]

-1 1 F
-1 2 F
... [frozen atom constraints]
```
- Use symmetry (C₃v) for faster convergence in Gaussian
- Save as `.gjf` and GaussView will handle symmetry

## Step 4: Single-point energy calculations

### Complex single-point
```
! PBE0 D3BJ grid4 gridx4 def2-QZVP def2/J RIJCOSX noautostart
%scf DirectResetFreq=1 end

[optimized coordinates from Step 3]
```

### Why def2-QZVP?
- Reaches basis set limit for DFT — BSSE is negligible
- DFT-D3 parameters were fit at def2-QZVP level
- RIJCOSX makes this computationally feasible even for large clusters

### Why `grid4 gridx4`?
For densely packed atomic systems, default integration grid is insufficient:
- Default grid: electron count integral = 1143.93 (deviation of 0.07 from integer)
- `grid4 gridx4`: electron count integral = 1144.0002 (nearly perfect)
- May also help SCF convergence and reduce total steps

### Why `DirectResetFreq=1`?
- Disables incremental Fock matrix acceleration
- Large basis sets (def2-QZVP) on dense metal clusters often oscillate with incremental Fock
- Without this, SCF may not converge even after 50+ cycles
- Reading a converged def2-SV(P) wavefunction as guess also helps but may not be sufficient alone

### Expected single-point behavior
- ~5 hours on 36-core dual Xeon E5-2696 v3
- ~40 SCF cycles — **be patient**, do not kill the job at 30 cycles
- def2-SV(P) converges in ~46 cycles; def2-QZVP with `DirectResetFreq=1` converges in ~40 cycles

### Fragment single-point calculations
After complex single-point completes:
1. Copy input, remove Ag atoms → **benzene single-point** (same computational level)
2. Copy input, remove benzene atoms → **Ag₅₈ single-point** (same computational level)

All three calculations use the **same geometry** from the optimized complex (BSSE-minimized approach).

## Step 5: Calculate binding energy

### Basic formula
```
E_bind = E(Ag₅₈-benzene) - E(benzene) - E(Ag₅₈)
```

### Example result
Using PBE0-D3(BJ)/def2-QZVP:
```
E(Ag₅₈-benzene) = -8760.730415916696 Hartree
E(benzene)      =   -232.068063781533 Hartree
E(Ag₅₈)         = -8528.632371853557 Hartree
E_bind = 627.51 × (-8760.730415916696 + 232.068063781533 + 8528.632371853557)
       = -18.8 kcal/mol
```

### Comparison with experiment
| Method | Binding Energy | Notes |
|--------|---------------|-------|
| **Experiment (enthalpy)** | -13 kcal/mol | Reference value |
| **PBE0 only (no D3)** | Positive (repulsive!) | Dispersion is the main attraction — PBE0 alone fails |
| **PBE0-D3(BJ)/def2-QZVP** | -18.8 kcal/mol | Qualitative agreement |
| **PBE0-D3(BJ)-ABC/def2-QZVP** | -16.9 kcal/mol | Including three-body correction |

### Including DFT-D3 three-body (ABC) correction
For densely packed, large-atom-count systems, the three-body dispersion term is non-negligible (~2 kcal/mol improvement).

**Using standalone dftd3 program:**
```bash
dftd3 complex.xyz -func pbe0 -bj -abc
dftd3 benzene.xyz -func pbe0 -bj -abc
dftd3 Ag58.xyz -func pbe0 -bj -abc
```

Then recompute binding energy with the ABC-corrected dispersion energies.

**Using ORCA:** Add `ABC` keyword to the input file (no cost increase).

**Recommendation:** Always include ABC for surface adsorption calculations. Three-body term has no analytic Hessian — include for single-point only.

### Sources of error
1. **Boundary effects** — larger cluster may improve results
2. **Method error** — PBE0-D3(BJ) has inherent DFT errors; try other functionals
3. **Thermal correction** — experiment measures enthalpy (includes thermal/vibrational); our calculation is electronic energy only. New vibrational modes upon adsorption make enthalpy more positive
4. **Structural relaxation** — ignored energy cost of molecular/surface deformation (negligible for rigid systems like benzene + Ag)
5. **Experimental uncertainty** — experimental data itself has error

## Step 6: NCI analysis (optional)

### Wavefunction source
Use the **optimization** wavefunction (def2-SV(P) level), not the single-point wavefunction (def2-QZVP level):
- Much lower computational cost
- NCI analysis is not sensitive to basis set quality — any reasonable basis works

### Workflow
1. Convert ORCA `.gbw` to molden format: `orca_2mkl complex_opt -molden`
2. Or configure Multiwfn's `settings.ini` with `orca_2mklpath` to read `.gbw` directly
3. Load into Multiwfn → NCI analysis

### Grid box setup
**Critical:** Restrict the grid box to only the interaction region (benzene + nearby Ag atoms):
- Select "Set box of grid data visually using a GUI window"
- Adjust box to cover benzene-surface interface only
- Even with 0.25 Bohr spacing, small box = fast calculation on 4 cores
- For smoother surfaces, reduce spacing to 0.15 Bohr

### Expected NCI result
- Large green isosurface area between benzene π system and Ag surface electron sea
- Visualizes extensive dispersion interaction (similar to π-π stacking appearance)
- Ag-Ag interactions also show isosurface — these can be ignored or masked (see sobereva.com/291)

### Visualization
- Use VMD with color scale -0.04 to 0.03 a.u.
- Color coding: blue (attractive), green (vdW/dispersion), red (repulsive)

## References

- sobereva.com/540 — This article (benzene on Ag(111) example)
- sobereva.com/615 — Cyclo[18]carbon on graphene cluster model study
- sobereva.com/46 — BSSE correction discussion
- sobereva.com/413 — When to add DFT-D3 dispersion correction
- sobereva.com/83 — DFT-D overview
- sobereva.com/464 — DFT-D4 usage
- sobereva.com/210 — DFT-D three-body correction
- sobereva.com/68 — NCI analysis with Multiwfn
- sobereva.com/291 — RDG analysis tips and common issues
- sobereva.com/387 — Why optimization doesn't need large basis sets
- sobereva.com/379 — Input file format conversion
- sobereva.com/490 — Multiwfn ORCA input generation
- sobereva.com/498 — OfakeG tool for ORCA output visualization
- sobereva.com/421 — Gaussian-xtb combined workflow
- J. Chem. Phys., 132, 154104 (2010) — DFT-D3 original paper
- J. Chem. Phys., 127, 024103 (2007) — B3LYP poor for metals
- J. Phys. Chem. C, 117, 5075 (2013) — PBE0 for Ag surfaces
