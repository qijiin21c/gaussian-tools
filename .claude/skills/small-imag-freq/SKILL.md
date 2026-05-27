---
name: small-imag-freq
description: This skill should be used when the user asks to "calculate thermodynamics with imaginary frequency", "small imaginary frequency", "小虚频", "虚频热力学", "ZPE with imag freq", "entropy with imag freq", "free energy imaginary frequency", "QRRHO", "Grimme quasi-RRHO", "ignore imaginary frequency", or mentions computing thermodynamic quantities (ZPE, entropy, enthalpy, free energy) for structures that have small imaginary frequencies after geometry optimization and frequency analysis.
version: 0.1.0
---

# Small Imaginary Frequency Thermodynamics Helper

Guidance for computing thermodynamic quantities when small imaginary frequencies are present after geometry optimization and frequency analysis, based on Sobereva's article on this topic.

**Important:** This skill applies ONLY to minima with small imaginary frequencies. It has NOTHING to do with transition states, which inherently have exactly one imaginary frequency. Do NOT apply the methods here to transition state cases.

## What is a "small imaginary frequency"?

A small imaginary frequency is one with a magnitude typically below 50 cm^-1 (e.g., 9.8i, 27.3i cm^-1). These commonly appear for:
- Large flexible molecules
- Weakly bound complexes
- Systems with very flat potential energy surface dimensions

Such modes typically correspond to methyl rotation, flexible skeleton deformation, or intermolecular relative motion.

**Do NOT judge solely by magnitude** — other causes (listed below) can also produce numerically small imaginary frequencies.

## First: Identify the cause of the imaginary frequency

Before deciding whether to tolerate or eliminate the imaginary frequency, identify its cause:

### Must-always-fix causes (simple to resolve):

1. **PES settings mismatch** — Frequency calculation uses different PES-affecting settings than the optimization. This is a basic error. Ensure identical theory level, basis set, `int`, `scrf`, etc. between optimization and frequency.

2. **Excessive initial symmetry** — Initial structure has higher symmetry than the actual minimum. The optimized structure retains this symmetry, and the imaginary frequency corresponds to symmetry-breaking distortion. **Fix:** Distort the structure along the imaginary frequency mode, then re-optimize. Sometimes such a structure actually corresponds to a transition state.

3. **Program bug** — e.g., Gaussian 09 D.01 has a bug in DFT-D3 dispersion contribution to analytic Hessian, causing imaginary frequencies for flat PES systems. **Fix:** Use a version without the bug or a different program.

4. **Method introduces numerical noise** — e.g., SMD solvent model in Gaussian introduces noticeable numerical noise. **Fix:** Switch to IEFPCM, or use SMD with SAS (solvent-accessible surface) definition.

### Tolerable causes (hard to fix, may be acceptable):

5. **Imprecise geometry optimization convergence** — Optimization convergence limit too loose, or Hessian quality poor. Can be fixed with tighter convergence, `calcfc`, `calcall`, `recalc=N`, but for large systems this may take days.

6. **Insufficient integration grid quality** — Particularly significant for Minnesota functionals (M06-2X, etc.) which are sensitive to grid points. Can be fixed with `int=ultrafine`, but for large systems the cost may be prohibitive.

**Causes (5) and (6) are the ones this skill addresses** — when the imaginary frequency is genuinely due to optimization imprecision or grid quality on a flat PES, and eliminating it would cost excessive computation time.

## Computing different quantities with small imaginary frequencies

### Electronic energy

**Generally safe with small imaginary frequencies.**

At the default convergence limit, even if the structure isn't exactly at the true minimum, the displacement is small. The maximum and average forces are already small (since convergence criteria consider them), and force = negative energy gradient. So moving slightly to the exact minimum changes energy very little.

**Conclusion:** Electronic energy computed with small imaginary frequencies is generally usable — the difference from the true minimum is negligible.

### Zero-point energy ZPE and U(0)

**Generally safe with small imaginary frequencies.**

Under the harmonic approximation, each vibrational mode contributes 1/2·h·ν to ZPE. Low-frequency modes contribute very little — each wavenumber contributes only 5.98 J/mol to ZPE. A 30 cm^-1 mode contributes only 0.18 kJ/mol (0.04 kcal/mol), far below errors from theory level, basis set, solvent model, etc.

Mainstream quantum chemistry programs (including Gaussian) and Shermo **by default ignore imaginary frequency contributions** to thermodynamic quantities. So the small imaginary frequency's contribution to ZPE is directly skipped. If the imaginary frequency were eliminated, the resulting real frequency would also be very low, contributing negligibly to ZPE.

After eliminating the imaginary frequency, other real frequencies (especially low-frequency ones) may shift by several to ~10 cm^-1, but their contribution to ZPE is also small. For large flexible systems, the ZPE difference before/after eliminating the imaginary frequency is typically at most 1-2 kJ/mol.

**Conclusion:** Electronic energy and U(0) can generally tolerate one or more small imaginary frequencies.

### Thermal correction to internal energy Uvib(0→T) and U(T)

**Moderate risk with small imaginary frequencies.**

Low-frequency modes contribute significantly more to Uvib(0→T) than high-frequency modes. However, in the small tens of wavenumbers range, the frequency value's effect on Uvib(0→T) is noticeable but not huge — within 2.0-2.4 kJ/mol range.

Missing one small imaginary frequency (i.e., not counting one low real mode) causes an underestimation of ~2.2 kJ/mol for Uvib(0→298.15K). This is not negligible but may be acceptable.

**Conclusion:**
- With one small imaginary frequency: U(T) underestimation is ~0.5 kcal/mol — borderline acceptable
- With multiple small imaginary frequencies: **do NOT compute U(T)**, unless T is much lower than room temperature, or use the "treat imaginary as real" approach described below

### Entropy S and Gibbs free energy G

**Higher risk with small imaginary frequencies.**

Low-frequency modes contribute much more to entropy than high-frequency modes, and at very low frequencies, the lower the frequency, the larger the contribution.

Under the traditional RRHO (rigid-rotor harmonic oscillator) model used by Gaussian and most programs, as frequency approaches 0, the vibrational entropy contribution diverges sharply. This leads to severe overestimation.

**Use QRRHO (quasi-RRHO) models instead** — they interpolate between free rotor and harmonic oscillator, giving much more reasonable entropy for low-frequency modes:

| QRRHO Model | Description |
|-------------|-------------|
| **QRRHO(Grimme)** | Interpolates free rotor and harmonic oscillator. Frequency closer to 0 → larger free rotor weight. Much less sensitive to frequency values than RRHO. |
| **QRRHO(Truhlar)** | Raises all frequencies below a threshold (typically 100 cm^-1) to that threshold before computing contributions. Less physically motivated. |
| **QRRHO(Minenkov)** | Same entropy treatment as Grimme, but also applies the interpolation to Ucorr (thermal correction to internal energy). Cannot compute ZPE separately. Slightly better in practice. |

**Error analysis for entropy and free energy:**

If a small imaginary frequency exists and would become a 20 cm^-1 real frequency after elimination, using QRRHO(Grimme) at 298.15 K:
- Missing this mode causes entropy error of ~-18 J/mol/K
- Free energy error: ~-298.15 × (-18) / 1000 = 5.4 kJ/mol (>1 kcal/mol) — this is significant

However, a "entropy error cancellation" effect often occurs: structures with small imaginary frequencies tend to have other low-frequency modes slightly underestimated, which overestimates their entropy contribution. This partially cancels the underestimation from missing the imaginary frequency mode.

**Conclusion:**
- With one small imaginary frequency at room temperature: borderline acceptable with QRRHO
- With multiple small imaginary frequencies or high-temperature calculations: **do NOT compute with imaginary frequencies**
- **Always use QRRHO, never RRHO** — RRHO is much more sensitive to low-frequency values
- Note: T越大, -T×S越大, entropy errors cause larger free energy errors

## Treating small imaginary frequencies as real frequencies

Some researchers (e.g., Grimme, Angew. Chem. Int. Ed. 2022) suggest: under QRRHO, treat small imaginary frequencies as real (e.g., 18i → 18 cm^-1). The rationale: after elimination, you'd get a real mode with similar low frequency anyway, so treating it as real "makes up" for the missing contribution.

Shermo supports this via `imagreal` parameter (e.g., `imagreal=50` treats all imaginary frequencies with magnitude <50 as real).

**Sobereva's view: NOT recommended as a general practice.**

Reasons:
1. The difference between "with imaginary" and "without imaginary" structures is not just one mode changing from imaginary to real — many other low-frequency modes also shift, often systematically increasing. Without the conversion, the "entropy error cancellation" helps; with the conversion, the missing-mode underestimation is resolved but the low-frequency overestimation has nothing to cancel against.
2. If the system has many modes around 10 cm^-1, even QRRHO models are sensitive to frequency values in this range.
3. This approach is non-mainstream, overly subjective and optimistic, and lacks systematic validation.

**When it may help:**
- For computing Ucorr (thermal correction to internal energy), treating imaginary as real can reduce the difference between "with" and "without" imaginary frequency cases
- Combined with QRRHO(Truhlar), this gives entropy close to the no-imaginary-freq case (because all low frequencies are raised to 100 cm^-1 anyway), but QRRHO(Truhlar) performs poorly for cluster reaction free energies

**Recommendation:**
- For entropy and Gcorr requiring high precision: **eliminate the imaginary frequency if possible**
- If elimination is impractical: use **QRRHO(Minenkov)** without the "imaginary as real" treatment
- Do NOT default to "imaginary as real" — it is not a universal, robust, or ideal solution

## Recommended workflow

When small imaginary frequencies are found after optimization + frequency:

1. **Identify the cause** — is it (1)-(4) (must fix) or (5)-(6) (may tolerate)?

2. **If (1)-(4):** Fix immediately — mismatched settings, symmetry, program bug, or numerical noise. These are simple and must be resolved.

3. **If (5)-(6) and computational resources allow:** Eliminate the imaginary frequency using:
   - Tighter optimization convergence: `opt=tight`
   - Better Hessian: `opt=calcfc`, `opt=calcall`, or `opt=recalc=3`
   - Better integration grid: `int=ultrafine`
   - Distort along imaginary mode and re-optimize

4. **If (5)-(6) and computational resources do NOT allow elimination:**

   | Quantity to compute | Recommendation |
   |---------------------|----------------|
   | Electronic energy | Safe to use directly |
   | ZPE, U(0) | Safe to use (programs ignore imaginary by default) |
   | U(T), H(T) with one imag freq | Borderline acceptable; prefer QRRHO(Minenkov) or QRRHO(Grimme) |
   | U(T), H(T) with multiple imag freq | Not recommended; if necessary, use QRRHO(Minenkov) + imagreal |
   | Entropy, G(T) with one imag freq at room T | Borderline; use QRRHO(Minenkov) or QRRHO(Grimme), NOT RRHO |
   | Entropy, G(T) with multiple imag freq or high T | **Eliminate imaginary frequency** |

## Practical tools

### Shermo

Shermo is a standalone program for computing thermodynamic quantities from quantum chemistry program output files. It supports all QRRHO models and the `imagreal` option.

- Manual and download: sobereva.com/552
- `ilowfreq` parameter: 0=RRHO, 1=QRRHO(Truhlar), 2=QRRHO(Grimme), 3=QRRHO(Minenkov)
- `imagreal` parameter: threshold for treating imaginary frequencies as real (e.g., 50)
- `prtvib=1`: outputs each vibrational mode's contribution to thermodynamic quantities

### Gaussian

Gaussian computes thermodynamic quantities internally but does not support QRRHO models. For small imaginary frequency cases, it is recommended to extract the frequency data from Gaussian output and use Shermo for thermodynamic calculations.

## Additional Resources

For detailed methodology and computational principles, consult:

- **`references/thermo-methods.md`** — Detailed explanation of RRHO and QRRHO models, error analysis
- **`references/practical-examples.md`** — Practical workflow examples with Shermo
