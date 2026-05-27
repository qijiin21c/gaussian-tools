# BSSE Theory and Counterpoise Method

Detailed theoretical explanation of basis set superposition error and the counterpoise correction method, based on Sobereva's article.

## What is BSSE?

When computing interaction energy between molecules A and B:

```
E_interaction = E_AB - E_A - E_B
```

The energy lowering of E_AB relative to E_A + E_B comes from TWO sources:

1. **Real intermolecular interaction energy** — what we want
2. **Basis function overlap** — A's and B's basis functions overlap in the complex, effectively enlarging the basis set and lowering E_AB (strictly, for variational methods). This is the **Basis Set Superposition Error (BSSE)**

If BSSE contaminates E_interaction, the interaction strength is **overestimated** (the true interaction is less negative than computed).

## Root cause explained

The fundamental issue: computing the complex and monomers at **different basis set levels**.

```
E_AB,bAB  ← computed in AB's combined basis (correct for complex)
E_A,bA    ← computed in A's basis only (correct for isolated A)
E_B,bB    ← computed in B's basis only (correct for isolated B)
```

The problem: atom in A near the A-B interface has **higher basis completeness** in the complex state (because B's basis functions invade its space) than when A is computed alone. This means the basis set error doesn't cancel when taking the difference — this is the root of BSSE.

**Only when the basis set is complete** (or when complex and monomers are computed at the same basis level) can we directly compute E_AB - E_A - E_B:

```
E_interaction = E_AB,bQ - E_A,bQ - E_B,bQ
```

Where Q represents a common basis — either plane waves or a combined set of atom-centered basis functions (e.g., all of AB's basis functions). This is why the counterpoise formula is:

```
E_interaction = E_AB - E_A,bAB - E_B,bAB
```

All three energies computed in the same AB basis.

## Why BSSE depends on basis set size

E_BSSE → 0 as the basis approaches completeness. Larger basis = smaller BSSE.

**def/def2 series vs 6-311G series:** The def/def2 basis sets are more diffuse than 6-311G at the same zeta level, so they have smaller BSSE. For example, def2-TZVP has less BSSE than 6-311G**.

## BSSE affects the potential energy surface

BSSE affects the entire PES, not just the energy at one point. Therefore:
- BSSE affects weak interaction energies most significantly
- BSSE also affects geometry optimization, frequency analysis, and other PES-dependent tasks
- However, BSSE's effect on geometry is small compared to its effect on interaction energy
- **Therefore:** BSSE correction is primarily discussed for interaction energy calculations

## The counterpoise method

Developed by Boys and Bernardi. Most widely used BSSE correction method.

### Principle

For n fragments, let:
- E_i = energy of fragment i in its own basis
- E_i' = energy of fragment i in the full n-fragment basis (all other fragments' basis functions present, but their nuclei and electrons absent)

Then:
```
E_BSSE = Σ(E_i - E_i')
E_interaction = E_complex - ΣE_i + E_BSSE
E_interaction = E_complex - ΣE_i'
```

For variational methods: E_i' < E_i (larger basis = lower energy), so E_BSSE > 0.

### DCBS vs MCBS

- **DCBS** (Dimer/N-mer Centered Basis Set): All fragments' basis functions present; own fragment's electrons and nuclei only
- **MCBS** (Monomer Centered Basis Set): Only own fragment's basis functions present

```
E_i' = DCBS calculation for fragment i
E_i = MCBS calculation for fragment i
```

### Each geometry has its own E_BSSE

E_BSSE depends on the geometry — different structures have different basis function overlaps. Typically, counterpoise is computed at the optimized complex geometry since that's the structure of interest.

## Why counterpoise is approximate

Counterpoise gives an **approximation** of the true E_BSSE — it is not fully rigorous or exact. No fully rigorous method exists for computing E_BSSE.

### Overcorrection mechanism

In E_A,bAB calculation, A sees completely "empty" B basis functions — fully available for A to use. In the actual complex, B's basis functions are partially occupied — not fully available to A. Since B's basis function state differs between these two situations, E_A - E_A,bAB overcorrects for A, underestimating the interaction energy.

In some cases, the overcorrected result is worse than no correction at all.

## Intramolecular BSSE

When a single molecule has intramolecular weak interactions (e.g., long chain folding into C-shape vs. extended):

**Problem:** Two "fragments" belong to the same molecule — counterpoise cannot be applied directly.

**Approach 1: Molecular cutting**
1. Cut the molecule at an appropriate position
2. Cap dangling bonds with H atoms
3. Separate the two fragments so the cut region is far apart (otherwise the cut region contributes to E_BSSE)
4. Keep the originally interacting regions at their original relative positions
5. Treat as two separate molecules for counterpoise

**Approach 2 (more elegant):**
- Use basis set with sufficient diffuse functions → BSSE naturally minimized
- Or use gCP without diffuse functions → no fragment cutting needed

## Counterpoise cost

For DFT, counterpoise takes **more than 3×** the single-point calculation time (5 separate energy evaluations for 2 fragments).

This is why gCP is attractive — it's "free" and has analytic derivatives.

## References

- sobereva.com/381 — Why not to use CP for bond energies
- sobereva.com/214 — gCP for large systems
- J. Chem. Theory Comput., 10, 49 (2013) — Half-counterpoise study
- Chem. Eur. J., DOI: 10.1002/chem.202402227 — def2-TZVP + gCP application
