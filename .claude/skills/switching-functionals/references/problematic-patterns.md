# Problematic Functional Switching Patterns

Common patterns of unjustified functional switching that will cause reviewer problems, and how to avoid them, based on Sobereva's article (sobereva.com/631).

## Pattern 1: Cheaper SP, more expensive opt (backwards)

### The problem
```
Optimization: M06-2X
Single-point: B3LYP-D3
```

**Why it's wrong:**
- B3LYP-D3 is cheaper than M06-2X
- B3LYP-D3 is typically less accurate than M06-26 for organic energies
- This violates the convention that SP accuracy should be ≥ opt accuracy
- It looks like you don't understand basic computational chemistry principles

**What a knowledgeable reviewer will think:**
- "The authors lack basic competence" — harsh criticism
- "Are they hiding bad M06-2X results?" — suspicion of data manipulation
- "Why would anyone do this?" — request for explanation you can't provide

**Fix:**
- If B3LYP-D3 is appropriate → use it for both opt and SP
- If M06-2X is appropriate → use it for both (or use double-hybrid for SP)

### Real-world example

A user asked: "Is M06-2X optimization + B3LYP-D3 single-point reasonable? The single-point method is cheaper than the optimization method. I feel M06-2X underestimates energies."

**Analysis:** This is clearly unreasonable. An experienced reviewer will either:
1. Criticize the author's lack of basic knowledge
2. Suspect intentional data cherry-picking
3. Suspect that important factors were ignored, making M06-2X perform poorly

**If M06-2X genuinely performs poorly for this specific problem:** Use B3LYP-D3 for everything — this makes the choice consistent and defensible.

## Pattern 2: Opt without D3, SP with D3

### The problem
```
Optimization: B3LYP
Single-point: B3LYP-D3(BJ)    [for weak interaction energy]
```

**Why it's wrong:**
- B3LYP describes dispersion completely incorrectly
- Weak interaction depends critically on dispersion
- B3LYP-optimized structures for dispersion-dominated systems may be qualitatively wrong
- D3 is free — there's no cost justification for omitting it during optimization

**Reviewer response:** Deserved instant rejection for weak interaction studies.

**Fix:** Use B3LYP-D3(BJ) for both opt and SP.

### When omitting D3 during opt IS acceptable
Only when the post-correction:
1. Significantly increases computational cost, OR
2. Has significant barriers during optimization (e.g., loss of analytic gradients)
3. Is not critically necessary during optimization

**Example where omission is OK:** Counterpoise (CP) correction for BSSE
- CP removes analytic gradients → optimization extremely expensive
- Without CP, geometry errors are usually small
- Therefore: CP is typically only applied at the SP stage

**Example where omission is NOT OK:** gCP (Grimme's geometric CP correction)
- gCP is free (like D3) — apply everywhere or nowhere
- Same logic as D3 applies

## Pattern 3: Cherry-picking to match experiment

### The problem
```
Absorption spectrum: use Functional A (closest to experiment)
Emission spectrum: use Functional B (closest to experiment)
```

**Why it looks bad:**
- Both are excitation energy calculations — why two functionals?
- Motive appears to be data-fitting, not scientific reasoning
- Experienced reviewers will detect the pattern

### The HF% tuning problem

It's well-known that higher HF% → higher excitation energy. Some researchers exploit this:

1. Try multiple functionals with different HF%
2. Pick the one whose excitation energy is closest to experiment
3. Publish with that functional, claiming "excellent agreement with experiment"

**Why this is meaningless:**
- Any functional can be made to "match" experiment by chance
- The match has no theoretical basis
- It tells us nothing about the system

### Example: Suspicious TPSSh switch

```
Optimization: B3LYP (20% HF)
Spectrum calculation: TPSSh (10% HF)    # because it matched experiment slightly better
```

**Why it's suspicious:**
- TPSSh is rarely used for organic excitation energies
- The only reason for the switch is better agreement with experiment
- Reviewer will ask: "Why TPSSh?"
- Answer "it matched experiment" confirms data-fitting suspicion

**Better approach:** Use B3LYP for everything. Slightly larger error is better than raising suspicion.

## Pattern 4: Mixed functional reaction pathway

### The problem
```
Main-group reaction steps: M06-2X
Transition metal reaction steps: M06
```

**Why it's wrong:**
- Different functionals have different systematic errors
- Relative energies (barriers, reaction energies) only make sense when computed with the same functional
- Cross-functional energy differences are meaningless

**The scenario:** A complex reaction involving both main-group and transition metal steps.
- M06-2X is best for main-group chemistry
- M06 is better for transition metals (arguably)

**What NOT to do:** Compute each step with its "best" functional and compare energies.

**What TO do:**
1. Use one balanced functional for the entire pathway:
   - MN15 (balanced for main-group and TM)
   - PBE0 (general-purpose)
   - B3LYP (general-purpose)
2. Then compute ALL energies at a high-level double-hybrid (e.g., in ORCA with density fitting)

**Trade-off:** The balanced functional may not be optimal for either main-group or TM steps individually. But consistency matters more than per-step optimization for relative energies.

## Pattern 5: Higher basis for opt, lower basis for SP

### The problem
```
Optimization: 6-31G**
Single-point: def2-SVP
```

**Why it's wrong:**
- Both basis sets are in the same tier
- No clear reason for switching
- Looks arbitrary — reviewer will ask "why?"

**Fix:**
- Use the same basis set throughout, OR
- Use a clearly higher basis for SP (e.g., def2-TZVP)

## Pattern 6: DFT opt, MP2 SP (organic systems)

### The problem
```
Optimization: M06-2X
Single-point: MP2
```

**Why it's wrong:**
- MP2 is worse than M06-2X for organic energies (well-established)
- MP2 is more expensive than M06-2X
- This violates the convention that SP accuracy ≥ opt accuracy
- It's doubly wrong: worse AND more expensive

**What a reviewer will think:**
- "The authors don't know that MP2 is outdated for organic chemistry"
- "They may have tried better methods and got bad results, so they're hiding it"
- Almost certainly will write a comment criticizing this

**Contrast:**
- MP2 for both opt and SP: reviewer may think "outdated" but won't comment
- M06-2X for both: reviewer may think "double-hybrid SP would be better" but won't comment
- M06-2X opt + MP2 SP: reviewer WILL comment — basic competence questioned

**Fix:** Use M06-2X for both, or double-hybrid for SP.

## Pattern 7: Obscure, rarely-used functionals

### The problem
```
BVP86 optimization    # or other obscure functional
```

**Why it's dangerous:**
- Google Scholar: BVP86 → ~300 results; BP86 → ~23,000+ results
- Reviewer may have never heard of it
- You'll be asked to justify the choice
- No literature support available
- No benchmark studies to cite

**Result:** You'll be forced to re-calculate or face rejection.

**Fix:** Use well-established functionals. Popularity ≠ quality, but obscurity = guaranteed scrutiny.

## Pattern 8: Copying a famous researcher's questionable practice

### The problem
"I saw [famous organic reaction computist] uses B3LYP opt + M06L SP and publishes in top journals."

**Why you shouldn't copy this:**
1. M06L is not a good choice for organic systems — M06-2X (parameterized for main-group) is clearly better
2. The famous researcher's reputation protects them — reviewers are often their acquaintances
3. Even if reviewers have concerns, they let it pass out of respect
4. You don't have that protection

**Fundamental principle:** Blindly copying practices without understanding the underlying principles is extremely dangerous.

## Responding to unreasonable reviewer comments

### Example reviewer comment

"Regarding the computational method used, the B3LYP/6-31G(d,p) method was used for geometry optimization and M062X/def2-TZVP was used for energy calculation. Using different functionals for geometry optimization and single-point energy calculation may lead to inconsistent energies and errors in the relative energy calculations. The authors should check the consistency of their results at the same level of DFT methods, e.g., B3LYP/6-31G(d,p) optimization and B3LYP/def2-TZVP single-point calculation."

### How to respond

This reviewer lacks basic computational chemistry knowledge. The switch from B3LYP (cheap) to M06-2X (more expensive, more accurate) is a standard and well-justified practice.

**Response strategy:**
1. Clearly explain the reason: "We used M06-2X for single-point calculations because it provides significantly better accuracy for [specific system type] energies compared to B3LYP, at a moderate increase in computational cost that is acceptable for single-point calculations. B3LYP was used for optimization because it provides reliable geometries at lower cost."
2. Cite published examples:
   - wB97XD opt + wB97X-V SP (sobereva.com/684) — weak interaction energy
   - wB97XD opt/TS + DLPNO-CCSD(T) SP (sobereva.com/630) — reaction barriers
3. Optionally: Provide a small test showing that B3LYP/def2-TZVP SP gives similar/different results, demonstrating that the M06-2X improvement is real

## Defending your functional choice

When reviewers question your functional, use these defense strategies:

### Strategy 1: Cite benchmark studies
- Find papers that tested multiple functionals on similar problems
- Read at least 3 benchmarks — single papers may have conflicting conclusions
- JCTC, JCC, PCCP, JCP are full of benchmark studies
- Even obscure properties (rotational constants, electric field gradient at nucleus) have been benchmarked

### Strategy 2: Cite common practice
- Show that many high-quality papers use the same functional for similar problems
- "Functional X is widely used for problem Y in systems like Z" — cite 5-10 papers

### Strategy 3: Present your own benchmark
- Compare multiple functionals against experimental or high-level theoretical values
- Show that your chosen functional performs well and is robust
- This is the strongest defense

### Strategy 4: Theoretical reasoning
- Explain based on functional characteristics (HF%, parameterization, known strengths)
- Subjective — requires strong theoretical foundation and communication skills
- May not convince all reviewers

## The "opt + freq + IRC must match" rule

These three tasks MUST use identical settings — no exceptions:

| Task | Must match? | Why |
|------|------------|-----|
| Geometry optimization | Yes | Structure depends on the PES defined by the functional |
| Frequency calculation | Yes | Hessian must correspond to the optimized structure's PES |
| IRC calculation | Yes | IRC follows the same PES as opt and freq |

**Example of forbidden switching:**
- Optimize with M06-2X in ORCA 4.0
- Switch to B3LYP for frequency because M06-2X lacks analytic Hessian in ORCA 4.0
- **Absolutely wrong** — frequency must match optimization level

If frequency at the opt level is too slow:
- Use a cheaper but still consistent level for the frequency test (to confirm minima)
- Or accept the computational cost
- Never switch to a different functional

## References

- sobereva.com/631 — This article (switching functionals)
- sobereva.com/272 — DFT functional selection guide
- sobereva.com/413 — When DFT-D3 is needed
- sobereva.com/554 — What makes a meaningful benchmark
- sobereva.com/684 — 18-carbon-ring molecular motor (wB97XD opt + wB97X-V SP)
- sobereva.com/630 — 18-carbon-ring Li switch (wB97XD opt + DLPNO-CCSD(T) SP)
- J. Chem. Theory Comput., 12, 459 (2016) — PBE0 geometry benchmark
