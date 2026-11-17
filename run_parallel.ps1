# ==============================================================================
# Maestro Parallel Test Runner for Local Multi-Device Environment
# Project: Logo Maker
# ==============================================================================

param(
    [string[]]$Devices = @(),       # Danh sách serial thiết bị (nếu để trống, tự động nhận diện từ adb)
    [string]$Folder = "test-suite", # Thư mục chứa test cases
    [string]$File = "",             # Lọc test file theo tên (nếu có)
    [string[]]$Exclude = @("TC_00", "TC_08_Test_Home_Screen"), # Test cases loại trừ
    [ValidateSet("Free", "Premium", "Auto")]
    [string]$Version = "Auto",     # Phiên bản app
    [int]$MaxDevices = 10,         # Số lượng thiết bị tối đa chạy song song (mặc định 10 để tự nhận toàn bộ máy)
    [switch]$InitFirstRun = $true, # Khởi tạo trạng thái lần đầu SONG SONG (Mặc định: BẬT để đảm bảo sạch state)
    [switch]$SkipInit,             # Bỏ qua bước khởi tạo nếu các máy đã ở sẵn Home Screen sạch
    [switch]$Resume                # Tiếp tục chạy các test case chưa hoàn thành / failed, giữ lại test đã PASS
)

# Chuẩn hóa danh sách Exclude và Devices
if ($Exclude.Count -gt 0) {
    $cleanExclude = @()
    foreach ($item in $Exclude) {
        foreach ($sub in ($item -split ",")) {
            $cleaned = $sub.Trim().Trim("@()'`"").Trim()
            if ($cleaned) { $cleanExclude += $cleaned }
        }
    }
    $Exclude = $cleanExclude
}
if ($Devices.Count -gt 0) {
    $cleanDevices = @()
    foreach ($item in $Devices) {
        foreach ($sub in ($item -split ",")) {
            $cleaned = $sub.Trim().Trim("@()'`"").Trim()
            if ($cleaned) { $cleanDevices += $cleaned }
        }
    }
    $Devices = $cleanDevices
}

$MaestroDir = "$PSScriptRoot/.maestro/$Folder"
$ReportsDir = "$PSScriptRoot/reports/parallel_local"
if (-not $Resume) {
    if (Test-Path $ReportsDir) {
        Remove-Item -Path $ReportsDir -Recurse -Force -ErrorAction SilentlyContinue
    }
} else {
    # Nếu bật -Resume, xóa bỏ các report FAILED cũ để runner chạy lại
    if (Test-Path $ReportsDir) {
        Get-ChildItem -Path $ReportsDir -Filter "report_*.json" -File | ForEach-Object {
            try {
                $c = Get-Content $_.FullName -Raw | ConvertFrom-Json
                if ($c.Failed -gt 0 -or $c.Passed -eq 0) {
                    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                }
            } catch {}
        }
    }
}
New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null

# Dọn dẹp session cũ của Maestro để tránh lỗi Session Lock khi chạy song song
Remove-Item "$HOME\.maestro\sessions" -Recurse -Force -ErrorAction SilentlyContinue

# Dọn dẹp các file tạm tmp*.apk trong %TEMP% để chống đầy ổ C:
$tempPath = [System.IO.Path]::GetTempPath()
Get-ChildItem -Path $tempPath -Filter "*tmp*.apk" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $tempPath -Filter "*.tmp" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 10MB } | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  MAESTRO PARALLEL TEST RUNNER - MULTI-DEVICE (AUTO-QUEUE)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 0. Luôn khởi động mới Multi-Threaded Template Service Daemon (Port 8765) để đảm bảo dùng đúng code/env mới nhất
$healthCheck = $null
try {
    $healthCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
} catch {}
if ($healthCheck -and $healthCheck.pid) {
    Stop-Process -Id $healthCheck.pid -Force -ErrorAction SilentlyContinue
}
if ($IsWindows -or ($env:OS -like "*Windows*")) {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*template_service.py*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Milliseconds 400

Write-Host "[INFO] Starting Multi-Threaded Template Service daemon on port 8765..." -ForegroundColor Cyan
$PythonCmd = "python"
try {
    $ver = & py --version 2>&1
    if ($LASTEXITCODE -eq 0 -or ($ver -match "Python")) { $PythonCmd = "py" }
} catch { $PythonCmd = "python" }

New-Item -ItemType Directory -Path "$PSScriptRoot/reports" -Force | Out-Null
$templateProc = Start-Process -FilePath $PythonCmd -ArgumentList "-X utf8 scripts/template_service.py" -WorkingDirectory $PSScriptRoot -RedirectStandardOutput "$PSScriptRoot/reports/template_service.log" -RedirectStandardError "$PSScriptRoot/reports/template_service_err.log" -WindowStyle Hidden -PassThru
$env:TEMPLATE_SERVICE_MANAGED = "1"
for ($waitIdx = 0; $waitIdx -lt 20; $waitIdx++) {
    Start-Sleep -Milliseconds 250
    try {
        $readyCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($readyCheck.status -eq "ok") { break }
    } catch {}
}

# 1. Phát hiện thiết bị kết nối qua ADB
$connectedDevices = @()
$adbOutput = adb devices 2>&1
foreach ($line in $adbOutput) {
    if ($line -match "^([A-Za-z0-9_\-\.]+)\s+device$") {
        $connectedDevices += $matches[1]
    }
}

$targetDevices = @()
if ($Devices.Count -gt 0) {
    foreach ($d in $Devices) {
        if ($connectedDevices -contains $d) {
            $targetDevices += $d
        } else {
            Write-Host "[WARNING] Thiết bị chỉ định '$d' không có trong danh sách adb devices!" -ForegroundColor Yellow
        }
    }
} else {
    $targetDevices = $connectedDevices
}

# Giới hạn số lượng thiết bị tối đa theo $MaxDevices
if ($targetDevices.Count -gt $MaxDevices) {
    $targetDevices = $targetDevices[0..($MaxDevices - 1)]
}

if ($targetDevices.Count -eq 0) {
    Write-Host "[ERROR] Không tìm thấy thiết bị Android nào kết nối! Hãy cắm cáp USB và bật USB Debugging." -ForegroundColor Red
    exit 1
}

Write-Host "  Thiết bị tham gia kiểm thử ($($targetDevices.Count) máy):" -ForegroundColor Green
for ($i = 0; $i -lt $targetDevices.Count; $i++) {
    Write-Host "    - Worker $($i + 1): $($targetDevices[$i])" -ForegroundColor White
}
Write-Host "================================================================================" -ForegroundColor Cyan

# 2. Chuẩn bị môi trường trên từng thiết bị (Wake screen, Push media)
$defaultMedia = "$PSScriptRoot/assets/image_Default.png"
foreach ($dev in $targetDevices) {
    Write-Host "[INIT] Chuẩn bị thiết bị $dev..." -ForegroundColor DarkGray
    adb -s $dev shell input keyevent 224 2>&1 | Out-Null
    adb -s $dev shell input keyevent 82 2>&1 | Out-Null
    adb -s $dev shell "svc power stayon true" 2>&1 | Out-Null
    if (Test-Path $defaultMedia) {
        adb -s $dev shell "rm -rf /sdcard/Pictures/LogoMaker/*" 2>&1 | Out-Null
        adb -s $dev push $defaultMedia /sdcard/Pictures/image_Default.png 2>&1 | Out-Null
        adb -s $dev shell "touch /sdcard/Pictures/image_Default.png" 2>&1 | Out-Null
        adb -s $dev shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Pictures/image_Default.png 2>&1 | Out-Null
    }
}

# 2.1. Khởi tạo trạng thái lần đầu SONG SONG trên tất cả thiết bị (Parallel Bootstrap)
if ($InitFirstRun -and (-not $SkipInit)) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  [BOOTSTRAP] Khởi tạo trạng thái lần đầu SONG SONG trên $($targetDevices.Count) thiết bị..." -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan

    $bootstrapFlow = "$PSScriptRoot/.maestro/config/Init_First_Run_State.yaml"
    $bootstrapJobs = @{}
    $bootstrapResults = @{}

    foreach ($dev in $targetDevices) {
        Write-Host "  -> [DISPATCH] Bắt đầu chạy Init_First_Run_State trên: $dev" -ForegroundColor Cyan
        $bootstrapJobs[$dev] = Start-Job -ScriptBlock {
            param($device, $flowPath, $ver)
            $output = maestro --device $device test -e APP_VERSION=$ver -e DEVICE_SERIAL=$device $flowPath 2>&1 | Out-String
            return @{
                Device   = $device
                ExitCode = $LASTEXITCODE
                Output   = $output
            }
        } -ArgumentList $dev, $bootstrapFlow, $Version
        Start-Sleep -Seconds 3
    }

    # Chờ tất cả thiết bị bootstrap xong và theo dõi thời gian thực
    $activeBootstrap = [System.Collections.ArrayList]::new($bootstrapJobs.Keys)
    while ($activeBootstrap.Count -gt 0) {
        Start-Sleep -Milliseconds 1500
        $completed = @()
        foreach ($dev in $activeBootstrap) {
            $job = $bootstrapJobs[$dev]
            if ($job.State -ne "Running") {
                $res = Receive-Job -Job $job -AutoRemoveJob -Wait
                $bootstrapResults[$dev] = $res
                if ($res.ExitCode -eq 0) {
                    Write-Host "  [BOOTSTRAP SUCCESS] Thiết bị $dev đã hoàn tất khởi tạo!" -ForegroundColor Green
                } else {
                    Write-Host "  [BOOTSTRAP FAILED] Thiết bị $dev khởi tạo thất bại (ExitCode: $($res.ExitCode))!" -ForegroundColor Red
                }
                $completed += $dev
            }
        }
        foreach ($c in $completed) {
            [void]$activeBootstrap.Remove($c)
        }
    }

    # Lọc danh sách thiết bị sẵn sàng: chỉ những máy bootstrap thành công mới nhận test
    $healthyDevices = @()
    foreach ($dev in $targetDevices) {
        if ($bootstrapResults[$dev] -and $bootstrapResults[$dev].ExitCode -eq 0) {
            $healthyDevices += $dev
        }
    }

    if ($healthyDevices.Count -eq 0) {
        Write-Host "[FATAL] Toàn bộ thiết bị đều khởi tạo thất bại! Dừng thực thi test suite." -ForegroundColor Red
        if ($templateProc) {
            Stop-Process -Id $templateProc.Id -Force -ErrorAction SilentlyContinue
        }
        exit 1
    } elseif ($healthyDevices.Count -lt $targetDevices.Count) {
        Write-Host "[WARNING] Có $($targetDevices.Count - $healthyDevices.Count) thiết bị khởi tạo thất bại. Tiếp tục chạy với $($healthyDevices.Count) thiết bị sẵn sàng." -ForegroundColor Yellow
        $targetDevices = $healthyDevices
    }
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# 3. Thu thập danh sách test cases
$testFiles = Get-ChildItem -Path $MaestroDir -Filter "*.yaml" -File
$queue = [System.Collections.Generic.Queue[string]]::new()
$allTestNames = @()
$resumedCompleted = [System.Collections.ArrayList]::new()

foreach ($tf in $testFiles) {
    if ($tf.Length -eq 0) { continue }
    $name = $tf.BaseName
    if ($File -ne "" -and $name -notlike "*$File*") { continue }
    if ($Exclude.Count -gt 0 -and ($Exclude | Where-Object { $name -like "*$_*" })) {
        Write-Host "  [SKIP] Loại trừ test case: $name" -ForegroundColor DarkYellow
        continue
    }

    # Nếu bật -Resume, kiểm tra xem test này đã PASS ở phiên trước hay chưa
    if ($Resume) {
        $repPath = "$ReportsDir/report_${name}.json"
        if (Test-Path $repPath) {
            try {
                $c = Get-Content $repPath -Raw | ConvertFrom-Json
                if ($c.Failed -eq 0 -and $c.Passed -gt 0) {
                    $res0 = if ($c.Results -and $c.Results.Count -gt 0) { $c.Results[0] } else { $null }
                    $dev = if ($c.Device) { $c.Device } elseif ($res0 -and $res0.Device) { $res0.Device } else { "Cached" }
                    $dur = if ($res0 -and $res0.Duration) { $res0.Duration } else { "N/A" }
                    $imgC = if ($res0 -and $res0.ImageComparisons) { $res0.ImageComparisons } else { @() }
                    Write-Host "  [RESUME] '$name' đã PASSED ở phiên trước ($dur trên $dev) -> Bỏ qua không chạy lại" -ForegroundColor Green
                    [void]$resumedCompleted.Add([ordered]@{
                        Test             = $name
                        Device           = $dev
                        Status           = "PASSED"
                        Duration         = $dur
                        FailedStep       = $null
                        ErrorMessage     = $null
                        ImageComparisons = if ($imgC -and $imgC.Count -gt 0) { $imgC } else { [object[]]@() }
                    })
                    $allTestNames += $name
                    continue
                }
            } catch {}
        }
    }

    $queue.Enqueue($name)
    $allTestNames += $name
}

$totalTests = $allTestNames.Count
Write-Host ""
Write-Host "  Tổng số test cases: $totalTests (Đã PASS: $($resumedCompleted.Count) | Còn lại cần chạy: $($queue.Count))" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 4. Trạng thái theo dõi chung (Shared State Tracking)
$statusFile = "$ReportsDir/test_status.json"
$state = [ordered]@{
    Total     = $totalTests
    Pending   = [System.Collections.ArrayList]::new($queue.ToArray())
    Running   = [ordered]@{}
    Completed = $resumedCompleted
}

function Save-State {
    $state | ConvertTo-Json -Depth 10 | Set-Content -Path $statusFile -Encoding utf8
}
Save-State

# 5. Vòng lặp điều phối Workers
$workers = @{}
foreach ($dev in $targetDevices) {
    $workers[$dev] = @{
        Device    = $dev
        Job       = $null
        CurrentTest = $null
        StartTime = $null
    }
}

$startTimeAll = Get-Date

while ($queue.Count -gt 0 -or ($workers.Values | Where-Object { $_.Job -ne $null }).Count -gt 0) {
    # 5.1 Gán việc cho các Worker đang rảnh
    foreach ($dev in $targetDevices) {
        $w = $workers[$dev]
        if ($w.Job -eq $null -and $queue.Count -gt 0) {
            $nextTest = $queue.Dequeue()
            $w.CurrentTest = $nextTest
            $w.StartTime = Get-Date
            $reportFile = "$ReportsDir/report_${nextTest}.json"

            # Cập nhật state
            [void]$state.Pending.Remove($nextTest)
            $state.Running[$nextTest] = [ordered]@{
                Device    = $dev
                StartTime = (Get-Date).ToString("HH:mm:ss")
            }
            Save-State

            Write-Host "  [DISPATCH] Giao '$nextTest' cho Worker: $dev" -ForegroundColor Cyan

            # Khởi chạy job chạy test case trên device cụ thể
            $scriptPath = "$PSScriptRoot/run_tests_windows.ps1"
            $workDir = $PSScriptRoot
            $w.Job = Start-Job -ScriptBlock {
                param($workDir, $scriptPath, $testName, $device, $version, $reportFile)
                Set-Location $workDir
                & $scriptPath -File $testName -Device $device -Version $version -ReportJson $reportFile
            } -ArgumentList $workDir, $scriptPath, $nextTest, $dev, $Version, $reportFile
            Start-Sleep -Seconds 3
        }
    }

    # 5.2 Kiểm tra các Worker đã hoàn thành
    foreach ($dev in $targetDevices) {
        $w = $workers[$dev]
        if ($w.Job -ne $null -and $w.Job.State -ne "Running") {
            $jobOutput = Receive-Job -Job $w.Job -AutoRemoveJob -Wait
            $testName = $w.CurrentTest
            $durationSec = [math]::Round(((Get-Date) - $w.StartTime).TotalSeconds, 1)

            # Đọc file report JSON nếu có
            $reportFile = "$ReportsDir/report_${testName}.json"
            $status = "FAILED"
            $failedStep = $null
            $errorMessage = $null
            $imgCompares = @()
            if (Test-Path $reportFile) {
                try {
                    $jsonContent = Get-Content $reportFile -Raw | ConvertFrom-Json
                    if ($jsonContent.Failed -eq 0 -and $jsonContent.Passed -gt 0) {
                        $status = "PASSED"
                    }
                    if ($jsonContent.Results -and $jsonContent.Results.Count -gt 0) {
                        $res0 = $jsonContent.Results[0]
                        $failedStep = $res0.FailedStep
                        $errorMessage = $res0.ErrorMessage
                        $imgCompares = $res0.ImageComparisons
                    }
                } catch {}
            }

            $color = if ($status -eq "PASSED") { "Green" } else { "Red" }
            Write-Host "  [$status] '$testName' trên $dev (${durationSec}s)" -ForegroundColor $color
            if ($status -eq "FAILED" -and $failedStep) {
                Write-Host "      [FAILED STEP]    $failedStep" -ForegroundColor Red
                if ($errorMessage) {
                    Write-Host "      [ERROR MESSAGE]  $errorMessage" -ForegroundColor Red
                }
            }

            # Cập nhật state
            $state.Running.Remove($testName)
            [void]$state.Completed.Add([ordered]@{
                Test             = $testName
                Device           = $dev
                Status           = $status
                Duration         = "${durationSec}s"
                FailedStep       = $failedStep
                ErrorMessage     = $errorMessage
                ImageComparisons = if ($imgCompares -and $imgCompares.Count -gt 0) { $imgCompares } else { [object[]]@() }
            })
            Save-State

            # Giải phóng worker
            $w.Job = $null
            $w.CurrentTest = $null
            $w.StartTime = $null
        }
    }

    Start-Sleep -Seconds 2
}

# 6. Tổng hợp kết quả
$totalDuration = [math]::Round(((Get-Date) - $startTimeAll).TotalSeconds, 1)
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  KẾT QUẢ KIỂM THỬ SONG SONG ($($targetDevices.Count) THIẾT BỊ) - $totalDuration s" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$passedCount = ($state.Completed | Where-Object { $_.Status -eq "PASSED" }).Count
$failedCount = ($state.Completed | Where-Object { $_.Status -eq "FAILED" }).Count

$state.Completed | Format-Table -Property Test, Device, Status, Duration, FailedStep -AutoSize

$failedItems = $state.Completed | Where-Object { $_.Status -eq "FAILED" }
if ($failedItems.Count -gt 0) {
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Red
    Write-Host "  CHI TIẾT LỖI (FAILED STEPS):" -ForegroundColor Red
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Red
    foreach ($fi in $failedItems) {
        Write-Host "  * Test: $($fi.Test) (Device: $($fi.Device))" -ForegroundColor Yellow
        Write-Host "    - Failed Step   : $($fi.FailedStep)" -ForegroundColor Red
        Write-Host "    - Error Message : $($fi.ErrorMessage)" -ForegroundColor Red
    }
    Write-Host ""
}

# Tổng hợp kết quả so sánh hình ảnh toàn bộ
$allComparesParallel = @()
foreach ($item in $state.Completed) {
    if ($item.ImageComparisons -and $item.ImageComparisons.Count -gt 0) {
        foreach ($c in $item.ImageComparisons) {
            $allComparesParallel += [PSCustomObject]@{
                Test       = $item.Test
                Device     = $item.Device
                Type       = $c.Type
                Target     = if ($c.Type -eq "Dual") { "$($c.Screenshot1) vs $($c.Screenshot2)" } else { $c.Template }
                MatchPct   = if ($null -ne $c.MatchPercentage) { "$([math]::Round($c.MatchPercentage, 2))%" } else { "N/A" }
                Status     = $c.Status
                Summary    = $c.Summary
            }
        }
    }
}

Write-Host "  Tổng số test: $totalTests | Passed: $passedCount | Failed: $failedCount" -ForegroundColor White
Write-Host "  Báo cáo chi tiết đã lưu tại: $statusFile" -ForegroundColor DarkGray
Write-Host "================================================================================" -ForegroundColor Cyan

# Dọn dẹp temp APKs sau khi chạy xong để giải phóng dung lượng ổ C:
Get-ChildItem -Path $tempPath -Filter "*tmp*.apk" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Hợp nhất toàn bộ báo cáo chi tiết
$mergeScript = "$PSScriptRoot/scripts/merge_reports.py"
if (Test-Path $mergeScript) {
    & $PythonCmd $mergeScript "$ReportsDir"
}

if ($templateProc) {
    Stop-Process -Id $templateProc.Id -Force -ErrorAction SilentlyContinue
}

if ($failedCount -gt 0) {
    exit 1
} else {
    exit 0
}

