# Gaussian calculation project

## Local Gaussian environment
- GAUSSIAN_EXE: C:\\Program\ Files\\G16W\\g16.exe
- GAUSS_SCRDIR: C:\\Users\\QiJi\\scratch
- Version: Gaussian 16W

## Directory layout
- `jobs/` — all .gjf, .log, and .chk files
- `scripts/` — submission scripts

## Rules
- Read/write calculation files only under `jobs/`
- Submit via `scripts/run-gaussian.ps1`
- Do not delete `*.chk` without explicit user approval

## Submit command
powershell -ExecutionPolicy Bypass -File scripts/run-gaussian.ps1 jobs/<name>.gjf