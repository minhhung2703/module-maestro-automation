---
name: maestro-project-initializer
description: >
  Tự động khởi tạo và nhân bản 100% hệ thống Mobile Automation Testing chuẩn Enterprise
  (Maestro E2E + Python OpenCV Visual Regression + PowerShell Runners + 10-Device Parallel CI/CD)
  sang bất kỳ dự án ứng dụng Android mới nào chỉ với 1 câu lệnh.
---

# Maestro Project Initializer — Turnkey Project Scaffolder

> **Kích hoạt skill này** khi người dùng yêu cầu:
> - "Khởi tạo hệ thống automation cho dự án mới"
> - "Setup framework kiểm thử cho app..."
> - "Nhân bản hệ thống sang dự án mới..."
> - "Scaffold automation framework"

---

## MỤC TIÊU CỐT LÕI

Khi nhận được yêu cầu chuyển sang hoặc bắt đầu dự án mới, Agent không cần phải viết lại code hay cấu hình lại từ đầu. Thay vào đó, Agent sẽ:
1. Thu thập 3 thông số định danh ứng dụng mới: **Tên Ứng Dụng**, **Application ID (Package Name)**, và **Thư Mục Đích**.
2. Thực thi kịch bản Scaffolder tự động tạo ra **toàn bộ 100% hệ thống kiểm thử**: Cây thư mục 3 tầng, bộ runners điều phối, các sub-flows cốt lõi, pipeline CI/CD GitHub Actions 10 Shards (đã tối ưu `retention-days: 1`), hệ thống tài liệu `AGENTS.md`, `README.md`, và test case mẫu đầu tiên.
3. Chạy thử nghiệm Smoke Test đầu tiên (`TC_01_Verify_Launch_App.yaml`) để kiểm tra kết nối thiết bị và tự động chụp ảnh Baseline ban đầu.

---

## QUY TRÌNH THỰC THI (STEP-BY-STEP WORKFLOW)

### BƯỚC 1: Thu thập Thông số Đầu vào (Input Gathering)

Xác định 3 thông số bắt buộc:
- **`ProjectName`**: Tên hiển thị của ứng dụng (Ví dụ: `Video Editor Pro`, `Music Player`, `Fit Tracker`).
- **`AppId`**: Package ID chính xác của ứng dụng trên Android (Ví dụ: `com.company.videoeditor`).
- **`TargetFolder`**: Thư mục gốc của dự án mới (Ví dụ: `D:\video-editor` hoặc thư mục hiện tại `.`).
- **`TargetDevice`** *(Tùy chọn)*: Mặc định là `Samsung Galaxy S20 FE (1080x2400 @ 480dpi, Android 13)`.

*Lưu ý*: Nếu người dùng chưa cung cấp đủ `AppId` hoặc `ProjectName`, Agent phải **hỏi ngay** một cách ngắn gọn trước khi thực hiện.

---

### BƯỚC 2: Thực thi Script Scaffolder Tự Động

Agent gọi lệnh PowerShell thực thi công cụ khởi tạo (chạy trực tiếp từ thư mục skill):

```powershell
.\.agents\skills\maestro-project-initializer\scripts\scaffold_automation.ps1 -ProjectName "<Tên_Dự_Án>" -AppId "<Package_ID>" -TargetFolder "<Đường_Dẫn_Thư_Mục>"
```

**Script trên sẽ tự động hoàn tất:**
1. Tạo cây thư mục chuẩn: `.maestro/`, `scripts/`, `assets/`, `reports/`, `screenshots/`, `ui-dumps/`, `docs/`, `.github/workflows/`, `.agents/`.
2. Sao chép động cơ Python: `compare.py`, `compare_screens.py`, `merge_reports.py`, `template_service.py`.
3. Sinh các common flows dùng chung (`Launch_App.yaml`, `Close_Ads_Screen.yaml`, `Close_IAP_Screen.yaml`, `Init_First_Run_State.yaml`).
4. Sinh runner điều phối Windows (`run_tests_windows.ps1`), runner song song (`run_parallel.ps1`), và Linux/CI runner (`run_tests.sh`).
5. Cấu hình GitHub Actions CI/CD ma trận 10 Shards với chính sách quota an toàn (`retention-days: 1`).
6. Sinh `AGENTS.md`, `README.md`, và `docs/AUTOMATION_TRANSFER_GUIDE.md` đã điền sẵn tên dự án và App ID mới.
7. Tạo sẵn test case mẫu: `.maestro/test-suite/TC_01_Verify_Launch_App.yaml`.

---

### BƯỚC 3: Kiểm tra Kết nối Thiết bị & Ứng dụng

Chạy chẩn đoán nhanh trên thiết bị Android:
```powershell
# 1. Kiểm tra kết nối ADB
adb devices

# 2. Kiểm tra app đã được cài đặt trên thiết bị chưa
adb shell pm list packages | Select-String "<Package_ID>"
```

- Nếu app chưa được cài: Nhắc người dùng cài đặt file APK của app vào thiết bị.
- Nếu app đã có sẵn: Chuyển sang Bước 4.

---

### BƯỚC 4: Chạy Smoke Test Khởi Đầu & Tạo Baseline Chuẩn

Chạy thử kịch bản `TC_01_Verify_Launch_App.yaml` kèm cờ `-UpdateBaseline` để tự động chụp và lưu ảnh màn hình mở đầu làm baseline:

```powershell
.\run_tests_windows.ps1 -File "TC_01_Verify_Launch_App.yaml" -Version "Premium" -UpdateBaseline
```

---

### BƯỚC 5: Bàn giao Báo cáo cho Người dùng

Sau khi hoàn tất, Agent xuất báo cáo bàn giao:

```markdown
## 🎉 Khởi Tạo Dự Án Automation Thành Công 100%!

- **Tên Ứng Dụng**: <Tên_Dự_Án>
- **Application ID**: `<Package_ID>`
- **Thư Mục Dự Án**: `<Đường_Dẫn>`

### 📦 Các thành phần đã sẵn sàng:
1. **Runner điều phối**: `run_tests_windows.ps1`, `run_parallel.ps1`, `run_tests.sh`
2. **Common Sub-flows**: `.maestro/config/` (`Launch_App.yaml`, `Close_Ads`, `Close_IAP`, `Init_First_Run`)
3. **Smoke Test Case**: `.maestro/test-suite/TC_01_Verify_Launch_App.yaml` (Đã lưu baseline chuẩn)
4. **Hệ thống Visual Regression**: `scripts/compare.py` (Đo đa vùng Dynamic Multi-Zone + MAE)
5. **CI/CD GitHub Actions**: `.github/workflows/maestro_local.yml` (10 Shards Parallel)
6. **Bộ quy tắc & Kỹ năng AI**: `AGENTS.md` và `.agents/skills/maestro-test-creator`

### 🚀 Lệnh thực thi tiếp theo:
```powershell
# Chạy test case vừa tạo:
.\run_tests_windows.ps1 -File "TC_01_Verify_Launch_App.yaml" -Version "Premium"

# Nhờ AI viết thêm test case mới:
"Hãy viết cho tôi test case kiểm tra [Tên_Màn_Hình], chụp ảnh assert và đăng ký runner."
```
```

