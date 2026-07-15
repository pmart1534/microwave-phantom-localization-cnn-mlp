# Render a .pptx to per-slide PNGs via PowerPoint COM.
# Usage: powershell -File render_pptx.ps1 <pptx> <outDir>
param([Parameter(Mandatory=$true)][string]$Pptx,[Parameter(Mandatory=$true)][string]$OutDir)
$Pptx = (Resolve-Path $Pptx).Path
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$OutDir = (Resolve-Path $OutDir).Path
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ppt.Presentations.Open($Pptx, $true, $false, $false)  # ReadOnly, Untitled, WithWindow=false
  $pres.Export($OutDir, "PNG", 1600, 900)
  $pres.Close()
  Write-Output ("exported {0} slides -> {1}" -f $pres.Slides.Count, $OutDir)
} finally {
  $ppt.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
