---
name: maestro-test-creator
description: >
  Quy trình tự động hoá end-to-end cho Maestro Mobile Testing trên Android.
  Agent sẽ tự phân tích yêu cầu người dùng, dump giao diện từ thiết bị thật,
  sinh test case YAML, thực thi trên device, và trả về script hoàn chỉnh kèm báo cáo kết quả.
---

# Maestro Auto Test Creator — Android Platform

> **Kích hoạt skill này** khi người dùng yêu cầu: tạo test case mới, viết kịch bản kiểm thử, test một tính năng, hoặc kiểm tra giao diện trên ứng dụng Logo Maker Android.

---

## PHASE 1: Phân tích Yêu cầu & Lên Kế hoạch

### Bước 1.1 — Thu thập thông tin từ người dùng

Khi nhận yêu cầu tạo test case, Agent cần xác định rõ các thông tin sau trước khi bắt đầu:

| Thông tin cần thu thập | Ví dụ |
|:---|:---|
| **Tính năng / Màn hình cần test** | Color Tool trên Edit Screen, Background Tool, Preview Screen... |
| **Loại kiểm thử** | Functional (tap, assert), Visual Regression (so sánh ảnh), Navigation (điều hướng) |
| **Trạng thái khởi đầu** | Từ Home Screen? Từ Edit Screen đã mở sẵn template? Clear state? |
| **Kỳ vọng kết quả (Expected)** | Element nào phải hiển thị? Ảnh phải giống baseline không? |
| **Có cần Visual Testing không?** | Nếu có → cần chụp screenshot và đăng ký so sánh trong PowerShell runner |

Nếu người dùng chỉ mô tả chung chung (ví dụ: "test tính năng Color"), Agent phải **chủ động hỏi thêm** hoặc **tự suy luận** dựa trên cấu trúc UI hierarchy hiện tại.

### Bước 1.2 — Xác định Test ID và vị trí file

- **Quy tắc đặt tên file**: `TC_{số thứ tự}_{Mô_tả_Tính_năng}.yaml`
- **Vị trí lưu**: `.maestro/test-suite/` (test chính) hoặc `.maestro/free-version/{Screen_Name}/` (test bản free)
- Kiểm tra file test hiện có trong `test-suite/` để xác định số thứ tự tiếp theo:
  ```powershell
  Get-ChildItem .maestro/test-suite/ -Filter "TC_*.yaml" | Sort-Object Name
  ```

---

## PHASE 2: Thu thập Dữ liệu UI từ Thiết bị Thật

### Bước 2.1 — Kiểm tra kết nối thiết bị

```powershell
adb devices
```

Nếu không có thiết bị → báo lỗi và hướng dẫn:
```powershell
adb kill-server
adb start-server
adb devices
```

### Bước 2.2 — Điều hướng đến màn hình cần test

Trước khi dump UI, Agent cần đưa ứng dụng đến đúng màn hình mục tiêu. Có 2 cách:

**Cách 1 — Chạy Maestro flow để điều hướng (Khuyến nghị):**
Tạo file tạm hoặc dùng `maestro test` với một flow ngắn chỉ chứa bước điều hướng:
```yaml
appId: com.thmobile.logomaker
---
- runFlow: "../config/Launch_App.yaml"
- runFlow:
    when:
      visible:
        text: "Get Full Access"
    file: "../config/Close_IAP_Screen.yaml"
# Điều hướng tới màn hình cần test...
- tapOn:
    id: "btnTemplate"
    containsDescendants:
      - text: "Template"
```

**Cách 2 — Điều hướng bằng tay (khi flow quá phức tạp):**
Yêu cầu người dùng tự mở app tới màn hình cần test trên thiết bị.

### Bước 2.3 — Dump XML Hierarchy

Sau khi ứng dụng đang hiển thị đúng màn hình mục tiêu:

```powershell
adb exec-out uiautomator dump /dev/tty > current_ui_dump.xml
```

Đọc file dump để trích xuất:
- **`resource-id`** của tất cả view (ưu tiên làm selector)
- **`text`** hiển thị trên giao diện
- **`class`** loại widget (TextView, ImageView, RecyclerView...)
- **`bounds`** vị trí và kích thước
- **`clickable`**, **`enabled`**, **`selected`** trạng thái tương tác

### Bước 2.4 — Phân tích cấu trúc UI

Từ XML dump, Agent phải xác định:

1. **Các element chính cần assert**: Tiêu đề, nút, tabs, menu items.
2. **Selector tối ưu cho từng element** (theo thứ tự ưu tiên):
   - `id` (resource-id) → ổn định nhất
   - `text` + `below`/`above`/`index` → khi id bị trùng
   - `containsDescendants` → khi cần xác định container
   - `point: "x%, y%"` → CHỈ khi element không có selector nào (Canvas, Color Picker)
3. **Các popup tiềm ẩn**: IAP Screen, Ads, Collapsible Ads, Discount Popup, Rate App.

---

## PHASE 3: Sinh Kịch bản Test Case YAML

### Bước 3.1 — Cấu trúc bắt buộc của mọi test file

```yaml
appId: com.thmobile.logomaker
---

# ============================================
# TC_{XX}_{Tên_Test_Case}
# Mô tả: {Mô tả ngắn gọn mục đích test}
# ============================================

# Step 1: Khởi động ứng dụng
- runFlow: "../config/Launch_App.yaml"

# Step 2: Đóng IAP nếu xuất hiện
- runFlow:
    when:
      visible:
        text: "Get Full Access"
    file: "../config/Close_IAP_Screen.yaml"

# Step 3: Điều hướng đến màn hình mục tiêu
# ... (tuỳ theo test case)

# Step 4: Đóng quảng cáo Collapsible nếu xuất hiện
- runFlow:
    when:
      visible: "Close button"
    commands:
      - tapOn: "Close button"

# Step 5: Thực hiện hành động kiểm thử
# ... (tuỳ theo test case)

# Step 6: Xác minh kết quả (Assert)
# ... (tuỳ theo test case)

# Step 7: Chụp ảnh màn hình (nếu cần Visual Testing)
- takeScreenshot: "screenshots/{Tên_Screenshot}"
```

### Bước 3.2 — Patterns phổ biến tham khảo

**Pattern A — Kiểm tra điều hướng & hiển thị:**
```yaml
- tapOn:
    id: "btnTemplate"
    containsDescendants:
      - text: "Template"

- assertVisible: "Select Template"

- tapOn:
    id: "tvCategory"
    text: "Coffee"

- assertVisible: "Coffee"
```

**Pattern B — Kiểm tra sub-tool trên Edit Screen:**
```yaml
# Chọn tool
- tapOn:
    id: "itemArt"
    containsDescendants:
      - text: "Art"

# Verify tool được chọn
- assertVisible:
    id: "itemArt"
    selected: true

# Verify sub-tabs hiển thị
- assertVisible:
    id: "layout_art_editor_menu"
    containsDescendants:
      - text: "Controls"
      - text: "Color"
      - text: "Outline"
```

**Pattern C — Xử lý Save & Export (Tương thích Đa hình Free vs Premium):**
```yaml
# Dùng Regex Selector vì nút Save đổi từ mnItemSave (Free) sang mnItemSavePremium (Premium)
- tapOn:
    id: ".*mnItemSave.*"
    enabled: true

# Xử lý adaptive: Bản Free hiện dialog chọn watermark, Bản Premium lưu trực tiếp
- runFlow:
    when:
      visible:
        id: "tvSaveMockupTitle"
    commands:
      - tapOn:
          id: "btn_save_with_watermark"

- runFlow:
    when:
      visible:
        id: "llExportLogo"
    commands:
      - tapOn:
          id: "llExportLogo"
      - tapOn:
          id: "layout_hd"
      - tapOn:
          id: "tvSave"

- runFlow:
    when:
      visible: "Test Ad"
    file: "../config/Close_Ads_Rewards.yaml"
```

**Pattern D — Cuộn và tìm element:**
```yaml
- scrollUntilVisible:
    element:
      text: "My Design"
      childOf:
        id: "btnMyDesignFile"
    direction: DOWN
```

**Pattern E — Lặp thao tác (repeat):**
```yaml
- repeat:
    times: 3
    commands:
      - tapOn:
          id: "btnLayerUp"
          above:
            text: "Layer up"
```

**Pattern F — Thao tác trên Canvas & Kéo thả Layer (khi không có element ID):**
```yaml
# Kéo di chuyển layer: bắt buộc dùng duration từ 300 - 500 ms để cử chỉ ổn định trên mọi loại cảm ứng
- swipe:
    start: 50%, 50%
    end: 10%, 70%
    duration: 300

# Chạm kích hoạt công cụ tại tâm Canvas mà không xê dịch layer:
- tapOn:
    point: "50%, 50%"
```

**Pattern G — Chờ tải tài nguyên ảnh bất đồng bộ từ mạng (Async Network Loading):**
```yaml
# Chờ Activity transition hoàn tất
- waitForAnimationToEnd:
    timeout: 20000

# Tạo trễ đồng bộ 3.5s để thư viện Glide/Picasso nạp đủ ảnh thumbnail từ mạng
- evalScript: ${var start = new Date().getTime(); while (new Date().getTime() < start + 3500); output.waited = true}

- takeScreenshot: "screenshots/TC_{ID}_{Tên_Chức_Năng}"
```

### Bước 3.3 — Checklist trước khi hoàn tất YAML

- [ ] Có `appId: com.thmobile.logomaker` ở dòng đầu tiên
- [ ] Có `---` phân tách header
- [ ] Bắt đầu bằng `runFlow: "../config/Launch_App.yaml"`
- [ ] Có bước xử lý IAP popup (`Close_IAP_Screen.yaml`)
- [ ] Có bước xử lý Collapsible Ads (`Close button`)
- [ ] Có bước xử lý Interstitial Ads (`Close_Ads_Screen.yaml`) sau mỗi hành động gây trigger ads (save, navigate back...)
- [ ] Comment phân đoạn rõ ràng (`# Step N: ...`)
- [ ] Selector ưu tiên `id` trước, `text` thứ hai, `point` cuối cùng
- [ ] Sử dụng Regex `id: ".*mnItemSave.*"` cho nút Save trên Edit Screen
- [ ] Sử dụng Regex `.*(Personal|Cá nhân|Sharing image).*` cho System Share Sheet
- [ ] Thao tác vuốt kéo layer dùng `duration: 300` đến `500` ms (tránh dùng 50ms gây trượt cảm ứng)
- [ ] Có bước `evalScript` trễ 3.5s trước khi chụp màn hình các danh sách ảnh nạp từ internet
- [ ] Dùng `waitForAnimationToEnd` thay vì `sleep` cứng cho các animation chuyển màn
- [ ] Dùng `hideKeyboard` trước khi tap nút ở dưới màn hình
- [ ] Tên screenshot bắt buộc có tiền tố Test Case: `screenshots/TC_{ID}_{Tên_Viết_Hoa_Mô_Tả}` (chống trùng lặp/ghi đè khi chạy song song)

---

## PHASE 4: Thực thi Test trên Thiết bị

### Bước 4.1 — Dọn dẹp session lock (phòng tránh kẹt)

```powershell
Remove-Item "$HOME\.maestro\sessions" -Force -ErrorAction SilentlyContinue
```

### Bước 4.2 — Chạy test case vừa tạo

**Debug nhanh (chỉ chạy Maestro CLI):**
```powershell
maestro test .maestro/test-suite/{TÊN_FILE}.yaml
```

**Chạy đầy đủ với Visual Regression (qua PowerShell runner):**
```powershell
.\run_tests_windows.ps1 -File "{TÊN_FILE}.yaml" -Version "Premium"
```

### Bước 4.3 — Phân tích kết quả

- **PASSED**: Test case đạt → hoàn tất, báo cáo cho người dùng.
- **FAILED**: Đọc output Maestro để xác định lỗi:
  - **Element not found** → Kiểm tra lại selector (kiểm tra xem ID có bị đổi giữa Free/Premium không), dump UI mới nếu cần.
  - **Timeout waiting for element** → Tăng timeout hoặc thêm `waitForAnimationToEnd`.
  - **Session lock error** → Dọn dẹp session file và thử lại.
  - **Visual comparison failed** → Kiểm tra ảnh baseline trong `assets/Premium/` hoặc `assets/Free/`, xem xét cập nhật baseline (`-UpdateBaseline`).

### Bước 4.4 — Vòng lặp sửa lỗi (Auto-Fix Loop)

Nếu test fail, Agent thực hiện vòng lặp tối đa **3 lần**:
1. Đọc output lỗi Maestro.
2. Dump lại UI hierarchy nếu cần (`adb exec-out uiautomator dump`).
3. Sửa file YAML dựa trên phân tích lỗi.
4. Chạy lại test.
5. Nếu vẫn fail sau 3 lần → dừng lại và báo cáo chi tiết cho người dùng.

---

## PHASE 5: Đăng ký Visual Comparison (nếu có)

### Bước 5.1 — Đăng ký vào `run_tests_windows.ps1`

Nếu test case có lệnh `takeScreenshot`, Agent phải tự động cập nhật file `run_tests_windows.ps1` vào cả `$imageCompareMap_Premium` và `$imageCompareMap_Free`:

**So sánh ảnh với baseline (`$imageCompareMap_Premium` / `$imageCompareMap_Free`):**
```powershell
"*{TÊN_TEST_CASE}*" = @(
    @{ Template = "assets/Premium/TC_{ID}_{Tên}.png"; CropId = $null; Screenshot = "screenshots/TC_{ID}_{Tên}" }
)
```

**So sánh 2 ảnh chụp runtime (`$dualCompareMap`):**
```powershell
"*{TÊN_TEST_CASE}*" = @(
    @{
        Screenshot1 = "screenshots/TC_{ID}_{Ảnh_1}"; CropId1 = "{element_id hoặc null}";
        Screenshot2 = "screenshots/TC_{ID}_{Ảnh_2}"; CropId2 = "{element_id hoặc null}"
    }
)
```

### Bước 5.2 — Tạo ảnh Baseline mới (nếu chưa có)

Nếu chưa có ảnh baseline trong `assets/Premium/` và `assets/Free/`:
1. Chạy test case để chụp screenshot thực tế.
2. Kiểm tra ảnh tại thư mục `screenshots/`.
3. Copy ảnh đạt yêu cầu sang `assets/Premium/` và `assets/Free/` để làm baseline:
   ```powershell
   Copy-Item "screenshots/TC_{ID}_{Tên}.png" "assets/Premium/TC_{ID}_{Tên}.png"
   Copy-Item "screenshots/TC_{ID}_{Tên}.png" "assets/Free/TC_{ID}_{Tên}.png"
   ```

---

## PHASE 6: Báo cáo Kết quả

Sau khi hoàn tất toàn bộ quy trình, Agent phải trình bày cho người dùng:

### Template báo cáo:

```
## 📋 Kết quả Tạo Test Case

**Test Case**: TC_{XX}_{Tên}
**File**: .maestro/test-suite/{tên_file}.yaml
**Trạng thái**: ✅ PASSED / ❌ FAILED

### Tổng quan các bước:
1. ✅ Khởi động app & đóng popup
2. ✅ Điều hướng đến {màn hình}
3. ✅ Thực hiện {hành động chính}
4. ✅ Assert {kết quả mong đợi}
5. ✅ Chụp screenshot: {tên_ảnh}

### Visual Testing:
- Đăng ký imageCompareMap: ✅/❌
- Đăng ký dualCompareMap: ✅/❌
- Baseline đã có: ✅/❌

### Lưu ý:
- {Các điểm cần chú ý, limitations, hoặc đề xuất cải thiện}
```

---

## Danh sách Common Flows có sẵn

| Flow File | Mục đích | Khi nào dùng |
|:---|:---|:---|
| `config/Launch_App.yaml` | Khởi động app (không clear state) | Bắt đầu mọi test case |
| `config/Launch_App_Clear_State.yaml` | Khởi động app + xoá dữ liệu | Test Onboarding, First-time flow |
| `config/Close_IAP_Screen.yaml` | Đóng popup mua hàng IAP | Khi thấy "Get Full Access" |
| `config/Close_Ads_Screen.yaml` | Đóng quảng cáo toàn màn hình | Sau save, navigate, khi thấy "Test Ad" |
| `config/Close_Ads_Rewards.yaml` | Đóng quảng cáo có thưởng | Sau export có reward ad |
| `config/Close_Collapsible_Ads.yaml` | Đóng quảng cáo thu gọn | Khi thấy "Close button" (banner ads) |
| `config/Close_Discount_Popup.yaml` | Đóng popup giảm giá | Khi thấy popup discount |
| `config/Back_Action.yaml` | Nhấn nút Back + xử lý ads | Quay lại màn hình trước |

---

## Danh sách UI Element IDs thường dùng

### Home Screen
| Element | ID | Mô tả |
|:---|:---|:---|
| Nút Template | `btnTemplate` | Mở màn hình chọn template |
| Nút My Design | `btnMyDesignFile` | Mở danh sách design đã lưu |

### Edit Screen (Toolbar)
| Element | ID | Mô tả |
|:---|:---|:---|
| Nút Save | `mnItemSave` | Menu save/export |
| Nút Undo | `btnUndo` / `ivUndo` | Hoàn tác |
| Nút Redo | `btnRedo` / `ivRedo` | Làm lại |
| Nút Layer | `imageViewLayerTag` | Mở dialog layer |
| Nút Grid | `imageShowGrid` | Bật/tắt lưới |

### Edit Screen (Bottom Tools)
| Element | ID | Mô tả |
|:---|:---|:---|
| Background | `itemBackground` | Tab Background |
| Art | `itemArt` | Tab Art/Sticker |
| Text | `itemText` | Tab Text |
| Effect | `itemEffect` | Tab Effect |
| Palette | `itemPalette` | Tab Color Palette |
| Image | `itemImage` | Tab thêm ảnh |

### Art Tool — Sub Controls
| Element | ID | Mô tả |
|:---|:---|:---|
| Layout menu | `layout_art_editor_menu` | Container các sub-tab Art |
| Layout controls | `layout_art_control` | Container nút di chuyển layer |
| Move Up | `imgMoveUp` | Di chuyển lên |
| Move Down | `imgMoveDown` | Di chuyển xuống |
| Move Left | `imgMoveLeft` | Di chuyển trái |
| Move Right | `imgMoveRight` | Di chuyển phải |
| Layer Up | `btnLayerUp` | Đẩy layer lên |
| Layer Down | `btnLayerDown` | Đẩy layer xuống |
| Duplicate | `btnDuplicate` | Nhân bản layer |

### Preview Screen
| Element | ID | Mô tả |
|:---|:---|:---|
| Share | `btnShare` | Chia sẻ |
| Home | `btnHome` | Về trang chính |
| AI Style | `btnAiLogoStyle` | Mở Style Magic AI |
| Brand Identify | `btnBrandIdentify` | Mở Mockup Preview |
| Preview Image | `imageTransparentGrid` | Ảnh preview logo |

### Save/Export Dialog
| Element | ID | Mô tả |
|:---|:---|:---|
| Save Project | `llSaveProject` | Lưu project |
| Export PNG | `llExportLogo` | Export ảnh PNG |
| HD Option | `layout_hd` | Chọn độ phân giải HD |
| Save Button | `tvSave` | Xác nhận lưu |

### Design Area
| Element | ID | Mô tả |
|:---|:---|:---|
| Design background | `bgDesignArea` | Vùng nền thiết kế (dùng cho crop khi so sánh ảnh) |
| Transparent grid | `layout_transparent` | Lưới trong suốt |
