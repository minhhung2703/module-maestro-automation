# Automation Engineer - Maestro Working Rules (Android Platform)

> **Mục tiêu**: Bộ quy tắc chuẩn dành cho AI Agent khi thiết kế, triển khai, debug và thực thi kịch bản kiểm thử tự động (Mobile Automation Testing) bằng **Maestro Framework** cho ứng dụng Android trên môi trường Windows & GitHub Actions CI/CD.

---

## ⛔ QUY TẮC BẮT BUỘC (STRICT CONSTRAINTS)

1. **BẢO TOÀN TRẠNG THÁI APP (CLEAR STATE AWARENESS)**:
   - Không tùy tiện sử dụng `clearState: true` trong `Launch_App.yaml` vì sẽ xóa mất trạng thái đã kích hoạt Premium và thiết lập First-Run của người dùng.
2. **REPORT PHẢI ĐẦY ĐỦ THÔNG TIN LỖI & SO SÁNH ẢNH**:
   - Khi test bị fail, report JSON bắt buộc phải trích xuất chính xác `FailedStep` và `ErrorMessage`.
   - Kết quả so sánh hình ảnh visual phải hiển thị mảng đầy đủ `ImageComparisons` của tất cả các ảnh, không được bỏ sót.
3. **BẢO VỆ PHIÊN BẢN FREE (`.maestro/free-version/`)**:
   - Tuyệt đối không tự ý sửa đổi hoặc xóa các file trong thư mục `.maestro/free-version/` khi đang thực thi nhiệm vụ trên nhánh Premium (`test/new_version/premium`). Chỉ chỉnh sửa thư mục này khi có yêu cầu rõ ràng từ người dùng cho bản Free.

---

## 1. Thông tin Dự án & Môi trường

- **Application ID**: `com.thmobile.logomaker`
- **Nền tảng**: Android (Emulator / Real Device kết nối qua ADB)
- **Thiết bị Mục tiêu**: Samsung Galaxy S20 FE (1080x2400 @ 480dpi, Android 13)
- **Hệ điều hành Thực thi**: Windows 11 (PowerShell terminal) & Linux (Ubuntu GitHub Actions)
- **Bộ công cụ Cốt lõi**:
  - **Maestro CLI**: Thực thi kịch bản test flow (`.yaml`).
  - **ADB (Android Debug Bridge)**: Quản lý thiết bị, chụp UI dump, chuyển file.
  - **PowerShell Runners**:
    - `.\run_tests_windows.ps1`: Runner chính thức điều phối test suite, sharding, kiểm tra device, dọn session, gọi Python compare.
    - `.\run_parallel.ps1`: Runner chạy song song nhiều thiết bị Local với hàng đợi thông minh.
  - **Python (Visual Regression & Computer Vision)**:
    - `scripts/compare.py`: So sánh đa vùng Dynamic Multi-Zone.
    - `scripts/compare_screens.py`: So sánh 2 ảnh chụp runtime (Dual Compare).
    - `scripts/template_service.py`: Daemon HTTP (Port 8765) dùng OpenCV quét và tap template không có UI ID.
    - `scripts/merge_reports.py`: Tổng hợp báo cáo từ nhiều Shards/máy ảo.

---

## 2. Cấu trúc Thư mục Dự án

```text
logo-maker/
├── .github/
│   └── workflows/
│       └── maestro_local.yml     # CI/CD chạy song song 10 máy ảo (10 Shards Parallel)
├── .maestro/
│   ├── config/                   # Common flows tái sử dụng (Launch, Ads, IAP, Popups, Bootstrap)
│   │   ├── Init_First_Run_State.yaml      # Luồng Bootstrap vượt qua First-Run (Solution 3)
│   │   ├── Launch_App.yaml                # Khởi động app an toàn (clearState: false)
│   │   ├── Launch_App_Clear_State.yaml    # Khởi động app xóa sạch state
│   │   ├── Navigate_To_Restaurant_Edit.yaml # Điều hướng vào Edit Screen qua OpenCV daemon
│   │   ├── Close_Ads_Screen.yaml          # Xử lý đóng quảng cáo
│   │   └── Close_IAP_Screen.yaml          # Xử lý đóng màn hình thanh toán
│   ├── test-suite/               # 16 Kịch bản kiểm thử tính năng cốt lõi (TC_00 -> TC_14)
│   └── free-version/             # Luồng test riêng cho bản Free
├── assets/                       # Ảnh baseline mẫu để so sánh visual
│   ├── Premium/                  # Ảnh mẫu riêng cho gói Premium
│   └── Free/                     # Ảnh mẫu riêng cho bản Free
├── docs/                         # Tài liệu chuyển giao & kịch bản kiểm thử
│   ├── AUTOMATION_TRANSFER_GUIDE.md       # Cẩm nang chuyển giao chi tiết từ A-Z
│   ├── REPORT_ASSETS_PREMIUM_COMPARISON.md # Phân tích đối sánh Visual Baseline
│   └── test-cases/                        # Đặc tả ca kiểm thử gốc
│       ├── Mockup_Preview_Screen_TestCases.txt # 12 ca kiểm thử Mockup Preview
│       └── ...
├── reports/                      # Báo cáo JSON & log thực thi
├── screenshots/                  # Ảnh chụp runtime từ thiết bị trong quá trình test
│   └── debug/                    # Ảnh chụp tạm phục vụ debug lỗi
├── scripts/                      # Scripts bổ trợ: Python OpenCV, JS bridge, Merge report
├── ui-dumps/                     # Dữ liệu dump XML phân tích hierarchy từ thiết bị
├── run_tests_windows.ps1         # Test runner chính thức trên Windows
├── run_parallel.ps1              # Test runner chạy song song nhiều thiết bị
├── run_tests.sh                  # Test runner trên Linux / GitHub Actions
├── AGENTS.md                     # Quy tắc chuẩn mực hoạt động của Agent (File này)
└── README.md                     # Tài liệu tổng quan dự án
```

---

## 3. Quy chuẩn Thiết kế Test Flow (`.yaml`)

Mọi test case mới tạo (ví dụ: `.maestro/test-suite/TC_*.yaml`) phải tuân thủ nghiêm ngặt các quy tắc sau:

### 3.1. Header và Khởi động Flow
- Luôn khai báo `appId` ở đầu file và phân tách bằng `---`.
- Bắt đầu test case bằng common flow khởi tạo:
  ```yaml
  appId: com.thmobile.logomaker
  ---
  - runFlow: "../config/Launch_App.yaml"
  ```

### 3.2. Cơ chế Bootstrap First-Run (Solution 3)
- Đối với môi trường máy mới, máy ảo GitHub Actions hoặc sau khi `pm clear`:
  - Luôn sử dụng cờ `-InitFirstRun` hoặc gọi flow [`.maestro/config/Init_First_Run_State.yaml`](file:///d:/logo-maker/.maestro/config/Init_First_Run_State.yaml) đầu tiên.
  - Flow này tự động: Chọn Language (English) -> Next 3 màn Onboarding -> Đóng IAP/Ads -> Vào 1 template bất kỳ -> Bấm `back` 8 lần giải phóng toàn bộ 8 tooltip Intro -> Relaunch app về Home Screen sạch sẽ.

### 3.3. Xử lý Popup ngoại lệ, Ads & Tải Template (Anti-Flaky)
- **Popup IAP & Ads**:
  ```yaml
  - runFlow:
      when:
        visible:
          text: "Get Full Access"
      file: "../config/Close_IAP_Screen.yaml"

  - runFlow:
      when:
        visible: "Close"
      file: "../config/Close_Ads_Screen.yaml"
  ```
- **Popup "Downloading resources" khi mở template**:
  Khi tải template đồ họa lần đầu, app hiển thị popup tải tài nguyên. Bắt buộc xử lý:
  ```yaml
  - runFlow:
      when:
        visible: "Downloading resources"
      commands:
        - runFlow:
            when:
              visible: "Download in background"
            commands:
              - tapOn: "Download in background"
        - extendedWaitUntil:
            notVisible: "Downloading resources"
            timeout: 30000
  ```

### 3.4. Thứ tự Ưu tiên Element Selector (Tránh phụ thuộc tọa độ)
1. **Ưu tiên 1 (`id`)**: Dùng `resource-id` (ổn định nhất, không phụ thuộc ngôn ngữ):
   ```yaml
   - tapOn:
       id: "btnTemplate"
   ```
2. **Cơ chế Selector Đa Hình (Polymorphic Regex)**:
   - Trên Edit Screen, nút Lưu có ID là `mnItemSave` ở bản Free nhưng tự động đổi thành `mnItemSavePremium` ở bản Premium.
   - Bắt buộc dùng regex: `id: ".*mnItemSave.*"` cho cả `assertVisible` và `tapOn` để tương thích 100% trên cả hai môi trường:
     ```yaml
     - assertVisible:
         id: ".*mnItemSave.*"
     - tapOn:
         id: ".*mnItemSave.*"
     ```
3. **Ưu tiên 2 (`text` + ngữ cảnh)**: Kết hợp `containsDescendants`, `below`, `above`, `index` khi ID bị trùng:
   ```yaml
   - tapOn:
       id: "imageView"
       index: 0
       below:
         text: "Restaurant"
   ```
4. **Ưu tiên 3 (`point`)**: Chỉ sử dụng click theo toạ độ `point: "x%, y%"` cho vùng vẽ Canvas hoặc thanh chọn màu Color Picker khi không có element con trong XML hierarchy.
   - *Lưu ý*: Với màn hình tỉ lệ 20:9 (1080x2400), tâm của Canvas vuông nằm ở khoảng `point: "50%, 35%"` (y ≈ 850px), tránh bấm trượt lên mép trên (`30%`).

### 3.5. Chờ & Cuộn màn hình (Waits & Scrolling)
- **Không dùng `sleep` cứng** kéo dài trừ khi chờ xử lý tác vụ mạng hoặc AI generation.
- Ưu tiên dùng:
  - `extendedWaitUntil`: Chờ element xuất hiện/biến mất với timeout tối đa.
  - `waitForAnimationToEnd`: Chờ animation hoàn tất trước khi bấm tiếp.
  - `scrollUntilVisible`: Tự động cuộn đến khi element hiển thị thay vì nhiều lệnh `swipe` liên tiếp.
- Gọi `- hideKeyboard` trước khi thao tác các nút nằm ở phần dưới màn hình để tránh bàn phím che khuất.

### 3.6. Quy chuẩn Thoát màn hình An toàn (Safe Exit Pattern)
- Khi hoàn tất chỉnh sửa ở Edit Screen và muốn quay về Home Screen:
  - Tránh dùng chuỗi lặp `Navigate up` phức tạp dễ bị kẹt trên activity trung gian.
  - Sử dụng cơ chế khởi động lại an toàn:
    ```yaml
    - stopApp
    - launchApp:
        clearState: false
        permissions:
          all: allow
    - waitForAnimationToEnd:
        timeout: 5000
    - extendedWaitUntil:
        visible:
          id: "btnTemplate"
        timeout: 10000
    ```

### 3.7. Quy chuẩn Luồng Lưu / Xuất Đồ họa Thích ứng (Adaptive Save Flow)
- Khi lưu Mockup hoặc Logo trên các phiên bản khác nhau:
  - **Bản Free**: Thường mở dialog `tvSaveMockupTitle` $\rightarrow$ bấm nút `btn_save_with_watermark` $\rightarrow$ hiện quảng cáo.
  - **Bản Premium**: Bấm nút Lưu sẽ lưu trực tiếp không qua dialog, hiển thị Toast thành công và nút chuyển ngay lập tức sang `btnShare`.
  - Kịch bản test phải thiết kế luồng kiểm tra điều kiện (conditional flow qua `when: visible`) để chạy trơn tru trên cả 2 phiên bản mà không bị vướng assertion:
    ```yaml
    - runFlow:
        when:
          visible:
            id: "tvSaveMockupTitle"
        commands:
          - tapOn:
              id: "btn_save_with_watermark"
    - extendedWaitUntil:
        visible:
          id: "btnShare"
        timeout: 10000
    ```

### 3.8. Xử lý Tải ảnh Bất đồng bộ từ Mạng (Asynchronous Network Image Loading)
- Lệnh `waitForAnimationToEnd` chỉ đợi hiệu ứng chuyển Activity hoàn tất (~300ms), **không thể đợi thư viện Glide tải ảnh qua mạng internet** (ví dụ: các ô mẫu Style Magic AI).
- Để tránh chụp phải màn hình trắng khi ảnh mạng chưa kịp tải, bắt buộc thêm đoạn delay đồng bộ trước khi chụp:
  ```yaml
  - waitForAnimationToEnd:
      timeout: 20000

  - evalScript: ${var start = new Date().getTime(); while (new Date().getTime() < start + 3500); output.waited = true}

  - takeScreenshot: "screenshots/TC_03_Verify_Navigated_to_Style_Magic_AI_Screen"
  ```

### 3.9. Độ nhạy Tần số Cảm ứng & Thời lượng Vuốt Kéo (`duration` trên `swipe`)
- **Tránh dùng `duration: 50` ms**: Cú vuốt 50ms quá nhanh (0.05s). Màn hình 60Hz thường drop gesture này (layer không di chuyển), trong khi màn 120Hz/240Hz của Samsung lại nhận diện thành cú kéo đầy đủ (layer bị lệch so với baseline trượt cũ).
- **Quy chuẩn**: Khi thực hiện kéo di chuyển layer hoặc con trỏ trên Canvas, luôn chỉ định `duration` từ **`300` ms đến `500` ms** (hoặc dùng `tapOn: point: "x%, y%"` nếu chỉ muốn kích hoạt thanh công cụ mà không xê dịch vị trí layer).

### 3.10. Khớp Dialog Chia sẻ Hệ thống Đa Ngôn ngữ (System Share Sheet Polymorphic Assertions)
- Hộp thoại Chia sẻ hệ thống của Android (`com.android.intentresolver`) có văn bản hiển thị thay đổi theo ngôn ngữ máy: Tiếng Anh (`Personal`, `Sharing image`), Tiếng Việt (`Cá nhân`).
- Bắt buộc dùng regex bao quát để không bị crash test khi chạy trên máy có cài đặt ngôn ngữ khác nhau:
  ```yaml
  - assertNotVisible: ".*(Personal|Cá nhân|Sharing image).*"
  ```
- Đồng thời runner `run_tests_windows.ps1` luôn tự động chạy `am force-stop com.android.intentresolver` trước mỗi lượt test để đóng triệt để mọi dialog chia sẻ còn sót lại.

### 3.11. Tránh Chọn Nhầm Category Khi Phân Trang Ngang (Relative Indexing Context)
- Khi Home Screen có nhiều danh mục (Categories) có cấu trúc giao diện tương đồng:
  - Nếu chỉ dùng `below: "Beauty & Wellness"`, hệ thống có thể chọn nhầm sang thẻ ở category phía dưới.
  - Phải dùng cấu trúc `below` kèm `index: 1` hoặc `containsDescendants` chặt chẽ:
    ```yaml
    - tapOn:
        id: "imageView"
        below:
          text: "Beauty & Wellness"
          index: 1
    ```

---

## 4. Quy tắc Visual Testing & Chụp ảnh Màn hình

1. **Quy chuẩn Đặt tên Screenshot (Tránh Xung đột)**:
   - Tên screenshot bắt buộc phải có tiền tố mã Test Case tương ứng:
     ```yaml
     - takeScreenshot: "screenshots/TC_11_Verify_Navigated_To_Mockup_Preview_Screen"
     ```
   - Tuyệt đối không dùng tên chung chung (như `screenshots/Verify_Screen`) vì sẽ bị ghi đè khi chạy test song song nhiều thiết bị.
2. **Quy trình Đăng ký vào PowerShell Runner (`run_tests_windows.ps1`)**:
   - Khi tạo screenshot mới, bắt buộc đăng ký vào `$imageCompareMap_Premium` và `$imageCompareMap_Free` trong file `run_tests_windows.ps1`.
   - Cung cấp ảnh mẫu chuẩn tương ứng vào `assets/Premium/` và `assets/Free/` (hoặc dùng cờ `-UpdateBaseline` để tự động lưu ảnh chuẩn từ runtime).
3. **Cơ chế So Sánh Đa Mật Độ Điểm Ảnh (Cross-Device & Cross-DPI Visual Regression)**:
   - Baseline chuẩn gốc được chụp trên Samsung Galaxy S20 FE (`1080x2400 @ 480dpi`).
   - Khi chạy trên thiết bị có DPI khác (như Google Pixel 6 `1080x2400 @ 420dpi`), `scripts/compare.py` tự động kích hoạt thuật toán Cross-DPI:
     - Sử dụng cửa sổ trượt dung sai dọc $\pm 20\text{–}30\text{px}$ để bù đắp sự chênh lệch chiều cao Status Bar / Navigation Bar giữa các hãng Android.
     - Duy trì Fast-path 1:1 cho máy 480dpi (Samsung S20 FE & GitHub Actions CI) để tối ưu tốc độ so khớp.
     - Thứ tự kiểm tra: Quét Canvas căn chỉnh cấu trúc trước khi fallback sang Sparse UI để tránh nhận nhầm các ô thẻ Mockup Preview hoặc tab Text Curve.
4. **Khóa Chiều Xoay Màn Hình Cố định (Portrait Orientation Lock)**:
   - Một số màn hình đặc thù (như Mockup Preview) có thể bị xoay ngang nếu thiết bị rung lắc hoặc để nghiêng. Runner `run_tests_windows.ps1` luôn tự động khóa cứng chiều dọc qua ADB (`accelerometer_rotation 0` và `user_rotation 0`) trước khi bắt đầu test.
5. **Quy chuẩn Loại trừ Kịch bản Ngoại lệ (`-Exclude`)**:
   - Khi chạy toàn bộ thư mục `test-suite`, luôn loại trừ kịch bản thanh toán Google Play (`TC_00`) và file Home lỗi cú pháp (`TC_08_Test_Home_Screen`):
     ```powershell
     .\run_tests_windows.ps1 -Folder "test-suite" -Version "Premium" -Exclude "TC_00,TC_08_Test_Home_Screen"
     ```

---

## 5. Quy trình Chạy & Debug Test Case trên Windows

### 5.1. Chạy Test từ Terminal
- **Chạy 1 file cụ thể (Chế độ Premium)**:
  ```powershell
  .\run_tests_windows.ps1 -File "TC_11_Test_Mockup_Preview_Screen.yaml" -Version "Premium"
  ```
- **Chỉ định thiết bị cụ thể khi cắm nhiều máy (Real device & Emulator)**:
  ```powershell
  .\run_tests_windows.ps1 -File "TC_11_Test_Mockup_Preview_Screen.yaml" -Device "R3CNA099XKL" -Version "Premium"
  ```
- **Chạy toàn bộ thư mục test kèm khởi tạo máy mới**:
  ```powershell
  .\run_tests_windows.ps1 -Folder "test-suite" -Version "Premium" -InitFirstRun -Exclude "TC_00","TC_08_Test_Home_Screen"
  ```
- **Chạy song song nhiều thiết bị local (bỏ qua init nếu đã ở Home)**:
  ```powershell
  .\run_parallel.ps1 -File "TC_03_Test_Art_Tool_On_Edit_Screen" -Version "Premium" -SkipInit
  ```
- **Chạy trực tiếp qua Maestro CLI để debug nhanh**:
  - *Lưu ý*: Nếu test case cần chọn template nhà hàng qua OpenCV, phải khởi động template service daemon trước:
    ```powershell
    Start-Process py -ArgumentList "scripts/template_service.py"
    maestro --device <SERIAL> test .maestro/test-suite/TC_11_Test_Mockup_Preview_Screen.yaml
    ```

### 5.2. Khắc phục sự cố thường gặp (Troubleshooting)

1. **Lỗi ứng dụng bị gỡ bỏ cho user 0 (`Package not installed for user 0`)**:
   - Khắc phục:
     ```powershell
     adb shell cmd package install-existing --user 0 com.thmobile.logomaker
     ```
2. **Kẹt 8 Tooltips Intro trên Edit Screen sau khi cài mới**:
   - Khắc phục: Gửi 8 sự kiện phím BACK để giải phóng toàn bộ tooltips che phủ:
     ```powershell
     1..8 | ForEach-Object { adb shell input keyevent 4; Start-Sleep -Milliseconds 500 }
     ```
3. **Lỗi "Failed to connect to device / Session lock"**:
   - Khắc phục:
     ```powershell
     Remove-Item "$HOME\.maestro\sessions" -Recurse -Force -ErrorAction SilentlyContinue
     ```
4. **Lỗi ADB offline / không nhận thiết bị**:
   - Khắc phục:
     ```powershell
     adb kill-server
     adb start-server
     adb devices
     ```
5. **Kẹt Template Service Daemon (Port 8765)**:
   - Khắc phục:
     ```powershell
     Get-Process | Where-Object { $_.ProcessName -like "*python*" } | Stop-Process -Force
     ```
6. **Lấy UI Hierarchy để tìm ID element mới**:
   - Dùng lệnh xuất dump XML sạch trực tiếp từ thiết bị:
     ```powershell
     adb shell uiautomator dump /sdcard/uidump.xml
     adb pull /sdcard/uidump.xml ui-dumps/current_ui_dump.xml
     ```
7. **Quản lý Hạn mức Lưu trữ GitHub Actions (0.5 GB quota)**:
   - Trong `.github/workflows/maestro_local.yml`, luôn duy trì `retention-days: 1` hoặc `2` ở bước `upload-artifact` để tự dọn dẹp ảnh chụp màn hình sau mỗi đợt chạy.

---

## 6. Tiêu chí Hoàn thành (Definition of Done cho Agent)

Khi nhận yêu cầu viết hoặc sửa một test case Maestro:
1. File `.yaml` phải có cấu trúc chuẩn, phân chia block comment rõ ràng (`# Step 1: ...`, `# Step 2: ...`).
2. Sử dụng selector bền vững (`id` > `text` > `descendants`), áp dụng regex selector đa hình `.*mnItemSave.*` khi thao tác nút Save.
3. Đã có bước xử lý popup, quảng cáo hoặc dialog tải template dự phòng.
4. Tên screenshot có tiền tố định danh duy nhất (`TC_{ID}_...`).
5. Đã đăng ký so sánh ảnh vào `$imageCompareMap` trong `run_tests_windows.ps1` và có ảnh baseline trong `assets/Premium/`.
6. Đảm bảo chạy thử thực tế trên thiết bị/máy ảo và đạt trạng thái **PASSED**.
7. Báo cáo sinh ra có đầy đủ thông tin `FailedStep`, `ErrorMessage` (nếu fail) và mảng `ImageComparisons`.

---

## 7. MƯỜI TRỤ CỘT KỸ THUẬT CỐT LÕI & BÀI HỌC THỰC CHIẾN (THE 10 ENGINEERING PILLARS)

Bộ 10 trụ cột kiến thức chuyên sâu đúc kết từ quá trình debug và tối ưu hóa hệ thống kiểm thử Logo Maker:

### Trụ cột 1: Cơ chế RecyclerView & Trôi Index (View Recycling & Computer Vision)
- **Bản chất**: Trên màn hình danh sách Category "Food & Drink", Android chỉ tạo sẵn 4–6 `ViewHolder` trong bộ nhớ và liên tục tái chế (recycle) chúng khi người dùng cuộn. Các thuộc tính như `index: 0` hay `index: 5` bị trôi dạt và thay đổi đối tượng hiển thị liên tục sau mỗi lần cuộn.
- **Giải pháp**: Bắt buộc dùng Thị giác máy tính (Computer Vision) qua `scripts/template_service.py` (daemon HTTP port 8765) và `cv2.matchTemplate`. Daemon quét tìm ảnh mẫu `assets/template_restaurant.png` trên toàn màn hình và tap thẳng vào tọa độ tâm của đối tượng mà không phụ thuộc vào thứ tự index trong XML hierarchy.

### Trụ cột 2: Tọa độ thao tác phần cứng (ADB Gestures & "Vết chạm chết" $x = 540$)
- **Bản chất**: Trên màn hình 1080×2400 bố trí lưới template 2 cột, đường thẳng đứng chính giữa màn hình $x = 540$ là rãnh phân cách tĩnh (divider space). Khi ADB gửi lệnh `input swipe 540 ...`, điểm chạm rơi vào khoảng trống không thuộc bất kỳ item nào, khiến hệ điều hành nuốt sự kiện và làm đơ thanh cuộn (`scroll stuck`).
- **Giải pháp**:
  - Không vuốt tại $x = 540$. Luôn tính toán tọa độ động: $x = \text{screen\_w} \times 0.30$ (nằm giữa cột 1) hoặc vuốt trong vùng an toàn $y \in [50\%, 20\%]$.
  - Tích hợp cơ chế phát hiện kẹt màn hình (`stuck_count >= 2` trong `select_premium_template.py`) để tự động chạm điểm an toàn $x = 75\%, y = 70\%$ giải phóng overlay trước khi cuộn tiếp.

### Trụ cột 3: Mạng ảo Android Emulator trên CI (netsim & DNS)
- **Bản chất**: Khi chạy giả lập trên môi trường Linux Headless (GitHub Actions Runner), module mạng `netsim` mặc định bị nghẽn DNS nội bộ, khiến ứng dụng không thể phân giải tên miền máy chủ CDN và không tải được danh sách template đồ họa.
- **Giải pháp**: Bắt buộc cấu hình bộ 3 tham số cứu cánh trong `emulator-options` của file `.github/workflows/maestro_local.yml`:
  ```yaml
  emulator-options: -no-window -no-snapshot -noaudio -no-boot-anim -camera-back none -gpu swiftshader_indirect -dns-server 8.8.8.8 -netdelay none -netspeed full
  ```
  kèm `disable-animations: true` để giải phóng toàn bộ băng thông mạng và vô hiệu hóa animation chuyển cảnh.

### Trụ cột 4: Tải ảnh bất đồng bộ (Glide/CDN) & Điểm số OpenCV rơi vào ~0.32
- **Bản chất**: Khi đường truyền mạng chậm hoặc app vừa cài mới, Glide chưa kịp tải ảnh mẫu từ máy chủ. RecyclerView chỉ hiển thị các khung xám placeholder. Khi OpenCV quét màn hình tìm `template_restaurant.png`, việc so khớp ảnh mẫu màu với khung xám chỉ đạt điểm tương quan $R \approx 0.30 - 0.35$ (dưới ngưỡng tối thiểu 0.70).
- **Giải pháp**:
  - Chèn khối chờ dialog tài nguyên biến mất hoàn toàn:
    ```yaml
    - extendedWaitUntil:
        notVisible: "Downloading resources"
        timeout: 30000
    ```
  - Chèn độ trễ đồng bộ 3.5s (`evalScript` với while loop timestamp) trước khi chụp ảnh để Glide nạp đủ thumbnail từ mạng.

### Trụ cột 5: Hiệu ứng Domino & Phân tích nguyên nhân gốc (RCA: TC_01 vs TC_03 → TC_14)
- **Hiện tượng**: `TC_01` luôn PASS (do chọn category trực tiếp trên Home), trong khi `TC_03` đến `TC_14` đều bị FAIL tại bước `assertVisible: "Logos4U"`.
- **Nguyên nhân gốc (RCA)**: Các test `TC_03` $\to$ `TC_14` đều gọi chung luồng `Navigate_To_Restaurant_Edit.yaml`. Khi bước OpenCV trước đó không tìm được template do mạng lag hoặc kẹt scroll, app vẫn đứng ở màn Category chứ chưa bao giờ vào Edit Screen. Do đó, bước kiểm tra tiêu đề `"Logos4U"` ở màn hình sau bị fail dây chuyền.
- **Bài học**: Khi debug kiểm thử tự động, không chỉ nhìn vào bước báo FAILED trong report mà phải lần ngược lại chuỗi hành động tiền đề (Pre-conditions) để xác định điểm gãy thực sự.

### Trụ cột 6: Xử lý Popup bất đồng bộ (Delayed IAP/Ads & Self-Healing 8 màn Intro)
- **Bản chất**: Popup quảng cáo và In-App Purchase thường được nạp bất đồng bộ qua SDK và bật lên trễ sau 6 đến 8 giây kể từ khi mở màn hình, dễ che khuất các phần tử UI của bước test tiếp theo. Đồng thời, khi mở Edit Screen lần đầu, app hiển thị liên hoàn 8 bong bóng hướng dẫn (Intro tooltips).
- **Giải pháp Self-Healing**:
  - Áp dụng cơ chế thoát bong bóng tự phục hồi:
    ```yaml
    - repeat:
        times: 8
        while:
          notVisible:
            id: "mnItemSave"
        commands:
          - back
          - waitForAnimationToEnd:
              timeout: 800
    ```
  - Bao bọc toàn bộ popup ngoại lệ trong khối điều kiện `when: visible: "Close"`.

### Trụ cột 7: Bẫy dung lượng lưu trữ (Storage Quota) trên GitHub Actions
- **Bản chất**: Chạy song song 10 Shards máy ảo, mỗi máy chụp hàng chục ảnh PNG 1080×2400. Tổng dung lượng artifacts dễ dàng vượt quá hạn ngạch 500MB miễn phí của GitHub Actions, gây lỗi ngắt pipeline `Storage quota exceeded`.
- **Giải pháp**:
  - Cấu hình `retention-days: 1` trong bước `upload-artifact` để GitHub tự động dọn rác ảnh chụp sau 24 giờ.
  - Sử dụng script `scripts/merge_reports.py` tổng hợp 10 file JSON báo cáo thành 1 bảng tóm tắt Markdown gọn nhẹ (~5KB) gắn trực tiếp vào `$GITHUB_STEP_SUMMARY`, vừa theo dõi tức thì vừa không chiếm hạn ngạch lưu trữ.

### Trụ cột 8: Điều phối Đa Thiết Bị Song Song (Multi-Device Parallelism) & Tranh Chấp File Lock trên Windows
- **Bản chất xung đột File Lock**: Maestro CLI trên nền tảng Windows sử dụng H2/RocksDB KeyValueStore lưu thông tin phiên làm việc vào `$HOME/.maestro/sessions`. Khi PowerShell chạy song song nhiều Worker (`Start-Job`) cùng một mili-giây, tiến trình Java thứ hai sẽ bị từ chối truy cập do cơ chế khóa file độc quyền của Windows (`java.io.IOException: The process cannot access the file because another process has locked a portion of the file`), dẫn đến Worker bị hủy ngay tại bước bootstrap.
- **Giải pháp Stagger Launch**: Thêm độ trễ kích hoạt 3 giây (`Start-Sleep -Seconds 3`) giữa các lần `Start-Job` trong runner `run_parallel.ps1`. Khoảng trễ này đảm bảo tiến trình Maestro đầu tiên khởi tạo xong phiên và lắng nghe socket trước khi tiến trình tiếp theo khởi chạy.

### Trụ cột 9: Cạn kiệt Ổ Đĩa Host (%TEMP% APK Exhaustion) & Phục Hồi Thất Bại Thông Minh (-Resume)
- **Bản chất rò rỉ dung lượng**: Mỗi lần Maestro CLI thực thi kịch bản, nó tự động giải nén `maestro-server.apk` vào thư mục tạm `%USERPROFILE%\AppData\Local\Temp` dưới dạng `tmp*.apk` (~40MB mỗi file). Sau hàng trăm lần chạy, hàng trăm file tạm tích tụ ngốn từ 10GB đến 20+ GB khiến ổ đĩa C: rơi vào tình trạng 0.0 GB Free (`java.io.IOException: There is not enough space on the disk`), làm tất cả các test case sau đó đồng loạt FAILED sau 2-4 giây.
- **Giải pháp Tự động Dọn Rác & Smart Resume**:
  - Tự động xóa sạch `*tmp*.apk` và các file `*.tmp` rác trong `%TEMP%` ở cả đầu và cuối chu trình chạy của runner `run_parallel.ps1`.
  - Cung cấp tham số `-Resume`: Khi chuỗi test bị gián đoạn do sự cố ngoại cảnh, runner đọc lại `reports/parallel_local/report_*.json`. Các test case đã `PASSED` ở phiên trước sẽ được tự động giữ nguyên và bỏ qua không chạy lại; chỉ những test chưa chạy hoặc bị `FAILED` mới được đưa vào hàng đợi (`$queue`) để phân bổ cho các Worker rảnh, tiết kiệm hàng chục phút kiểm thử lặp lại vô ích.

### Trụ cột 10: Visual Regression Đa Mật Độ Điểm Ảnh (Cross-DPI / Cross-Device)
- **Bản chất chênh lệch DPI**: Các thiết bị Android thực tế có mật độ hiển thị khác nhau (ví dụ: Google Pixel 6 chạy ở 420dpi, Samsung Galaxy S20 FE chạy ở 480dpi) dù cùng độ phân giải vật lý $1080 \times 2400$. Hệ thống layout và kích thước icon/tool zone trên 420dpi sẽ nhỏ hơn so với 480dpi theo tỉ lệ $420 / 480 = 0.875$.
- **Giải pháp Multi-Scale Normalization**:
  - Thuật toán `scripts/compare.py` sử dụng tập tỉ lệ candidate DPI scales ($0.875, 1.0, 1.143$) kết hợp bù trừ Status Bar offset và đánh giá vùng cục bộ (`_score_tool_zone_cross_dpi`), giúp bộ ảnh mẫu Baseline chụp trên thiết bị 480dpi vẫn so khớp đạt tỉ lệ tuyệt đối (90% – 100%) khi thực thi trên thiết bị 420dpi mà không cần phải chụp lại bộ baseline riêng cho từng dòng máy.

### Trụ cột 11: Lỗi Mã Hóa Ký Tự Đầu Ra Trên Windows (`UnicodeEncodeError: 'charmap'` trong Python Daemon)
- **Bản chất**: Trên Windows, khi một tiến trình Python daemon ngầm (như `template_service.py` hoặc các helper script gọi ADB/OpenCV) được khởi chạy và redirect stdout/stderr ra file log bằng PowerShell (`Start-Process -RedirectStandardOutput ...`), Python mặc định sử dụng bảng mã OEM của hệ thống (thường là `cp1252` hoặc `cp936`). Khi script in các chuỗi log có dấu tiếng Việt (ví dụ: `print(f"... Chờ ảnh tải qua mạng ...")`), Python văng ngoại lệ `UnicodeEncodeError: 'charmap' codec can't encode character '\u1edd'` và crash ngay lập tức tiến trình HTTP service ở cổng 8765. Hậu quả là toàn bộ các test case gọi daemon OpenCV đều bị đứt kết nối và FAIL đồng loạt.
- **Giải pháp**:
  - Tuyệt đối dùng tiếng Anh chuẩn ASCII cho toàn bộ câu lệnh in log trong các script daemon ngầm.
  - Luôn cấu hình ép chuẩn UTF-8 ngay đầu script: `if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8', errors='replace')`.
  - Trong PowerShell runner (`run_tests_windows.ps1` và `run_parallel.ps1`), luôn truyền cờ `-X utf8` khi gọi `Start-Process $PythonCmd -ArgumentList "-X utf8 scripts/template_service.py"`.

### Trụ cột 12: Quản Lý Hạn Ngạch CI/CD GitHub Actions & Bẫy 10-Shard Chi Phí
- **Bản chất**: Workflow chạy song song 10 Shards trên đám mây GitHub (`maestro-shard-test` với Android Emulator QEMU x86_64) tiêu thụ khoảng ~250 phút Actions cho mỗi lần push. Trên tài khoản cá nhân/private repo, hạn mức 2.000 phút miễn phí sẽ bị cạn kiệt chỉ sau 8 lần chạy, dẫn đến lỗi toàn bộ job bị hủy ngay lập tức với thông báo `The job was not started because recent account payments have failed or your spending limit needs to be increased`.
- **Giải pháp**:
  - Không để trigger tự động `push` / `pull_request` chạy 10 shards liên tục trên các nhánh feature. Chuyển sang kích hoạt thủ công bằng `workflow_dispatch`.
  - Cấu hình nâng hạn mức chi tiêu `Spending limits` trên GitHub Billing nếu cần chạy cloud runner.
  - Chuyển đổi runner sang `runs-on: self-hosted` để tận dụng máy thật nội bộ không bị giới hạn phút và không mất chi phí.

### Trụ cột 13: Quy Trình Di Chuyển Repository Sạch (Zero-History Orphan Branch Migration)
- **Bản chất**: Khi cần chuyển giao toàn bộ thành quả automation từ một tài khoản/tổ chức cũ sang tài khoản cá nhân độc lập mà không được để lộ lịch sử commit, tác giả cũ hoặc dính líu đến repository URL cũ.
- **Giải pháp**:
  - Sử dụng kỹ thuật Orphan Branch: `git checkout --orphan clean-main`.
  - Khử toàn bộ hardcoded repo name trong các file script (`run_tests.sh`, config).
  - Tạo 1 root commit duy nhất mang tên tác giả cá nhân: `git commit -m "Initial commit: Maestro Automation Framework"`.
  - Đẩy lên remote mới: `git push -u origin clean-main:main`.
  - Cắt toàn bộ tracking cũ: `git fetch --prune origin` và dọn dẹp các nhánh local cũ bằng `git branch -D`.

### Trụ cột 14: Cạm Bẫy Tự Động Nhận Diện Phiên Bản (Auto-Detect App Version) Theo Tên Nhánh Git
- **Bản chất**: Runner sử dụng logic auto-detect phiên bản ứng dụng (`Free` vs `Premium`) dựa trên tên nhánh git: `if ($gitBranch -match "premium") { $resolvedVersion = "Premium" } else { $resolvedVersion = "Free" }`. Khi dự án chuyển sang nhánh chính (`main`, `master`, hoặc `develop`), tên nhánh không chứa từ khóa `"premium"`. Runner sẽ tự động fallback về `Free`.
- **Hậu quả**:
  - Truyền nhầm tham số `-e APP_VERSION=Free` vào Maestro, kích hoạt các nhánh logic dành riêng cho bản Free thay vì Premium.
  - Runner so sánh ảnh chụp màn hình với thư mục `assets/Free/` thay vì `assets/Premium/`, dẫn đến toàn bộ bài test Premium bị fail hoặc sai lệch logic so khớp ảnh.
- **Giải pháp**:
  - Trong CI/CD pipeline (`maestro_local.yml`), luôn truyền tường minh tham số `-Version "Premium"`.
  - Tuyệt đối không phó mặc cho cơ chế auto-detect theo tên nhánh khi thực thi bộ test suite chính trên nhánh `main`.

### Trụ cột 15: Chiến Lược Cân Bằng Hạn Ngạch CI/CD Sharding (5 Shards vs 10 Shards Trade-off)
- **Bản chất**: Chạy song song 10 Shards máy ảo trên GitHub Actions tiêu tốn ~250 phút Actions cho mỗi lần push. Trên tài khoản cá nhân với private repo, hạn mức 2.000 phút/tháng sẽ bị cạn kiệt chỉ sau 8 lần chạy.
- **Giải pháp Điểm Cân Bằng Vàng (5 Shards)**:
  - Cấu hình 5 Shards là tỉ lệ tối ưu cho bộ test 14-16 test cases: mỗi Shard chạy 2-3 test case trong khoảng 8-12 phút.
  - Cắt giảm ngay lập tức **50% số phút tiêu thụ**, kéo dài thời gian sử dụng hạn ngạch hàng tháng gấp đôi.
  - Thời gian chờ kết quả tổng thể (wall-clock time) gần như không thay đổi, vì phần lớn thời gian chạy của runner CI bị chiếm bởi overhead khởi tạo máy ảo QEMU/Android Emulator (3-5 phút boot ban đầu).

### Trụ cột 16: Kiến Trúc Tự Động Quay Video Màn Hình Android (`adb shell screenrecord`) & Cạm Bẫy `--time-limit`
- **Bản chất**: Để hỗ trợ debug trực quan và ghi lại bằng chứng khi test case bị FAILED, hệ thống runner tích hợp khả năng tự động quay video màn hình ngầm qua ADB `screenrecord` ở độ phân giải gốc $1080 \times 2400$.
- **Cạm bẫy Native Android Time Limit**: Lệnh `screenrecord` của Android có giới hạn cứng tham số `--time-limit` trong khoảng `[1, 180]` (tối đa 180 giây = 3 phút). Nếu truyền `--time-limit 1800` (hoặc bất kỳ giá trị nào > 180), tiến trình sẽ crash ngay tức khắc khi khởi động với thông báo lỗi `Time limit 1800s outside acceptable range [1,180]`, dẫn đến không có video nào được tạo.
  - *Giải pháp*: Luôn đặt tham số `--time-limit 180` (hoặc để mặc định 180s) kết hợp `--bit-rate 4000000` (4 Mbps) để cân bằng giữa độ nét sắc sảo và dung lượng file siêu nhẹ (~5-15MB/test).
- **Cơ chế đóng container MP4 an toàn (Graceful SIGINT Termination)**: Khác với ảnh PNG, định dạng MP4 bắt buộc phải ghi khối dữ liệu `moov atom` (chứa index, metadata và duration) vào đuôi file khi kết thúc. Nếu dừng tiến trình bằng force kill (`kill -9` hoặc ngắt process `adb` từ Windows đột ngột), file MP4 sẽ bị hỏng hoàn toàn (corrupt container) và không mở được. Đồng thời lệnh `pkill -2 screenrecord` trên một số dòng máy (Samsung) có thể bị từ chối quyền `Operation not permitted`.
  - *Quy chuẩn dừng an toàn*:
    ```powershell
    adb -s $env:ANDROID_SERIAL shell "kill -2 `$(pidof screenrecord 2>/dev/null)" 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    if ($videoProc -and (-not $videoProc.HasExited)) {
        Stop-Process -Id $videoProc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    adb -s $env:ANDROID_SERIAL pull $deviceVideoPath $localVideoFile
    ```

### Trụ cột 17: Quản Lý Vòng Đời Video Artifacts Trên CI/CD (GitHub Actions vs Local)
- **Chiến lược `-RecordOnlyOnFailure`**: Trên GitHub Actions chỉ lưu video khi bài test FAILED. Nếu bài test PASSED, runner lập tức xóa video trên thiết bị (`rm -f $deviceVideoPath`) và không kéo về máy host, giúp tiết kiệm 100% dung lượng kéo file và lưu trữ Artifacts.
- **Cơ chế lưu trữ trên GitHub Actions**: Mỗi Workflow Run được cấp một Run ID riêng biệt với môi trường máy ảo sạch (Clean VM). Video lỗi được nén trong gói Artifact của từng Run ID, **hoàn toàn không bị ghi đè** giữa các lần build khác nhau (có thể xem lại lịch sử video của các commit trước trong thời hạn retention).
- **Khác biệt trên máy Local**: Trên máy tính cá nhân, runner lưu video theo tên bài test `reports/videos/<test>.mp4`, lần chạy sau sẽ tự động **ghi đè** lên lần chạy trước để bảo vệ dung lượng ổ cứng.

### Trụ cột 18: Cạm Bẫy Nhận Diện Nút Save Trên Edit Screen Giữa Các Bản Quyền (`mnItemSave` vs `mnItemSavePremium`)
- **Bản chất**: Trên màn hình thiết kế (Edit Screen), resource-id của nút Lưu thay đổi động tùy theo trạng thái bản quyền của mẫu thiết kế:
  - Nếu mở mẫu thiết kế Free: Nút lưu có id là `com.thmobile.logomaker:id/mnItemSave`.
  - Nếu mở mẫu thiết kế Premium (có icon vương miện PRO): Nút lưu có id là `com.thmobile.logomaker:id/mnItemSavePremium`.
- **Hậu quả**: Nếu script test assert cứng `id: "mnItemSave"` thì khi chạy trên template Premium, Maestro sẽ báo lỗi `Element not found: id: mnItemSave` và đánh rớt test case oan uổng.
- **Quy chuẩn**: Trong mọi kịch bản Maestro, khi kiểm tra hoặc chạm vào nút Save trên Edit Screen, **bắt buộc dùng Regex**:
  ```yaml
  - assertVisible:
      id: ".*mnItemSave.*"
  ```

### Trụ cột 19: Chuẩn Hóa Lọc Danh Sách Test Phân Tách Dấu Phẩy Cho PowerShell Runner
- **Bản chất**: Khi cần chạy linh hoạt một nhóm test case (ví dụ chạy nhanh từ `TC_01` đến `TC_05`), tham số `$File` mặc định chỉ chấp nhận một chuỗi so khớp đơn (`-notlike "*$File*"`).
- **Giải pháp**: Chuẩn hóa `$filterFiles = $File -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }`, cho phép truyền lệnh dạng `-File "TC_01,TC_02,TC_03,TC_04,TC_05"` ở cả runner đơn và runner song song.


