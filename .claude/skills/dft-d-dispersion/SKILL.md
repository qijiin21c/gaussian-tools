---
name: dft-d-dispersion
description: This skill should be used when the user asks to "add dispersion correction", "DFT-D3", "DFT-D3(BJ)", "DFT-D4", "EmpiricalDispersion", "色散校正", "GD3", "GD3BJ", "GD2", "dispersion correction Gaussian", "B3LYP-D3", "when to use DFT-D", "DFT-D parameters", "custom D3 parameters", "TPSSh-D3", "MN15-D3", "damping function", "zero-damping", "BJ damping", "Grimme dispersion", "D3(BJ) frequency imaginary", or mentions adding dispersion corrections to DFT calculations in Gaussian or other quantum chemistry programs.
version: 0.1.0
---

# DFT-D Dispersion Correction

Guide to using DFT-D dispersion corrections in Gaussian, based on Sobereva's articles (sobereva.com/83, sobereva.com/413).

**Core principle:** If your system has ANY dispersion-related interactions (weak interactions, large molecules, flexible chains), you MUST add DFT-D correction. It's free and improves accuracy universally.

## Quick reference: DFT-D versions

| Version | Status | Notes |
|---------|--------|-------|
| DFT-D1 | Obsolete | Do not use |
| DFT-D2 | Obsolete | Limited element coverage; only used by B97D, wB97XD, B2PLYPD (built-in) |
| **DFT-D3** | **Current standard** | H to Pu, all major functionals, zero computational overhead |
| DFT-D4 | Emerging | Considers electronic structure effect on dispersion; limited program support |

## DFT-D3 damping functions

| Damping | Gaussian keyword | When to use |
|---------|-----------------|-------------|
| **Zero-damping (D3(0))** | `EmpiricalDispersion=GD3` or `em=GD3` | Default choice. Required for M05/06/08 series (M06-2X etc.) |
| **BJ-damping (D3(BJ))** | `EmpiricalDispersion=GD3BJ` or `em=GD3BJ` | Slightly better overall; better for intramolecular dispersion. Use for B3LYP, PBE, BLYP, etc. |
| DFT-D2 | `EmpiricalDispersion=GD2` or `em=GD2` | Only for older Gaussian versions or specific needs |

## When DFT-D is essential

| System type | Without DFT-D | With DFT-D |
|-------------|--------------|------------|
| **Van der Waals complexes** (e.g., Ar₂) | No minimum at all — cannot even find dimer | Correct minimum position |
| **π-π stacking** (e.g., DNA base pairs) | Stacking distances completely wrong | Matches experiment |
| **Large molecule conformations** (e.g., remdesivir) | Wrong conformer ordering | Correct |
| **Long-chain alkanes** | Conformational energies qualitatively wrong | Reasonable |
| **Physical adsorption** | Binding energies near zero | Matches CCSD(T) qualitatively |
| **Electrostatic H-bonds** (e.g., water dimer) | Qualitatively OK | Quantitatively improved |

**Even for electrostatic-dominated interactions (H-bonds, halogen bonds):** DFT-D still provides significant quantitative improvement. Adding DFT-D is beneficial and harmless.

## When NOT to add DFT-D

| Situation | Reason |
|-----------|--------|
| **Built-in dispersion functional** (B97D, wB97XD, B2PLYPD) | Already have DFT-D2 built-in; don't double-correct |
| **M06-2X, M06, M05-2X** | Already have medium-range correlation; adding D3(BJ) causes double-counting. D3(0) gives slight improvement but optional |
| **Double-hybrid with built-in D** (B2PLYPD3) | Already includes dispersion |

**Note:** Even for M06-2X and wB97XD which already describe dispersion reasonably, adding DFT-D3 still provides slight improvement. But it's optional for these functionals.

## How to use in Gaussian

### Gaussian 16 / G09 D.01 and later (recommended)

```
# B3LYP/def2-SVP EmpiricalDispersion=GD3BJ opt
# or shorthand:
# B3LYP/def2-SVP em=GD3BJ opt
```

**Output confirmation:** When DFT-D is enabled, Gaussian prints:
```
R6Disp:  Grimme-D3(BJ) Dispersion energy=       -0.0018363766 Hartrees.
Nuclear repulsion after empirical dispersion term =       41.9082499513 Hartrees.
```

### Built-in dispersion-corrected functionals

These functionals work directly without `EmpiricalDispersion`:
- `B2PLYPD3`, `B97D3` — DFT-D3(BJ) built-in
- `B97D`, `wB97XD`, `B2PLYPD` — DFT-D2 built-in

### G09 A/B/C (before D.01)

No DFT-D3 support. Use functionals with built-in dispersion:
- `wB97XD` — good for most weak interactions
- `M062X` — slightly better than wB97XD for some systems
- `B2PLYPD` — double-hybrid, higher accuracy

Both wB97XD and M062X are significantly slower than B3LYP.

### G03

No DFT-D support at all. Use `M052X` (only in later G03 versions).

## Custom DFT-D3 parameters (Gaussian 16)

For functionals not built into Gaussian (TPSSh, MN15, MN15L, BHandHLYP, etc.), use IOp to define D3 parameters:

**IOp mapping (parameter × 1,000,000):**
| IOp | Parameter |
|-----|-----------|
| IOp(3/174) | S6 |
| IOp(3/175) | S8 |
| IOp(3/176) | SR6 (zero-damping) |
| IOp(3/177) | A1 (BJ-damping) |
| IOp(3/178) | A2 (BJ-damping) |

**Examples:**

```
! TPSSh-D3(BJ)
# TPSSh/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=2238200,3/177=452900,3/178=4655000)

! MN15L-D3(0)
# MN15L/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=0,3/176=3338800)

! MN15-D3(BJ)
# MN15/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=786200,3/177=2097100,3/178=7592300)

! BHandHLYP-D3(BJ)
# BHandHLYP/def2-TZVP em=GD3BJ IOp(3/174=1000000,3/175=1035400,3/177=279300,3/178=4961500)

! BHandHLYP-D3(0)
# BHandHLYP/def2-TZVP em=GD3 IOp(3/174=1000000,3/175=1442000,3/176=1370000)
```

**CRITICAL WARNING:** When Gaussian runs multi-step tasks (e.g., `opt freq`), **IOp settings only apply to the first step**. The freq step will NOT receive the custom D3 parameters, causing opt and freq to use different methods — a serious inconsistency. **Solution:** Run opt and freq as separate calculations.

## Common mistakes

| Mistake | Consequence | Fix |
|---------|------------|-----|
| `# B3LYP/def2-SVP opt freq em=GD3BJ` + IOp | freq uses wrong D3 parameters | Separate opt and freq into two jobs |
| B3LYP without D3 for weak interaction | Cannot find minimum; wrong energies | Always use `em=GD3BJ` |
| Adding D3 to wB97XD | Double-correction | wB97XD already has DFT-D2 built-in |
| M06-2X with D3(BJ) | Double-counting of medium-range correlation | Use D3(0) or nothing for M06-2X |
| G09 D.01 D3(BJ) frequency | Missing r⁻⁸ term → false imaginary frequencies | Use G09 E.01+, or use D3(0) for opt+freq in D.01 |

## Recommended functional + D3 combinations

| Study type | Recommended level |
|-----------|-------------------|
| **General weak interaction** | `B3LYP-D3(BJ)/def2-SVP` — fast, reliable, well-validated |
| **Higher accuracy** | `B3LYP-D3(BJ)/def2-TZVP` → `PWPB95-D3/def2-TZVP` SP |
| **Organic molecules (non-weak)** | `B3LYP-D3(BJ)/def2-SVP` — D3 adds universality |
| **Transition metal** | `TPSSh-D3(BJ)/def2-SVP` |
| **Conformational search** | `B3LYP-D3(BJ)` — final refinement level |
| **High-precision benchmark** | `wB97X-V` or `DSD-PBEP86-D3(BJ)` |

## DFT-D3 program (standalone)

Grimme's standalone DFT-D3 program computes dispersion energy and gradients for any structure. Useful for:
- Analyzing pairwise atomic dispersion contributions
- Computing intermolecular dispersion energy decomposition
- Fragment-based dispersion analysis

**Usage:**
```bash
./dftd3 test.xyz -func b3-lyp -bj          # D3(BJ) correction
./dftd3 test.xyz -func b-lyp -zero         # D3(0) correction
./dftd3 test.xyz -func b3-lyp -bj -anal    # pairwise contribution analysis
./dftd3 test.xyz -func b3-lyp -bj -grad    # gradients
./dftd3 test.xyz -func b3-lyp -bj -abc     # three-body term
```

**Functional name format:** Must follow Turbomole convention: `b3-lyp`, `pbe0`, `b-lyp`, `cam-b3lyp`, `m062x`, `b2-plyp`, etc.

**Fragment analysis:** Create a `fragment` file in the working directory:
```
2-4
1,6
```
This defines fragment 1 (atoms 2-4), fragment 2 (atoms 1,6), and fragment 3 (remaining atom 5). Output shows intra-fragment and inter-fragment dispersion energies.

## DFT-D: Why it works (beyond just long-range)

DFT-D is often thought of as only fixing the long-range C₆/R⁶ behavior. **But it also improves medium-range correlation and benefits ALL properties, not just weak interactions.**

**Root cause:** Local/semilocal correlation potentials have wrong medium- and long-range behavior. DFT-D, while designed to fix long-range dispersion,本质上 also corrects the correlation potential — improving thermochemistry, barriers, and other areas where the original functional was already "decent."

**DFT-D is safe:** When parameters are properly fitted, DFT-D only improves functional performance — it never makes things worse.

**Caveat:** DFT-D adds an energy term but does NOT modify the Kohn-Sham potential operator. Therefore, electron density cannot respond to weak interactions during SCF. In practice, this density difference is negligible.

## Four approaches to dispersion in DFT

| Approach | Examples | Pros | Cons | Status |
|----------|----------|------|------|--------|
| **Nonlocal correlation (DFT-NL)** | vdW-DF-04, vdW-DF-10, VV09, VV10 | Strict principle, less empirical | Complex, unpopular, poor prospects | Not recommended |
| **Parameterized functional** | M06-2X, M11, M11-L | Convenient, widely supported | Semilocal form limits long-range C₆/R⁶; distant branch-chain dispersion poorly described | Use with DFT-D for best results |
| **DFT-D (empirical correction)** | D2, D3, D4 | Free, simple, widely supported, universally beneficial | Doesn't modify KS potential (density doesn't respond) | **Recommended** |
| **Dispersion-correcting potentials (DCP/1ePOT)** | DiLabio's DCP | Can use with any ECP-supporting program | Too many parameters; too empirical; limited element coverage; no proper C₆/R⁶ asymptotic | Not recommended |

**LC (long-range corrected) ≠ dispersion correction.** LC fixes exchange potential at long range (for CT excitations, polarizability) but does NOT fix Coulomb correlation — it does NOT help with dispersion. HF has LC but describes dispersion terribly.

## Functional performance with D3 (GMTKN30 benchmark)

Grimme's PCCP 2011 GMTKN30 benchmark (30 subsets: atomization, reaction energies, barriers, weak interactions):

**Jacob's ladder still holds with D3:** Double-hybrid-D3 > Hybrid-D3 > meta-GGA-D3 > GGA-D3 > LSDA-D3

| Tier | Functionals | Notes |
|------|------------|-------|
| **Best double-hybrid-D3** | DSD-BLYP-D3, PWPB95-D3 | DSD-BLYP-D3 best at 4-zeta; PWPB95-D3 best at 3-zeta (less basis-dependent) |
| **Best hybrid-D3** | M06-2X-D3(0), PW6B95-D3 | M06-2X-D3 best but convergence/grid-sensitive; PW6B95-D3 nearly as good |
| **Best GGA-D3** | revPBE-D3 | Recommended when GGA is required |
| **meta-GGA-D3** | TPSS-D3 | Limited improvement over GGA-D3 |

**Important:** Double-hybrid-D3 results degrade significantly at double-zeta basis — use at least 3-zeta. 3-zeta → 4-zeta improvement is noticeable; 4-zeta → higher is unnecessary.

## Functional-specific notes for weak interactions

| Functional | Weak interaction performance | Verdict |
|-----------|----------------------------|---------|
| **PBE** | Best among GGA, still inadequate | Use PBE-D3 |
| **B3LYP** | Barely acceptable for H-bonds; useless for vdW | Use B3LYP-D3(BJ) |
| **X3LYP** | Good for H-bonds; terrible for stacking | **Do not use** — DFT-D3 makes it obsolete |
| **B97D** | D2 built-in, superseded by D3 | **Do not use** — use B97D3 instead |
| **revPBE-D3** | Best GGA-D3 | Good when GGA needed |
| **M06-2X** | Good without D3; unbeatable with D3(0) | Use M06-2X-D3(0); may underestimate some π-π stacking |
| **M11** | Worse than predecessor M06-2X for weak interactions | **Do not recommend** |
| **M11-L** | Best non-hybrid/non-DFT-D for weak interactions | Good for strong multireference systems |
| **PW6B95-D3** | Second to M06-2X-D3 among hybrids | Use if M06-2X has issues; limited program support |
| **wB97X-D** | Excellent — has both LC and dispersion | Versatile; can replace B3LYP in principle but slower |
| **ωB97X-D vs ωB97X** | Only dispersion improved; other properties slightly worsened | LC already solved some medium-range issues |

## Method recommendation by budget (for weak interactions)

| Budget tier | Recommended method | Basis set |
|------------|-------------------|-----------|
| **乞丐 (Bare minimum)** | Molecular mechanics (MM3, MMFF94, GAFF, OPLS-AA, UFF) | — |
| **特困 (Ultra-poor)** | PM6-D3H4 > PM6-D3 | — |
| **穷人 (Poor)** | B3LYP-gCP-D3 > PBEh-3c | 6-31G* |
| **低保 (Basic)** | PW6B95-D3 ≈ M06-2X-D3 ≥ wB97X-D > B3LYP-D3 | 6-31+G** |
| **小康 (Comfortable)** | Same as above | 6-311+G**; add counterpoise for dispersion-dominated |
| **致富 (Wealthy)** | DSD-BLYP ≈ PWPB95-D3 > B2PLYP-D3 | jun-cc-pVTZ or jul-cc-pVTZ; counterpoise for dispersion |
| **富裕 (Rich)** | SCS-MI-CCSD > MP2.5 | jun-cc-pVTZ or jul-cc-pVTZ; counterpoise for dispersion |
| **小土豪 (Small tycoon)** | CCSD(T) + counterpoise | aug-cc-pVTZ |
| **大土豪 (Big tycoon)** | CCSD(T)/CBS | CBS extrapolation from aug-cc-pVTZ and aug-cc-pVQZ with counterpoise |

**Notes:**
1. All D3 corrections above refer to **BJ damping** except M06-2X which uses **zero damping**
2. **Do NOT use 6-311++G(d,p)** — hydrogen diffuse functions add cost without value. 6-31+G* is the minimum for weak interactions. 6-31G** without any diffuse is unacceptable.
3. If dropping to 6-31G*, you MUST use counterpoise or gCP for BSSE
4. For electrostatic-dominated interactions (H-bonds, halogen bonds, etc.), optimization does NOT need diffuse functions
5. Counterpoise is for single-point only — NEVER optimize with counterpoise
6. If using ORCA, the RI technology completely changes this cost hierarchy — see sobereva.com/214

## Semi-empirical methods with dispersion

| Method | Notes |
|--------|-------|
| **PM3, AM1** | **Never use** — obsolete |
| **PM6** | Terrible for weak interactions without correction |
| **PM6-DH1/DH2** | Early dispersion + H-bond corrections |
| **PM6-DH+** | Improved; comparable to PM7 |
| **PM6-D3H4** | **Recommended** — best overall semi-empirical for weak interactions |
| **PM7** | Qualitative improvement over PM6 for weak interactions, but slightly worse than PM6-D3H4 |
| **AM1-D, OM3-D, DFTB-DH2** | Similar corrections applied to other semi-empirical methods |

## B3LYP-gCP-D3/6-31G* composite method

B3LYP/6-31G* has two error sources: (1) missing dispersion, (2) large BSSE from small basis. Correcting both simultaneously:

```
# B3LYP/6-31G* EmpiricalDispersion=GD3BJ   (+ gCP in ORCA)
```

- gCP (geometric counterpoise) corrects BSSE based on geometry — essentially free
- DFT-D3 corrects dispersion
- Both must be applied together — applying only one may make errors worse
- Result is significantly better than bare B3LYP/6-31G*, though still inferior to B3LYP-D3 with large basis

## PBEh-3c composite method

PBE0 with increased HF% + gCP + DFT-D3 + modified def2-SV(P) basis. Designed for low-cost reasonable weak interaction accuracy — better than B3LYP-D3-gCP/6-31G*. See DOI: 10.1002/open.201500192.

## Month basis sets for weak interactions

For saving time with large basis sets, truncate diffuse functions strategically:

| Basis | Modification | Impact on weak interaction |
|-------|-------------|--------------------------|
| aug-cc-pVDZ | Remove H diffuse → **maug-cc-pVDZ** | Negligible |
| aug-cc-pVDZ | For optimization: also remove C d-diffuse | Still OK |
| aug-cc-pVnZ → may/jun/jul/cc-pVnZ | Systematic diffuse truncation | See sobereva.com/119 |

See sobereva.com/119 for detailed "month" basis set discussion.

## High-accuracy approximation via additivity

```
E(CCSD(T)/aug-cc-pVQZ) ≈ E(MP2/aug-cc-pVQZ) - E(MP2/aug-cc-pVDZ) + E(CCSD(T)/aug-cc-pVDZ)
```

(Basis set correction added to small-basis CCSD(T))

## Minnesota functional grid sensitivity

M06-2X is criticized for convergence difficulty and spurious PES minima from over-parameterization. However:
- M06-2X-D3: spurious minima largely weakened
- `int=fine` is usually sufficient for geometry optimization
- `int=ultrafine` brings negligible accuracy improvement for M06-2X compared to other functionals
- If absolute precision is needed and cost is acceptable: use `int=ultrafine`

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/dft-d3-theory.md`** — DFT-D3 theory, damping functions, three-body term, other dispersion methods (TS, XDM, VV10, vdW-DF, MBD)
- **`references/gaussian-dftd-usage.md`** — Gaussian version capabilities, keyword usage, custom D3 parameters via IOp, G09 D.01 frequency bug, external keyword workflow
- **`references/functional-performance-d3.md`** — GMTKN30 benchmark results, functional-by-functional analysis, method recommendation by budget tier, semi-empirical methods with dispersion, B3LYP-gCP-D3 and PBEh-3c composite methods, month basis sets for weak interactions
