$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "streamlit.*run|streamlit.exe.*run" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Push-Location $projectRoot
try {
    & $python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
}
finally {
    Pop-Location
}
