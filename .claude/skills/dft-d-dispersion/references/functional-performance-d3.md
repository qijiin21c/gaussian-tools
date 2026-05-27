# Functional Performance with DFT-D3 and Method Recommendations

Detailed analysis of functional performance for weak interactions with DFT-D3 correction, method recommendation tiers, and related practical guidance, based on Sobereva's articles (sobereva.com/83, sobereva.com/210).

## Why DFT functionals fail for weak interactions

Local/semilocal correlation potentials have incorrect medium- and long-range behavior, especially at long range where the van der Waals C₆/R⁶ behavior cannot be manifested.

**Two levels of problem:**
1. **Medium range:** Correlation is partially described but inadequate
2. **Long range:** Completely empty — no C₆/R⁶ behavior at all

**Solution strategies:** Strengthen medium range, fill the long-range gap entirely.

## Four approaches to incorporating dispersion in DFT

### 1. Nonlocal correlation functionals (DFT-NL / vdW-DF / VV)

These use nonlocal correlation functionals — the energy calculation requires a double integral over two variables instead of a single-variable integral (local form):

```
E_c,NL = ∫∫ ρ(r₁) φ(r₁,r₂) ρ(r₂) dr₁ dr₂
```

| Method | Combined with | Notes |
|--------|--------------|-------|
| vdW-DF-04 | LSDA | Original |
| vdW-DF-10 | LSDA | Reparameterized |
| VV09 | LSDA | Simpler than vdW-DF |
| VV10 | PBE | Simplest form |

**Pros:** Strict principle, less empirical content
**Cons:** Computationally complex, unpopular
**Verdict:** No development or application prospects. Not recommended.

### 2. Parameterized functionals (Minnesota family)

Functionals like M06-2X, M11, M11-L are parameterized with weak interaction systems included in the training set.

**Pros:** Convenient, widely supported in mainstream programs
**Cons:**
- Still limited by semilocal form — cannot exhibit C₆/R⁶ behavior
- Medium range is OK, but long range (distant fragments) is still poor
- Example: A large molecule with several distant branches — inter-branch dispersion is poorly described

**Verdict:** Better than standard functionals but still limited. Adding DFT-D to Minnesota functionals further improves results by fixing the semilocal form's intrinsic long-range defect.

### 3. DFT-D (empirical dispersion correction)

The most promising and popular approach. Originally used with HF in the 1970s, revived around 2000, exploded in popularity from 2007 onward.

**Form:** Like molecular force fields — compute C₆/R⁶ for each atom pair and sum, multiplied by a damping function f(R) that goes to zero at short range, returning to the original DFT functional form.

**Additional benefit:** DFT-D correction energy can be easily extracted as an estimate of dispersion interaction energy.

**Why DFT-D improves ALL properties (not just weak interactions):**
- The reason dispersion is poorly described is because the correlation potential is wrong
- DFT-D, while designed to fix dispersion,本质上 corrects the correlation potential
- Therefore DFT-D improves areas where the original functional was already "decent"
- Practice confirms: DFT-D improves even the functional's own strengths

**C₈/R⁸ term:** Sometimes included to further strengthen medium-range description.

**DFT-D safety:** As long as parameters are properly fitted, results only improve — never worsen.

**DFT-D's one limitation:** It does NOT modify the Kohn-Sham potential operator — it only adds an energy term. Therefore, electron density cannot respond to weak interactions during SCF. In practice, this density difference is usually negligible.

**Grimme's DFT-D3 advantages:**
- Solves the "atom type" problem via fractional coordination number (CN) concept
- CN depends only on molecular coordinates — no topology dependence
- Example: H in CH₄ has CN ≈ 1; free H has CN = 0; H during reaction may have CN = 0.7 → interpolation between precomputed CN=0 and CN=1 dispersion coefficients
- This frees DFT-D from topological constraints — crucial for reaction transition states
- Includes three-body dispersion term (E_disp(ABC) ≠ E_disp(AB) + E_disp(BC) + E_disp(AC))
- Three-body term improves accuracy for large systems but is small; also removes analytic gradient → generally not computed by default

**XDM (exchange-dipole moment):** Special DFT-D variant that auto-computes parameters from wavefunction — no pre-fitting needed, automatically responds to chemical environment. But: limited functional compatibility, complex form, inconvenient gradient computation, requires wavefunction (not just coordinates).

### 4. Dispersion-correcting potentials (DCP / 1ePOT)

Modifies the one-electron effective potential by adding equivalent vdW potentials from surrounding atoms (long-range weak attraction + short-range weak repulsion), similar to ECP approach.

**Pros:** Any program supporting ECP can use it; moderate computational cost; can combine with existing functionals
**Cons:**
- Too many parameters — each element + each functional + each basis set needs its own set
- Too empirical
- Too few elements parameterized
- No proper C₆/R⁶ asymptotic behavior
- Large system results significantly worse than small systems (DOI: 10.1002/open.201500192)
- Not widely supported by quantum chemistry programs

**Verdict:** Not opposed in principle, but DFT-D is clearly better operated, more convenient, more widely applied, and more proven.

## LC (long-range correction) ≠ dispersion correction

LC separates the 1/r₁₂ operator into short-range and long-range parts, using 100% HF exchange at long range instead of pure DFT exchange. This fixes:
- TDDFT charge-transfer excitations
- Polarizability calculations
- Exchange potential asymptotic behavior

**But LC does NOT fix dispersion:**
- The long-range Coulomb correlation (most directly related to dispersion) is still not considered
- HF has LC but describes dispersion terribly
- MP2's form shows that virtual orbital interactions (the essential component) are not introduced by LC

**However:** Using LC well (e.g., ωB97X) does improve results — more degrees of freedom in parameterization help. But it cannot replace DFT-D.

## GMTKN30 benchmark results (PCCP 2011)

Grimme's comprehensive benchmark using 30 subsets (atomization energies, reaction energies, barriers, weak interactions, etc.):

### Jacob's ladder still holds with D3

**Double-hybrid-D3 > Hybrid-D3 > meta-GGA-D3 > GGA-D3 > LSDA-D3**

### GGA-D3
- **revPBE-D3** is the best GGA-D3, good for all problems
- PBE-D3 is nearly as good and more popular

### meta-GGA-D3
- Limited improvement over GGA-D3
- TPSS-D3 is acceptable

### Hybrid-D3
- **M06-2X-D3(0)** is the best — unbeatable for both weak interactions and reaction energies/atomization energies
- **Caveat:** Minnesota functionals are convergence-difficult and grid-sensitive. Grimme used the worst case (M06HF) to argue against all Minnesota functionals, which unfairly tarnishes M06-2X
- **PW6B95-D3** is second only to M06-2X-D3 with no other issues — recommended alternative
- Note: PW6B95 has limited program support (NWChem, Q-Chem, ORCA)

### Double-hybrid-D3
- Significantly better than hybrid-D3
- **DSD-BLYP-D3** (B2PLYP with SCS-MP2-style spin scaling + D3): Best at 4-zeta basis
- **PWPB95-D3**: Second only to DSD-BLYP-D3; best at 3-zeta (less basis-dependent)
- **Critical:** Double-hybrid-D3 MUST use at least 3-zeta basis — at double-zeta, results are barely better than hybrid-D3
- 3-zeta → 4-zeta improvement is noticeable; 4-zeta → higher is unnecessary

### Important finding
- Good atomization energy ≠ good reaction energy
- Atomization energy calculation has little practical application value — should not be used as the sole metric for method quality

### Caveat
GMTKN30 mainly contains low-period elements with single-reference character. Results may not transfer to other problems (e.g., transition metals). Metal system testing was ongoing at the time of publication.

## Functional-by-functional analysis for weak interactions

### PBE
Best among GGA functionals for weak interactions, still inadequate. Use PBE-D3.

### B3LYP
Obsolete. Claims that B3LYP is "not bad" for H-bonds (JPCA, 111, 10439) are generous — it's barely acceptable. For van der Waals: completely useless — cannot describe dispersion at all. **Use B3LYP-D3(BJ).**

### X3LYP
Claims of good H-bond performance are true sometimes, but stacking interaction performance is terrible (see Grimme's review). **Do not use.** With DFT-D3 available, X3LYP's value is nearly zero.

### B97D
Grimme 2007, proposed with D2. Available since G09 initial release. **Do not use** — D3 was later proposed with larger training set parameterization. Use B97D3 instead.

### revPBE-D3
Modified PBE + DFT-D3. Best GGA-D3 for all problems. Still inferior to dispersion-corrected hybrid and double-hybrid functionals. Recommended when GGA is required and dispersion correction is available.

### SSB-D2
Author claims excellent performance on difficult systems. Not widely supported. Note: SSB-D3 performed poorly in Grimme's PCCP comparison — either D3 doesn't suit it (D2 does), or different training sets, or the author's test set was too small.

### M06-2X
Already good for weak interactions without D3 (may severely underestimate binding for some π-π stacking like benzene dimer). Widely supported. Can incorporate weak interaction effects into density. **With DFT-D3(0): unbeatable in all aspects** — weak interactions, reaction energies, atomization energies — best among hybrid functionals in Grimme's survey.

### M11
Newer than M06-2X. Hybrid meta-GGA with range-separated form: 100% HF at long range, 42.8% HF at short range. Paper claims comprehensive performance similar to M06-2X, improved multireference handling, no improvement in weak interactions/excited states. **Sobereva's test (JMM, 19, 5387): M11 describes weak interactions significantly worse than M06-2X.** Not recommended.

### M11-L
Meta-GGA, no HF component. Best non-hybrid/non-DFT-D functional for weak interactions (training set included weak interaction systems). Overall performance (including weak interactions) inferior to M11, but excellent for strong multireference systems — far superior to other functionals.

### PW6B95-D3
Second only to M06-2X-D3 among dispersion-corrected hybrids. Use when M06-2X has issues. Good for all problems, not just weak interactions. Limited program support: NWChem, Q-Chem, ORCA.

### wB97X-D
Head-Gordon 2008. ωB97X + reparameterized dispersion correction (damping function differs from Grimme D2). Available in G09 as `wB97XD`. With both LC and dispersion correction, very versatile — good for weak interactions, TDDFT, and thermochemistry (among the best dispersion-corrected hybrids).

**Caveat:** Dispersion correction does NOT bring the same side benefits as DFT-D to other properties. ωB97X-D vs ωB97X: only dispersion improved; other properties show no improvement (LC may have already solved many medium-range issues, leaving no room for DFT-D intervention); TDDFT slightly worsened.

**Overall:** Excellent —可以放心 use for any problem. Can replace B3LYP in principle, but significantly slower — use discretion.

## Post-HF methods for weak interactions

### MP2
Good for H-bonds. Overestimates weak interactions (binds too strongly) — but still far better than uncorrected DFT. Extremely accurate for saturated molecule dimers (e.g., methane dimer) — near CCSD(T). Requires larger basis sets than DFT. **No longer necessary** — double-hybrids are better.

### SCS-MP2
Better dispersion than MP2 (but saturated molecule dimer results worsen). Reaches double-hybrid level. H-bonds worse than MP2. Good for reaction energies. No other improvement over MP2. Other variants (SOS-MP2, S2-MP2) are worse than MP2. **Use only when DFT cannot be used** (e.g., severe SIE).

### MP2.5
MP2 + 0.5 × MP3 third-order correction. Better than all spin-scaled MP2 variants. Main improvement: π-π stacking. Weak interactions approach CCSD(T)/CBS at moderate basis sets (even without diffuse). 10× MP2 cost, 10× less than CCSD.

### MP2.X
MP2.5 with basis-set-specific weights fitted from S66 test set. Makes even 6-31G* give weak interaction energies comparable to MP2.5/aug-cc-pVTZ. Tempting but reliability on broader systems needs verification. **Use with caution.**

### SCS-CCSD
Like SCS-MP2 applied to CCSD. Weak interactions and reaction energies much better than CCSD — near CCSD(T).

### SCS-MI-CCSD
Parameters fitted from weak interaction systems. Much better than SCS-CCSD for weak interactions. More expensive than MP2.X but better results. Cost-effective.

## Double-hybrid performance for weak interactions

### XYG3
Xu-Xin/Goddard 2009. Good for main-group, reaction energies, weak interactions — better than uncorrected double-hybrids. But no dedicated dispersion term; MP2 is only partial at long range → incorrect van der Waals asymptotic. Parameters fitted only to G3/99 thermochemistry. After other double-hybrids adopted D3, XYG3 is clearly disadvantaged for weak interactions.

### B2PLYP
Earliest double-hybrid. MP2 component makes it clearly better than standard DFT for weak interactions. Slightly better than standard DFT-D (including M06-2X, wB97XD) but significantly more expensive — not cost-effective. Some normal systems worse than standard DFT.

### B2PLYP-D3
Always better than B2PLYP, but not necessarily better than the best hybrid-D3.

### B2GPPLYP-D3
Slightly better than B2PLYP-D3, slightly worse than DSD-BLYP-D3. Mid-range among double-hybrids.

### DSD-BLYP-D3
DSD-BLYP + D3. At 4-zeta, Grimme claims it's the best overall dispersion-corrected functional — not just for weak interactions but for all problems.

### PWPB95-D3
Best dispersion-corrected functional at 3-zeta for all problems. Second only to DSD-BLYP-D3 at 4-zeta.

## CCSD(T)

At CBS basis set extrapolation: **the gold standard for weak interactions.** Use when budget allows.

## Composite methods for cost-effective calculations

### B3LYP-gCP-D3/6-31G*

B3LYP/6-31G* has two error sources:
1. Neglected dispersion
2. Large BSSE from small basis

Correcting both:
- DFT-D3 for dispersion
- gCP (geometry-based BSSE correction) — essentially free
- Both must be applied simultaneously — applying only one may increase errors
- Result is significantly better than B3LYP/6-31G*, especially for barriers and weak interactions
- Still inferior to B3LYP-D3 with large basis, but best option at 6-31G* level

### PBEh-3c

PBE0 with increased HF% + gCP + DFT-D3 + modified def2-SV(P) basis. Purpose: reasonable weak interaction accuracy at low cost. Better than B3LYP-D3-gCP/6-31G*. See DOI: 10.1002/open.201500192.

## Semi-empirical methods with dispersion

Old semi-empirical methods (PM3, AM1): **never use.**

PM6: best before PM7, but terrible for weak interactions without correction.

Dispersion-corrected variants (similar purpose to DFT-D but different form):
| Method | Notes |
|--------|-------|
| PM6-DH1 | Early dispersion + H-bond correction |
| PM6-DH2 | Improved DH1 |
| PM6-DH+ | Further improved — comparable to PM7 |
| **PM6-D3H4** | **Recommended** — best overall |
| PM7 | Latest; qualitative improvement over PM6 for weak interactions; similar to PM6-DH+ overall; other improvements marginal |
| AM1-D, OM3-D, DFTB-DH2 | Similar corrections for other methods |

**Caveat:** PM7 has minor issues for special weak interaction cases where PM6-DH+ succeeds (see sobereva.com/217 — PM7/PM6-DH+ failure in base pair optimization). Overall: PM6-D3H4 recommended; PM7 has larger errors.

## High-accuracy approximation via additivity

Using basis set and correlation additivity:
```
E(CCSD(T)/aug-cc-pVQZ) ≈ E(MP2/aug-cc-pVQZ) - E(MP2/aug-cc-pVDZ) + E(CCSD(T)/aug-cc-pVDZ)
```

(First two terms give basis set correction, added to small-basis CCSD(T) to approximate large-basis CCSD(T))

## Basis set truncation for efficiency

When using large basis sets, remove some basis functions to save time:

| Truncation | Impact |
|-----------|--------|
| aug-cc-pVDZ → remove H diffuse | Negligible for benzene dimer |
| For optimization: also remove C d-diffuse | Still OK — geometry less sensitive than energy |
| **maug-cc-pVDZ**: Only keep one layer of s,p diffuse on heavy atoms; remove all H diffuse | Good balance |
| **may/jun/jul-cc-pVnZ**: Systematic truncation of aug-cc-pVnZ diffuse | See sobereva.com/119 |

See Review in Computational Chemistry vol.26, Chapter 1 for time-saving techniques. See sobereva.com/119 for "month" basis sets.

## Minnesota functional grid sensitivity and PES issues

Criticisms of Minnesota functionals:
- Convergence difficulty
- Over-parameterization causes spurious PES minima
- Requires high integration grid precision (ultrafine) to eliminate

**Reality for M06-2X-D3:**
- D3 correction likely weakens spurious minima significantly
- Small PES wrinkles during optimization are surmountable
- `int=fine` is sufficient for geometry optimization
- `int=ultrafine` brings negligible accuracy improvement — only slightly larger than other functionals' improvement, far less than the worst case (M06HF)
- If absolute precision is needed and cost is acceptable: use `int=ultrafine`

## References

- sobereva.com/83 — DFT-D overview (this article)
- sobereva.com/210 — DFT-D usage details
- sobereva.com/214 — Large system weak interaction solutions
- sobereva.com/119 — Month basis sets and diffuse functions
- sobereva.com/217 — PM7/PM6-DH+ base pair optimization failure
- sobereva.com/344 — Non-built-in methods in Gaussian
- sobereva.com/685 — sobEDA energy decomposition
- sobereva.com/442 — Multiwfn force-field energy decomposition
- sobereva.com/490 — Multiwfn generating ORCA input
- sobereva.com/550 — Custom range-separated functionals
- sobereva.com/554 — Meaningful benchmarks
- WCMS, DOI: 10.1002/wcms.30 — Grimme DFT-D review
- PCCP, 13, 21121 (2011) — GMTKN30 benchmark
- POC, DOI: 10.1002/poc.1606 — Dispersion in DFT review (DiLabio)
- J. Mol. Model., 19, 5387 (2013) — M11 vs M06-2X test
- Chem. Phys. Lett., 268, 345 (1997) — VWN3 vs VWN5
- DOI: 10.1002/open.201500192 — PBEh-3c and DCP large system performance
- JCP, 132, 154104 (2010) — DFT-D3
