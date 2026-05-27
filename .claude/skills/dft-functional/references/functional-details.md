# DFT Functional Details

Detailed commentary on major functionals, double-hybrid selection guide, and excited-state functional selection. Based on Sobereva's article (sobereva.com/272).

## B3LYP: The old workhorse

**History:** 1994 to present — 30+ years, still the most used functional.

**Why it persists:** Despite being outdated, B3LYP is robust and well-balanced. While hundreds of functionals beat it on their specialties, few significantly exceed its universality.

**Two critical weaknesses:**
1. **Dispersion (van der Waals) attraction completely missing** — fixed by adding DFT-D3(BJ), which also slightly improves thermochemistry accuracy
2. **Charge-transfer (CT) and Rydberg excitations are terrible** — use CAM-B3LYP instead (CAM-B3LYP is generally worse than B3LYP for other purposes)

**Other limitations:**
- Poor for strong static correlation (common to all hybrid functionals)
- Overestimates high-spin stability in some TM complexes — fix: reduce HF from 20% to 15% (JCP,117,4729; TCA,107,48)
- Misses barrier for some reactions (e.g., F+H2→HF+H)
- Over-planarizes large conjugated systems with equalized bond lengths — see sobereva.com/557 for detailed discussion

**No functional is perfect** (except the legendary "holy grail" functional, which would be too expensive to use anyway). B3LYP roughly achieves a balance where improving A property's accuracy degrades B property's accuracy.

**Bottom line:** Except for dispersion-dominated weak interactions and CT/Rydberg excitations (where B3LYP absolutely must NOT be used), when facing a new problem and unsure which functional to use — try B3LYP-D3(BJ) first.

## M06-2X: The thermochemistry specialist

**Born:** 2008

**Strengths:**
- Weak interactions well-described (parameterized with them in mind)
- CT/Rydberg excitations good (54% HF component)
- Excellent organic thermochemistry: reaction energies, isomerization energies, barriers — sometimes approaching double-hybrid accuracy

**Weaknesses:**
- **Slower than B3LYP** — functional form is complex
- **Requires fine integration grid** — Minnesota functionals need higher grid quality than ordinary functionals. In Gaussian 09, use `int=ultrafine`. Occasionally need `int=superfine` for some weak interaction systems. Increases cost noticeably.
- Grid quality issues can cause geometry optimization convergence problems and small imaginary frequencies after optimization
- **NOT suitable for TM/lanthanide/actinide systems** — parameterized for main-group only. This is critical — using M06-2X for TM systems is "basically seeking disaster." Use MN15 or MN15L if Minnesota family is needed for TM.
- Poor for static correlation (high HF component makes it worse)
- Significantly overestimates HOMO-LUMO gap
- Overestimates singlet local valence excitation energies
- Terrible for anharmonic frequencies (JCTC,6,2115)

## wB97XD / wB97X-D3: The long-range corrected option

**Born:** 2008 (wB97XD); later wB97X-D3 improved it

**wB97XD:**
- Uses DFT-D2 dispersion correction → good weak interaction accuracy
- Long-range correction → good CT/Rydberg excitations
- Parameterized for main-group but not as bad as M06-2X for TM systems
- Slower than B3LYP
- Same static correlation / HOMO-LUMO gap issues

**wB97X-D3 (recommended over wB97XD):**
- Upgraded dispersion from DFT-D2 to DFT-D3
- Improved parameters
- Better overall accuracy for thermochemistry and weak interactions
- Supported by ORCA but NOT Gaussian
- If your program supports wB97X-D3, use it instead of wB97XD

## wB97M-V: The accuracy champion (non-double-hybrid)

**Born:** 2016

**Status:** Among all non-double-hybrid functionals, wB97M-V has the highest average accuracy for ground-state energy problems. More accurate than lower-ranked double-hybrids like B2PLYP.

**Characteristics:**
- Parameterized mainly for main-group but performs well for TM systems too
- Only supported by ORCA, Q-Chem — NOT by Gaussian (as of G16 C.02)
- Higher cost than B3LYP but with ORCA's RIJCOSX acceleration, wB97M-V on large systems can be FASTER than B3LYP in Gaussian
- **Analytical gradient supported** (ORCA 5.0+) but **NO analytical Hessian** → frequency analysis is extremely expensive
- SCF convergence is often difficult; wB97X-V may converge more easily
- wB97X-V is similar in characteristics, slightly less accurate overall but sometimes better for TM systems

**Recommendation:** Use wB97M-V only for single-point energy calculations, NOT for opt+freq. For opt+freq, use B3LYP-D3(BJ) — fast, reliable, easy to converge, unlikely to have imaginary frequencies.

**Note:** wB97M-D3(BJ) and wB97M-D4 can compute analytical Hessian, but CPSCF convergence during frequency analysis is often very difficult in ORCA 5.0. wB97X with dispersion correction doesn't have this problem.

## PBE0

**Strengths:**
- Good for vertical local valence excitation energies (~0.3 eV average error)
- Good for electron density distribution
- Good for main-group clusters
- Recommended for 4d/5d metal-ligand bond lengths (medium-HF functional)
- Good starting point for TM/lanthanide/actinide complexes

## TPSSh

**Strengths:**
- Good for main-group clusters
- Good for Cu/Ag/Au clusters
- Good for electron density distribution
- Good for dipole moments and ESP
- Recommended for 3d metal-ligand bond lengths
- Good for TM complexes (actinides especially)
- Good for main-group bridged TM (e.g., Fe-S-Fe)
- Good for spin-state energy differences (with MN15L)

## CAM-B3LYP

**Strengths:**
- Good for large conjugated system excitations
- Good for CT and Rydberg excitations
- Good for hyperpolarizability

**Note:** Generally worse than B3LYP for non-excitation purposes.

## r2SCAN / r2SCAN-3c

**Strengths:**
- Good for strong multireference character systems
- r2SCAN-3c composite method: cheap and likely more accurate than any pure functional + dispersion with large basis set
- Good for 3d metal-ligand bond lengths

## BHandHLYP

**Strengths:**
- Good for polarizability (especially large conjugated systems)
- Good for hyperpolarizability

## Double-hybrid functionals

Double-hybrids are generally one tier more accurate than ordinary functionals and demolish MP2, at only slightly higher cost than MP2.

**However:** Some newer ordinary functionals (e.g., wB97M-V) can match or exceed older/middling double-hybrids in some cases. Don't assume double-hybrids are always better.

**Always add DFT-D3(BJ) even for non-weak-interaction calculations** to improve overall performance.

**Geometry optimization/frequency with double-hybrids:** Much more expensive than ordinary functionals, with little accuracy advantage for these tasks. Use ordinary functionals for opt+freq, double-hybrids for single-point energy.

### Notable double-hybrids

| Functional | Status | Program support | Notes |
|------------|--------|----------------|-------|
| **PWPB95-D3(BJ)** | High robustness, good overall accuracy | ORCA etc. (NOT Gaussian) | Best for metal-organic reactions. Ranks high for intermolecular weak interactions. ORCA users should prefer this over B2PLYP. |
| **B2PLYP-D3(BJ)** | Oldest, mediocre accuracy | Widely supported | Sometimes落后 from newer ordinary functionals like wB97M-V. Acceptable for Gaussian users. ORCA users should use PWPB95 instead. |
| **DSD-PBEP86-D3(BJ)** | Very good in some tests, shocking failures in others | Gaussian 16 (built-in as DSDPBEP86) | High risk — can give surprisingly bad results. Built into G16. |
| **DSD-BLYP-D3(BJ)** | Similar to DSD-PBEP86 | — | Same risk profile. |
| **revDSD-PBEP86-D3(BJ)** | Improved DSD-PBEP86 (2019) | ORCA 6.0+; Gaussian via custom (sobereva.com/344) | Notable improvement claimed. Good for weak interaction energies and main-group reaction energies. **First choice for Gaussian users** (via custom definition). Robustness still uncertain for all cases. |
| **wB97X-2-D3(BJ)** | Very good overall accuracy, robust | ORCA, GAMESS-US, Q-Chem | Good for intramolecular weak interactions, mediocre for intermolecular. DFT-D3(BJ) parameters not built-in in ORCA 5.0/GAMESS-US — get from PCCP,20,23175(2018) SI. ORCA users can use Multiwfn to generate input (sobereva.com/490). |
| **wB97M(2)** | Best performing double-hybrid (2018) | ORCA 6.0+, Q-Chem 5.2+ | Most excellent overall. |

### Double-hybrids for excited states

| Excitation type | Recommended method | Notes |
|----------------|-------------------|-------|
| **Local excitation** | DSD-PBEP86 TDDFT | Directly supported by ORCA. Ideal. |
| **Intramolecular CT** | DSD-PBEP86 TDDFT | Also good. |
| **Intermolecular CT** | RS-PBEP86 / SOS-CIS(D) | Best accuracy. Only supported by MRCC program. |
| **Intermolecular CT (ORCA)** | RSX-QIDH TDDFT | Inferior to RS-PBEP86/SOS-CIS(D) but much better than DSD-PBEP86 TDDFT. |

Source: JCTC (2022) DOI: 10.1021/acs.jctc.1c01307

## Excited state functional selection summary

| Scenario | Recommended |
|----------|-------------|
| Vertical local valence excitation | PBE0 |
| Large conjugated / CT / Rydberg | CAM-B3LYP, wB97XD (PBE38 also for large conjugated) |
| Triplet excitation | M06-2X |
| General (single functional) | PBE0, CAM-B3LYP, PBE38, wB97XD |
| Best overall (extra cost) | ω-tuned LC-ωPBE (optimize ω per system per structure — see sobereva.com/346) |
| Best accuracy (much more cost) | DSD-PBEP86 TDDFT (ORCA) |

See sobereva.com/265 for detailed excited state calculation guidance.
