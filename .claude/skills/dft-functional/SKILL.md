---
name: dft-functional
description: This skill should be used when the user asks to "choose DFT functional", "which functional to use", "B3LYP vs M06-2X", "泛函选择", "DFT-D3", "wB97M-V", "dispersion correction", "CAM-B3LYP for charge transfer", "PBE0 vs B3LYP", "functional for transition metal", "TDDFT functional", "double hybrid functional", "wB97XD", "DSD-PBEP86", or mentions selecting exchange-correlation functionals for DFT calculations.
version: 0.1.0
---

# DFT Functional Selection Guide

Comprehensive guidance for choosing DFT functionals based on the system and problem type, based on Sobereva's authoritative article (sobereva.com/272).

**Important:** Do NOT blindly copy functional choices from published papers. Many papers use inappropriate functionals or are severely outdated. Do NOT do your own "functional benchmarking" without understanding what makes a meaningful benchmark — see sobereva.com/554.

## Core principle: Accuracy hierarchy

For energy-related problems (highest to lowest accuracy):
**CCSD(T) > Double-hybrid > Properly chosen ordinary functional > MP2 > HF > Semi-empirical**

**Do NOT use HF** — it's completely obsolete. DFT with any reasonable functional is much better, and in Gaussian, DFT costs only slightly more than HF. Reviewers with basic knowledge will reject HF-based papers.

**Do NOT use MP2** — significantly more expensive than ordinary functionals, worse accuracy than well-chosen functionals, double-hybrids at similar cost demolish MP2. MP2 performs terribly for open-shell and transition metal systems. Only a few remaining uses: (1) H-bond energies with large basis sets (but double-hybrids are better), (2) NMR/hyperpolarizability (but some double-hybrids beat it), (3) Estimating CCSD(T)/large-basis energies (see SKILL.md Section 6).

## When in doubt: B3LYP-D3(BJ)

B3LYP (1994) remains the most used default functional despite being 30+ years old. It's robust and well-balanced. While hundreds of functionals exist that beat B3LYP on their specialty, few significantly exceed its universality.

**B3LYP's two critical weaknesses:**
1. Cannot describe dispersion (van der Waals) attraction — **fixed by adding DFT-D3(BJ)**
2. Terrible for charge-transfer (CT) and Rydberg excitations — **use CAM-B3LYP instead for these**

**Other B3LYP limitations:**
- Poor for strong static correlation (common to all hybrid functionals)
- Overestimates high-spin stability in some transition metal complexes — fix by reducing HF component from 20% to 15%
- Poor for some reactions (e.g., F+H2→HF+H misses barrier)
- Tends to over-planarize large conjugated systems with equalized bond lengths — use wB97XD instead

**Rule of thumb:** If you encounter a new problem, don't know which functional to use, and can't be bothered to look it up — try B3LYP-D3(BJ) first (except for dispersion-dominated weak interactions and CT/Rydberg excitations where B3LYP absolutely must not be used).

## DFT-D dispersion correction

**Always add DFT-D3(BJ) unless you know it's unnecessary.** If your program supports DFT-D4 and has parameters for your functional, prefer DFT-D4 — especially for transition metal organometallic reactions and weak interactions where it can noticeably improve accuracy over DFT-D3. For organic systems, DFT-D4 vs DFT-D3 difference is small.

## Quick selection by task

| Task | Recommended functional | Notes |
|------|----------------------|-------|
| **Vertical local valence excitation** | PBE0 | ~0.3 eV average error, slightly better than B3LYP |
| **Large conjugated system excitation / CT / Rydberg** | CAM-B3LYP, wB97XD | PBE38 also works for large conjugated |
| **Triplet excitation energy** | M06-2X | |
| **General excitation (single functional)** | PBE0, CAM-B3LYP, PBE38, wB97XD | |
| **Polarizability** | PBE0, BHandHLYP (large conjugated) | |
| **Hyperpolarizability** | wB97, LC-τHCTH | BHandHLYP, CAM-B3LYP also OK |
| **NMR (13C, 1H)** | B3LYP + scaling method | Or revTPSS/pcSseg-1 without scaling |
| **Vibrational frequency** | B3LYP | B3LYP-D3(BJ) if dispersion strongly affects conformation |
| **Main-group geometry optimization** | B3LYP | B3LYP-D3(BJ) if dispersion is important; wB97XD for large conjugated |
| **HOMO-LUMO gap** | B3LYP | |
| **Organic thermochemistry** | wB97M-V > M06-2X | |
| **Weak interactions** | wB97M-V ≥ wB97X-V ≥ PW6B95-D3(BJ) ≥ M06-2X ≈ wB97X-D3 ≥ B3LYP-D3(BJ) | r2SCAN-3c in ORCA for speed |
| **Halogen bonds** | M06-2X | |
| **Main-group clusters** | PBE0, TPSSh | B3LYP also OK for carbon clusters |
| **Cu/Ag/Au clusters** | TPSS, TPSSh | revDSD-PBEP86 double-hybrid is significantly better |
| **Strong multireference character** | r2SCAN, TPSS, MN15L | |
| **Vertical electron affinity / Fundamental gap** | wB97X, wB97XD | ω-tuned functionals even better |
| **Vertical ionization energy** | M06-2X | |
| **Electron density distribution** | PBE0, TPSSh | |
| **Dipole/multipole moment, ESP** | wB97M-V | TPSSh, B3LYP also OK; revDSD-PBEP86-D3(BJ) much better |

## Transition metal / lanthanide / actinide systems

| Task | Recommended functional | Notes |
|------|----------------------|-------|
| **Closed-shell TM-organic reaction/barrier** | wB97X-V or wB97M-V | Then PBE0-D3(BJ), MN15; TPSSh-D3(BJ) also decent. Pure: B97M-rV > SCAN-D3(BJ) > TPSS-D3(BJ) |
| **Open-shell TM-organic reaction/barrier** | TPSS0-D4 | Then PBE0-D4 (PBE0-D3(BJ) slightly worse). Pure: B97M-V best |
| **3d metal-ligand bond length** | TPSS, TPSSh | r2SCAN also good. Use pure or low-HF functionals |
| **4d/5d metal-ligand bond length** | PBE0 | Use medium-HF functionals |
| **TM/lanthanide/actinide complexes** | PBE0, TPSSh, MN15, MN15L, r2SCAN | Use several + D3(BJ)/D4. Single-point: wB97X-V or wB97M-V better. B3LYP is mediocre |
| **TM-TM d-orbital bonds / TM clusters** | r2SCAN, TPSS, PBE | MN15L also OK. Must use pure functionals (strong static correlation) |
| **Main-group bridged TM (e.g., Fe-S-Fe)** | TPSSh | |
| **Spin-state energy difference** | MN15L, TPSSh | |

## When nothing above applies

Try **B3LYP-D3(BJ)** first. If results are unsatisfactory, try **wB97M-V** or **MN15**. If you can afford higher cost, use a **double-hybrid functional**.

## Workflow recommendation: Optimize with ordinary functional, single-point with double-hybrid

For anything but the smallest systems:
1. **Geometry optimization + frequency:** Ordinary functional (B3LYP-D3(BJ) or wB97XD) — fast, reliable, unlikely to have imaginary frequencies
2. **Single-point energy:** Double-hybrid (revDSD-PBEP86-D3(BJ), wB97M-V, etc.) — much better accuracy for energy

**Why:** Geometry optimization and frequency analysis are far less sensitive to the calculation level than energy calculations. Double-hybrids offer little accuracy advantage for opt/freq but are much more expensive.

## M06-2X and wB97XD: Potential B3LYP alternatives

Both emerged in 2008, supported by mainstream programs like Gaussian.

**M06-2X strengths:**
- Good for weak interactions (parameterized with them)
- Good for CT/Rydberg excitations (54% HF component)
- Excellent for organic thermochemistry (reaction energies, isomerization, barriers) — sometimes near double-hybrid accuracy

**M06-2X weaknesses:**
- Slower than B3LYP
- Requires finer integration grid (int=ultrafine in Gaussian, sometimes int=superfine) — increases cost further
- **Absolutely NOT suitable for transition metal / lanthanide / actinide systems** — parameterized for main-group only. Use MN15 or MN15L instead if Minnesota family is needed
- Poor for static correlation (high HF component)
- Significantly overestimates HOMO-LUMO gap
- Terrible for anharmonic frequencies

**wB97XD strengths:**
- Good for weak interactions (DFT-D2 built-in)
- Good for CT/Rydberg excitations (long-range corrected)
- Less bad than M06-2X for transition metal systems (but still not recommended)

**wB97XD weaknesses:**
- Slower than B3LYP
- Same static correlation / HOMO-LUMO gap issues as M06-2X
- **Prefer wB97X-D3 instead** if your program supports it (ORCA does, Gaussian doesn't) — improved dispersion from DFT-D3, better overall accuracy

**Neither has truly replaced B3LYP as the default** due to speed and the issues listed above. Use them when specifically needed.

## MN15 / MN15L (Minnesota 2016)

- **MN15:** Balanced for transition metals and main-group. No advantage over M06-2X for main-group. Mixed results for TM systems. Limited practical value.
- **MN15L:** Intended to replace M06L. No substantial improvement.

## APFD — Do NOT use

Gaussian's "Exploring Chemistry" book v3 uses APFD throughout, misleading beginners. In benchmark studies, APFD performs mediocrity — no advantage over B3LYP-D3(BJ). Rarely used in the literature. If a reviewer asks why you used it, you'll have no good answer. **Do not be misled by that book.**

## Additional Resources

For detailed methodology and comprehensive coverage, consult:

- **`references/functional-details.md`** — Detailed commentary on every major functional, double-hybrid selection, excited-state functional selection
- **`references/practical-tips.md`** — Practical computation tips: ORCA vs Gaussian, program recommendations, when to switch functionals, CCSD(T) usage
- **`references/non-built-in-methods.md`** — How to use non-built-in functionals and methods in Gaussian via IOp: custom functional definition rules (IOp(3/76-78)), SCS-MP2/SCSN-MP2/MP2.5, B3LYP variants (B3LYP*, VWN5-B3LYP), PBE0 variants (PBE0-1/3, PBE38), range-separated ω tuning, QTP17, double-hybrid customization (B2GP-PLYP, DSD-PBEP86-D3(BJ), revDSD), CRITICAL warning about IOp only applying to first step in multi-step tasks
