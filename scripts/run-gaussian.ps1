param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile
)

$GaussianExe = $env:GAUSSIAN_EXE
if (-not $GaussianExe) {
    $GaussianExe = "C:\Program Files\G16W\g16.exe"
}

$GaussianDir = Split-Path $GaussianExe -Parent
$Scratch = $env:GAUSS_SCRDIR
if (-not $Scratch) {
    $Scratch = "C:\Users\QiJi\scratch"
}

New-Item -ItemType Directory -Force -Path $Scratch | Out-Null

if (-not (Test-Path $InputFile)) {
    Write-Error "Input not found: $InputFile"
    exit 1
}

$jobDir = Split-Path (Resolve-Path $InputFile) -Parent

Write-Host "Gaussian exe : $GaussianExe"
Write-Host "Scratch    : $Scratch"
Write-Host "Job dir    : $jobDir"
Write-Host "Input file : $InputFile"
Write-Host "---"

Push-Location $jobDir
try {
    $env:GAUSS_EXEDIR = $GaussianDir
    $env:GAUSS_SCRDIR = $Scratch
    & $GaussianExe (Split-Path $InputFile -Leaf)
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
