# Common IRC Failure Patterns

## Pre-check: Before running IRC

1. **TS optimization must be completed** — IRC must start from a properly optimized transition state
2. **Strictly identical settings** — TS optimization and IRC must use exactly the same theory level, basis set, `int=ultrafine`, `scrf` settings, etc. Any setting affecting the PES must match. Compare single-point energies to verify.
3. **Correct starting structure** — Use the TS structure from optimization (not a guess), either written directly or via `geom=check` from the TS .chk file.

---

## Pattern 1: "Maximum number of corrector steps exceeded" — HPC failure

**Symptom:** IRC fails with this error message. This is the most common IRC error.

**Cause:** HPC method's corrector step (modified Bulirsch-Stoer iteration) fails to converge.

**Solutions (try in order):**

1. **Switch to LQA** — 100% solves the problem but sacrifices some accuracy:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,LQA)
   ```

2. **Reduce stepsize** — smaller stepsize = higher chance of avoiding the error:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,stepsize=5)
   ```

3. **Add calcall or recalc** — more accurate Hessian helps corrector convergence:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,calcall)
   # or for lower cost:
   # B3LYP/6-31G(d) IRC(calcfc,recalc=3)
   ```

4. **Switch to GS2** — completely avoids HPC corrector failures:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,GS2)
   ```

5. **Do NOT use maxcyc=N** — increasing corrector iteration limit almost never works. This is a common beginner mistake.

6. **Do NOT use tight** — tightening corrector convergence makes failures MORE likely, not less.

---

## Pattern 2: IRC stops after a few steps, or both sides produce the same curve

**Symptom:** IRC terminates prematurely, or the "energy vs reaction coordinate" plot shows both sides going in the same direction.

**Cause:** TS optimization was not accurate enough. The TS structure is slightly offset from the true saddle point, so when going "left," the program detects energy increasing and thinks it has reached a minimum.

**Diagram (from article):**
```
         TS (true saddle point)
          |
    ------●------   ← correct IRC goes both directions
         /
        ○           ← actual TS found (offset)
       / \
      /   →→→→→→→→  ← both sides go right
```

**Solutions (try in order):**

1. **Verify settings** — IRC uses the exact TS structure, and both TS and IRC use strictly identical settings (same keywords, int, scrf, etc.)

2. **Improve TS accuracy:**
   ```
   # B3LYP/6-31G(d) opt(calcfc,noeigen,TS,tight) int=ultrafine
   # Then IRC with same settings:
   # B3LYP/6-31G(d) IRC=calcfc int=ultrafine
   ```
   Or use `calcall`/`recalc=3` during TS optimization.

3. **Increase IRC stepsize** to 20 or 30 — this may allow the IRC to "jump over" the offset TS:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,stepsize=25)
   ```

4. **Wavefunction mismatch** — Check if the first SCF Done energy in IRC differs from the last SCF Done in TS optimization. If different, the PES is effectively different. Fix:
   ```
   # B3LYP/6-31G(d) IRC(calcfc) Guess=Read
   ```
   Also consider running Forward and Reverse as two separate jobs.

5. **SMD solvent model** — Numerical noise from SMD can cause early termination. Switch both TS optimization and IRC to IEFPCM:
   ```
   # B3LYP/6-31G(d) opt(calcfc,noeigen,TS) SCRF=(IEFPCM,Solvent=ethanol)
   # B3LYP/6-31G(d) IRC(calcfc) SCRF=(IEFPCM,Solvent=ethanol)
   ```

---

## Pattern 3: L502 error during IRC (SCF non-convergence)

**Symptom:** IRC fails with L502 error — SCF did not converge at one of the IRC points.

**Cause:** SCF convergence failure at an intermediate IRC point.

**Solutions:**
1. Apply SCF convergence methods (see scf-convergence skill)
2. If first SCF in IRC fails: add `Guess=Read` to read wavefunction from TS .chk
3. If mid-IRC SCF fails: reduce stepsize — smaller steps mean the previous point's wavefunction is a better guess:
   ```
   # B3LYP/6-31G(d) IRC(calcfc,stepsize=5) SCF=XQC Guess=Read
   ```

---

## Pattern 4: IRC curve is sharp/spiky at the TS position

**Symptom:** The "energy vs reaction coordinate" plot shows a sharp peak or irregularity at the TS (reaction coordinate = 0) instead of a smooth curve.

**Cause:** TS position not accurately located, or PES settings differ between TS and IRC, or wavefunction mismatch.

**Solutions:**
1. Verify TS structure is from optimization, not a guess
2. Verify all PES-affecting settings are identical between TS and IRC
3. Increase TS accuracy: `tight`, `calcall`/`recalc=x`, `int=ultrafine`
4. Try GS2 algorithm or calcall for IRC
5. Ensure first SCF in IRC converges to the same wavefunction as last step of TS optimization (`Guess=Read`)

---

## Pattern 5: IRC endpoint optimization gives wrong minima

**Symptom:** After optimizing the IRC endpoints, the resulting structures are not the expected reactant/product.

**Cause:** Either (a) the TS actually connects to different minima than expected, or (b) the optimization jumped to a neighboring minimum.

**Solutions:**
1. Run IRC longer (larger maxpoints) to verify which minima the TS actually connects to
2. For endpoint optimization, use smaller stepsize:
   ```
   # B3LYP/6-31G(d) opt(maxstep=5,noTrust)
   ```
3. Use `calcall` or `recalc=3` during endpoint optimization for accurate Hessian
4. Run IRC longer first to get endpoints closer to minima, then optimize

---

## Pattern 6: Intermediate point "drops down" in energy plot

**Symptom:** When viewing an incomplete IRC output file, one point appears to suddenly drop to much lower energy than surrounding points.

**This is normal.** This is an artifact of viewing incomplete output. After the IRC task completes normally, this phenomenon disappears.

---

## Pattern 7: IRC with shoulder or bump on one side

**Symptom:** The "energy vs reaction coordinate" plot shows a shoulder or bump on one side of the TS.

**This is normal.** As long as:
- Calculation flow is correct
- Trajectory looks normal
- TS position is smooth

Shoulders often indicate complex electronic structure changes — the reaction may have two stages despite being a single step. Analyze with:
- Bond order changes along the path
- ELF / density difference / atomic charge evolution
- Use Multiwfn for wavefunction analysis along IRC

---

## Pattern 8: IRC restart after interruption

**Scenario:** IRC was interrupted before completing.

**Solution:**
```
%chk=same_as_original_irc.chk
# B3LYP/6-31G(d) IRC(restart,maxpoints=15)
```

**Note:** Must use the same .chk file as the original IRC job.

---

## Pattern 9: Extend completed IRC

**Scenario:** IRC finished normally but didn't run long enough. Want to add more points.

**Solution:**
```
%chk=same_as_original_irc.chk
# B3LYP/6-31G(d) IRC(restart,maxpoints=20)
```

If original was maxpoints=15 and you want 5 more per direction, set to 20.

**Important:** GaussView must open the .chk/.fch file (not .out/.log) to see the full restarted IRC trajectory. Opening .out/.log only shows the newly added points.

---

## Pattern 10: IRC for methods without analytic Hessian (CCSD, etc.)

**Scenario:** Theory method supports analytic gradient but not analytic Hessian.

**Finding TS:**
```
# CCSD/cc-pVDZ opt(TS,modRedend,noeigen)
# or
# CCSD/cc-pVDZ opt(TS,gediis,noeigen)
# or use QST2/QST3
```

Or with semi-numerical Hessian:
```
# Step 1: compute Hessian (expensive)
# CCSD/cc-pVDZ freq
# Step 2: read Hessian for TS optimization
# CCSD/cc-pVDZ opt(TS,noeigen,readfc)
```

**Running IRC:**
```
# CCSD/cc-pVDZ IRC(gradientonly,euler)
```
Quality is poor — often very oscillatory. This is a limitation of the method.

---

## Pattern 11: IRC with Cartesian keyword (unintentional MEP)

**Symptom:** User added `Cartesian` to IRC without knowing what it means, getting different results.

**Cause:** `IRC=Cartesian` executes in Cartesian coordinates — technically this is MEP (Minimum Energy Path), not IRC. Results are not isotope-dependent.

**Fix:** Remove `Cartesian` unless you specifically want MEP. This is a commonly copied-by-mistake keyword from online sources.
