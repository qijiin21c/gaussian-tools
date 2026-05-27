# gaussian-tools

A local Gaussian 16 workflow powered by a Claude Code project agent. Write `.gjf` inputs, submit jobs, and parse `.log`/`.out` results — all automatically triggered by Claude Code.

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

Or simply ask Claude Code: *"帮我写一个水分子的优化+频率计算"* — the agent handles input preparation, submission, and result analysis automatically.

## What's Included

| File | Description |
|------|-------------|
| `.claude/agents/gaussian-runner.md` | Claude Code agent — auto-triggers for Gaussian workflows |
| `.claude/settings.json` | Environment variables and permissions |
| `scripts/run-gaussian.ps1` | Job submission script (handles GAUSS_EXEDIR, scratch) |
| `CLAUDE.md` | Project-level Claude Code instructions |

## Agent Capabilities

- **Input preparation** — write and validate `.gjf` files
- **Job submission** — submit via the run script with proper environment
- **Result parsing** — check Normal termination, SCF energy, frequencies, convergence
- **Error diagnosis** — read failed logs and suggest fixes

## Directory Layout

```
├── .claude/
│   ├── agents/gaussian-runner.md    # Agent definition
│   ├── settings.json                # Env vars + permissions
│   └── skills/SKILL.md              # Skill pointer
├── CLAUDE.md                        # Project instructions
├── jobs/                            # .gjf inputs, .log/.out outputs
├── scripts/
│   └── run-gaussian.ps1             # Submission script
└── .gitignore                       # Ignore .chk, .rwf, .out, .log
```

## License

MIT
