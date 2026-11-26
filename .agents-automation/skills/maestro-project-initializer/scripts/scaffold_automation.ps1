# ==============================================================================
# Mobile Automation Scaffolder - Turnkey Project Generator (Portable Agent Tool)
# Location: .agents/skills/maestro-project-initializer/scripts/scaffold_automation.ps1
# Purpose: Replicate 100% of the proven Maestro Automation framework to any new project
# ==============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [Parameter(Mandatory = $true)]
    [string]$AppId,

    [string]$TargetFolder = ".",

    [string]$TargetDevice = "Samsung Galaxy S20 FE (1080x2400 @ 480dpi, Android 13)",
    [string]$GitHubRepo = ""
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  MAESTRO MOBILE AUTOMATION SCAFFOLDER (PORTABLE AGENT ENGINE)" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Project Name  : $ProjectName" -ForegroundColor Yellow
Write-Host "App ID        : $AppId" -ForegroundColor Yellow
Write-Host "Target Folder : $TargetFolder" -ForegroundColor Yellow
Write-Host "Target Device : $TargetDevice" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------------"

$TemplateDir = (Resolve-Path "$PSScriptRoot\..\templates").Path
$TargetRoot = (Resolve-Path (New-Item -ItemType Directory -Path $TargetFolder -Force)).Path

Write-Host "[1/7] Creating standard 3-tier directory structure..." -ForegroundColor Green
$dirs = @(
    ".maestro/config",
    ".maestro/test-suite",
    ".maestro/free-version",
    "assets/Free",
    "assets/Premium",
    "screenshots/debug",
    "reports",
    "ui-dumps",
    "scripts",
    "docs/test-cases",
    ".github/workflows",
    ".agents/rules",
    ".agents/skills/maestro-test-creator",
    ".agents/skills/mobile-automation-mastery",
    ".agents/skills/maestro-project-initializer"
)

foreach ($d in $dirs) {
    $fullPath = Join-Path $TargetRoot $d
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    $gitkeep = Join-Path $fullPath ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        "" | Out-File -FilePath $gitkeep -Encoding utf8 -NoNewline
    }
}

Write-Host "[2/7] Copying core Python & intelligence scripts from templates..." -ForegroundColor Green
$coreScripts = @(
    "compare.py",
    "compare_screens.py",
    "merge_reports.py",
    "inspect_ui.py",
    "template_service.py"
)
foreach ($s in $coreScripts) {
    $src = Join-Path "$TemplateDir\scripts" $s
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination (Join-Path "$TargetRoot\scripts" $s) -Force
    }
}

Write-Host "[3/7] Generating reusable Maestro config flows..." -ForegroundColor Green
# 1. Launch_App.yaml
@"
appId: $AppId
---
- launchApp:
    clearState: false
    permissions:
      all: allow
- waitForAnimationToEnd:
    timeout: 5000
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Launch_App.yaml") -Encoding utf8

# 2. Launch_App_Clear_State.yaml
@"
appId: $AppId
---
- launchApp:
    clearState: true
    permissions:
      all: allow
- waitForAnimationToEnd:
    timeout: 5000
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Launch_App_Clear_State.yaml") -Encoding utf8

# 3. Close_Ads_Screen.yaml
@"
appId: $AppId
---
- runFlow:
    when:
      visible: "Close"
    commands:
      - tapOn: "Close"
- runFlow:
    when:
      visible:
        id: ".*close.*|.*dismiss.*|.*btn_close.*|.*iv_close.*"
    commands:
      - tapOn:
          id: ".*close.*|.*dismiss.*|.*btn_close.*|.*iv_close.*"
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Close_Ads_Screen.yaml") -Encoding utf8

# 4. Close_IAP_Screen.yaml
@"
appId: $AppId
---
- runFlow:
    when:
      visible:
        id: ".*close.*|.*dismiss.*|.*btn_close.*|.*iv_close.*"
    commands:
      - tapOn:
          id: ".*close.*|.*dismiss.*|.*btn_close.*|.*iv_close.*"
- back
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Close_IAP_Screen.yaml") -Encoding utf8

# 5. Back_Action.yaml
@"
appId: $AppId
---
- back
- runFlow:
    when:
      visible: "Close"
    file: "Close_Ads_Screen.yaml"
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Back_Action.yaml") -Encoding utf8

# 6. Init_First_Run_State.yaml (Bootstrap starter)
@"
appId: $AppId
---
# Step 1: Launch App
- runFlow: "Launch_App.yaml"

# Step 2: Handle Onboarding / Language if visible
- runFlow:
    when:
      visible:
        text: "English"
    commands:
      - tapOn: "English"
      - tapOn:
          id: ".*next.*|.*continue.*|.*btn_next.*"

# Step 3: Dismiss Paywall / IAP
- runFlow:
    when:
      visible:
        text: "Get Full Access|Subscribe|Premium|Start Free Trial"
    file: "Close_IAP_Screen.yaml"

# Step 4: Dismiss Ads
- runFlow:
    when:
      visible: "Close"
    file: "Close_Ads_Screen.yaml"
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\config" "Init_First_Run_State.yaml") -Encoding utf8

# 7. Starter Smoke Test: TC_01_Verify_Launch_App.yaml
@"
appId: $AppId
---
# Step 1: Khởi động ứng dụng an toàn
- runFlow: "../config/Launch_App.yaml"

# Step 2: Xử lý Paywall / IAP mở đầu nếu có
- runFlow:
    when:
      visible:
        text: "Get Full Access|Subscribe|Premium|Start Free Trial"
    file: "../config/Close_IAP_Screen.yaml"

# Step 3: Xử lý Popup quảng cáo mở đầu nếu có
- runFlow:
    when:
      visible: "Close"
    file: "../config/Close_Ads_Screen.yaml"

# Step 4: Chờ giao diện chính ổn định
- waitForAnimationToEnd:
    timeout: 5000

# Step 5: Chụp ảnh màn hình kiểm thử Visual Regression
- takeScreenshot: "screenshots/TC_01_Verify_Launch_App"
"@ | Out-File -FilePath (Join-Path "$TargetRoot\.maestro\test-suite" "TC_01_Verify_Launch_App.yaml") -Encoding utf8

Write-Host "[4/7] Generating PowerShell Runners & Linux CI runner from templates..." -ForegroundColor Green
# 1. run_tests_windows.ps1
$ps1Template = Join-Path "$TemplateDir\runners" "run_tests_windows.ps1"
$ps1Content = Get-Content $ps1Template -Raw -Encoding utf8
$cleanMap = @"
`$imageCompareMap_Free = @{
    "*TC_01_Verify_Launch_App*" = @(
        @{ Template = "assets/Free/TC_01_Verify_Launch_App.png"; CropId = `$null; Screenshot = "screenshots/TC_01_Verify_Launch_App" }
    )
}

`$imageCompareMap_Premium = @{
    "*TC_01_Verify_Launch_App*" = @(
        @{ Template = "assets/Premium/TC_01_Verify_Launch_App.png"; CropId = `$null; Screenshot = "screenshots/TC_01_Verify_Launch_App" }
    )
}

`$dualCompareMap = @{}
"@
$ps1Content = $ps1Content -replace 'Project: Logo Maker', "Project: $ProjectName"
$ps1Content = [regex]::Replace($ps1Content, '(?ms)\$imageCompareMap_Free = @\{.*?\$dualCompareMap = @\{.*?\}', $cleanMap)
$ps1Content | Out-File -FilePath (Join-Path $TargetRoot "run_tests_windows.ps1") -Encoding utf8

# 2. run_parallel.ps1
$parallelTemplate = Join-Path "$TemplateDir\runners" "run_parallel.ps1"
$parallelContent = Get-Content $parallelTemplate -Raw -Encoding utf8
$parallelContent = $parallelContent -replace 'Project: Logo Maker', "Project: $ProjectName"
$parallelContent = $parallelContent -replace 'Exclude = @\("TC_00", "TC_08_Test_Home_Screen"\)', 'Exclude = @()'
$parallelContent | Out-File -FilePath (Join-Path $TargetRoot "run_parallel.ps1") -Encoding utf8

# 3. run_tests.sh
$shTemplate = Join-Path "$TemplateDir\runners" "run_tests.sh"
$shContent = Get-Content $shTemplate -Raw -Encoding utf8
$shContent = $shContent -replace 'com.thmobile.logomaker', $AppId
$shContent = $shContent -replace 'Logo Maker', $ProjectName
$targetRepoName = if ($GitHubRepo) { $GitHubRepo } else { "owner/$ProjectName" }
$shContent = $shContent -replace 'hungnm-prog/logo-maker', $targetRepoName
$shContent | Out-File -FilePath (Join-Path $TargetRoot "run_tests.sh") -Encoding utf8

Write-Host "[5/7] Copying and adapting AI Agent intelligence (.agents/ & AGENTS.md)..." -ForegroundColor Green
$AgentsSourceDir = (Resolve-Path "$PSScriptRoot\..\..\..").Path
if ($AgentsSourceDir -ne (Join-Path $TargetRoot ".agents")) {
    Copy-Item -Path $AgentsSourceDir -Destination (Join-Path $TargetRoot ".agents") -Recurse -Force
}

# Adapt skills content
$creatorSkill = Join-Path "$TargetRoot\.agents\skills\maestro-test-creator" "SKILL.md"
if (Test-Path $creatorSkill) {
    $c = Get-Content $creatorSkill -Raw -Encoding utf8
    $c = $c -replace 'com.thmobile.logomaker', $AppId
    $c = $c -replace 'Logo Maker', $ProjectName
    $c | Out-File -FilePath $creatorSkill -Encoding utf8
}

# Generate AGENTS.md
$agentsMdTemplate = Join-Path "$AgentsSourceDir\rules" "maestro-android.md"
if (Test-Path $agentsMdTemplate) {
    $agentsMd = Get-Content $agentsMdTemplate -Raw -Encoding utf8
    $agentsMd = $agentsMd -replace 'com.thmobile.logomaker', $AppId
    $agentsMd = $agentsMd -replace 'Logo Maker', $ProjectName
    $agentsMd = $agentsMd -replace 'Samsung Galaxy S20 FE \(1080x2400 @ 480dpi, Android 13\)', $TargetDevice
    $agentsMd | Out-File -FilePath (Join-Path $TargetRoot "AGENTS.md") -Encoding utf8
    $agentsMd | Out-File -FilePath (Join-Path "$TargetRoot\.agents\rules" "maestro-android.md") -Encoding utf8
}

Write-Host "[6/7] Generating GitHub Actions CI/CD workflow (10 Shards Parallel with 1-day retention)..." -ForegroundColor Green
$ciTemplate = Join-Path "$TemplateDir\ci" "maestro_local.yml"
$ciContent = Get-Content $ciTemplate -Raw -Encoding utf8
$ciContent = $ciContent -replace 'com.thmobile.logomaker', $AppId
$ciContent = $ciContent -replace 'Logo Maker', $ProjectName
$ciContent | Out-File -FilePath (Join-Path "$TargetRoot\.github\workflows" "maestro_local.yml") -Encoding utf8

Write-Host "[7/7] Generating project README.md and Transfer Guide..." -ForegroundColor Green
# Starter README.md
@"
# $ProjectName — Mobile Automation Testing Framework

> **Hệ thống kiểm thử tự động chuyên nghiệp (End-to-End & Smart Visual Regression)** cho ứng dụng Android **$ProjectName** sử dụng **Maestro Framework**, **Python OpenCV** và **PowerShell Runners**.

---

## 📱 Thông Tin Ứng Dụng & Thiết Bị
- **Application ID**: \`$AppId\`
- **Thiết bị Mục tiêu**: $TargetDevice
- **Môi trường Thực thi**: Windows 11 (PowerShell terminal) & Linux / GitHub Actions CI/CD

---

## 📂 Cấu trúc Thư mục
\`\`\`text
$ProjectName/
├── .github/workflows/maestro_local.yml  # CI/CD chạy song song 10 máy ảo (retention-days: 1)
├── .maestro/
│   ├── config/                          # Common flows tái sử dụng (Launch, Ads, IAP, Bootstrap)
│   ├── test-suite/                      # Kịch bản kiểm thử tính năng cốt lõi (TC_01, TC_02...)
│   └── free-version/                    # Kịch bản kiểm thử riêng cho bản Free
├── assets/                              # Ảnh mẫu baseline chuẩn
│   ├── Free/                            # Baseline bản Free
│   └── Premium/                         # Baseline bản Premium
├── scripts/                             # Bộ công cụ Python OpenCV so sánh ảnh đa vùng
├── screenshots/                         # Ảnh chụp runtime từ thiết bị
├── reports/                             # Báo cáo JSON kiểm thử
├── run_tests_windows.ps1                # Runner chính trên Windows
├── run_parallel.ps1                     # Runner chạy song song nhiều thiết bị local
├── run_tests.sh                         # Runner trên Linux / macOS / CI
├── AGENTS.md                            # Quy chuẩn hoạt động cho AI Agent
└── README.md                            # Tài liệu dự án
\`\`\`

---

## 🚀 Hướng Dẫn Chạy Kiểm Thử

### 1. Chạy 1 Test Case cụ thể (Bản Premium):
\`\`\`powershell
.\run_tests_windows.ps1 -File "TC_01_Verify_Launch_App.yaml" -Version "Premium"
\`\`\`

### 2. Tự động lưu ảnh chụp runtime thành ảnh mẫu chuẩn (Update Baseline):
\`\`\`powershell
.\run_tests_windows.ps1 -File "TC_01_Verify_Launch_App.yaml" -Version "Premium" -UpdateBaseline
\`\`\`

### 3. Chạy toàn bộ test suite kèm khởi tạo máy mới:
\`\`\`powershell
.\run_tests_windows.ps1 -Folder "test-suite" -Version "Premium" -InitFirstRun
\`\`\`

### 4. Chạy song song nhiều thiết bị local:
\`\`\`powershell
.\run_parallel.ps1 -Version "Premium" -MaxDevices 2 -SkipInit
\`\`\`

---

## 🤖 Hướng dẫn AI Agent Tạo Test Mới
Người dùng chỉ cần yêu cầu:
> *"Hãy viết cho tôi test case kiểm tra [Tên Tính Năng], chụp ảnh assert giao diện và đăng ký vào runner."*
AI Agent sẽ tự động kết nối thiết bị lấy XML hierarchy, sinh file YAML chuẩn, chạy thử trên điện thoại và báo cáo kết quả!
"@ | Out-File -FilePath (Join-Path $TargetRoot "README.md") -Encoding utf8

# Transfer Guide
$transferGuideTemplate = Join-Path "$TemplateDir\docs" "AUTOMATION_TRANSFER_GUIDE.md"
if (Test-Path $transferGuideTemplate) {
    $transferGuide = Get-Content $transferGuideTemplate -Raw -Encoding utf8
    $transferGuide = $transferGuide -replace 'com.thmobile.logomaker', $AppId
    $transferGuide = $transferGuide -replace 'Logo Maker', $ProjectName
    $transferGuide | Out-File -FilePath (Join-Path "$TargetRoot\docs" "AUTOMATION_TRANSFER_GUIDE.md") -Encoding utf8
}

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "  SCAFFOLDING COMPLETED SUCCESSFULLY! (100% READY)" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "Target directory ready at: $TargetRoot" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Connect device: adb devices" -ForegroundColor Gray
Write-Host "  2. Test smoke run: .\run_tests_windows.ps1 -File 'TC_01_Verify_Launch_App.yaml' -UpdateBaseline" -ForegroundColor Gray

