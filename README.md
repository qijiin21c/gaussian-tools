# gaussian-tools

A local Gaussian 16 workflow powered by Claude Code — write `.gjf` inputs, submit jobs, parse `.log` results, and troubleshoot calculations, all through Claude Code skills and agents.

## Quick Start

### 1. Prerequisites

- [Gaussian 16 for Windows](https://gaussian.com/gaussian16/) installed
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) installed
- Windows (PowerShell)

### 2. Configure

Edit `.claude/settings.json` to match your installation:

```json
{
  "env": {
    "GAUSSIAN_EXE": "C:\\Program Files\\G16W\\g16.exe",
    "GAUSS_EXEDIR": "C:\\Program Files\\G16W",
    "GAUSS_SCRDIR": "C:\\Users\\YourName\\scratch"
  }
}
```

### 3. Submit a Calculation

Place `.gjf` files in `jobs/` and submit:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-gaussian.ps1 jobs/h2o_opt_freq.gjf
```

Or ask Claude Code: *"帮我写一个水分子的优化+频率计算"* — the agent handles input preparation, submission, and result analysis automatically.

## Skills (26 Topics)

Each skill provides specialized knowledge and automated workflows for common Gaussian tasks:

### Structure & Input
| Skill | Description |
|-------|-------------|
| `cartesian-to-internal` | Convert Cartesian to Z-matrix/internal coordinates, preserve symmetry |
| `basis-set` | Basis set selection guide (Pople, Dunning, Ahlrichs, etc.) |
| `diffuse-functions` | When and how to add diffuse functions |
| `pseudopotential` | ECP/effective core potential selection and usage |
| `dft-functional` | DFT functional recommendations by task type |
| `dft-d-dispersion` | DFT-D3/D4 dispersion corrections |
| `switching-functionals` | Legitimate vs problematic functional switching patterns |

### Calculation Types
| Skill | Description |
|-------|-------------|
| `task-methods` | Method selection for different computational tasks |
| `excited-state` | Excited state calculations with TD-DFT |
| `tdfft-gaussian` | Advanced TD-DFT topics (solvent models, etc.) |
| `nmr-chemical-shift` | NMR chemical shift prediction (scaling, revTPSS protocol) |
| `pes-scan` | Potential energy surface scans (rigid & relaxed) |
| `solvation-free-energy` | Solvation free energy calculations |
| `ionic-liquid-solvation` | Ionic liquid solvation with SMD/GIL parameters |
| `bsse-correction` | Basis set superposition error (counterpoise) |
| `basis-extrapolation` | CBS extrapolation (cc-pVXZ → CBS limit) |
| `read-energy` | Read and extract energies from Gaussian output |

### Convergence & Troubleshooting
| Skill | Description |
|-------|-------------|
| `scf-convergence` | Fix SCF convergence failures (SCF=XQC, level shifts, etc.) |
| `opt-convergence` | Geometry optimization convergence issues |
| `small-imag-freq` | Handling small imaginary frequencies |
| `eliminate-imag-freq` | Eliminating imaginary frequencies (precision, special cases) |

### Special Systems
| Skill | Description |
|-------|-------------|
| `lanthanide-complexes` | Lanthanide/actinide complex calculations |
| `metal-surface-cluster` | Metal surface cluster models (e.g., benzene on Ag(111)) |
| `large-system-weak-interaction` | Large systems with weak/non-covalent interactions |

### Reaction Path
| Skill | Description |
|-------|-------------|
| `irc` | Intrinsic reaction coordinate (IRC) calculations |
| `restricted-opt` | Constrained/restricted geometry optimizations |

## Job Examples (`jobs/`)

### Small Molecules
- `h2o_opt_freq.gjf` — H₂O optimization + frequency
- `C2H2.gjf` — Acetylene
- `C6H6.gjf` — Benzene
- `ph3.gjf` — Phosphine

### F₂O₂ System
- `F2O2_opt.gjf` — F₂O₂ geometry optimization
- `F2O2_opt_b3lyp.gjf` — B3LYP level
- `F2O2_opt_m062x.gjf` — M06-2X level
- `F2O2_opt_ccsdt.gjf` — CCSD(T) level

### F + CClH₃ Reaction
- `F_CClH3_ts.gjf`, `F_CClH3_ts2.gjf` — Transition state searches
- `F_CClH3_ts_b3lyp.gjf`, `F_CClH3_ts_c3v.gjf` — TS with different methods/symmetry
- `F_CClH3_qst2.gjf` — QST2 TS search
- `F_CClH3_irc.gjf` — IRC following
- `F_CClH3_irc_restart.gjf` — IRC restart
- `F_CClH3_scan_fc.gjf` — Force constant scan
- `F_CClH3_opt_reactant.gjf`, `F_CClH3_opt_product.gjf` — Reactant/product optimization

### Other
- `F_CH4_scan.gjf` — F + CH₄ potential energy scan
- `Ferrocene-D5d.gjf` — Ferrocene D₅d symmetry
- `Naphthalene.gjf` — Naphthalene
- `test.gjf` — Test calculation

## Scripts

| File | Description |
|------|-------------|
| `run-gaussian.ps1` | Gaussian 16 job submission (handles GAUSS_EXEDIR, scratch) |
| `detect_symmetry.py` | Molecular symmetry detection using libmsym |

## Directory Layout

```
├── .claude/
│   ├── agents/gaussian-runner.md      # Agent definition
│   ├── settings.json                  # Env vars + permissions
│   └── skills/                        # 26 specialized calculation skills
│       ├── SKILL.md                   # Skill system pointer
│       ├── scf-convergence/
│       ├── opt-convergence/
│       ├── irc/
│       ├── basis-set/
│       ├── dft-functional/
│       ├── cartesian-to-internal/
│       ├── ... (20+ more)
│       └── switching-functionals/
├── CLAUDE.md                          # Project instructions
├── SKILLS-WORKFLOW.md                 # Skills workflow documentation
├── jobs/                              # .gjf inputs + .log/.out results
├── scripts/
│   ├── run-gaussian.ps1               # Gaussian submission script
│   └── detect_symmetry.py             # Symmetry detection
└── .gitignore                         # Ignore .chk, .rwf
```

## License

MIT
