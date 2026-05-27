# Basis Set Theory and Selection Details

Detailed explanation of why different methods need different basis sets, basis set construction, and general selection principles.

## Why DFT and post-HF need different basis sets

### (1) Dependence on angular momentum and zeta count

**DFT and HF:**
- Don't need many high-angular-momentum basis functions
- Improvement comes primarily from adding s and p angular momentum functions
- Going from 2-zeta to 3-zeta gives significant improvement
- Adding more f polarization on top of insufficient zeta level is backwards

Example of a bad choice: Using `6-31G(2df,p)` for DFT — this doesn't even reach 3-zeta level, but wastes resources on f polarization that has minimal impact on DFT results. The area that needs improvement (zeta count) isn't improved, while resources go to functions that don't matter much for DFT.

**Post-HF (MP2, CCSD(T), multireference):**
- Require more high-angular-momentum functions to adequately describe electron dynamic correlation
- Need at least def2-TZVP for CCSD(T); using 6-311G** with CCSD(T) is like putting flowers in cow dung
- MP2 needs at least def-TZVP as a starting point

**MCSCF:**
- Focuses on static correlation, not dynamic correlation
- Basis set requirements are the same as DFT

### (2) Timing: GTF count vs basis function count

**DFT timing:**
- Most time spent on two-electron integrals
- Formally proportional to GTF (Gaussian-type function) count to the 4th power
- Therefore, GTF count is the most direct impact on DFT timing
- **Preference:** Basis sets with fewer GTFs per basis function — fragment-contracted (Pople, def2, pcseg) are better

**Post-HF timing:**
- Most time depends on basis function count (and electron count)
- This directly determines Slater determinant/configuration state function count and AO→MO integral transformation cost
- SCF iteration two-electron integral cost is secondary
- **Preference:** Dunning cc-pVnZ series (semi-generalized contraction) is fine for post-HF since GTF count matters less

### Dunning cc-pVnZ for DFT: lower cost-performance

cc-pVnZ series has relatively more GTFs due to semi-generalized contraction, and was parameterized specifically for post-HF electron correlation calculations. For DFT:
- cc-pVTZ is clearly inferior to def2-TZVPP at similar cost
- def2, pcseg are better choices for DFT at equivalent tiers

## Basis set hierarchy explained

### Zeta number

- **Single-zeta (SZ):** One basis function per valence orbital — too crude for any serious calculation
- **Double-zeta (DZ):** Two basis functions per valence orbital — minimum for meaningful results
- **Triple-zeta (TZ):** Three basis functions — good accuracy for most applications
- **Quadruple-zeta (QZ):** Four basis functions — high precision, often overkill
- **Quintuple-zeta (5Z):** Five basis functions — extremely expensive, usually reached via CBS extrapolation

### Polarization functions

- **d on heavy atoms, p on H:** First level of polarization — essential for any meaningful calculation
- **f on heavy atoms, d on H:** Second level — important for post-HF, less so for DFT
- **g on heavy atoms, f on H:** Third level — only for very high precision post-HF

### Diffuse functions

- **s, p on heavy atoms:** Most common — essential for anions, Rydberg states, weak interactions
- **s, p on H:** Rarely needed — only for very specific cases
- **d on heavy atoms, p on H:** Second layer of diffuse polarization — for high-precision polarizability

## CBS (Complete Basis Set) extrapolation

CBS = complete basis set. At CBS, basis set incompleteness error is zero. In practice, CBS is reached by extrapolating results from finite basis sets.

**Common approach:**
- Compute energies at two basis set levels (e.g., TZ and QZ)
- Extrapolate to the infinite basis set limit using known convergence formulas
- Typical notation: CCSD(T)/CBS means CCSD(T) energy extrapolated to CBS limit

For detailed methodology, see: sobereva.com/172

## Where to get basis sets

### Built-in basis sets
Gaussian has many built-in basis sets. Check Gaussian documentation for what's available.

### External basis sets
Most basis sets can be shared across Gaussian-based programs since they all use Gaussian-type functions. Sources:

1. **BSE (Basis Set Exchange):** https://www.basissetexchange.org — Most comprehensive public basis set database
2. **Original literature:** Parameters from the original publication
3. **Developer websites:** e.g., Ahlrichs group website for def2 series
4. **Other program libraries:** Can be borrowed and converted

### Basis set coverage
Only a few basis sets (UGBS, WTBS) cover nearly the entire periodic table. Most basis sets are defined for only a subset of elements. Check BSE to see which elements a basis set covers.

## Contracted vs decontracted basis sets

### Fully contracted
- All GTFs for a given angular momentum are combined into one contracted function
- Fewer basis functions, faster calculations
- May lack flexibility for describing subtle electronic effects

### Segment-contracted (fragment-contracted)
- Different groups of GTFs contracted separately
- Good balance of cost and flexibility
- Examples: Pople, def2, pcseg

### Semi-generalized contraction (Dunning)
- Some GTFs shared between contracted functions
- More flexible but more GTFs
- Examples: cc-pVnZ series

### Uncontracted
- All GTFs used individually
- Maximum flexibility, maximum cost
- Used for special cases like all-electron relativistic calculations (UGBS)

## When to use pseudopotentials

Pseudopotentials serve two purposes:
1. Replace core electrons with an effective potential — dramatically reduces cost
2. Implicitly include scalar relativistic effects

**Guidelines:**
- **4th period:** Relativistic effects start to appear, but ignoring them is usually acceptable
- **5th period and beyond:** Relativistic effects are不可忽视 (cannot be ignored) — must use pseudopotentials or all-electron relativistic methods
- Use RECP (relativistic effective core potential) pseudopotentials to include relativistic effects

For detailed pseudopotential selection, see: sobereva.com/373

## Key references

- sobereva.com/119 — Diffuse functions and "month" basis sets
- sobereva.com/340 — Adding diffuse functions to def2 series
- sobereva.com/309 — Online basis set and pseudopotential databases
- sobereva.com/172 — Energy basis set extrapolation
- sobereva.com/60 — Gaussian mixed/custom/pseudopotential basis input
- sobereva.com/156 — Wavefunction analysis with pseudopotentials
- sobereva.com/387 — Why optimization and frequency don't need large basis sets
- sobereva.com/373 — Pseudopotential basis set selection
- sobereva.com/46 — BSSE and Gaussian's handling
- sobereva.com/214 — Large system weak interaction solutions (density fitting)
