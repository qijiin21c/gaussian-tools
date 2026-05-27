# Common Geometry Optimization Failure Patterns

## Pattern 1: Oscillation — most common cause of non-convergence

**Symptom:** "Error termination request processed by link 9999" with "Number of steps exceeded"

**Cause:** Optimization oscillates — forces and geometry change with periodic/cyclic trends instead of monotonically decreasing.

**Diagnosis:**
1. Use GaussView with "Read intermediate geometries" enabled
2. Play optimization animation to visually inspect oscillation
3. Results → Optimization: check energy/force/displacement curves — if they oscillate without overall decreasing trend, oscillation confirmed

**Fix (try in recommended order):**
1. `int=ultrafine` (G09 DFT only); if using SMD, switch to IEFPCM
2. `opt=calcall` (small system) or `opt=recalc=3` (large system)
3. `opt=GDIIS`
4. `opt(GDIIS,maxstep=5,noTrust)`
5. `opt=loose` (last resort — freq afterward may show imaginary frequencies)

---

## Pattern 2: SCF failure during optimization

**Symptom:** Optimization fails mid-process not due to geometry convergence but because a single-point energy calculation failed

**Cause:** SCF non-convergence at one of the optimization steps

**Fix:** See scf-convergence skill. Common approach: `SCF=XQC` or `SCF=NoVarAcc` combined with the optimization keywords.

```
# B3LYP/6-31G(d) opt SCF=XQC
```

---

## Pattern 3: High-symmetry initial structure preventing convergence

**Symptom:** Optimization starts with a highly symmetric structure, maintains symmetry throughout, but never converges. Even if it does converge, imaginary frequencies appear.

**Cause:** The actual PES minimum does not have the initial symmetry.

**Fix:** Manually perturb the initial structure slightly — twist a dihedral angle a bit, displace one atom slightly, etc.

**Conversely — system becoming symmetric but not converging:**
1. Extract the current structure
2. GaussView → Edit → Point Group → lower tolerance → identify highest point group → Symmetrize
3. Re-optimize (optionally with `symm=loose` if Gaussian doesn't recognize the point group)

---

## Pattern 4: Ring system non-convergence in internal coordinates

**Symptom:** Single-molecule ring system fails to converge with internal coordinates

**Cause:** Ring is defined from one atom going around — head and tail atoms are geometrically close but not connected in internal coordinates, causing strong coupling.

**Fix:**
1. Use redundant internal coordinates (default) — Gaussian automatically adds bond terms for nearby atoms including ring head-tail
2. If still failing, add manual redundant terms with `opt=modredundant`:

```
# B3LYP/6-31G(d) opt=modredundant

[coordinates with blank line after]
1 6
```

---

## Pattern 5: Weak interaction / hydrogen bond cluster oscillation

**Symptom:** Water cluster or other molecular cluster oscillates during optimization

**Cause:** Weak interactions (hydrogen bonds, van der Waals) between distant atoms don't get automatic bond length terms in redundant internal coordinates.

**Fix:** Add bond length terms for all relevant weak interactions:

```
# B3LYP/6-31G(d) opt=modredundant

[coordinates]

# H...O hydrogen bonds
2 8
4 10
6 12

# O...O (optional, may further help)
1 7
3 9
```

---

## Pattern 6: Deep narrow potential well — overshooting

**Symptom:** Optimization oscillates with moderate displacement per step but large forces

**Cause:** Process is stuck in a deep, narrow potential well, overshooting the minimum each step.

**Fix:** Reduce step size limit:

```
# B3LYP/6-31G(d) opt(maxstep=5,noTrust)
```

Use `noTrust` to prevent dynamic trust radius adjustment. Combine with GDIIS if needed:

```
# B3LYP/6-31G(d) opt(GDIIS,maxstep=3,noTrust)
```

**Don't do this too early** — if the structure is still far from minimum, reducing step size just slows things down.

---

## Pattern 7: Cartesian coordinate failure for cluster systems

**Symptom:** Multi-molecule cluster optimization fails or is very slow in Cartesian coordinates

**Cause:** Cartesian coordinates have high coupling between atoms — moving one atom along x affects many nearby atoms' forces.

**Fix:** Use redundant internal coordinates (default) or explicitly:

```
# B3LYP/6-31G(d) opt
```

Or if redundant internal coordinate definition fails (e.g., colinear dihedral), switch to Cartesian:

```
# B3LYP/6-31G(d) opt=Cartesian
```

---

## Pattern 8: Dihedral angle oscillating between two values

**Symptom:** A specific dihedral angle oscillates between two values during optimization

**Fix:** Set the initial dihedral to the average of the two oscillating values, then restart (ideally with calcfc):

```
# B3LYP/6-31G(d) opt=calcfc
# [set dihedral to average value in coordinates]
```

---

## Pattern 9: Large system — calcall too expensive

**Symptom:** `opt=calcall` would help but each step is prohibitively expensive for a large system

**Fix:**
1. `opt=recalc=3` or `opt=recalc=5` (G16 only) — recompute Hessian every 3 or 5 steps
2. `opt=calcfc` — exact Hessian at first step only
3. Lower-level freq → `opt=readfc` at target level:

```
# Step 1: get Hessian at lower level
# HF/3-21G Freq
# Step 2: use for target-level optimization
# B3LYP/6-31G(d) opt=readfc
```

---

## Pattern 10: SMD solvent model causing optimization difficulty

**Symptom:** Optimization with SMD solvent model is harder to converge, and after convergence, frequency analysis shows imaginary frequencies

**Cause:** SMD introduces numerical noise in the potential energy surface.

**Fix:**
1. Switch to IEFPCM: `scrf=(IEFPCM,Solvent=Water)` or just `scrf=(Solvent=Water)` (IEFPCM is default)
2. If IEFPCM also fails and solvent is not absolutely necessary, optimize in vacuum, then compute single-point with SMD:

```
# Step 1: optimize in vacuum
# B3LYP/6-31G(d) opt
# Step 2: single-point with SMD
# B3LYP/6-31G(d) SCRF=(SMD,Solvent=Water) SP Guess=Read Geom=Check
```

**Note:** Optimization and single-point do NOT need the same solvent model.

---

## Pattern 11: Transition state optimization non-convergence

**Symptom:** TS optimization fails or heads toward chemically meaningless structure

**Cause:** Initial TS guess is not close enough to actual TS. TS optimization is much more sensitive to initial structure than minimum optimization.

**Fix:**
1. **Hessian quality is critical** — use `calcall` or `recalc=3`:

```
# B3LYP/6-31G(d) opt(calcalc,noeigen,TS)
# or (G16):
# B3LYP/6-31G(d) opt(recalc=3,noeigen,TS)
```

2. **Check structure evolution** — use GaussView to verify the TS structure is evolving toward a chemically sensible geometry
3. **Abandon QST2** if structure heads in wrong direction — use `opt=TS` with manually constructed guess instead

---

## Pattern 12: High-symmetry point group not recognized

**Symptom:** Gaussian fails to recognize a high-symmetry point group (e.g., Ih for C60) even after structure symmetrization in GaussView

**Cause:** Program limitations and input file precision issues.

**Fix:**
1. Use internal coordinates instead of Cartesian in the input file
2. `symm=loose` to relax point group recognition criteria

```
# B3LYP/6-31G(d) opt symm=loose
```

---

## Pattern 13: Optimization heading in wrong direction

**Symptom:** Optimization structure evolves toward obviously unreasonable or unexpected geometry

**Cause:** Initial structure is clearly wrong, or theory level/basis set/electronic state/calculation model is unreasonable.

**Fix:**
1. Rebuild the initial structure
2. Verify theory level is appropriate for the system (e.g., don't use B3LYP for van der Waals complexes without dispersion correction)
3. Verify charge and multiplicity are correct
4. Check for input errors (missing basis set definitions, ECP issues, etc.)
