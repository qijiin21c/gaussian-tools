# SCF Keyword Reference

Based on Sobereva (sobereva.com/61). Every keyword Gaussian supports for addressing SCF convergence.

## Integration Grid Keywords

### int=fine
- G09 default DFT integration grid (75,302)
- From G16 onward, this is NO LONGER the default

### int=ultrafine
- Finer grid (99,590)
- Recommended for Minnesota functionals (M06, M06-2X, etc.) in G09
- For non-Minnesota functionals, effect is limited
- From G16 onward, this is the default — only needed for G09

### int=acc2e=N
- Controls 2-electron integral accuracy
- G09 default: acc2e=10
- G16 default: acc2e=12 (already higher)
- Effective for large systems with many diffuse functions

## Variable Accuracy Keywords

### SCF=NoVarAcc
- Disables Gaussian's automatic reduction of integral precision in early SCF cycles
- Relevant specifically when diffuse functions are present
- Not applicable for systems without diffuse functions
- Also needed to ensure SCF=Conver=N actually takes effect (varacc can override Conver=N, considered a bug)

## Incremental Fock Keywords

### SCF=NoIncFock
- Disables Incremental Fock construction
- Gaussian default uses Incremental Fock to approximate Fock matrix construction, saving time but sometimes hindering convergence
- Recommended combined with NoVarAcc and int=acc2e=12 for large systems with heavy diffuse basis sets

## Level Shift Keywords

### SCF=VShift=N
- Raises virtual orbital energies by N (typically 300-500)
- Increases HOMO-LUMO gap, prevents excessive mixing between virtual and occupied orbitals
- Does NOT affect any final results (including orbital energies), only the convergence process
- Worth trying for small-gap systems, especially transition metal complexes

## Convergence Criterion Keywords

### SCF=Tight
- Default for single-point calculations in G09/16
- Equivalent to SCF=Conver=8

### SCF=Conver=N
- Density matrix RMS convergence limit: 1E-N
- Density matrix max change and energy convergence: 1E(-N+2)
- Conver=8 (default): tight, but density matrix requirement may be too strict
- Conver=6: safe for HF, semi-empirical, CASSCF, DFT (except double-hybrid) single-point
- For geometry optimization and frequency: do NOT reduce convergence limit (may give inaccurate results or hinder optimization)
- Exception: if initial geometry is far from real structure, reduce to Conver=6 (but not looser) for rough convergence, then re-optimize with default at final structure
- Note: must use NoVarAcc to ensure Conver=N actually works
- Note: G16 Opt/Freq/TDDFT/double-hybrid/post-HF require special IOp when reducing convergence (see sobereva.com/625)

## Initial Guess Keywords

### Guess (default)
- Uses Harris functional DFT-based initial guess (free-atom density superposition to build KS operator)

### Guess=Huckel
- Extended Huckel method
- Non-iterative, fast
- Default initial guess for some semi-empirical methods

### Guess=INDO
- Mixed INDO/CNDO/Huckel approach
- Iterative — requires its own initial guess (Extended Huckel)
- May itself fail to converge

### Guess=Core
- Core Hamiltonian only (single-electron terms, density matrix = zero matrix)
- Too rough for most ab initio/DFT calculations
- Default for some semi-empirical methods

### Guess=AM1
- Generally not directly usable as initial guess

### Guess=Read
- Reads wavefunction from .chk file
- Essential for restarting or using converged wavefunction from another calculation

## SCF Algorithm Keywords

### DIIS (default)
- Direct Inversion in the Iterative Subspace
- Default convergence accelerator
- Significantly reduces number of steps needed
- In rare cases, can actually cause non-convergence

### SCF=NoDIIS
- Disables DIIS
- Falls back to simpler damping approach
- Try when DIIS makes convergence worse

### SCF=QC (Quadratic Convergence)
- Newton-Raphson approach
- Fewer steps needed, some chance of solving non-convergence
- **Do NOT use lightly — only as last resort!**
- Reasons:
  1. Each step takes several times longer than normal
  2. Very likely to converge to an unstable (higher-energy) wavefunction — results may be meaningless. Always use `Stable` keyword to check
  3. High probability of L508 error after wasting significant time
- QC does NOT guarantee convergence — "forced convergence" is a myth

### SCF=XQC
- Standard iteration first, then QC if standard fails
- G09: switches after 64 cycles (or MaxCyc value)
- G16: switches after MaxConventionalCycles=N cycles (default 32)
- Same warnings as QC apply — do NOT use as default keyword

### SCF=Fermi
- Fermi-Dirac distribution for fractional orbital occupation
- Also automatically applies level shift and damping as appropriate
- Useful for metallic and small-gap systems

### SCF=DM (Direct Minimization)
- Iteratively minimizes energy with respect to orbital rotation
- More robust than DIIS for difficult cases
- Slower per cycle

### SCF=SD (Steepest Descent)
- Oldest and simplest method
- Very slow, rarely used

## Maximum Cycles

### SCF=MaxCyc=N
- Increases SCF iteration limit (default 128)
- Equivalent to scfcyc=N
- **Most misused approach** — >99% of cases, setting N to hundreds/thousands is pointless
- Only useful when iteration history shows energy and density matrix changes are gradually decreasing (not oscillating), suggesting convergence beyond 128 is plausible
- Rare situation (most commonly lanthanide/actinide complexes with small-core pseudopotentials)

## Other Keywords

### Symm=Nosymm
- Disables molecular symmetry

### Stable
- Checks wavefunction stability
- Should be used when QC is employed to verify the converged wavefunction is the ground state

---

Note: This reference covers all Gaussian-supported SCF convergence options as listed in Sobereva's article (sobereva.com/61).
