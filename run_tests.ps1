# ============================================
# Cross-Platform PowerShell Test Runner Wrapper
# Project: Logo Maker
# ============================================
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

& "$PSScriptRoot/run_tests_windows.ps1" @RemainingArgs
exit $LASTEXITCODE

