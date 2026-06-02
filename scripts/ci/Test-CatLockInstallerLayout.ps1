param(
    [string] $InstallerPath = ".\build\CatLockSetup.exe",

    [string] $InstallDir = (Join-Path $env:TEMP "CatLockInstallerSmoke")
)

$installer = (Resolve-Path -LiteralPath $InstallerPath -ErrorAction Stop).Path

Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path (Join-Path $InstallDir "config") -Force | Out-Null
'{"hotkey":"ctrl+x","opacity":0.5,"notificationsEnabled":false}' |
    Set-Content -Path (Join-Path $InstallDir "config\config.json") -Encoding UTF8

& $installer /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="$InstallDir"
if ($LASTEXITCODE -ne 0) {
    throw "Installer smoke test failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path (Join-Path $InstallDir "CatLock.exe"))) {
    throw "Installed CatLock.exe was not found"
}
if (-not (Test-Path (Join-Path $InstallDir "_internal"))) {
    throw "Installed _internal directory was not found"
}
if (-not (Test-Path (Join-Path $InstallDir "config\config.json"))) {
    throw "Existing config was not preserved"
}

$smokeTestScript = Join-Path $PSScriptRoot "Invoke-CatLockSmokeTest.ps1"
& $smokeTestScript `
    -ExePath (Join-Path $InstallDir "CatLock.exe") `
    -Label "Installed app"
