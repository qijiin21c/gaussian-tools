# Optimization Keyword Reference

Based on Sobereva (sobereva.com/62). Every keyword Gaussian supports for addressing geometry optimization convergence.

## Optimization Method Keywords

### opt=RFO
- Rational Function Optimization
-改良 of Newton-Raphson
- Default in G03 (Berny method)
- Good general-purpose method

### opt=GDIIS
- Geometric Direct Inversion in the Iterative Subspace
- Combined with RFO in Gaussian
- Default for semi-empirical in G03
- Generally faster than RFO for large systems with flat PES (small forces but large displacements)
- **Strongly recommended** for weak interaction systems and large flexible systems with non-convergence
- Note: Even with `cartesian` specified, GDIIS still uses redundant internal coordinates

### opt=GEDIIS
- Generalized EDIIS
- Default in G09
- Claimed to be most efficient but often not better in practice

## Hessian Matrix Keywords

### Default (no keyword)
- Approximate Hessian from valence force field
- Updated with gradients at each step
- Hessian remains approximate throughout optimization
- Why subsequent Freq often shows non-convergence (Freq uses exact Hessian)

### opt=calcfc
- Compute exact Hessian at first step only
- Subsequent steps use gradient-updated approximate Hessian
- Good balance of cost and reliability

### opt=calcall
- Compute exact Hessian at every step
- Solves many optimization failures
- Typically reduces required steps
- Guarantees accurate final result (convergence judged based on exact Hessian)
- Each step is much more expensive

### opt=recalc=N
- G16 only
- Recompute exact Hessian every N steps
- N=1 corresponds to calcall
- Recommended: N = 3~5 for balancing cost and convergence

### opt=readfc
- Read initial Hessian from .chk file
- Useful when even calcfc is too expensive at target level
- Strategy: freq at lower level → readfc at higher level

## Coordinate System Keywords

### opt=Cartesian
- Cartesian coordinates
- Usually slower than redundant internal coordinates
- Suitable for cluster systems with many molecules
- Use when redundant internal coordinate fails due to coordinate definition issues (e.g., dihedral atoms become colinear)

### opt=Z-Matrix
- Internal coordinates
- Faster than Cartesian for single-molecule systems
- Not suitable for clusters or ring systems (without dummy atoms)
- Very useful for high-symmetry systems (reduces variables with clever design)

### opt=ModRedundant (default: redundant internal coordinates)
- Redundant internal coordinates (default for unspecified opt)
- Automatically constructed — nearby atoms get bond length terms
- Usually easiest to converge for single-molecule systems
- Especially good for ring systems

To manually add bond length terms for weak interactions:
```
# B3LYP/6-31G(d) opt=modredundant

[coordinates]

3 7
12 14
```

Adds R(3,7), R(12,14) bond length terms to the redundant internal coordinate set.

## Step Control Keywords

### opt=maxcyc=N
- Sets maximum optimization steps (equivalent to scfcyc=N for opt)
- Default: varies by system size
- **Most misused approach** — only useful when convergence trend is clearly decreasing
- Pre-G16: internal cap exists (shown as "maximum allowed number of steps" in output)

### opt=maxstep=N
- Sets step size upper limit (trust radius) to 0.01N Bohr/radians
- Default: N=30
- Reduce to N=3~5 when oscillation with moderate displacement but large forces
- Don't reduce too early — slows optimization

### opt=noTrust
- Keeps maxstep setting fixed throughout (prevents dynamic trust radius adjustment)
- Recommended together with maxstep for small oscillation cases

## Convergence Criteria Keywords

### opt=loose
- Relaxed convergence criteria
- Use when high precision not needed
- **Warning:** Frequency analysis afterward more likely to show imaginary frequencies

### opt=tight
- Tighter convergence criteria
- Use for systems with very weak interactions or when accurate frequencies needed

### opt=verytight
- Very tight convergence criteria
- For highest precision requirements

## Symmetry Keywords

### symm=loose
- Relaxes point group recognition criteria
- Use when Gaussian fails to recognize high-symmetry point groups (e.g., Ih for C60)

## DFT Integration Keywords

### int=ultrafine
- (99,590) integration grid
- G09: upgrade from default fine grid (75,302)
- G16: already the default — only needed for G09
- Particularly important for Minnesota functionals

## Solvent Model Considerations

### scrf (default: IEFPCM)
- IEFPCM is recommended for opt+freq tasks
- Does not introduce significant numerical noise

### SMD solvent model
- **Not recommended for opt+freq tasks**
- Can make optimization harder and introduce imaginary frequencies in freq analysis
- Use for single-point calculations after optimization instead

## Transition State Keywords

### opt=TS
- Transition state search (first-order saddle point)

### opt(noeigen,TS)
- TS search without eigenvalue check (prevents early termination if Hessian has wrong number of negative eigenvalues)

### opt(calcfc,noeigen,TS)
- **Recommended typical TS keyword**
- Compute exact Hessian at first step, TS search without eigenvalue check

### opt(calcall,noeigen,TS)
- TS search with exact Hessian at every step
- Most reliable for difficult TS searches

### QST2
- Generates TS guess from reactant + product via interpolation
- Often produces unreasonable guesses
- Generally not recommended over manually constructed TS guesses

---

Note: This reference covers all Gaussian-supported optimization convergence options as listed in Sobereva's article (sobereva.com/62).
