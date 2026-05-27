---
name: bsse-correction
description: This skill should be used when the user asks to "BSSE", "counterpoise", "counterpoise correction", "basis set superposition error", "BSSE校正", "counterpoise=2", "DCBS", "MCBS", "ghost atom", "Bq", "gCP", "interaction energy BSSE", "binding energy BSSE", "do I need BSSE correction", "counterpoise optimization", "BSSE solvent", "half-counterpoise", "overcorrection BSSE", or mentions basis set superposition error, counterpoise correction, or ghost atom calculations in Gaussian or quantum chemistry interaction energy computations.
version: 0.1.0
---

# BSSE Correction and Counterpoise

Guide to basis set superposition error (BSSE) correction and counterpoise calculations in Gaussian, based on Sobereva's articles (sobereva.com/381, sobereva.com/214).

**Core principle:** Whether you need BSSE correction depends entirely on your basis set and interaction type. Always state both when discussing BSSE. Without context, "BSSE" is meaningless.

## When BSSE correction is needed

| Basis set level | BSSE severity | Action |
|----------------|--------------|--------|
| **def2-QZVP, cc-pVQZ** | Negligible | Generally skip BSSE correction |
| **aug-cc-pVTZ, jul-cc-pVnZ** | Very small | Generally skip |
| **def2-TZVP, 6-311+G(2d,p)** | Moderate | Passable without CP; better with CP |
| **6-311G\*\*, 6-31+G\*\*, def2-SVP** | Severe | **Must correct** — either counterpoise or gCP |
| **6-31G\*, def2-SV(P)** | Extreme | **Must correct** — results unusable otherwise |

**Adding diffuse functions** to 3-zeta and below basis sets significantly reduces BSSE.

## Interaction type matters

| Interaction type | With diffuse 3-zeta basis | Without diffuse / 2-zeta |
|-----------------|--------------------------|-------------------------|
| **H-bond, halogen bond** (electrostatic-dominated, moderate strength) | Acceptable without CP | Must correct |
| **Van der Waals, π-π stacking** (dispersion-dominated, very weak) | Should still correct | Must correct |

**Key insight:** For very weak interactions (vdW, π-π stacking), even with diffuse 3-zeta basis, BSSE is often not negligible — better to correct.

## Counterpoise method in Gaussian

### Basic usage

```
# B2PLYPD3/jul-cc-pVTZ counterpoise=2
```

**Fragment assignment:** Each atom gets an integer indicating which fragment it belongs to.

**Input format 1 — fragment numbers after coordinates:**
```
0 1
H 0.00 0.00 0.92 1
F 0.17 0.00 2.73 2
H 0.77 0.00 3.43 2
F 0.00 0.00 0.00 1
```

**Input format 2 — fragment keyword in coordinates:**
```
0 1
H(fragment=1) 0.00 0.00 0.92
F(fragment=2) 0.17 0.00 2.73
H(fragment=2) 0.77 0.00 3.43
F(fragment=1) 0.00 0.00 0.00
```

**Different charge/multiplicity for fragments:**
```
overall_charge, overall_mult, frag1_charge, frag1_mult, frag2_charge, frag2_mult
```

### What Gaussian computes

For `counterpoise=2`, Gaussian automatically computes 5 energies in sequence:

| Order | Symbol | Description |
|-------|--------|-------------|
| 1 | E_AB | Complex energy in AB basis |
| 2 | E_A,bAB | Fragment A energy in full AB basis (DCBS) |
| 3 | E_B,bAB | Fragment B energy in full AB basis (DCBS) |
| 4 | E_A | Fragment A energy in A basis only (MCBS) |
| 5 | E_B | Fragment B energy in B basis only (MCBS) |

**DCBS** = Dimer Centered Basis Set (both fragments' basis functions present)
**MCBS** = Monomer Centered Basis Set (only own fragment's basis functions)

### Output interpretation (G16 / recent G09)

```
Counterpoise corrected energy =    -200.665575667261
BSSE energy =       0.001681932370
sum of monomers =    -200.659550058648
complexation energy =      -4.84 kcal/mole (raw)
complexation energy =      -3.78 kcal/mole (corrected)
```

### BSSE formula

```
E_BSSE = (E_A - E_A,bAB) + (E_B - E_B,bAB)
E_corrected = E_AB + E_BSSE
E_interaction = E_AB - E_A - E_B + E_BSSE
```

For variational methods, E_BSSE is always positive (larger basis = lower energy).

### Multi-fragment counterpoise

For n fragments: `counterpoise=n`

```
E_BSSE = Σ(E_i - E_i')  where E_i' = fragment i energy in full complex basis
```

Output order: E_complex, E_1', E_2', ..., E_n', E_1, E_2, ..., E_n

## Ghost atom method (manual counterpoise)

When `counterpoise` keyword is unavailable (very old Gaussian versions), use ghost atoms:

```
# B3LYP/6-31G(d)
! To compute E_A,bAB: make all B atoms ghost
0 1
H 0.00 0.00 0.92
F-Bq 0.17 0.00 2.73    ← Ghost: has basis functions but no nucleus/electrons
H-Bq 0.77 0.00 3.43
F 0.00 0.00 0.00
```

Add `nosymm` if ghost atoms break symmetry.

**Advantage of manual method:** Preserves symmetry for monomer/complex calculations — can be significantly faster for highly symmetric systems (Gaussian's counterpoise keyword disables symmetry for all steps).

## Critical rules

### NEVER use counterpoise for chemical bond energies

**When fragments are connected by chemical bonds, do NOT apply counterpoise.** See sobereva.com/381.

**For strong interactions (chemical bonds):** Just use a sufficiently large basis set.
- Minimum: def-TZVP
- Better: def2-TZVP
- For post-HF/double-hybrid: cc-pVQZ or def2-QZVP
- No diffuse functions needed unless the interaction region carries significant negative charge

### NEVER optimize with counterpoise

**Do NOT run geometry optimization or frequency calculations with counterpoise:**

| Issue | Consequence |
|-------|------------|
| No analytic gradients | Optimization extremely slow (numerical gradients only) |
| No analytic Hessian | Frequency calculation unbearably slow |
| BSSE effect on geometry is small | Not worth the cost |

**Correct workflow:**
1. Optimize WITHOUT counterpoise (def-TZVP or def2-SVP sufficient)
2. Compute interaction energy WITH counterpoise at the optimized structure

### If you MUST optimize with BSSE correction

Use **gCP** (Grimme's geometric CP correction) in ORCA:
- Analytic first and second derivatives available
- "Free" — negligible computational overhead
- Works for both weak and strong interactions
- Not available in Gaussian (as of G16)

## BSSE correction methods comparison

| Method | Cost | Derivatives | Gaussian support | Notes |
|--------|------|------------|-----------------|-------|
| **Counterpoise** | 3× single-point | None (numerical only) | Yes | Most widely used; gold standard |
| **gCP** | ~0 (free) | Yes (analytic) | No (ORCA only) | Good for large systems; see sobereva.com/214 |
| **Large basis (def2-QZVP+)** | Expensive SP | Yes | Yes | No correction needed at this level |

## Important caveats

### 1. Half-counterpoise for certain basis sets

JCTC, 10, 49 (2013): For aug-cc-pVDZ/TZ basis sets, using **half** the counterpoise correction performs better than full CP or no CP. For aug-cc-pVQZ and above, or CBS extrapolation, use **full** counterpoise.

### 2. Overcorrection problem

Counterpoise can overcorrect because:
- In E_A,bAB calculation, fragment A sees completely "empty" B basis functions — fully utilizable
- In the actual complex, B's basis functions are partially occupied — not fully utilizable by A
- Since B's basis function state differs between these two situations, using E_A - E_A,bAB overcorrects for A
- This can underestimate interaction energy; occasionally worse than no correction

### 3. Solvent model + BSSE

No rigorous approach exists. Common practice:
1. Compute E_BSSE in gas phase via counterpoise
2. Compute E_interaction in solvent model normally: E_AB(solvent) - E_A(solvent) - E_B(solvent)
3. Add: E_interaction(solvent) ≈ E_AB(solvent) - E_A(solvent) - E_B(solvent) + E_BSSE(gas)

### 4. Intramolecular weak interactions

When a single molecule has intramolecular weak interactions (e.g., long chain folding):
- **Cannot use counterpoise directly** — fragments belong to same molecule
- **Workaround 1:** Cut the molecule at appropriate position, cap dangling bonds with H, separate the cut ends, treat as two molecules for counterpoise
- **Workaround 2 (better):** Use basis set with sufficient diffuse functions, or use gCP without diffuse functions

### 5. Which counterpoise method to specify

When asking about BSSE correction, always specify which method:
- Counterpoise (Boys-Bernardi)
- gCP (Grimme's geometric CP)
- Large basis set approach
- Half-counterpoise

## Quick decision guide

```
What basis set are you using?
├── def2-QZVP / cc-pVQZ / aug-cc-pVTZ → Skip BSSE correction
├── def2-TZVP / 6-311+G(2d,p) → Optional; counterpoise improves results
├── 6-311G** / def2-SVP / 6-31+G** → Must correct
│   ├── Gaussian user → counterpoise=N at optimized geometry
│   └── ORCA user → gCP (free, has derivatives)
└── 6-31G* / def2-SV(P) → Must correct; results unusable without it
```

## References

- sobereva.com/381 — BSSE in bond energy calculations (why NOT to use CP)
- sobereva.com/214 — gCP for large system weak interactions
- sobereva.com/685 — sobEDA energy decomposition with BSSE discussion
- sobereva.com/336 — Basis set selection guide
- sobereva.com/413 — When DFT-D3 is needed (weak interaction types)
- sobereva.com/119 — Month basis sets (jul-cc-pVnZ, etc.)
- sobereva.com/542 — Counterpoise in ORCA via Multiwfn
- J. Chem. Theory Comput., 10, 49 (2013) — Half-counterpoise for aug-cc-pVDZ/TZ
- Chem. Eur. J., DOI: 10.1002/chem.202402227 — def2-TZVP + gCP for large carbon ring/fullerene system
