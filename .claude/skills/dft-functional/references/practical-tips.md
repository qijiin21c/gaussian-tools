# Practical DFT Computation Tips

Practical computation tips, program comparisons, and CCSD(T) usage. Based on Sobereva's article (sobereva.com/272).

## Switching functionals between tasks

A common question: Is it OK to use different functionals for task A and task B?

**Yes, this is common practice and perfectly acceptable.** See detailed discussion at sobereva.com/415.

**Typical workflow:**
- Optimization + frequency: B3LYP-D3(BJ) or wB97XD (ordinary functional)
- Single-point energy: wB97M-V, revDSD-PBEP86-D3(BJ), or other higher-level functional

This is NOT inconsistent — it's the recommended approach for balancing cost and accuracy.

## Large organic/flexible systems

For large, especially flexible, organic systems:

**Recommendation:** Use B3LYP-D3(BJ) for optimization and frequency, M06-2X for single-point energy.

**Why not M06-2X for optimization?**
- Complex functional form → slower than B3LYP
- Sometimes requires very fine integration grid (`int=ultrafine` or even `int=superfine`) to solve convergence and small imaginary frequency problems
- Further increases cost

**When to use B3LYP for optimization:** See detailed discussion at sobereva.com/557 — when B3LYP is appropriate and when it's NOT. For large conjugated systems, wB97XD is often much better.

## Double-hybrid for opt+freq: Generally NOT recommended

Unless the system is very small:
- Use **ordinary functional** for geometry optimization and frequency analysis
- Use **double-hybrid** for single-point energy calculation

**Why:** Opt+freq are much less sensitive to calculation level than energy calculations (see sobereva.com/387). Double-hybrids' accuracy advantage for opt+freq is far smaller than for energy calculations, but the cost is much higher.

## Gaussian vs ORCA

**ORCA advantages:**
- Significantly lower cost for similar accuracy, or significantly higher accuracy for similar cost
- RI technology for double-hybrids: dramatically lower time and memory/disk usage compared to Gaussian
- RIJCOSX acceleration for wB97M-V can make it faster than B3LYP in Gaussian for large systems

**Double-hybrid comparison (example — 60+ atom organic system, def2-TZVPP):**
| Program | Time | Temp file |
|---------|------|-----------|
| ORCA (RI, 36-core) | ~6 minutes | ~3 GB |
| Gaussian | ~3 hours | up to 1 TB |

ORCA with RI can handle 200+ atom organic systems with double-hybrids, or 100+ atoms with def2-QZVPP. Gaussian cannot handle these.

**ORCA setup:**
- Installation: sobereva.com/451
- Multiwfn can generate ORCA input files: sobereva.com/490
- See ORCA category at sobereva.com for more articles

## CP2K for very large systems

For systems with hundreds of non-hydrogen atoms, especially near-spherical (large clusters, cluster models cut from crystals):

**CP2K is the most efficient choice** — even faster than ORCA.
- Can compute single-point energy for 1000+ atom systems on a standard dual-socket server
- For pure functionals, can handle thousands of atoms
- Uses plane waves as auxiliary basis → Coulomb interaction cost is far lower than quantum chemistry programs
- Free and powerful
- Easy to learn with Multiwfn integration
- Training: sobereva.com/workshop/KFP_content.html

## CCSD(T): The next tier above double-hybrids

If you need results one tier higher than double-hybrids:

**Baseline:** CCSD(T)/cc-pVTZ (minimum: def2-TZVP). Very expensive — for asymmetric organic systems, typically limited to ~30 atoms even on good servers.

**CCSD(T) limitations:** Not ideal for strong static correlation cases — use multireference methods (NEVPT2, MRCI) instead.

### DLPNO-CCSD(T): For larger systems

ORCA supports DLPNO-CCSD(T) — low-scaling coupled cluster.
- With `tightPNO` and cc-pVTZ: can handle 70+ atom systems
- Example: 66-atom organic system on 36-core machine in ~8 hours, 117 GB temp file
- Accuracy nearly identical to canonical CCSD(T)

### Improving CCSD(T) basis set from TZ to QZ

From cc-pVTZ/def2-TZVPP to cc-pVQZ/def2-QZVPP gives non-negligible improvement, but cost is extremely high. Two strategies to reduce cost:

**(1) Explicit correlation F12:**
- CCSD(T)-F12/cc-pVDZ-F12 achieves CCSD(T)/cc-pVQZ accuracy at much lower cost
- See "显式相关计算" section at sobereva.com/workshop/KAQC_content.html for ORCA examples

**(2) MP2-based correction:**
- CCSD(T)/cc-pVDZ (or TZ) + [MP2/cc-pVQZ - MP2/cc-pVDZ (or TZ)] correlation energy correction
- Commonly used but less elegant/robust than F12
- See Section 5 of sobereva.com/378 for an example

## DFT-D dispersion correction versions

| Version | Notes |
|---------|-------|
| **DFT-D2** | Built into wB97XD. Older. |
| **DFT-D3** | Most common. DFT-D3(BJ) recommended over DFT-D3(0). |
| **DFT-D3(BJ)** | Recommended version. Becke-Johnson damping. |
| **DFT-D4** | Newer. If your program supports it and has parameters for your functional, prefer DFT-D4. Significant improvement for TM organometallic reactions and weak interactions. Small difference for organic systems. |

See:
- sobereva.com/413 — Whether to add DFT-D3
- sobereva.com/210 — Using DFT-D correction
- sobereva.com/464 — DFT-D4 introduction and usage
- sobereva.com/83 — Rambling about DFT-D
- sobereva.com/214 — Solutions for large-system weak interactions

## Key references

- sobereva.com/272 — This article (functional selection)
- sobereva.com/415 — Switching functionals between tasks
- sobereva.com/557 — When B3LYP optimization is appropriate
- sobereva.com/387 — Why opt+freq don't need large basis sets
- sobereva.com/554 — What makes a meaningful benchmark
- sobereva.com/543 — Understanding HOMO, LUMO, and gap
- sobereva.com/354 — NMR chemical shift calculation
- sobereva.com/265 — Excited state calculation methods
- sobereva.com/378 — Post-HF method accuracy comparison
- sobereva.com/344 — Using non-built-in methods/functionals in Gaussian
- sobereva.com/490 — Multiwfn generating ORCA input files
- sobereva.com/214 — Large system weak interaction solutions (ORCA vs Gaussian comparison)
- sobereva.com/346 — optDFTw tool for optimizing ω parameter
