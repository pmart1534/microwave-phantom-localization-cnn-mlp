# Sim hardware x bandwidth grid: tuned GPU CNN, random 8-fold, center ~3.25 GHz.
# 5 antenna rows x 7 band cols, with SKIP-AFTER-BREAK (>20mm -> skip narrower).
$MAT = "C:\Program Files\MATLAB\R2025b\bin\matlab.exe"
$SCRIPT = "C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_SimReg.m"
$RES = "C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\results"
$env:SIM_LABEL = "grid"; $env:SIM_NFREQ = "256"; $env:SIM_KFOLD = "8"
$env:CNN_LOSO_EPOCHS = "60"; $env:SIM_CV = "kfold"
$BROKEN = 20.0

$rows = @(
  @{ant="all16";  name="16 S-params (full)"},
  @{ant="refl";   name="4 ant, refl only"},
  @{ant="pair13"; name="2 ant (1&3), full S"},
  @{ant="refl2";  name="2 ant (1&3), refl only"},
  @{ant="refl1";  name="1 ant (S11 only)"}
)
# band cols at center ~3.25 GHz (sim floor is 2 GHz; widest col = full 2-8)
$cols = @(
  @{w="full";    fmin="";      fmax=""},
  @{w="2GHz";    fmin="2.25";  fmax="4.25"},
  @{w="1GHz";    fmin="2.75";  fmax="3.75"},
  @{w="0.5GHz";  fmin="3";     fmax="3.5"},
  @{w="0.25GHz"; fmin="3.125"; fmax="3.375"},
  @{w="0.1GHz";  fmin="3.2";   fmax="3.3"},
  @{w="0.05GHz"; fmin="3.225"; fmax="3.275"}
)

foreach ($r in $rows) {
  $env:SIM_ANT = $r.ant
  $broke = $false
  foreach ($c in $cols) {
    if ($broke) { Write-Output ("SKIP  {0} / {1}  (after break)" -f $r.name, $c.w); continue }
    $band = if ($c.fmin -eq "") { "" } else { "_b$($c.fmin)-$($c.fmax)" }
    $antt = if ($r.ant -eq "all16") { "" } else { "_$($r.ant)" }
    $file = Join-Path $RES ("cnn_simreg_8fold_nf256_5mmgrid{0}{1}_grid.json" -f $band, $antt)
    if (Test-Path $file) {
      $err = (Get-Content $file -Raw | ConvertFrom-Json).lateral_medianMm
      Write-Output ("RESUME (exists) {0} / {1}: {2:N1} mm" -f $r.name, $c.w, $err)
      if ($err -gt $BROKEN) { $broke = $true }
      continue
    }
    if ($c.fmin -ne "") { $env:SIM_FMIN = $c.fmin; $env:SIM_FMAX = $c.fmax }
    else { Remove-Item Env:SIM_FMIN,Env:SIM_FMAX -ErrorAction SilentlyContinue }
    Write-Output ("===== {0} / {1} =====" -f $r.name, $c.w)
    & $MAT -batch "run('$SCRIPT')"
    $err = 999.0
    if (Test-Path $file) { $err = (Get-Content $file -Raw | ConvertFrom-Json).lateral_medianMm }
    Write-Output ("  -> {0:N1} mm  ({1})" -f $err, $(if ($err -gt $BROKEN) {"BROKEN"} else {"ok"}))
    if ($err -gt $BROKEN) { $broke = $true }
  }
}
Write-Output "SIM GRID DONE"
