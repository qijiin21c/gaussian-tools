# Common SCF Convergence Failure Patterns

## Pre-check: Before trying any SCF fix, verify these

1. **Atoms too close** — Check for unreasonably short interatomic distances
2. **Severely distorted geometry** — Structure far from real molecular geometry leads to unphysical electronic structure
3. **Unreasonable structure** — Missing hydrogens, unsaturated dangling bonds in cluster models, or structures lacking basic chemical sense
4. **Wrong spin multiplicity** — Especially for transition metal complexes, non-ground-state multiplicity is harder to converge
5. **Keyword errors** — e.g., `gen` without ECP specification, missing basis set definitions, defining basis but not ECP portion
6. **Wrong charge or problematic settings** — Net charge incorrect. External field calculations are inherently harder; excessively strong fields can cause electrons to leave the system

---

## Pattern 1: Large system with heavy diffuse basis set

**Symptom:** SCF fails with aug-cc-pVTZ or larger basis sets containing many diffuse functions

**Cause:** Diffuse functions make SCF significantly harder, especially in large systems

**Recommended triple combination (high success rate, moderate extra cost):**

```
# B3LYP/aug-cc-pVTZ SCF(NoVarAcc,NoIncFock) int=acc2e=12
```

**Alternative:** Remove diffuse functions, converge wavefunction, then use as Guess=Read with diffuse functions:

```
# Step 1: converge without diffuse
# B3LYP/cc-pVTZ SP
# Step 2: use as guess with diffuse
# B3LYP/aug-cc-pVTZ Guess=Read SP
```

---

## Pattern 2: Minnesota functional non-convergence (G09)

**Symptom:** M06, M06-2X, or other Minnesota functionals fail to converge

**Cause:** Minnesota functionals require finer integration grids

**Fix:**
1. `int=ultrafine` (G09 only — G16 default is already ultrafine)
2. Try a different functional (e.g., B3LYP), then `Guess=Read`

```
# G09 only
# M06-2X/6-31G(d) int=ultrafine
```

---

## Pattern 3: Small HOMO-LUMO gap / transition metal complex

**Symptom:** SCF oscillates or diverges for transition metal complexes

**Cause:** Near-degenerate d orbitals, small gap between occupied and virtual orbitals

**Fix (try in order):**
1. `SCF=VShift=300` (or 500) — level shift virtual orbitals
2. `SCF=Fermi` — Fermi broadening
3. Try functionals with higher HF percentage (generally easier to converge)
4. `SCF=NoDIIS`

**Example:**
```
# B3LYP/6-31G(d) SCF=VShift=300
```

---

## Pattern 4: ROHF/RO-DFT open-shell non-convergence

**Symptom:** Restricted open-shell calculation fails

**Cause:** RO formalism is MUCH harder to converge than unrestricted (U)

**Fix:**
1. Switch to unrestricted: `UB3LYP` instead of `RB3LYP`
2. Calculate closed-shell ion first, then `Guess=Read`
3. For cationic open-shell: calculate dianion first, then `Guess=Read`

**Example:**
```
# Step 1: converge closed-shell ion
# B3LYP/6-31G(d) SP
# Step 2: use as guess for open-shell
# UB3LYP/6-31G(d) Guess=Read SP
```

---

## Pattern 5: Geometry optimization first-step SCF failure

**Symptom:** SCF fails during the first step of Opt

**Cause:** Initial geometry is far from equilibrium

**Fix:**
1. Use `SCF=Conver=6` (but not looser) for rough convergence
2. Then re-optimize with default convergence at the final structure
3. Or: optimize at lower level first, then `Guess=Read`

**Note:** For G16 Opt/Freq, reducing convergence requires special IOp (see sobereva.com/625).

```
# First rough convergence
# B3LYP/6-31G(d) SCF(Conver=6,NoVarAcc) Opt
# Then strict convergence
# B3LYP/6-31G(d) Opt Guess=Read
```

---

## Pattern 6: Solvent model SCF failure

**Symptom:** SCF fails with PCM/SMD solvent model

**Fix:**
1. Try vacuum or different solvent first
2. Converge there, then `Guess=Read` for target solvent

```
# Step 1: converge in vacuum
# B3LYP/6-31G(d) SCRF=None SP
# Step 2: use as guess for solvent
# B3LYP/6-31G(d) SCRF=(Solvent=Water) Guess=Read SP
```

---

## Pattern 7: Anion non-convergence

**Symptom:** Anion calculation fails, but neutral or cation converges

**Cause:** Extra electrons make SCF harder, especially with diffuse functions

**Fix:**
1. Calculate neutral or cation first
2. Use converged wavefunction as `Guess=Read` for anion

```
# Step 1: converge neutral
# B3LYP/6-31+G(d) SP charge=0
# Step 2: use as guess for anion
# B3LYP/6-31+G(d) Guess=Read SP charge=-1
```

---

## Pattern 8: Oscillation

**Symptom:** Energy alternates between values across consecutive cycles

**Cause:** DIIS extrapolating past the solution

**Fix (try in order):**
1. `SCF=NoDIIS`
2. `SCF=VShift=300`
3. `SCF=Fermi`

---

## Pattern 9: Slow convergence within max cycles

**Symptom:** Energy trending downward but not within 128 cycles

**Only increase MaxCyc when iteration clearly shows decreasing changes (not oscillating):**

```
# B3LYP/6-31G(d) SCF=MaxCyc=512
```

**Note:** This is the most commonly misused approach. >99% of cases, setting N to hundreds/thousands is pointless. Only useful for specific situations (e.g., lanthanide/actinide complexes with small-core pseudopotentials).

---

## Pattern 10: Desperation case — QC as last resort

When nothing else works and QC is attempted:

```
# B3LYP/6-31G(d) SCF=QC Stable
```

**Warnings:**
- Extremely expensive per step
- High probability of converging to unstable wavefunction — always add `Stable`
- High probability of L508 error after wasting time
- QC does NOT guarantee convergence

---

## Pattern 11: Try another program

If Gaussian cannot converge at all:
1. Try ORCA, GAMESS, or other programs
2. If another program converges, convert wavefunction via Multiwfn:
   - Load .molden from other program
   - Main function 100 → sub-function 2 → export as .fch
   - formchk .fch → .chk
   - `Guess=Read` in Gaussian
