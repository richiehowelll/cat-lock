param(
    [Parameter(Mandatory = $true)]
    [string] $ExePath,

    [string] $Label = "CatLock app",

    [int] $TimeoutSeconds = 30
)

$resolvedPath = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
$process = Start-Process `
    -FilePath $resolvedPath `
    -ArgumentList "--smoke-test" `
    -PassThru

if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    $process.Kill()
    throw "$Label smoke test timed out after $TimeoutSeconds seconds"
}

if ($process.ExitCode -ne 0) {
    throw "$Label smoke test failed with exit code $($process.ExitCode)"
}
