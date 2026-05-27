---
name: scf-convergence
description: This skill should be used when the user asks to "help SCF converge", "fix SCF convergence failure", "SCF did not converge", "add SCF=XQC", "change SCF algorithm", "convergence problem", "guess=mix", "SCF不收敛", or mentions Gaussian SCF convergence issues including oscillation, divergence, and failed geometry optimization due to SCF.
version: 0.1.0
---

# SCF Convergence Helper

Comprehensive guidance for diagnosing and resolving SCF convergence failures in Gaussian, based on Sobereva's authoritative article (sobereva.com/61).

**Important:** No method guarantees 100% convergence. All applicable methods must be tried systematically, sometimes combined. If every method below has been attempted and nothing works, no other Gaussian approach will solve it either.

## Pre-check: Verify input correctness before trying SCF fixes

When SCF fails, first check these common input errors:

1. **Atoms too close** — Some interatomic distances are unreasonably short
2. **Severely distorted geometry** — Structure is far from the real molecular geometry, leading to unphysical electronic structure
3. **Unreasonable structure** — Missing hydrogens, unsaturated dangling bonds in cluster models, or structures lacking basic chemical sense
4. **Wrong spin multiplicity** — Especially for transition metal complexes, non-ground-state multiplicity is harder to converge
5. **Keyword errors** — e.g., using gen without specifying ECP for pseudopotential basis sets, missing basis set definitions for some atoms, defining basis but not ECP portion
6. **Wrong charge** — Net charge set incorrectly. External field calculations are inherently harder to converge; excessively strong fields can cause electrons to leave the system entirely

## Diagnostic workflow

1. **Read the .log/.out file** — check the SCF iteration details (use `#P` to print full details)
2. **Identify the failure mode:**
   - Oscillation: energy alternates between values across cycles
   - Divergence: energy grows without bound
   - Slow convergence: still improving but not within 128 (default max) cycles
3. **Try the resolution methods below in sequence.** Each method should be attempted before moving to the next.

## Resolution methods

### (1) Increase DFT integration grid: `int=ultrafine`

For Minnesota functionals (M06, M06-2X, etc.), increasing grid accuracy can help. G09 default is `int=fine` (75,302); upgrade to `int=ultrafine` (99,590). For non-Minnesota functionals, this has limited effect.

**Note:** From G16 onward, the default is already `int=ultrafine`, so this only applies to G09.

```
# M06-2X/6-31G(d) int=ultrafine
```

### (2) Disable variable accuracy: `SCF=NoVarAcc`

Gaussian automatically reduces integral precision in early SCF cycles to speed up computation, but this can hinder convergence. This is specifically relevant when **diffuse functions are present** (not applicable otherwise).

**Note:** From G16 onward, this is less of an issue by default, but still worth trying for diffuse-function cases.

```
# B3LYP/aug-cc-pVDZ SCF=NoVarAcc
```

### (3) Increase integral accuracy: `int=acc2e=12`

G09 default is `int=acc2e=10`; upgrade to `int=acc2e=12`. Effective for large systems with many diffuse functions. Less useful for systems without diffuse functions.

**Note:** From G16 onward, the default is already `int=acc2e=12`.

```
# B3LYP/aug-cc-pVTZ int=acc2e=12
```

### (4) Disable Incremental Fock: `SCF=NoIncFock`

Gaussian default uses Incremental Fock to approximate Fock matrix construction each step, saving time but sometimes hindering convergence.

**Recommended triple combination for large systems with heavy diffuse basis sets** (e.g., aug-cc-pVTZ and larger):

```
# B3LYP/aug-cc-pVTZ SCF(NoVarAcc,NoIncFock) int=acc2e=12
```

This combination has a good chance of solving convergence problems with moderate extra cost. However, it is not guaranteed. For basis sets without many diffuse functions, this combination has lower success rate — try other methods below if it fails.

Removing diffuse functions first, converging the wavefunction, and using it as initial guess (see method 8) is also very effective.

### (5) Level shift virtual orbitals: `SCF=VShift=N`

Raise virtual orbital energies by N (typically 300-500) to increase the HOMO-LUMO gap and prevent excessive mixing between virtual and occupied orbitals. This only affects the convergence process — it does **not** change any final results, including orbital energies. Worth trying for systems with small HOMO-LUMO gaps, especially transition metal complexes.

```
# B3LYP/6-31G(d) SCF=VShift=300
```

### (6) Adjust convergence criterion: `SCF=Conver=N`

Sets density matrix RMS convergence limit to 1E-N, with density matrix max change and energy convergence at 1E(-N+2). G09/16 default for single-point is `SCF=Tight` (= `SCF=Conver=8`), but the density matrix requirement can be too strict — energy is usually already converged to high precision.

- For HF, semi-empirical, CASSCF, DFT (except double-hybrid) single-point calculations: can safely reduce to `Conver=6` (100x looser), energy change at convergence is typically still very small.
- For geometry optimization and frequency analysis: do **not** reduce the default SCF convergence limit, or results may be inaccurate and may hinder optimization convergence.
- However, if the initial geometry is far from the real structure (making early optimization steps hard to converge), reducing to `Conver=6` (but not looser) to get a rough convergence, then re-optimizing with default convergence at the final structure, is a helpful approach.

**Note 1:** Gaussian often uses lower integral precision early on (varacc), during which `SCF=Conver=N` does not take effect (considered a bug). Use `NoVarAcc` to ensure `SCF=Conver=N` actually works.

**Note 2:** For G16 geometry optimization, frequency analysis, TDDFT, double-hybrid, or post-HF methods, reducing SCF convergence requires special IOp settings, otherwise the calculation will fail the convergence check. See sobereva.com/625.

```
# For single-point (looser, faster convergence)
# B3LYP/6-31G(d) SCF=Conver=6
```

### (7) Try a different functional

If one functional fails to converge, try another. If it converges, use `Guess=Read` to read the converged wavefunction as initial guess.

Minnesota functionals (M06-2X, etc.) are typically harder to converge than others. If stuck, try B3LYP or other functionals. Higher HF percentage functionals generally converge more easily, especially for transition metal complexes.

```
# Step 1: converge with easier functional
# B3LYP/6-31G(d) SP
# Step 2: use converged wavefunction as guess
# M06-2X/6-31G(d) Guess=Read SP
```

### (8) Use a smaller basis set first, then Guess=Read

Small basis sets converge more easily than large ones. When the large basis set fails but a smaller one succeeds, use the smaller-basis converged wavefunction as the initial guess.

- def2-TZVP fails but def2-SVP converges → use def2-SVP result as guess for def2-TZVP
- aug-cc-pVTZ fails → try cc-pVTZ, then use converged wavefunction for aug-cc-pVTZ
- Basis sets that are too different in size (e.g., STO-3G → def2-TZVP) provide little benefit
- For extremely difficult cases, step up gradually: STO-3G → 3-21G → 6-31G* → 6-311G** → def2-TZVP

```
# Step 1: converge with small basis
# B3LYP/def2-SVP SP
# Step 2: use as guess for target basis
# B3LYP/def2-TZVP Guess=Read SP
```

### (9) Change initial guess method

- `Guess=Huckel` — Extended Huckel method (non-iterative, fast)
- `Guess=INDO` — Mixed INDO/CNDO/Huckel (iterative, may itself fail to converge)
- `Guess=Core` — Core Hamiltonian only (too rough, only for semi-empirical defaults)
- `Guess=AM1` — Generally not directly usable

The default uses Harris functional DFT-based initial guess (free-atom density superposition). INDO requires its own initial guess (Extended Huckel) and may not converge itself.

```
# B3LYP/6-31G(d) Guess=Huckel
```

### (10) Quadratic Convergence: `SCF=QC` / `SCF=XQC`

QC uses Newton-Raphson approach, typically requiring fewer steps and having some chance of solving SCF non-convergence.

- `SCF=QC` — Full QC from the start
- `SCF=XQC` — Standard iteration first, switch to QC if it fails
  - G09: switches after 64 cycles (or MaxCyc value)
  - G16: switches after MaxConventionalCycles=N cycles (default 32)

**Strong warning: Do NOT use QC or XQC lightly, and absolutely do NOT make them default keywords!** Try all other methods first; only resort to QC as a last resort. Reasons:

1. QC is extremely expensive — each SCF step takes several times longer than normal
2. If QC is required for convergence, the resulting wavefunction is very likely NOT the most stable one, meaning the energy may be higher than the true ground state — the result is meaningless. Always add `Stable` keyword to check wavefunction stability when using QC.
3. High probability that QC will also fail to converge, producing L508 error after wasting significant computation time.

QC does **not** guarantee convergence despite what some online sources claim — "forced convergence" is a myth.

```
# Last resort only
# B3LYP/6-31G(d) SCF=QC Stable
```

### (11) Fermi broadening: `SCF=Fermi`

Uses Fermi-Dirac distribution for fractional orbital occupation. Also automatically applies level shift and damping as appropriate.

```
# B3LYP/6-31G(d) SCF=Fermi
```

### (12) Disable DIIS: `SCF=NoDIIS`

DIIS is the default convergence accelerator, reducing the number of steps needed. However, in rare cases it can actually cause non-convergence. Try disabling it.

```
# B3LYP/6-31G(d) SCF=NoDIIS
```

### (13) Slightly modify molecular geometry

Slightly shorten/elongate bond lengths or change bond angles. If a converged wavefunction is obtained, use it as the initial guess for the original geometry. During geometry optimization, Gaussian automatically uses the previous step's converged wavefunction as the initial guess for the next step — this strategy works on the same principle.

### (14) Open-shell systems: try closed-shell ion first

For open-shell systems, first calculate the corresponding closed-shell ion to get a converged wavefunction, then read it as initial guess.

**Important:** RO (restricted open-shell) calculations are much, much harder to converge than U (unrestricted). If RO fails to converge, switch to U first.

```
# Step 1: converge closed-shell ion
# B3LYP/6-31G(d) SP
# Step 2: use as guess for open-shell
# UB3LYP/6-31G(d) Guess=Read SP
```

### (15) Cationic systems converge more easily

Systems with fewer electrons (e.g., cations vs anions) generally converge more easily. Calculate the ionized state first, then use the converged wavefunction as initial guess.

### (16) Solvent model: try different solvent or vacuum

For SCF non-convergence in solvent calculations, try a different solvent, vacuum, or different solvent model. If it converges, use the converged wavefunction as initial guess for the original solvent.

```
# Step 1: converge in vacuum
# B3LYP/6-31G(d) SCRF=None SP
# Step 2: use as guess for solvent
# B3LYP/6-31G(d) SCRF=(Solvent=Water) Guess=Read SP
```

### (17) Increase maximum SCF cycles: `SCF=MaxCyc=N`

Increases the SCF iteration limit to hundreds or thousands.

**This is the most commonly misused approach by beginners and should be a last consideration.** Within Gaussian's default 128 cycles (which is already generous), increasing N rarely helps — it wastes time computing useless extra cycles. Only increase MaxCyc when the iteration history shows energy and density matrix changes are gradually decreasing (not oscillating), suggesting convergence beyond 128 cycles is plausible. This situation is rare (most commonly with lanthanide/actinide complexes using small-core pseudopotentials, see sobereva.com/581).

If increasing MaxCyc to hundreds or thousands solved convergence, why wouldn't Gaussian just default to that?

```
# Only when iteration trend clearly shows gradual convergence
# B3LYP/6-31G(d) SCF=MaxCyc=512
```

### (18) Switch method, basis set, or program

If none of the above works, try a different method, basis set, or quantum chemistry program. If another program converges with the same level of theory and comparability is needed:

1. Use Multiwfn to load the other program's output containing basis function info (e.g., .molden file, see sobereva.com/379)
2. Enter main function 100 → sub-function 2 → export wavefunction as .fch file
3. Use Gaussian's formchk to convert .fch to .chk
4. Use `Guess=Read` in Gaussian to read the wavefunction as initial guess — this has a high probability of working

Gaussian-converged wavefunctions can also be converted back for use in other programs (see sobereva.com/517).

## Additional Resources

For detailed keyword reference and failure patterns, consult:

- **`references/scf-strategies.md`** — Detailed explanation of every SCF keyword
- **`references/common-failures.md`** — Common failure patterns with before/after examples
