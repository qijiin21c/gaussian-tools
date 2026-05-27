# Special Cases for Imaginary Frequency Elimination

Special causes and solutions for imaginary frequencies beyond optimization precision issues. Based on Sobereva's article (sobereva.com/608).

## 1. Symmetry too high in initial structure

### The problem

If the initial structure has higher symmetry than the true minimum, the optimization process may maintain this symmetry throughout, producing a structure at a symmetry-constrained point that is NOT the true minimum. The imaginary frequency corresponds to the symmetry-breaking distortion mode.

### Classic example: Biphenyl

- Ground state: two phenyl rings have a dihedral angle (twisted)
- If starting from a planar structure: optimization maintains planarity → imaginary frequency for the torsional mode between the two rings

### Solution: Distort along the imaginary mode

1. Open the optimized structure in GaussView
2. Go to the vibration mode view for the imaginary frequency
3. Select **Manual Displacement**
4. Drag the slider to distort slightly along the imaginary mode
5. Click **Save Structure** to get the new distorted structure
6. Create a new input file from this structure
7. Re-optimize and re-run frequency

### When this works well

- Single imaginary frequency caused by excessive initial symmetry
- Large systems where local regions have too-high symmetry

### When this is ineffective

- Other causes of imaginary frequencies (low optimization precision, etc.)
- Multiple imaginary frequencies — unlikely to resolve all at once
- Non-symmetry-related single imaginary frequencies — may work occasionally but not reliably

### Common beginner mistake

Many people, whenever they see ANY imaginary frequency, immediately try to distort along the imaginary mode. **This is wrong!** The optimization precision improvement methods (tight, calcfc/calcall/recalc, int=ultrafine) should be tried FIRST. Distorting along the mode has limited success rate for non-symmetry causes.

## 2. SMD implicit solvent model

### The problem

SMD (Solvation Model based on Density) is very popular (see sobereva.com/327). However:

- SMD introduces significant **numerical noise** on the PES
- This easily produces **false imaginary frequencies**
- Can also cause **optimization convergence difficulty**

### Solution: Use IEFPCM for opt+freq, SMD for energy

**Recommended workflow:**

Step 1 — Optimize and frequency in IEFPCM:
```
# B3LYP/6-31G(d) opt SCRF=(IEFPCM,Solvent=water)
# B3LYP/6-31G(d) freq SCRF=(IEFPCM,Solvent=water)
```

Step 2 — Single-point energy in SMD:
```
# B3LYP/6-31G(d) SCRF=(SMD,Solvent=water) SP Guess=Read Geom=Check
```

### Why this is the right approach

- SMD vs IEFPCM makes **no structural difference** — SMD's advantage is accounting for non-polar solvent contributions
- Non-polar contributions are important for energy calculations
- Non-polar contributions have **negligible effect on optimized geometry**
- See sobereva.com/327 for detailed discussion

**Strong recommendation:** Do NOT use SMD for opt and freq tasks.

## 3. IOp-defined custom functionals

### The problem

When using IOp to define custom functionals in Gaussian (see sobereva.com/344 and sobereva.com/550):

- **IOp settings do NOT carry over to the next task**
- With `opt freq`, IOp applies only to opt, NOT to freq
- This means opt and freq use **different functional definitions**
- Different functionals → different PES → likely imaginary frequencies

### Solution: Separate opt and freq jobs

When using custom functionals via IOp, run optimization and frequency as **two separate jobs**:

Job 1 — Optimization:
```
%chk=myopt.chk
# B3LYP/6-31G(d) opt IOp(xxx/yyy=zzz)
```

Job 2 — Frequency (read geometry and wavefunction from opt):
```
%chk=myopt.chk
# B3LYP/6-31G(d) freq Guess=Read Geom=Check
```

This ensures IOp settings are applied correctly to both steps.

### Custom range-separated functionals

The same issue applies to custom range-separated functionals (sobereva.com/550). Must separate opt and freq.

## 4. Program bug: Gaussian 09 D.01 DFT-D3(BJ)

### The bug

Gaussian 09 D.01 introduced DFT-D3 dispersion correction (see sobereva.com/413, sobereva.com/210, sobereva.com/83):

- Two versions: zero-damping `em=gd3` and BJ-damping `em=gd3bj`
- BJ-damping is more commonly used (better accuracy for interaction energies)
- **BJ-damping has a bug in analytical second derivatives in G09 D.01**
- Result: Even with perfectly converged optimization, freq with DFT-D3(BJ) may show imaginary frequencies

### Solutions

1. **Upgrade:** Use Gaussian 09 E.01 or later versions
2. **Workaround:** Use zero-damping DFT-D3(0) for both opt and freq:
   ```
   # B3LYP-D3(0)/6-31G(d) opt
   # B3LYP-D3(0)/6-31G(d) freq
   ```

## 5. Why calcall freq criteria might still differ from opt

If you used `opt=calcall` but freq still shows different criteria or NO, possible causes:

### (1) Level/setting mismatch
Freq uses different theory level, basis set, or numerical settings (e.g., DFT integration grid) than opt. Ensure strictly identical settings.

### (2) GaussView decimal precision loss
Reading the opt output in GaussView and saving as freq input loses decimal precision → introduces numerical error. Use `Geom=Check` from .chk instead.

### (3) GDIIS effect
Opt uses GDIIS (or GEDIIS which has GDIIS component). GDIIS predicts the next step's displacement using information from previous steps → differs from freq's Newton-method-based displacement check. This is normal and expected.

### (4) Different wavefunction convergence
Freq converged to a different wavefunction than opt's last step.

**How to check:** Compare single-point energies from both calculations. If they differ significantly, the wavefunctions are different. The higher-energy one is the unstable wavefunction for the current structure.

**Note:** Even the lower-energy one may not correspond to the stable wavefunction — need wavefunction stability test to confirm.

**Fix:** Use `Guess=Read` in freq to read the converged wavefunction from opt's .chk file:
```
%chk=opt_job.chk
# B3LYP/6-31G(d) freq Guess=Read Geom=Check
```

## Additional references

- sobereva.com/608 — This article (eliminating imaginary frequencies)
- sobereva.com/699 — Computing thermodynamic quantities with small imaginary frequencies
- sobereva.com/328 — Hess2freq program for computing frequencies from Hessian in .fch
- sobereva.com/69 — Grid integration method in DFT
- sobereva.com/44 — Transition state and reaction path calculation methods
- sobereva.com/327 — Solvation free energy and system free energy under implicit solvent model
- sobereva.com/344 — Using non-built-in methods/functionals in Gaussian
- sobereva.com/550 — Custom range-separated functionals in Gaussian
- sobereva.com/413 — Whether to add DFT-D3 dispersion correction
- sobereva.com/210 — Using DFT-D correction
- sobereva.com/83 — Rambling about DFT-D
