# Lanthanide Complex Workflow — Ho(III) Example

Detailed step-by-step workflow for a Ho(III) complex calculation, based on Sobereva's article (sobereva.com/581).

## Example system: Ho(III) 12-crown-4 pentahydrate complex

A Ho³⁺ ion coordinated by one 12-crown-4 ether and five water molecules, forming a 9-coordinate complex.

### Step 0: Build the structure

1. **From CSD crystal structure (GINREA entry):**
   - Download the CIF file from Cambridge Structural Database
   - Open in GaussView or Molden
   - Extract the Ho(III) coordination sphere
   - Add hydrogens if missing

2. **Manual construction:**
   - Place Ho at origin
   - 4 oxygen atoms from 12-crown-4 (equatorial plane)
   - 5 oxygen atoms from water molecules (axial positions)
   - Optimize initial geometry with molecular mechanics first

3. **Charge and multiplicity:**
   - Ho(III) = +3 charge
   - 12-crown-4 = neutral
   - 5 × H₂O = neutral
   - **Total charge: +3**
   - With large-core ECP (MWB56, 4f pseudized): Ho has 8 valence electrons (5s²5p⁶), all closed-shell → **singlet**
   - With small-core ECP (SDD/MWB28, 4f explicit): 10 4f electrons, high-spin: 7α + 3β → **quintet** (7-3+1=5)

### Step 1: Geometry optimization + frequency (large-core ECP)

```
%chk=ho_crown_opt.chk
%mem=8GB
%nprocshared=8
#p PBE1PBE/genecp em=gd3bj int=fine opt freq

Ho(III) 12-crown-4 pentahydrate - Opt+Freq with large-core ECP

0 1
 Ho    0.000000    0.000000    0.000000
 O     2.350000    0.000000    0.000000
 O     0.000000    2.350000    0.000000
 O    -2.350000    0.000000    0.000000
 O     0.000000   -2.350000    0.000000
 O     1.800000    1.800000    1.500000
 O    -1.800000    1.800000   -1.500000
 O     1.800000   -1.800000   -1.500000
 O    -1.800000   -1.800000    1.500000
 O     0.000000    0.000000    2.800000
 [remaining C and H atoms...]

C O H
6-31G*
****
Ho
MWB56
****

Ho
MWB56
```

**Key points:**
- `genecp` keyword for mixed basis + ECP
- `em=gd3bj` for Grimme D3(BJ) dispersion correction
- `int=fine` for standard integration grid
- `opt freq` for optimization + frequency at the same level
- Large-core MWB56: 56 core electrons, pseudizes 4f → easy SCF
- Singlet multiplicity (4f not described)

**Expected results:**
- SCF converges in 10-20 cycles
- Optimization converges in 20-40 steps
- No imaginary frequencies (true minimum)
- If imaginary frequencies appear, see `eliminate-imag-freq` skill

### Step 2: Single-point energy with small-core ECP + stability check

```
%chk=ho_crown_sp.chk
%mem=16GB
%nprocshared=16
#p PBE1PBE/genecp em=gd3bj int=fine stable=opt SCF=maxcyc=200 guess=read

Ho(III) 12-crown-4 pentahydrate - Single-point with small-core ECP + stability

0 5
 Ho    [coordinates from optimized structure]
 O     [coordinates from optimized structure]
 [all atoms...]

C O H
6-311G*
****
Ho
SDD
****

Ho
SDD
```

**Key points:**
- `stable=opt` — **critical** for lanthanide complexes
- `SCF=maxcyc=200` — acceptable for lanthanides
- `guess=read` — read initial guess from .chk if available
- Small-core SDD (= MWB28): explicit 4f description → much harder SCF
- Quintet multiplicity (10 4f electrons: 7α + 3β)
- Better basis set for ligands (6-311G* vs 6-31G*)

**SCF convergence challenges:**
- Expect 50-100+ SCF cycles
- If still not converging after 200 cycles:
  1. Try `SCF=conver=6` (relaxed convergence) — **warning:** Gaussian 16 may refuse `stable=opt` without tight convergence
  2. **BHandHLYP trick:**
     ```
     #p BHandHLYP/genecp [...] SCF=maxcyc=500
     ```
     Converge with BHandHLYP first (50% HF exchange → larger HOMO-LUMO gap), then:
     ```
     #p PBE1PBE/genecp [...] guess=read
     ```
     Read the converged wavefunction as starting guess for PBE0

**Stability analysis output:**
```
 Stability analysis shows the wavefunction is unstable.
 Attempting to optimize to a stable wavefunction...
 ```
- If unstable: Gaussian automatically finds and optimizes to stable wavefunction
- Check `<S²>` value after optimization:
  - Quintet ideal: S(S+1) = 5(5+1)/4 = 6.0 (in atomic units, <S²> = 2.0 for doublet, 6.0 for quintet)
  - If <S²> ≈ 6.0: weak spin polarization, good
  - If <S²> >> 6.0: strong spin contamination, may need multireference treatment
- Energy typically drops significantly after stability optimization (10+ kJ/mol is common)

### Step 3: All-electron DKH4 calculation (optional, higher accuracy)

```
%chk=ho_crown_dkh.chk
%mem=32GB
%nprocshared=32
#p PBE1PBE/gen em=gd3bj int(DKHSO,fine) stable=opt

Ho(III) 12-crown-4 pentahydrate - All-electron DKH4

0 5
 Ho    [coordinates]
 O     [coordinates]
 [all atoms...]

[Custom x2c-TZVPall basis set definitions from BSE]
****
```

**Key points:**
- `int(DKHSO,fine)` — DKH Hamiltonian with spin-orbit coupling
- **All-electron basis sets only** — never mix ECP with DKH
- x2c-TZVPall basis set from BSE for all elements
- More expensive but no pseudopotential approximation
- Use for benchmark calculations or when pseudopotential accuracy is insufficient

## SCF convergence troubleshooting

### Common SCF convergence issues with lanthanide complexes

| Problem | Solution |
|---------|----------|
| Tiny oscillations at end of SCF | `SCF=conver=6` (relax convergence) |
| No convergence after 200 cycles | BHandHLYP trick → read wavefunction → PBE0 |
| Wavefunction instability | `stable=opt` (always recommended) |
| Wrong initial guess | `guess=alter` to swap orbital occupations |
| Near-degenerate f-orbitals | `SCF=qc` (quadratic convergence, slower but more robust) |
| Memory issues | Increase `%mem`, use `SCF=incore` if memory allows |

### BHandHLYP trick in detail

When PBE0 SCF won't converge:

1. **First, converge with BHandHLYP:**
   ```
   #p BHandHLYP/genecp SCF=maxcyc=500
   ```
   BHandHLYP has 50% HF exchange → larger HOMO-LUMO gap → easier convergence for near-degenerate f-orbital systems

2. **Then, single-point with PBE0 reading the converged wavefunction:**
   ```
   #p PBE1PBE/genecp guess=read SCF=maxcyc=200
   ```
   The BHandHLYP-converged wavefunction is a much better starting point than the default initial guess

3. **Check the final wavefunction:**
   - Compare energy with direct PBE0 attempt
   - Verify `<S²>` value
   - Run `stable=opt` to confirm stability

## Frequency calculation notes

- After `stable=opt`, the wavefunction may have changed → **re-run frequency** if thermochemistry is needed
- Frequency calculation requires stable wavefunction — unstable wavefunctions can give wrong vibrational modes
- For large-core ECP: frequency is usually fine without `stable=opt`
- For small-core ECP: always run `stable=opt` before frequency

## References

- sobereva.com/581 — This article (lanthanide complex calculation)
- sobereva.com/355 — Gaussian calculation basics
- sobereva.com/82 — Wavefunction stability analysis
- sobereva.com/60 — Gaussian mixed basis/ECP input
- sobereva.com/272 — DFT functional selection
- Inorg. Chem., 58, 411 (2019) — PBE0 for lanthanide complexes
