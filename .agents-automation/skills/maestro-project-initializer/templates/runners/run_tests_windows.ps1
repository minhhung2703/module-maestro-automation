# ============================================
# Maestro Test Runner Script
# Project: Logo Maker
# ============================================

param(
    [string]$Folder = "",          # Run tests in a specific folder (e.g. "test-suite", "free-version")
    [string]$File = "",            # Run a specific test file name
    [string[]]$Exclude = @(),      # File names or patterns to exclude
    [string]$Device = "",          # Device ID/Serial khi có nhiều thiết bị
    [ValidateSet("Free", "Premium", "Auto")]
    [string]$Version = "Auto",     # App version: "Free", "Premium", or "Auto" (auto-detect from git branch)
    [switch]$UpdateBaseline,       # Cập nhật baseline template từ ảnh chụp runtime nếu được chỉ định
    [int]$ShardIndex = 0,          # Shard hiện tại (1-based index, 0 = không phân chia)
    [int]$ShardTotal = 0,          # Tổng số shards (0 = không phân chia)
    [string]$ReportJson = "",      # Đường dẫn file JSON xuất kết quả
    [switch]$InitFirstRun,         # Khởi tạo trạng thái lần đầu (Language, Onboarding, Edit Intro)
    [switch]$RecordVideo,          # Tự động quay video màn hình thiết bị (.mp4) trong khi chạy test
    [switch]$RecordOnlyOnFailure   # Chỉ giữ lại file video khi test case FAILED (tiết kiệm dung lượng đĩa)
)

$MaestroDir = "$PSScriptRoot/.maestro"
$Passed = 0
$Failed = 0
$Warned = 0
$Total = 0
$Results = @()

# Chuẩn hóa danh sách Exclude: Hỗ trợ cả mảng PowerShell và chuỗi phân tách bởi dấu phẩy từ Bash CLI (CI/CD)
$normalizedExclude = @()
foreach ($item in $Exclude) {
    if ($item) {
        $parts = $item -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        $normalizedExclude += $parts
    }
}
$Exclude = $normalizedExclude

# Chuẩn hóa danh sách File lọc: Hỗ trợ 1 tên hoặc danh sách phân tách bởi dấu phẩy
$filterFiles = @()
if ($File) {
    $filterFiles = $File -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

# Folders to exclude from auto-discovery
$ExcludeFolders = @("config", "screenshots")

# Ensure Maestro and Python are in PATH if available
$extraPaths = @(
    "$HOME/.maestro/bin"
)
if ($IsWindows -or ($env:OS -like "*Windows*")) {
    $extraPaths += @(
        "C:\Users\PC\AppData\Local\Programs\Python\Launcher",
        "C:\Users\PC\AppData\Local\Programs\Python\Python314",
        "C:\Users\PC\AppData\Local\Programs\Python\Python314\Scripts"
    )
}
$pathSep = [System.IO.Path]::PathSeparator
foreach ($p in $extraPaths) {
    if ((Test-Path $p) -and ($env:Path -split $pathSep -notcontains $p)) {
        $env:Path = "$p$pathSep" + $env:Path
    }
}

# Resolve Python command (Ưu tiên py trên Windows để tránh WindowsApps stub, ưu tiên python3 trên Linux/CI)
$PythonCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" }
             elseif (Test-Path "$env:LOCALAPPDATA/Programs/Python/Python313/python.exe") { "$env:LOCALAPPDATA/Programs/Python/Python313/python.exe" }
             elseif (Test-Path "C:/Users/PC/AppData/Local/Programs/Python/Python314/python.exe") { "C:/Users/PC/AppData/Local/Programs/Python/Python314/python.exe" }
             elseif ((Get-Command python3 -ErrorAction SilentlyContinue) -and ((Get-Command python3 -ErrorAction SilentlyContinue).Source -notlike "*WindowsApps*")) { "python3" }
             elseif ((Get-Command python -ErrorAction SilentlyContinue) -and ((Get-Command python -ErrorAction SilentlyContinue).Source -notlike "*WindowsApps*")) { "python" }
             elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" }
             else { "python" }

# Resolve App Version (Free / Premium)
$resolvedVersion = $Version
$gitBranch = ""
if ($Version -eq "Auto") {
    try {
        $gitBranch = (& git branch --show-current 2>$null).Trim()
    } catch {
        $gitBranch = ""
    }
    # Fallback cho GitHub Actions khi checkout ở trạng thái detached HEAD (PR / Tag)
    if (-not $gitBranch) {
        if ($env:GITHUB_HEAD_REF) {
            $gitBranch = $env:GITHUB_HEAD_REF.Trim()
        } elseif ($env:GITHUB_REF_NAME) {
            $gitBranch = $env:GITHUB_REF_NAME.Trim()
        }
    }
    if ($gitBranch -match "premium") {
        $resolvedVersion = "Premium"
    } else {
        $resolvedVersion = "Free"
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  MAESTRO TEST RUNNER - Logo Maker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
$versionColor = if ($resolvedVersion -eq "Premium") { "Magenta" } else { "Yellow" }
Write-Host "  App Version    : $resolvedVersion" -ForegroundColor $versionColor
if ($Version -eq "Auto" -and $gitBranch -ne "") {
    Write-Host "  (Auto-detected from git branch: $gitBranch)" -ForegroundColor DarkGray
}
if ($ShardTotal -gt 0 -and $ShardIndex -gt 0) {
    Write-Host "  Shard          : $ShardIndex of $ShardTotal" -ForegroundColor Cyan
}
if ($UpdateBaseline) {
    Write-Host "  Mode           : UPDATE BASELINE (Screenshots -> Assets)" -ForegroundColor Green
}
if ($RecordVideo) {
    $videoModeStr = if ($RecordOnlyOnFailure) { "ENABLED (Only save on FAILURE)" } else { "ENABLED (All tests -> reports/videos/)" }
    Write-Host "  Video Record   : $videoModeStr" -ForegroundColor Magenta
}
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Maestro CLI
if (-not (Get-Command maestro -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Maestro CLI not found! Please ensure Maestro is installed and added to PATH." -ForegroundColor Red
    exit 1
}

# Check device connection
$connectedDevices = @()
$devices = adb devices 2>&1
foreach ($line in $devices) {
    if ($line -match "^([A-Za-z0-9_\-\.]+)\s+device$") {
        $connectedDevices += $matches[1]
    }
}
if ($connectedDevices.Count -eq 0) {
    Write-Host "[ERROR] No Android device connected! Please connect a device first." -ForegroundColor Red
    exit 1
}

# Xử lý chọn thiết bị:
if ($Device -ne "") {
    if ($connectedDevices -notcontains $Device) {
        Write-Host "[ERROR] Device '$Device' not found in connected devices: $($connectedDevices -join ', ')" -ForegroundColor Red
        exit 1
    }
    $env:ANDROID_SERIAL = $Device
} elseif ($connectedDevices.Count -eq 1) {
    # Trường hợp 1 máy: Tự động dùng máy đó mà không cần tham số -Device
    $env:ANDROID_SERIAL = $connectedDevices[0]
} else {
    # Trường hợp nhiều máy nhưng không truyền -Device:
    $env:ANDROID_SERIAL = if ($connectedDevices -contains "R3CNA099XKL") { "R3CNA099XKL" } else { $connectedDevices[0] }
    Write-Host "[NOTE] Multiple devices detected ($($connectedDevices -join ', ')). Defaulting to: $env:ANDROID_SERIAL (Use -Device '<id>' to specify)" -ForegroundColor Yellow
}
Write-Host "[OK] Target Device: $env:ANDROID_SERIAL" -ForegroundColor Green

# Ensure test media is synced to device gallery
$defaultMedia = "$PSScriptRoot/assets/image_Default.png"
if (Test-Path $defaultMedia) {
    adb shell "rm -rf /sdcard/Pictures/LogoMaker/*" 2>&1 | Out-Null
    adb push $defaultMedia /sdcard/Pictures/image_Default.png 2>&1 | Out-Null
    adb shell "touch /sdcard/Pictures/image_Default.png" 2>&1 | Out-Null
    adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Pictures/image_Default.png 2>&1 | Out-Null
}

# Lock Portrait orientation and dismiss any leftover system Share sheet before suite runs
adb shell "settings put system accelerometer_rotation 0" 2>&1 | Out-Null
adb shell "settings put system user_rotation 0" 2>&1 | Out-Null
adb shell "am force-stop com.android.intentresolver" 2>&1 | Out-Null

# Ensure Template Service (Python OpenCV daemon) is running on port 8765
$expectedTemplateServiceVersion = "2.1-multi-device-strict"
$global:TemplateServiceProc = $null
$templateServiceRunning = $false
$isManagedByParallel = ($env:TEMPLATE_SERVICE_MANAGED -eq "1")

function Stop-StaleTemplateService {
    param($HealthInfo)
    if ($HealthInfo -and $HealthInfo.pid) {
        Stop-Process -Id $HealthInfo.pid -Force -ErrorAction SilentlyContinue
    }
    if ($IsWindows -or ($env:OS -like "*Windows*")) {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -like "*template_service.py*" } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    } else {
        & pkill -f "template_service.py" 2>$null | Out-Null
    }
}

$healthCheck = $null
try {
    $healthCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
} catch {}

if ($isManagedByParallel -and $healthCheck -and $healthCheck.status -eq "ok" -and $healthCheck.version -eq $expectedTemplateServiceVersion) {
    $templateServiceRunning = $true
} elseif (-not $isManagedByParallel) {
    # Ở chế độ chạy đơn, luôn dọn daemon cũ nếu còn treo từ phiên trước để tránh dùng nhầm code/ANDROID_SERIAL cũ
    if ($healthCheck -or ($IsWindows -or ($env:OS -like "*Windows*"))) {
        $staleProcs = if ($IsWindows -or ($env:OS -like "*Windows*")) {
            Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*template_service.py*" }
        } else { $null }
        if ($healthCheck -or $staleProcs) {
            Write-Host "[INFO] Restarting existing Template Service daemon on port 8765 for clean state..." -ForegroundColor Yellow
            Stop-StaleTemplateService -HealthInfo $healthCheck
            Start-Sleep -Milliseconds 500
        }
    }
}

if (-not $templateServiceRunning) {
    Write-Host "[INFO] Starting Template Service daemon on port 8765..." -ForegroundColor Cyan
    $reportsLogDir = "$PSScriptRoot/reports"
    if (-not (Test-Path $reportsLogDir)) {
        New-Item -ItemType Directory -Path $reportsLogDir -Force | Out-Null
    }
    if ($IsWindows -or ($env:OS -like "*Windows*")) {
        $global:TemplateServiceProc = Start-Process -FilePath $PythonCmd -ArgumentList "-X utf8 scripts/template_service.py" -WorkingDirectory $PSScriptRoot -RedirectStandardOutput "$reportsLogDir/template_service.log" -RedirectStandardError "$reportsLogDir/template_service_err.log" -WindowStyle Hidden -PassThru
    } else {
        $global:TemplateServiceProc = Start-Process -FilePath $PythonCmd -ArgumentList "-X utf8 scripts/template_service.py" -WorkingDirectory $PSScriptRoot -PassThru
    }
    for ($waitIdx = 0; $waitIdx -lt 20; $waitIdx++) {
        Start-Sleep -Milliseconds 250
        try {
            $readyCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($readyCheck.status -eq "ok") { break }
        } catch {}
    }
}

if ($InitFirstRun) {
    Write-Host "[INFO] Running First-Run Bootstrap Setup Flow (.maestro/config/Init_First_Run_State.yaml)..." -ForegroundColor Cyan
    maestro --device $env:ANDROID_SERIAL test -e APP_VERSION=$resolvedVersion -e DEVICE_SERIAL=$env:ANDROID_SERIAL "$MaestroDir/config/Init_First_Run_State.yaml"
}
Write-Host ""

# Helper function: Trích xuất step bị lỗi và message lỗi từ Maestro output
function Extract-MaestroError {
    param([string]$Output)

    $failedStep = $null
    $errorMessage = $null

    if (-not $Output) { 
        return @{ FailedStep = "Unknown"; ErrorMessage = "No output from Maestro" } 
    }

    $lines = $Output -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

    # Tìm các dòng kết thúc bằng '... FAILED' hoặc 'FAILED'
    $failedIndices = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "\.\.\.\s*FAILED$|\bFAILED$") {
            $failedIndices += $i
        }
    }

    if ($failedIndices.Count -gt 0) {
        # Ưu tiên lấy dòng lá đầu tiên không phải là "Run flow when" hay "Run .*\.ya?ml"
        $leafIndex = -1
        foreach ($idx in $failedIndices) {
            $lineText = $lines[$idx]
            if ($lineText -notmatch "^Run\s+(flow\s+when|.*\.ya?ml)") {
                $leafIndex = $idx
                break
            }
        }
        if ($leafIndex -eq -1) {
            $leafIndex = $failedIndices[0]
        }

        $stepLine = $lines[$leafIndex]
        $failedStep = ($stepLine -replace "\s*\.\.\.\s*FAILED$", "") -replace "\s*FAILED$", ""

        # Tìm error message: thường nằm ngay sau chuỗi các dòng FAILED
        $lastFailedIdx = $failedIndices[-1]
        for ($j = $lastFailedIdx + 1; $j -lt [math]::Min($lines.Count, $lastFailedIdx + 8); $j++) {
            $candidate = $lines[$j]
            if ($candidate -match "^(Assertion is false|Element not found|CommandFailed|Exception|Error|Failed):?" -or 
                ($candidate -notmatch "^==== Debug output" -and $candidate -notmatch "^Result:" -and $candidate -notmatch "^Possible causes" -and $candidate -notmatch "^- ")) {
                $errorMessage = $candidate
                break
            }
        }
    }

    if (-not $failedStep) {
        foreach ($l in $lines) {
            if ($l -match "(Invalid Command:.*|Syntax error:.*|Error parsing:.*)") {
                $failedStep = "Maestro Syntax Error"
                $errorMessage = $matches[1]
                break
            }
            if ($l -match "(Assertion is false:.*|Element not found:.*|CommandFailed:.*)") {
                $errorMessage = $matches[1]
                $failedStep = "Maestro Command Failed"
                break
            }
        }
    }

    return @{
        FailedStep = if ($failedStep) { $failedStep } else { "Maestro Flow Failed" }
        ErrorMessage = if ($errorMessage) { $errorMessage } else { "Step execution failed in Maestro" }
    }
}

# Helper function: Phân tích kết quả so sánh hình ảnh từ compare.py
function Parse-CompareResult {
    param(
        [string]$Type,
        [hashtable]$Config,
        [string]$Output,
        [int]$ExitCode
    )
    
    $matchPct = $null
    $canvasZone = $null
    $toolZone = $null
    $summary = $null
    $status = if ($ExitCode -eq 0) { "PASSED" } else { "FAILED" }

    if ($Output -match "MATCH PERCENTAGE(?:\s*\(Overall\))?:\s*([0-9\.]+)%") {
        $matchPct = [double]$matches[1]
    }
    if ($Output -match "\[Zone Canvas\]\s*:\s*([0-9\.]+)%") {
        $canvasZone = [double]$matches[1]
    }
    if ($Output -match "\[Zone Tool\]\s*:\s*([0-9\.]+)%") {
        $toolZone = [double]$matches[1]
    }
    if ($Output -match "(PASSED:.*|FAILED:.*|Error:.*)") {
        $summary = $matches[1].Trim()
    } else {
        $summary = if ($status -eq "PASSED") { "Match" } else { "Image mismatch or comparison error" }
    }

    if ($Type -eq "Dual") {
        return [ordered]@{
            Type            = "Dual"
            Screenshot1     = $Config.Screenshot1
            CropId1         = $Config.CropId1
            Screenshot2     = $Config.Screenshot2
            CropId2         = $Config.CropId2
            Status          = $status
            MatchPercentage = $matchPct
            Summary         = $summary
        }
    } else {
        return [ordered]@{
            Type            = "Template"
            Template        = $Config.Template
            Screenshot      = $Config.Screenshot
            CropId          = $Config.CropId
            Status          = $status
            MatchPercentage = $matchPct
            CanvasZone      = $canvasZone
            ToolZone        = $toolZone
            Summary         = $summary
        }
    }
}

# Discover folders to run
$foldersToRun = @()
if ($Folder -ne "") {
    # Run a specific folder
    $targetDir = "$MaestroDir/$Folder"
    if (-not (Test-Path $targetDir)) {
        Write-Host "[ERROR] Folder not found: $targetDir" -ForegroundColor Red
        exit 1
    }
    $foldersToRun += Get-Item $targetDir
} else {
    # Run all folders (excluding config, screenshots, etc.)
    $foldersToRun = Get-ChildItem -Path $MaestroDir -Directory | Where-Object { $_.Name -notin $ExcludeFolders }
}

# Function to run a single test file and handle results
function Run-TestFile {
    param(
        [System.IO.FileInfo]$TestFile,
        [string]$FolderName,
        [string]$ScreenName
    )

    $testVersion = $resolvedVersion
    if ($FolderName -eq "free-version") {
        $testVersion = "Free"
    } elseif ($FolderName -eq "premium-version") {
        $testVersion = "Premium"
    }

    $script:Total++
    $testName = $TestFile.BaseName
    Write-Host ""
    Write-Host "    [$($script:Total)] Running: $testName" -ForegroundColor White
    Write-Host "        File: $($TestFile.FullName)" -ForegroundColor DarkGray
    $modeColor = if ($testVersion -eq "Premium") { "Magenta" } else { "Yellow" }
    Write-Host "        Version: $testVersion" -ForegroundColor $modeColor

    # Clean up stale session lock file if present to prevent Windows file lock conflicts
    $sessionFile = "$HOME/.maestro/sessions"
    if (Test-Path $sessionFile) {
        Remove-Item $sessionFile -Force -ErrorAction SilentlyContinue
    }

    # Khởi tạo quay màn hình video nếu bật cờ -RecordVideo
    $videoProc = $null
    $deviceVideoName = "rec_${testName}_$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()).mp4"
    $deviceVideoPath = "/sdcard/$deviceVideoName"
    if ($RecordVideo) {
        Write-Host "        [VIDEO] Starting screen recording on device..." -ForegroundColor Cyan
        adb -s $env:ANDROID_SERIAL shell "rm -f /sdcard/rec_*.mp4" 2>&1 | Out-Null
        $videoProc = Start-Process -FilePath "adb" `
            -ArgumentList "-s $env:ANDROID_SERIAL shell screenrecord --bit-rate 4000000 --time-limit 180 $deviceVideoPath" `
            -WindowStyle Hidden -PassThru
        Start-Sleep -Milliseconds 600
    }

    $startTime = Get-Date
    $imageComparisons = [System.Collections.Generic.List[object]]::new()
    $failedStep = $null
    $errorMessage = $null
    $output = maestro --device $env:ANDROID_SERIAL test -e APP_VERSION=$testVersion -e DEVICE_SERIAL=$env:ANDROID_SERIAL $TestFile.FullName 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    $duration = ((Get-Date) - $startTime).TotalSeconds

    if ($exitCode -eq 0) {
        # ==============================================================================
        # 1. BẢNG ÁNH XẠ SO SÁNH HÌNH ẢNH DÀNH RIÊNG CHO PHIÊN BẢN FREE
        #    (Chỉ sử dụng khi chạy bản Free: Template trỏ vào assets/Free/)
        # ==============================================================================
        $imageCompareMap_Free = [ordered]@{
            # Onboarding Screen
            "*TC_05-Verify_Display_Image_Preview*" = @{ Template = "assets/Free/onboarding_1.png"; CropId = $null; Screenshot = "screenshots/onboarding_step1_preview" }
            "*TC_16-Verify_Displayed_Onboarding3*" = @{ Template = "assets/Free/Onboarding_Step3.png"; CropId = "img"; Screenshot = "screenshots/onboarding3_compare" }
            "*TC_21-Verify_Click_On_Get_Started_Button*" = @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare" }
            "*TC_24-Verify_IAP_Screen_Is_Displayed_After_Killing_App_On_Onboarding*" = @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare" }
            
            # IAP Screen
            "*TC_02-Verify_Logo_Background_Template_Displayed*" = @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare" }
            "*TC_02.2-Verify_Logo_Background_Template_Displayed*" = @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare" }
            "*TC_04-Verify_Displayed_Comparing_Table*" = @{ Template = "assets/Free/IAP_Screen.png"; CropId = "rvAllFeatures"; Screenshot = "screenshots/comparing_table" }
        
            # test-suite
            "*TC_00_Get_Payment_Flow*" = @(
                #  Splash Screen
                # @{ Template = "assets/Free/Splash_Screen.png"; CropId = $null; Screenshot = "screenshots/Splash_Screen"}
                # @{ Template = "assets/Free/Splash_Screen.png"; CropId = $null; Screenshot = "screenshots/Splash_Screen_2"}

                 # IAP Screen
                @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare"}
                @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare_2"} 
                @{ Template = "assets/Free/IAP_Screen.png"; CropId = $null; Screenshot = "screenshots/IAP_compare_3"} 
                
                # Onboarding Screen
                @{ Template = "assets/Free/onboarding_1.png"; CropId = $null; Screenshot = "screenshots/Onboarding_Screen_1"},
                @{ Template = "assets/Free/onboarding_2.png"; CropId = $null; Screenshot = "screenshots/Onboarding_Screen_2"},
                @{ Template = "assets/Free/onboarding_3.png"; CropId = $null; Screenshot = "screenshots/Onboarding_Screen_3"},
               
                # Home Screen
                @{ Template = "assets/Free/Home_Screen.png"; CropId = $null; Screenshot = "screenshots/Home_Screen"}
            )
            
            "*TC_02_Test_Background_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/backgroundTool_on_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/backgroundTool_on_Edit_Screen" },
                @{ Template = "assets/Free/Custom_Gradient.png"; CropId = $null; Screenshot = "screenshots/Custom_Gradient" },
                @{ Template = "assets/Free/background_Select_Screen.png"; CropId = $null; Screenshot = "screenshots/background_Select_Screen" },
                @{ Template = "assets/Free/texture_Select_Screen.png"; CropId = $null; Screenshot = "screenshots/texture_Select_Screen" },
                @{ Template = "assets/Free/Add_Image_Background_on_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Add_Image_Background_on_Edit_Screen" },
                @{ Template = "assets/Free/Verify_Displayed_Save_Options_Popup.png"; CropId = $null; Screenshot = "screenshots/Verify_Displayed_Save_Options_Popup" }
            )

            "*TC_03_Test_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Displayed_Art_Tool_On_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Displayed_Art_Tool_On_Edit_Screen" },
                @{ Template = "assets/Free/Verify_Display_Dialog_Layer_On_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Display_Dialog_Layer_On_Edit_Screen" },
                @{ Template = "assets/Free/Verify_Move_Layer_To_Down_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer" },
                @{ Template = "assets/Free/Verify_Move_Layer_To_Top_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer" },
                @{ Template = "assets/Free/Verify_duplicate_Layer_To_Top_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer" },
                @{ Template = "assets/Free/Closing_Layer_Dialog.png"; CropId = $null; Screenshot = "screenshots/Closing_Layer_Dialog" },
                @{ Template = "assets/Free/Verify_Move_Layer_To_Top_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer_2" },
                @{ Template = "assets/Free/Verify_Move_Layer_To_Down_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer_2" },
                @{ Template = "assets/Free/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2" },
                @{ Template = "assets/Free/Verify_Move_Layer_By_Using_pointer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_By_Using_pointer" },
                @{ Template = "assets/Free/Verify_Undo_On_The_Template_Detail_Successfully.png"; CropId = $null; Screenshot = "screenshots/Verify_Undo_On_The_Template_Detail_Successfully" },
                @{ Template = "assets/Free/Verify_Redo_On_The_Template_Detail_Successfully.png"; CropId = $null; Screenshot = "screenshots/Verify_Redo_On_The_Template_Detail_Successfully" },
                @{ Template = "assets/Free/Rate_App_Popup_On_Preview.png"; CropId = $null; Screenshot = "screenshots/Rate_App_Popup_On_Preview" },
                @{ Template = "assets/Free/Verify_Navigated_to_Style_Magic_AI_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Navigated_to_Style_Magic_AI_Screen" },
                @{ Template = "assets/Free/Verify_Displayed_Last_Image_On_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Displayed_Last_Image_On_Mockup_Preview_Screen" },
                @{ Template = "assets/Free/Verify_Navigated_To_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Navigated_To_Mockup_Preview_Screen" }
            )

            "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Color_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/Color_SubTab_Default" },
                @{ Template = "assets/Free/Color_Opacity_Changed.png"; CropId = $null; Screenshot = "screenshots/Color_Opacity_Changed" },
                @{ Template = "assets/Free/Color_Solid_Red_Applied.png"; CropId = $null; Screenshot = "screenshots/Color_Solid_Red_Applied" },
                @{ Template = "assets/Free/Color_Palette_Dialog.png"; CropId = $null; Screenshot = "screenshots/Color_Palette_Dialog" },
                @{ Template = "assets/Free/Color_Custom_Gradient_Screen.png"; CropId = $null; Screenshot = "screenshots/Color_Custom_Gradient_Screen" },
                @{ Template = "assets/Free/Color_Texture_Scale_Displayed.png"; CropId = $null; Screenshot = "screenshots/Color_Texture_Scale_Displayed" },
                @{ Template = "assets/Free/Color_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Color_Tool_Result" }
            )

            "*TC_05_Test_Sub_Outline_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Outline_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/Outline_SubTab_Default" },
                @{ Template = "assets/Free/Outline_Width_Changed.png"; CropId = $null; Screenshot = "screenshots/Outline_Width_Changed" },
                @{ Template = "assets/Free/Outline_Solid_Red_Applied.png"; CropId = $null; Screenshot = "screenshots/Outline_Solid_Red_Applied" },
                @{ Template = "assets/Free/Outline_Eyedropper_Screen.png"; CropId = $null; Screenshot = "screenshots/Outline_Eyedropper_Screen" },
                @{ Template = "assets/Free/Outline_Palette_Dialog.png"; CropId = $null; Screenshot = "screenshots/Outline_Palette_Dialog" },
                @{ Template = "assets/Free/Outline_Custom_Hex_View.png"; CropId = $null; Screenshot = "screenshots/Outline_Custom_Hex_View" },
                @{ Template = "assets/Free/Outline_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Outline_Tool_Result" }
            )

            "*TC_06_Test_Sub_3D_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/3D_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/3D_SubTab_Default" },
                @{ Template = "assets/Free/3D_X_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_X_Rotation_Applied" },
                @{ Template = "assets/Free/3D_Y_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_Y_Rotation_Applied" },
                @{ Template = "assets/Free/3D_Z_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_Z_Rotation_Applied" },
                @{ Template = "assets/Free/3D_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/3D_Tool_Result" }
            )

            "*TC_07_Test_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Input_Text_Screen_Default.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Screen_Default" },
                @{ Template = "assets/Free/Input_Text_Empty_Validation.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Empty_Validation" },
                @{ Template = "assets/Free/Input_Text_Typing_Result.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Typing_Result" },
                @{ Template = "assets/Free/Text_Tool_Applied_Result.png"; CropId = $null; Screenshot = "screenshots/Text_Tool_Applied_Result" },
                @{ Template = "assets/Free/Input_Text_Edit_Existing.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Edit_Existing" },
                @{ Template = "assets/Free/Text_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Text_Tool_Final_Result" }
            )

            "*TC_08_Test_Home_Screen*" = @(
                @{ Template = "assets/Free/Home_Screen.png"; CropId = $null; Screenshot = "screenshots/Home_Screen" }
            )

            "*TC_08_Test_Sub_Control_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Control_SubTab_Opened_After_Text.png"; CropId = $null; Screenshot = "screenshots/Control_SubTab_Opened_After_Text" },
                @{ Template = "assets/Free/Control_Move_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Move_Result" },
                @{ Template = "assets/Free/Control_Align_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Align_Result" },
                @{ Template = "assets/Free/Control_Duplicate_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Duplicate_Result" },
                @{ Template = "assets/Free/Control_Final_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Final_Result" },
                @{ Template = "assets/Free/Control_Text_Frame_Moved.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Frame_Moved" },
                @{ Template = "assets/Free/Control_Text_Flipped.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Flipped" },
                @{ Template = "assets/Free/Control_Text_Zoomed.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Zoomed" },
                @{ Template = "assets/Free/Control_Text_Rotated.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Rotated" }
            )

            "*TC_09_Test_Sub_Tabs_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Free/Text_SubTab_Fonts_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Fonts_Applied" },
                @{ Template = "assets/Free/Text_SubTab_Color_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Color_Applied" },
                @{ Template = "assets/Free/Text_SubTab_Shadow_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Shadow_Applied" },
                @{ Template = "assets/Free/Text_SubTab_Background_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Background_Applied" },
                @{ Template = "assets/Free/Text_SubTab_Outline_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Outline_Applied" },
                @{ Template = "assets/Free/Text_SubTab_Curve_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Curve_Applied" },
                @{ Template = "assets/Free/Text_SubTab_3D_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_3D_Applied" },
                @{ Template = "assets/Free/Text_SubTabs_All_Applied_Result.png"; CropId = $null; Screenshot = "screenshots/Text_SubTabs_All_Applied_Result" }
            )

            "*TC_11_Test_Mockup_Preview_Screen*" = @(
                @{ Template = "assets/Free/TC_11_Verify_Navigated_To_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/TC_11_Verify_Navigated_To_Mockup_Preview_Screen" },
                @{ Template = "assets/Free/TC_11_Verify_Displayed_Last_Image_On_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/TC_11_Verify_Displayed_Last_Image_On_Mockup_Preview_Screen" }
            )
        }

        # ==============================================================================
        # 2. BẢNG ÁNH XẠ SO SÁNH HÌNH ẢNH DÀNH RIÊNG CHO PHIÊN BẢN PREMIUM
        #    (Chỉ sử dụng khi chạy bản Premium: Template trỏ vào assets/Premium/)
        # ==============================================================================
        $imageCompareMap_Premium = [ordered]@{
            "*TC_02_Test_Background_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/backgroundTool_on_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/backgroundTool_on_Edit_Screen" },
                @{ Template = "assets/Premium/Custom_Gradient.png"; CropId = $null; Screenshot = "screenshots/Custom_Gradient" },
                @{ Template = "assets/Premium/background_Select_Screen.png"; CropId = $null; Screenshot = "screenshots/background_Select_Screen" },
                @{ Template = "assets/Premium/texture_Select_Screen.png"; CropId = $null; Screenshot = "screenshots/texture_Select_Screen" },
                @{ Template = "assets/Premium/Add_Image_Background_on_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Add_Image_Background_on_Edit_Screen" },
                @{ Template = "assets/Premium/Verify_Displayed_Save_Options_Popup.png"; CropId = $null; Screenshot = "screenshots/Verify_Displayed_Save_Options_Popup" }
            )

            "*TC_03_Test_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Displayed_Art_Tool_On_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Displayed_Art_Tool_On_Edit_Screen" },
                @{ Template = "assets/Premium/Verify_Display_Dialog_Layer_On_Edit_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Display_Dialog_Layer_On_Edit_Screen" },
                @{ Template = "assets/Premium/Verify_Move_Layer_To_Down_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer" },
                @{ Template = "assets/Premium/Verify_Move_Layer_To_Top_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer" },
                @{ Template = "assets/Premium/Verify_duplicate_Layer_To_Top_On_Dialog_Layer.png"; CropId = $null; Screenshot = "screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer" },
                @{ Template = "assets/Premium/Closing_Layer_Dialog.png"; CropId = $null; Screenshot = "screenshots/Closing_Layer_Dialog" },
                @{ Template = "assets/Premium/Verify_Move_Layer_To_Top_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer_2" },
                @{ Template = "assets/Premium/Verify_Move_Layer_To_Down_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer_2" },
                @{ Template = "assets/Premium/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2.png"; CropId = $null; Screenshot = "screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2" },
                @{ Template = "assets/Premium/Verify_Move_Layer_By_Using_pointer.png"; CropId = $null; Screenshot = "screenshots/Verify_Move_Layer_By_Using_pointer" },
                @{ Template = "assets/Premium/Verify_Undo_On_The_Template_Detail_Successfully.png"; CropId = $null; Screenshot = "screenshots/Verify_Undo_On_The_Template_Detail_Successfully" },
                @{ Template = "assets/Premium/Verify_Redo_On_The_Template_Detail_Successfully.png"; CropId = $null; Screenshot = "screenshots/Verify_Redo_On_The_Template_Detail_Successfully" },
                @{ Template = "assets/Premium/Rate_App_Popup_On_Preview.png"; CropId = $null; Screenshot = "screenshots/Rate_App_Popup_On_Preview" },
                @{ Template = "assets/Premium/Verify_Navigated_to_Style_Magic_AI_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Navigated_to_Style_Magic_AI_Screen" },
                @{ Template = "assets/Premium/Verify_Displayed_Last_Image_On_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Displayed_Last_Image_On_Mockup_Preview_Screen" },
                @{ Template = "assets/Premium/Verify_Navigated_To_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/Verify_Navigated_To_Mockup_Preview_Screen" }
            )

            "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Color_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/Color_SubTab_Default" },
                @{ Template = "assets/Premium/Color_Opacity_Changed.png"; CropId = $null; Screenshot = "screenshots/Color_Opacity_Changed" },
                @{ Template = "assets/Premium/Color_Solid_Red_Applied.png"; CropId = $null; Screenshot = "screenshots/Color_Solid_Red_Applied" },
                @{ Template = "assets/Premium/Color_Palette_Dialog.png"; CropId = $null; Screenshot = "screenshots/Color_Palette_Dialog" },
                @{ Template = "assets/Premium/Color_Custom_Gradient_Screen.png"; CropId = $null; Screenshot = "screenshots/Color_Custom_Gradient_Screen" },
                @{ Template = "assets/Premium/Color_Texture_Scale_Displayed.png"; CropId = $null; Screenshot = "screenshots/Color_Texture_Scale_Displayed" },
                @{ Template = "assets/Premium/Color_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Color_Tool_Result" }
            )

            "*TC_05_Test_Sub_Outline_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Outline_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/Outline_SubTab_Default" },
                @{ Template = "assets/Premium/Outline_Width_Changed.png"; CropId = $null; Screenshot = "screenshots/Outline_Width_Changed" },
                @{ Template = "assets/Premium/Outline_Solid_Red_Applied.png"; CropId = $null; Screenshot = "screenshots/Outline_Solid_Red_Applied" },
                @{ Template = "assets/Premium/Outline_Eyedropper_Screen.png"; CropId = $null; Screenshot = "screenshots/Outline_Eyedropper_Screen" },
                @{ Template = "assets/Premium/Outline_Palette_Dialog.png"; CropId = $null; Screenshot = "screenshots/Outline_Palette_Dialog" },
                @{ Template = "assets/Premium/Outline_Custom_Hex_View.png"; CropId = $null; Screenshot = "screenshots/Outline_Custom_Hex_View" },
                @{ Template = "assets/Premium/Outline_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Outline_Tool_Result" }
            )

            "*TC_06_Test_Sub_3D_Art_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/3D_SubTab_Default.png"; CropId = $null; Screenshot = "screenshots/3D_SubTab_Default" },
                @{ Template = "assets/Premium/3D_X_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_X_Rotation_Applied" },
                @{ Template = "assets/Premium/3D_Y_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_Y_Rotation_Applied" },
                @{ Template = "assets/Premium/3D_Z_Rotation_Applied.png"; CropId = $null; Screenshot = "screenshots/3D_Z_Rotation_Applied" },
                @{ Template = "assets/Premium/3D_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/3D_Tool_Result" }
            )

            "*TC_07_Test_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Input_Text_Screen_Default.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Screen_Default" },
                @{ Template = "assets/Premium/Input_Text_Empty_Validation.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Empty_Validation" },
                @{ Template = "assets/Premium/Input_Text_Typing_Result.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Typing_Result" },
                @{ Template = "assets/Premium/Text_Tool_Applied_Result.png"; CropId = $null; Screenshot = "screenshots/Text_Tool_Applied_Result" },
                @{ Template = "assets/Premium/Input_Text_Edit_Existing.png"; CropId = $null; Screenshot = "screenshots/Input_Text_Edit_Existing" },
                @{ Template = "assets/Premium/Text_Tool_Baseline.png"; CropId = $null; Screenshot = "screenshots/Text_Tool_Final_Result" }
            )

            "*TC_08_Test_Home_Screen*" = @(
                @{ Template = "assets/Premium/Home_Screen.png"; CropId = $null; Screenshot = "screenshots/Home_Screen" }
            )

            "*TC_08_Test_Sub_Control_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Control_SubTab_Opened_After_Text.png"; CropId = $null; Screenshot = "screenshots/Control_SubTab_Opened_After_Text" },
                @{ Template = "assets/Premium/Control_Move_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Move_Result" },
                @{ Template = "assets/Premium/Control_Align_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Align_Result" },
                @{ Template = "assets/Premium/Control_Duplicate_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Duplicate_Result" },
                @{ Template = "assets/Premium/Control_Final_Result.png"; CropId = $null; Screenshot = "screenshots/Control_Final_Result" },
                @{ Template = "assets/Premium/Control_Text_Frame_Moved.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Frame_Moved" },
                @{ Template = "assets/Premium/Control_Text_Flipped.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Flipped" },
                @{ Template = "assets/Premium/Control_Text_Zoomed.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Zoomed" },
                @{ Template = "assets/Premium/Control_Text_Rotated.png"; CropId = $null; Screenshot = "screenshots/Control_Text_Rotated" }
            )

            "*TC_09_Test_Sub_Tabs_Text_Tool_On_Edit_Screen*" = @(
                @{ Template = "assets/Premium/Text_SubTab_Fonts_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Fonts_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_Color_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Color_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_Shadow_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Shadow_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_Background_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Background_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_Outline_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Outline_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_Curve_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_Curve_Applied" },
                @{ Template = "assets/Premium/Text_SubTab_3D_Applied.png"; CropId = $null; Screenshot = "screenshots/Text_SubTab_3D_Applied" },
                @{ Template = "assets/Premium/Text_SubTabs_All_Applied_Result.png"; CropId = $null; Screenshot = "screenshots/Text_SubTabs_All_Applied_Result" }
            )

            "*TC_11_Test_Mockup_Preview_Screen*" = @(
                @{ Template = "assets/Premium/TC_11_Verify_Navigated_To_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/TC_11_Verify_Navigated_To_Mockup_Preview_Screen" },
                @{ Template = "assets/Premium/TC_11_Verify_Displayed_Last_Image_On_Mockup_Preview_Screen.png"; CropId = $null; Screenshot = "screenshots/TC_11_Verify_Displayed_Last_Image_On_Mockup_Preview_Screen" }
            )
        }
        
        # Example dual compare map
        $dualCompareMap = [ordered]@{
            "*AI_TC_08.2-Verify_Spam_Button_AI_Magic_Style_On_Saved_Screen*" = @(
                @{
                    Screenshot1 = "screenshots/Saved_Screen_Card"; CropId1 = "imgStory";
                    Screenshot2 = "screenshots/AI_Magic_Style_Card"; CropId2 = "img_preview"
                }
            )

            "*TC_02_Test_Background_Tool_On_Edit_Screen*" = @(
                @{
                    Screenshot1 = "screenshots/Add_Image_Background_on_Edit_Screen"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/preview_screen_logo"; CropId2 = "imageTransparentGrid"
                },
                @{
                    Screenshot1 = "screenshots/backgroundTool_on_Edit_Screen"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/backgroundTool_on_Edit_Screen2"; CropId2 = "bgDesignArea";
                },
                @{
                    Screenshot1 = "screenshots/backgroundTool_on_Edit_Screen"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/backgroundTool_on_Edit_Screen3"; CropId2 = "bgDesignArea";
                },
                @{
                    Screenshot1 = "screenshots/backgroundTool_on_Edit_Screen"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/backgroundTool_on_Edit_Screen4"; CropId2 = "bgDesignArea";
                },
                @{
                    Screenshot1 = "screenshots/backgroundTool_on_Edit_Screen"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/backgroundTool_on_Edit_Screen5"; CropId2 = "bgDesignArea";
                },
                @{
                    Screenshot1 = "screenshots/Add_Image_Background_on_Edit_Screen"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/TemplateDraft_Displayed_correctly"; CropId2 = "bgDesignArea";
                },
                @{
                    Screenshot1 = "screenshots/Verify_Logo_Inside_Circle_Shape_On_Canvas"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/Verify_Logo_Inside_Circle_Shape_After_Back_To_Edit_Screen"; CropId2 = "bgDesignArea";
                }
            )

            "*TC_03_Test_Art_Tool_On_Edit_Screen*" = @(
                @{
                    Screenshot1 = "screenshots/Verify_Redo_On_The_Template_Detail_Successfully"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/Preview_Screen"; CropId2 = "imageTransparentGrid";
                },
                @{
                    Screenshot1 = "screenshots/Verify_Image_On_Style_Magic_AI_Matches_Template"; CropId1 = "image";
                    Screenshot2 = "screenshots/Preview_Screen"; CropId2 = "imageTransparentGrid";
                },
                @{
                    Screenshot1 = "screenshots/Verify_Redo_On_The_Template_Detail_Successfully"; CropId1 = "bgDesignArea";
                    Screenshot2 = "screenshots/TemplateDraft_Displayed_correctly_For_Art_Feature"; CropId2 = "bgDesignArea";
                }

                # Verify template matchs image on the Preview Screen
                # @{
                #     Screenshot1 = "screenshots/Preview_Screen"; CropId2 = "imageTransparentGrid";
                #     Screenshot2 = "Verify_template_Matching_On_The_Preview_Screen", CropId2 = "bgDesignArea";
                # }
            )

            "*TC_10_Test_Preview_Screen*" = @(
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_Screen_Baseline"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_Screen_First"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_Screen_After_Move_Down"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_Screen_Result"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Shape"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Shape"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Color"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Color"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Gradient"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Gradient"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Preset"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Preset"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Texture"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Texture"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Gradient_2"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Gradient_2"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Background_Image"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Background_Image"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_10_Edit_After_Art_Add"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_10_Preview_After_Art_Add"; CropId2 = "imageTransparentGrid";
                }
            )

            "*TC_13_Test_Feature_Usage_And_Save_On_Edit_Screen*" = @(
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Background"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Background"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Art_Move"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Art_Move"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Text_Add"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Text_Add"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Effect"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Effect"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Palette"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Palette"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_13_Edit_After_Image_Add"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_13_Preview_After_Image_Add"; CropId2 = "imageTransparentGrid";
                }
            )

            "*TC_14_Test_Background_Sub_Features_And_Save_On_Edit_Screen*" = @(
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Shape_Triangle"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Shape_Triangle"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Color"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Color"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Gradient"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Gradient"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Background_Preset"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Background_Preset"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Texture"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Texture"; CropId2 = "imageTransparentGrid";
                },
                @{ 
                    Screenshot1 = "screenshots/TC_14_Edit_After_Custom_Image"; CropId1 = "layout_transparent";
                    Screenshot2 = "screenshots/TC_14_Preview_After_Custom_Image"; CropId2 = "imageTransparentGrid";
                }
            )
        }
        
        # Lựa chọn bảng ánh xạ so sánh ảnh theo phiên bản (Free / Premium)
        if ($testVersion -eq "Premium") {
            Write-Host "        [INFO] Runner so sánh ảnh: PHIÊN BẢN PREMIUM (Chỉ so sánh ảnh trong assets\Premium)" -ForegroundColor Magenta
            $activeCompareMap = $imageCompareMap_Premium
        } else {
            Write-Host "        [INFO] Runner so sánh ảnh: PHIÊN BẢN FREE (Chỉ so sánh ảnh trong assets\Free)" -ForegroundColor Yellow
            $activeCompareMap = $imageCompareMap_Free
        }

        # Tìm template configs phù hợp với test name hiện tại
        $imageConfigs = @()
        foreach ($pattern in $activeCompareMap.Keys) {
            if ($testName -like $pattern) {
                $val = $activeCompareMap[$pattern]
                # Hỗ trợ cả single hashtable và array of hashtables
                if ($val -is [Array]) {
                    $imageConfigs = $val
                } else {
                    $imageConfigs = @($val)
                }
                break
            }
        }

        # Tìm dual compare configs phù hợp với test name hiện tại
        $dualConfigs = @()
        foreach ($pattern in $dualCompareMap.Keys) {
            if ($testName -like $pattern) {
                $val = $dualCompareMap[$pattern]
                if ($val -is [Array]) {
                    $dualConfigs = $val
                } else {
                    $dualConfigs = @($val)
                }
                break
            }
        }

        $compareFailed = $false

            # Chạy tất cả dual compare configs
            foreach ($dualConfig in $dualConfigs) {
                # Chế độ so sánh 2 screenshot runtime
                Write-Host "        [INFO] Running dual screenshot comparison..." -ForegroundColor Cyan
                Write-Host "        [INFO] Screenshot 1: $($dualConfig.Screenshot1) (crop: $($dualConfig.CropId1))" -ForegroundColor Cyan
                Write-Host "        [INFO] Screenshot 2: $($dualConfig.Screenshot2) (crop: $($dualConfig.CropId2))" -ForegroundColor Cyan

                $crop1Arg = if ($dualConfig.CropId1) { $dualConfig.CropId1 } else { "none" }
                $crop2Arg = if ($dualConfig.CropId2) { $dualConfig.CropId2 } else { "none" }

                $compareOutput = & $PythonCmd scripts/compare.py "$PSScriptRoot" dual $dualConfig.Screenshot1 $crop1Arg $dualConfig.Screenshot2 $crop2Arg 2>&1 | Out-String
                $compareExitCode = $LASTEXITCODE

                # In kết quả so sánh ra console
                Write-Host "        ----------------------------------------" -ForegroundColor DarkGray
                if ($compareOutput) {
                    $compareOutput.Split("`n") | ForEach-Object {
                        $line = $_.Trim()
                        if ($line -ne "") {
                            if ($line -match "PASSED") {
                                Write-Host "        $line" -ForegroundColor Green
                            } elseif ($line -match "FAILED|Error") {
                                Write-Host "        $line" -ForegroundColor Red
                            } elseif ($line -match "MATCH PERCENTAGE") {
                                if ($compareExitCode -eq 0) {
                                    Write-Host "        $line" -ForegroundColor Green
                                } else {
                                    Write-Host "        $line" -ForegroundColor Red
                                }
                            } else {
                                Write-Host "        $line" -ForegroundColor Gray
                            }
                        }
                    }
                }
                Write-Host "        ----------------------------------------" -ForegroundColor DarkGray

                # Ghi nhận chi tiết so sánh ảnh dual
                $compRes = Parse-CompareResult -Type "Dual" -Config $dualConfig -Output $compareOutput -ExitCode $compareExitCode
                $imageComparisons += $compRes

                if ($compareExitCode -ne 0) {
                    $compareFailed = $true
                    if (-not $failedStep) {
                        $failedStep = "Visual Comparison: $($dualConfig.Screenshot1) vs $($dualConfig.Screenshot2)"
                        $errorMessage = $compRes.Summary
                    }
                }
            }

            # Chạy tất cả image compare configs
            foreach ($imgConfig in $imageConfigs) {
                $templatePath = $imgConfig.Template.Replace('\', '/')
                $cropId = $imgConfig.CropId
                $screenshotName = if ($imgConfig.Screenshot) { $imgConfig.Screenshot.Replace('\', '/') } else { $null }

                # Kiểm tra file template tồn tại
                if (-not (Test-Path "$PSScriptRoot/$templatePath")) {
                    Write-Host "        [ERROR] Template image not found: $templatePath" -ForegroundColor Red
                    $compareFailed = $true
                    $compRes = [ordered]@{
                        Type            = "Template"
                        Template        = $templatePath
                        Screenshot      = $screenshotName
                        CropId          = $cropId
                        Status          = "FAILED"
                        MatchPercentage = $null
                        CanvasZone      = $null
                        ToolZone        = $null
                        Summary         = "Template image not found: $templatePath"
                    }
                    $imageComparisons += $compRes
                    if (-not $failedStep) {
                        $failedStep = "Visual Comparison: $templatePath"
                        $errorMessage = "Template image not found: $templatePath"
                    }
                    continue
                }

                # Cập nhật baseline nếu có cờ -UpdateBaseline
                if ($UpdateBaseline -and $screenshotName) {
                    $srcScreenshot = "$PSScriptRoot/$screenshotName.png"
                    if (-not (Test-Path $srcScreenshot)) {
                        $found = Get-ChildItem -Path "$PSScriptRoot/screenshots" -Filter "$([System.IO.Path]::GetFileName($screenshotName)).png" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
                        if ($found) { $srcScreenshot = $found.FullName }
                    }
                    if (Test-Path $srcScreenshot) {
                        $destPath = "$PSScriptRoot/$templatePath"
                        $destDir = [System.IO.Path]::GetDirectoryName($destPath)
                        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                        Copy-Item -Path $srcScreenshot -Destination $destPath -Force
                        Write-Host "        [BASELINE UPDATED] Copied $srcScreenshot -> $destPath" -ForegroundColor Green
                    }
                }

                Write-Host "        [INFO] Running image comparison post-step..." -ForegroundColor Cyan
                
                # Xây dựng lệnh gọi Python script
                $cropArg = if ($cropId) { $cropId } else { "none" }
                $screenshotArg = if ($screenshotName) { $screenshotName } else { "none" }
                
                if ($cropId) {
                    Write-Host "        [INFO] Cropping to element: $cropId" -ForegroundColor Cyan
                }
                if ($screenshotName) {
                    Write-Host "        [INFO] Looking for screenshot: $screenshotName" -ForegroundColor Cyan
                }
                
                $compareOutput = & $PythonCmd scripts/compare.py "$PSScriptRoot" $templatePath $cropArg $screenshotArg 2>&1 | Out-String
                $compareExitCode = $LASTEXITCODE
                
                # In kết quả so sánh ra console
                Write-Host "        ----------------------------------------" -ForegroundColor DarkGray
                if ($compareOutput) {
                    $compareOutput.Split("`n") | ForEach-Object {
                        $line = $_.Trim()
                        if ($line -ne "") {
                            if ($line -match "PASSED") {
                                Write-Host "        $line" -ForegroundColor Green
                            } elseif ($line -match "FAILED|Error") {
                                Write-Host "        $line" -ForegroundColor Red
                            } elseif ($line -match "MATCH PERCENTAGE") {
                                if ($compareExitCode -eq 0) {
                                    Write-Host "        $line" -ForegroundColor Green
                                } else {
                                    Write-Host "        $line" -ForegroundColor Red
                                }
                            } else {
                                Write-Host "        $line" -ForegroundColor Gray
                            }
                        }
                    }
                }
                Write-Host "        ----------------------------------------" -ForegroundColor DarkGray

                # Ghi nhận chi tiết so sánh template
                $compRes = Parse-CompareResult -Type "Template" -Config $imgConfig -Output $compareOutput -ExitCode $compareExitCode
                $imageComparisons += $compRes

                if ($compareExitCode -ne 0) {
                    $compareFailed = $true
                    if (-not $failedStep) {
                        $cropDesc = if ($cropId) { " (crop: $cropId)" } else { "" }
                        $failedStep = "Visual Comparison: $templatePath$cropDesc"
                        $errorMessage = $compRes.Summary
                    }
                }
            }

            # Xác định status cuối cùng
            if ($compareFailed) {
                $script:Failed++
                $status = "FAILED"
                $color = "Red"
            } else {
                if ($output -match "WARNED") {
                    $script:Warned++
                    $status = "WARNED"
                    $color = "Yellow"
                } else {
                    $script:Passed++
                    $status = "PASSED"
                    $color = "Green"
                }
            }
    } else {
        $script:Failed++
        $status = "FAILED"
        $color = "Red"
        Write-Host "        [MAESTRO OUTPUT]" -ForegroundColor Yellow
        $output.Split("`n") | ForEach-Object {
            $line = $_.Trim()
            if ($line -ne "") {
                Write-Host "        $line" -ForegroundColor Yellow
            }
        }
        $errInfo = Extract-MaestroError -Output $output
        $failedStep = $errInfo.FailedStep
        $errorMessage = $errInfo.ErrorMessage
        Write-Host ""
        Write-Host "        [FAILED STEP]    $failedStep" -ForegroundColor Red
        Write-Host "        [ERROR MESSAGE]  $errorMessage" -ForegroundColor Red
    }

    # Xử lý dừng và thu hồi file video nếu có cờ -RecordVideo
    $videoRelPath = $null
    if ($RecordVideo) {
        Write-Host "        [VIDEO] Finalizing screen recording..." -ForegroundColor Cyan
        adb -s $env:ANDROID_SERIAL shell "kill -2 `$(pidof screenrecord 2>/dev/null)" 2>&1 | Out-Null
        Start-Sleep -Seconds 2
        if ($videoProc -and (-not $videoProc.HasExited)) {
            Stop-Process -Id $videoProc.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1

        $videosDir = "$PSScriptRoot/reports/videos"
        if (-not (Test-Path $videosDir)) {
            New-Item -ItemType Directory -Path $videosDir -Force | Out-Null
        }
        $localVideoFile = "$videosDir/${testName}.mp4"

        if ($RecordOnlyOnFailure -and ($status -ne "FAILED")) {
            adb -s $env:ANDROID_SERIAL shell "rm -f $deviceVideoPath" 2>&1 | Out-Null
            Write-Host "        [VIDEO] Test PASSED - Skipped saving video (-RecordOnlyOnFailure active)." -ForegroundColor DarkGray
        } else {
            adb -s $env:ANDROID_SERIAL pull $deviceVideoPath $localVideoFile 2>&1 | Out-Null
            adb -s $env:ANDROID_SERIAL shell "rm -f $deviceVideoPath" 2>&1 | Out-Null
            if (Test-Path $localVideoFile) {
                $videoRelPath = "reports/videos/${testName}.mp4"
                Write-Host "        [VIDEO] Exported: $videoRelPath" -ForegroundColor Green
            } else {
                Write-Host "        [VIDEO] Note: No video retrieved from device." -ForegroundColor DarkYellow
            }
        }
    }

    Write-Host "        Result: $status ($([math]::Round($duration, 1))s)" -ForegroundColor $color

    $script:Results += [PSCustomObject]@{
        Test             = $testName
        Folder           = $FolderName
        Screen           = $ScreenName
        Status           = $status
        Duration         = "$([math]::Round($duration, 1))s"
        Video            = $videoRelPath
        FailedStep       = $failedStep
        ErrorMessage     = $errorMessage
        ImageComparisons = if ($imageComparisons -and $imageComparisons.Count -gt 0) { $imageComparisons } else { [object[]]@() }
    }
}

# Main execution loop
foreach ($folderItem in $foldersToRun) {
    Write-Host "========================================" -ForegroundColor DarkGray
    Write-Host "  Folder: $($folderItem.Name)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor DarkGray

    # 1. Run direct YAML files in this folder
    $directFiles = Get-ChildItem -Path $folderItem.FullName -Filter "*.yaml" -File
    $eligibleFiles = @()
    foreach ($testFile in $directFiles) {
        if ($testFile.Length -eq 0) {
            Write-Host "    [SKIP] Empty test file: $($testFile.Name)" -ForegroundColor DarkGray
            continue
        }
        if ($filterFiles.Count -gt 0) {
            $matchedFile = $false
            foreach ($pf in $filterFiles) {
                if ($testFile.Name -like "*$pf*") { $matchedFile = $true; break }
            }
            if (-not $matchedFile) { continue }
        }
        if ($Exclude.Count -gt 0 -and ($Exclude | Where-Object { $testFile.Name -like "*$_*" })) {
            Write-Host "    [SKIP] Excluded test file: $($testFile.Name)" -ForegroundColor DarkYellow
            continue
        }
        $eligibleFiles += $testFile
    }

    $filesToExecute = @()
    if ($ShardTotal -gt 0 -and $ShardIndex -gt 0) {
        for ($i = 0; $i -lt $eligibleFiles.Count; $i++) {
            if (($i % $ShardTotal) -eq ($ShardIndex - 1)) {
                $filesToExecute += $eligibleFiles[$i]
            } else {
                Write-Host "    [SHARD-SKIP] File not in Shard $ShardIndex/${ShardTotal} - $($eligibleFiles[$i].Name)" -ForegroundColor DarkGray
            }
        }
    } else {
        $filesToExecute = $eligibleFiles
    }

    foreach ($testFile in $filesToExecute) {
        Run-TestFile -TestFile $testFile -FolderName $folderItem.Name -ScreenName $folderItem.Name
    }

    # 2. Run YAML files in subdirectories (screens)
    $subDirs = Get-ChildItem -Path $folderItem.FullName -Directory
    foreach ($screenDir in $subDirs) {
        Write-Host ""
        Write-Host "  Screen: $($screenDir.Name)" -ForegroundColor Magenta

        $testFiles = Get-ChildItem -Path $screenDir.FullName -Filter "*.yaml" -File
        $eligibleSubFiles = @()
        foreach ($testFile in $testFiles) {
            if ($testFile.Length -eq 0) {
                Write-Host "    [SKIP] Empty test file: $($testFile.Name)" -ForegroundColor DarkGray
                continue
            }
            if ($filterFiles.Count -gt 0) {
                $matchedFile = $false
                foreach ($pf in $filterFiles) {
                    if ($testFile.Name -like "*$pf*") { $matchedFile = $true; break }
                }
                if (-not $matchedFile) { continue }
            }
            if ($Exclude.Count -gt 0 -and ($Exclude | Where-Object { $testFile.Name -like "*$_*" })) {
                Write-Host "    [SKIP] Excluded test file: $($testFile.Name)" -ForegroundColor DarkYellow
                continue
            }
            $eligibleSubFiles += $testFile
        }

        $subFilesToExecute = @()
        if ($ShardTotal -gt 0 -and $ShardIndex -gt 0) {
            for ($i = 0; $i -lt $eligibleSubFiles.Count; $i++) {
                if (($i % $ShardTotal) -eq ($ShardIndex - 1)) {
                    $subFilesToExecute += $eligibleSubFiles[$i]
                } else {
                    Write-Host "    [SHARD-SKIP] File not in Shard $ShardIndex/${ShardTotal} - $($eligibleSubFiles[$i].Name)" -ForegroundColor DarkGray
                }
            }
        } else {
            $subFilesToExecute = $eligibleSubFiles
        }

        foreach ($testFile in $subFilesToExecute) {
            Run-TestFile -TestFile $testFile -FolderName $folderItem.Name -ScreenName $screenDir.Name
        }
    }
}

# Summary
Write-Host ""
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
$Results | Format-Table -Property Test, Status, Duration, FailedStep -AutoSize
Write-Host "  Total: $Total | Passed: $Passed | Warned: $Warned | Failed: $Failed" -ForegroundColor White
Write-Host ""

$failedTests = $Results | Where-Object { $_.Status -eq "FAILED" }
if ($failedTests.Count -gt 0) {
    Write-Host "--------------------------------------------" -ForegroundColor Red
    Write-Host "  CHI TIẾT LỖI (FAILED STEPS):" -ForegroundColor Red
    Write-Host "--------------------------------------------" -ForegroundColor Red
    foreach ($ft in $failedTests) {
        Write-Host "  * Test: $($ft.Test)" -ForegroundColor Yellow
        Write-Host "    - Failed Step   : $($ft.FailedStep)" -ForegroundColor Red
        Write-Host "    - Error Message : $($ft.ErrorMessage)" -ForegroundColor Red
    }
    Write-Host ""
}

# Image Comparisons Summary table
$allCompares = @()
foreach ($r in $Results) {
    if ($r.ImageComparisons -and $r.ImageComparisons.Count -gt 0) {
        foreach ($c in $r.ImageComparisons) {
            $allCompares += [PSCustomObject]@{
                Test       = $r.Test
                Type       = $c.Type
                Target     = if ($c.Type -eq "Dual") { "$($c.Screenshot1) vs $($c.Screenshot2)" } else { $c.Template }
                MatchPct   = if ($null -ne $c.MatchPercentage) { "$([math]::Round($c.MatchPercentage, 2))%" } else { "N/A" }
                Status     = $c.Status
                Summary    = $c.Summary
            }
        }
    }
}

if ($RecordVideo) {
    $videoList = $Results | Where-Object { $_.Video }
    if ($videoList.Count -gt 0) {
        Write-Host "--------------------------------------------" -ForegroundColor Magenta
        Write-Host "  DANH SÁCH FILE VIDEO ĐÃ XUẤT:" -ForegroundColor Magenta
        Write-Host "--------------------------------------------" -ForegroundColor Magenta
        foreach ($vItem in $videoList) {
            Write-Host "  * Test: $($vItem.Test)" -ForegroundColor Yellow
            Write-Host "    - Video File : $($vItem.Video)" -ForegroundColor White
        }
        Write-Host ""
    }
}

if ($global:TemplateServiceProc) {
    Stop-Process -Id $global:TemplateServiceProc.Id -Force -ErrorAction SilentlyContinue
}

if ($ReportJson -ne "") {
    try {
        $reportDir = [System.IO.Path]::GetDirectoryName($ReportJson)
        if ($reportDir -and (-not (Test-Path $reportDir))) {
            New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        }
        $reportData = [ordered]@{
            Total      = $Total
            Passed     = $Passed
            Warned     = $Warned
            Failed     = $Failed
            Device     = $env:ANDROID_SERIAL
            ShardIndex = $ShardIndex
            ShardTotal = $ShardTotal
            Results    = $Results
        }
        $reportData | ConvertTo-Json -Depth 10 | Set-Content -Path $ReportJson -Encoding utf8
        Write-Host "[REPORT] Saved test results to $ReportJson" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not save report to $ReportJson : $_" -ForegroundColor Yellow
    }
}

if ($Failed -gt 0) {
    Write-Host "  SOME TESTS FAILED!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
