$ErrorActionPreference = "Stop"

$demoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $demoDir
try {
    New-Item -ItemType Directory -Force -Path "output" | Out-Null
    pandoc draft.md --citeproc --bibliography refs.bib --csl styles/american-medical-association.csl -o output/draft.docx
    Write-Host "Wrote output/draft.docx"
}
finally {
    Pop-Location
}

