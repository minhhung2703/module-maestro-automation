# KỊCH BẢN THUYẾT TRÌNH DỰ ÁN: MOBILE AUTOMATION TESTING FRAMEWORK
## Dự án: Logo Maker (Android Platform)
> **Người trình bày**: Automation QA Engineer / Technical Lead  
> **Chủ đề**: Tự Động Hóa Kiểm Thử Các Luồng & Tính Năng Trọng Yếu Đảm Bảo Chất Lượng Kịp Tiến Độ Phát Hành (Release on Schedule)  
> **Đối tượng người nghe**: Management, Product Owner, QA Lead, Mobile Developers

---

## 🧭 CẤU TRÚC TỔNG THỂ BÀI THUYẾT TRÌNH

| Phần | Nội dung | Mục tiêu truyền tải |
| :--- | :--- | :--- |
| **Phần 1** | Mở đầu & Bối cảnh bài toán (Slide 1, 2) | Nêu bật áp lực tiến độ phát hành & khó khăn khi kiểm thử thủ công ứng dụng đồ họa |
| **Phần 2** | Kiến trúc Hệ thống & Bộ 3 Thuật Toán Cốt Lõi (Slide 3, 4) | Kiến trúc 3 tầng & Bộ ba thuật toán xử lý hình ảnh, bắt mẫu đồ họa và selector đa hình |
| **Phần 3** | Hạ Tầng Kiểm Thử Tự Động Trên Thiết Bị Thật (Slide 5) | Đóng vai trò Quality Gate chốt chặn chất lượng trước mỗi đợt Release |
| **Phần 4** | Bao Phủ Toàn Bộ Luồng Sống Còn & Giá Trị Release (Slide 6, 7) | 16 kịch bản bao phủ trọn vẹn các luồng chính, đảm bảo app ra thị trường đúng tiến độ |
| **Phần 5** | Live Demo Minh Họa (Slide 8) | Trực quan hóa kịch bản phức tạp TC_11 Mockup Preview chạy trên máy thật |
| **Phần 6** | Tổng Kết & Hỏi Đáp Phản Biện Q&A (Slide 9 & Q&A) | Giải đáp tự tin các câu hỏi trọng tâm về công nghệ, tính ổn định và hiệu quả dự án |

---

## 📽 SLIDE BREAKDOWN & LỜI THOẠI CHI TIẾT (WORD-FOR-WORD SCRIPT)

### SLIDE 1: MỞ ĐẦU & TIÊU ĐỀ
* **Tiêu đề Slide**: *Tự Động Hóa Kiểm Thử Các Luồng & Tính Năng Trọng Yếu: Chốt Chặn Chất Lượng Đảm Bảo Kịp Tiến Độ Phát Hành (Release On Schedule)*
* **Hình ảnh trên slide**: Logo ứng dụng Logo Maker, huy hiệu Quality Gate (Sẵn sàng phát hành), thiết bị thật Samsung S20 FE đang chạy kiểm thử, các công nghệ chủ chốt (Maestro, Python OpenCV, CI/CD).
* **Lời thoại Presenter**:
> *"Kính chào các anh chị Ban Lãnh đạo và các bạn đồng nghiệp,*
> 
> *Trong chu kỳ phát triển ứng dụng di động, thách thức lớn nhất của đội ngũ là làm sao vừa đưa sản phẩm ra thị trường đúng thời hạn (Time-to-Market), vừa đảm bảo tuyệt đối chất lượng, không để phát sinh lỗi hồi quy hay crash làm ảnh hưởng đến trải nghiệm người dùng và điểm xếp hạng trên Store.*
> 
> *Đối với một ứng dụng thiết kế đồ họa phức tạp như **Logo Maker**, việc kiểm thử thủ công lặp đi lặp lại hàng trăm kịch bản trước mỗi đợt phát hành luôn là một nút thắt cổ chai lớn. Hôm nay, tôi xin đại diện đội ngũ QA trình bày về **Hệ thống Tự động hóa Kiểm thử Toàn diện** — giải pháp giúp chúng ta kiểm chứng tự động toàn bộ các luồng người dùng và tính năng cốt lõi trên thiết bị thật, tạo ra một chốt chặn chất lượng vững chắc để ứng dụng tự tin phát hành kịp tiến độ cam kết."*

---

### SLIDE 2: BÀI TOÁN & THÁCH THỨC ĐẶC THÙ CỦA ỨNG DỤNG ĐỒ HỌA
* **Tiêu đề Slide**: *Tại sao Mobile Automation truyền thống thất bại trên Logo Maker?*
* **Nội dung hiển thị**:
  1. **Canvas "Mù" (Pure Graphics)**: Các đối tượng vẽ, icon logo, background không có Resource-ID hay Text trong XML hierarchy.
  2. **Rủi ro Báo Pass Ảo (False Pass)**: Thuật toán so sánh ảnh thông thường bị đánh lừa bởi vùng nền phẳng hoặc viền ngoài quá lớn.
  3. **Độ Flaky Cao**: Popup quảng cáo, màn hình gói VIP (IAP), cùng các tooltip hướng dẫn che phủ màn hình sau khi cài mới.
  4. **Phân hóa Phiên bản (Free vs Premium)**: Cùng tính năng Lưu, bản Free có ID `mnItemSave` và hiện popup Watermark; bản Premium đổi thành `mnItemSavePremium` và lưu trực tiếp.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Khi tiếp cận bài toán kiểm thử cho Logo Maker, nếu sử dụng các công cụ truyền thống như Appium, chúng ta sẽ lập tức gặp phải các rào cản kỹ thuật nghiêm trọng:*
> 
> *1. Logo Maker là ứng dụng đồ họa. Trên vùng Canvas, toàn bộ chi tiết logo là các layer đồ họa render trực tiếp — chúng hoàn toàn không có ID, không có Text để các công cụ thông thường định vị.*  
> *2. Khi kiểm thử đổi màu nền hoặc xoay 3D, nếu chỉ so sánh ảnh toàn màn hình một cách thô sơ, việc chữ trên logo bị biến dạng có thể bị bỏ lọt và hệ thống vẫn báo PASS ảo.*  
> *3. Thêm vào đó là sự phân hóa giữa bản Free và Premium: Nút Lưu tự đổi ID từ `mnItemSave` sang `mnItemSavePremium`, luồng lưu bản Free bật popup bắt xem quảng cáo, bản Premium lại chuyển thẳng sang nút Share.*
> 
> *Nếu chỉ dựa vào kiểm thử thủ công, đội ngũ sẽ mất rất nhiều công sức rà soát lặp đi lặp lại, dễ mệt mỏi và bỏ sót lỗi, dẫn đến nguy cơ chậm trễ lịch phát hành. Để giải quyết triệt để, chúng tôi đã xây dựng một **kiến trúc Hybrid Automation 3 tầng**."*

---

### SLIDE 3: KIẾN TRÚC GIẢI PHÁP HYBRID AUTOMATION 3 TẦNG
* **Tiêu đề Slide**: *Kiến Trúc Framework 3 Tầng: Ổn Định — Thông Minh — Tự Động Hóa Hoàn Toàn*
* **Sơ đồ trên slide** *(Hiển thị flowchart 3 tầng)*:
  - **Tầng 1 (Execution Layer)**: Maestro Declarative YAML (Tương tác trực tiếp tầng OS/Accessibility, cú pháp khai báo sạch, chạy ổn định tuyệt đối).
  - **Tầng 2 (Intelligence & Vision Layer)**: Python 3 + OpenCV Engine + HTTP Daemon (Dynamic Multi-Zone, MAE Color Distance, Image Template Matching).
  - **Tầng 3 (Orchestration Layer)**: PowerShell Runners & CI/CD Pipeline (Điều phối kiểm thử thiết bị thật, tự động dọn session và gom báo cáo kết quả).
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Bức tranh tổng thể về kiến trúc giải pháp gồm 3 tầng bổ trợ chặt chẽ cho nhau:*
> 
> *Ở **Tầng 1 - Test Execution**, chúng tôi ứng dụng **Maestro Framework**. Khác với các công cụ cồng kềnh qua trung gian WebDriver, Maestro giao tiếp trực tiếp ở tầng OS/Accessibility của Android bằng cú pháp YAML khai báo. Nhờ vậy, kịch bản cực kỳ ổn định, tốc độ thực thi native và triệt tiêu các lỗi mất kết nối giữa chừng.*
> 
> *Ở **Tầng 2 - Thị giác máy tính (Intelligence Layer)**, bộ script Python chuyên sâu đóng vai trò là 'đôi mắt' của hệ thống: tự động phân tích ảnh đa vùng, thích ứng màu sắc và chạy dịch vụ ngầm để nhận diện đồ họa.*
> 
> *Ở **Tầng 3 - Điều phối & Hạ tầng (Orchestration)**, bộ Runner thông minh điều phối kịch bản chạy trực tiếp trên thiết bị thật, tự động dọn dẹp môi trường sau mỗi lượt và xuất báo cáo trực quan lên hệ thống CI/CD."*

---

### SLIDE 4: BỘ 3 THUẬT TOÁN ĐỘT PHÁ — THỊ GIÁC MÁY TÍNH & TỰ THÍCH ỨNG
* **Tiêu đề Slide**: *Bộ 3 Thuật Toán Cốt Lõi: Đột Phá Xử Lý Hình Ảnh & Kháng Lỗi Giao Diện*
* **Hình ảnh trên slide (Trình bày 3 cột trực quan)**:
  - **Cột 1: Thuật toán Dynamic Multi-Zone & MAE (Visual Regression)**:
    - Safe Insets loại bỏ vùng nhiễu StatusBar và Gesture Pill.
    - Chia 2 vùng kiểm thử độc lập: Canvas Zone (ngưỡng khắt khe) và Tool Zone.
    - Thích ứng toán học: Khi kiểm tra nền phẳng đơn sắc (Flat Color), hệ thống tự động chuyển sang đo khoảng cách sai số màu (MAE) trong không gian RGB, loại bỏ hiện tượng lỗi chia cho 0 gây fail oan.
  - **Cột 2: Thuật toán Template Matching Đa Tỷ Lệ (OpenCV Daemon)**:
    - Daemon Python chạy ngầm nhận request qua HTTP từ Maestro JavaScript Bridge.
    - Áp dụng thuật toán chuẩn hóa tương quan `cv2.matchTemplate` (`TM_CCOEFF_NORMED`) quét ma trận ảnh màn hình.
    - Tự động tính tâm tọa độ và gửi lệnh tap trực tiếp, định vị chính xác các phần tử đồ họa "mù" không có UI ID hay Text.
  - **Cột 3: Thuật toán Selector Đa Hình (Regex) & Cây Quyết Định Thích Ứng (Adaptive Flow)**:
    - Khớp biểu thức chính quy: `id: ".*mnItemSave.*"` nhận diện xuyên suốt nút Lưu trên cả bản Free và Premium.
    - Cây quyết định trạng thái thích ứng: Tự động rẽ nhánh xử lý dialog watermark ở bản Free hoặc xác nhận trạng thái nút Share ở bản Premium. 1 kịch bản duy nhất chạy thông suốt cả 2 môi trường.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Trọng tâm công nghệ giúp hệ thống kiểm thử chính xác mà không gặp lỗi 'báo động giả' nằm ở **Bộ 3 Thuật Toán Cốt Lõi**:*
> 
> *1. **Thuật toán Dynamic Multi-Zone & Thích ứng MAE**: Hệ thống tự động cắt bỏ thanh trạng thái và vạch cử chỉ, chia màn hình thành vùng Canvas và vùng công cụ để đánh giá với ngưỡng riêng biệt. Với các màn hình đổi màu nền phẳng — nơi các thuật toán tương quan thông thường dễ bị lỗi chia cho 0 và báo trượt oan — hệ thống tự động chuyển sang đo khoảng cách màu MAE, đảm bảo kiểm tra chuẩn xác từng thay đổi màu sắc.*
> 
> *2. **Thuật toán Thị giác máy tính OpenCV Template Matching**: Để chọn đúng các mẫu logo dạng ảnh không có ID hay text, một dịch vụ ngầm sẽ quét màn hình, xác định tọa độ khớp nhất và điều khiển bấm chính xác vào tâm đối tượng.*
> 
> *3. **Thuật toán Selector Đa hình & Cây Quyết định Thích ứng**: Kịch bản áp dụng biểu thức Regex `.*mnItemSave.*` kết hợp cơ chế tự động rẽ nhánh. Nhờ vậy, cùng một kịch bản có thể kiểm thử mượt mà trên cả bản Free lẫn bản Premium mà không bị gãy luồng khi lập trình viên thay đổi tiền tố ID nút bấm.*
> 
> *Ba thuật toán này tạo nên bộ khung vững chắc giúp việc kiểm thử tự động diễn ra ổn định và hoàn toàn tin cậy."*

---

### SLIDE 5: HẠ TẦNG CI/CD — CHỐT CHẶN CHẤT LƯỢNG TRÊN THIẾT BỊ THẬT TRƯỚC GIỜ RELEASE
* **Tiêu đề Slide**: *Quality Gate Tự Động Trên Thiết Bị Thật: Bảo Đảm Chất Lượng Kịp Tiến Độ Release*
* **Hình ảnh trên slide**:
  - Mô hình kiểm thử tự động tích hợp CI/CD điều phối trực tiếp trên thiết bị phần cứng thật (Samsung Galaxy S20 FE, Android 13).
  - So sánh mô thức kiểm thử:
    - *Kiểm thử thủ công*: Hàng trăm bước lặp lại, dễ mệt mỏi và sót lỗi -> **Rất chậm · Dễ trễ Release**.
    - *Quality Gate tự động*: Kiểm tra toàn diện 6 luồng sống còn trên máy thật -> **Nhanh chóng · Sẵn sàng Release**.
    - *Kiểm tra 1 màn hình*: Xác thực tính năng ngay khi lập trình viên sửa code -> **Tức thì · Phản hồi ngay**.
  - Tối ưu báo cáo: Tự động gom kết quả JSON, trích xuất ảnh đối sánh visual về GitHub Summary, chính sách dọn dẹp dữ liệu lưu trữ giữ chi phí hạ tầng ở mức $0.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Một bộ kiểm thử tự động sẽ chỉ thực sự mang lại giá trị khi nó được kiểm chứng trên chính môi trường phần cứng thực tế của người dùng.*
> 
> *Thay vì chạy trên các máy ảo giả lập vốn thường gặp sai lệch về màu sắc hiển thị hoặc khả năng render GPU, toàn bộ hệ thống của chúng tôi được thực thi trực tiếp trên **thiết bị phần cứng thật (Samsung Galaxy S20 FE, Android 13)**.*
> 
> *Điều này tạo ra 3 giá trị sống còn cho tiến độ phát hành:*
> 1. **Độ tin cậy tuyệt đối**: Mọi thao tác vẽ Canvas, chọn màu, lưu Mockup đều chạy trên màn hình thực, chip xử lý thực và bộ nhớ RAM thực tế.*
> 2. **Chốt chặn chất lượng (Quality Gate) tự động**: Trước mỗi đợt Release, thay vì phải chờ đợi QA rà soát thủ công qua nhiều vòng căng thẳng, hệ thống sẽ tự động thực thi toàn bộ kịch bản kiểm thử, đưa ra kết quả xanh mướt và xác thực mọi tính năng hoạt động hoàn hảo.*
> 3. **Tối ưu chi phí $0**: Toàn bộ quy trình được tích hợp vào pipeline với cơ chế tự động dọn dẹp dữ liệu lưu trữ, hoàn toàn không phát sinh chi phí hạ tầng cloud hay thuê dịch vụ ngoài.*
> 
> *Nhờ đó, đội ngũ hoàn toàn chủ động về mặt tiến độ, sẵn sàng đưa sản phẩm lên Store mà không gặp bất kỳ trở ngại nào!"*

---

### SLIDE 6: BÁO CÁO THÀNH QUẢ — PHỦ KÍN TOÀN BỘ CÁC LUỒNG & TÍNH NĂNG CHÍNH
* **Tiêu đề Slide**: *Báo Cáo Thành Quả: Bao Phủ 100% Các Luồng & Tính Năng Trọng Yếu Của Ứng Dụng*
* **Số liệu ấn tượng trên slide**:
  - **16 / 16** Kịch Bản Tự Động Hóa Lớn đạt trạng thái **PASSED 100%**.
  - **317** Ca kiểm thử chi tiết từ tài liệu đặc tả được tự động hóa toàn diện.
  - **Phủ kín 100%** toàn bộ các luồng trải nghiệm người dùng sống còn.
  - Xuất bản tự động bộ tài liệu Excel chuyên nghiệp: [`docs/LogoMaker_Automation_TestSuite.xlsx`](file:///d:/logo-maker/docs/LogoMaker_Automation_TestSuite.xlsx).
* **Nội dung 6 luồng trọng yếu đã được bảo vệ tự động**:
  1. *Luồng Khởi Động & Mua Hàng (IAP Paywall Flow)*: Mở app, bảng giá VIP tuần/năm, dùng thử 3 ngày, đóng mở paywall an toàn.
  2. *Luồng Điều Hướng & Khám Phá Mẫu (Template Discovery Flow)*: Duyệt danh mục, chọn mẫu logo, tải tài nguyên vào Edit Canvas không lỗi.
  3. *Luồng Công Cụ Chỉnh Sửa Cốt Lõi (Core Edit Flow)*: Background đổi màu/texture/cắt ảnh, Art controls/layers/3D, Text nhập chữ/font nghệ thuật/size/14 tính năng con.
  4. *Luồng Lưu & Xuất Bản Đồ Họa (Save & HD Export Flow)*: Lưu nháp Draft, xuất PNG HD chất lượng cao, hộp thoại đánh giá Rate dialog, chia sẻ Preview Screen.
  5. *Luồng Nhận Diện Thương Hiệu (Mockup Preview Flow)*: Xem logo trên 5 sản phẩm thực tế, lưu mockup có/không watermark, chuyển trạng thái Save -> Share.
  6. *Luồng Sáng Tạo Bằng AI (AI Studio Flow)*: Nhập Prompt ý tưởng, chọn Style Preset, sinh logo AI và đưa kết quả vào Canvas.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Nhìn vào bức tranh thành quả, hệ thống đã bảo vệ toàn diện **6 luồng trải nghiệm người dùng sống còn** của Logo Maker:*
> 
> *Toàn bộ **16 kịch bản tự động hóa** tương ứng với **317 ca kiểm thử chi tiết** đều đã đạt trạng thái **PASSED 100%** trên thiết bị thật.*
> *Từ luồng thanh toán mua gói VIP, điều hướng chọn template, chỉnh sửa đa lớp trên Canvas, cho đến lưu xuất file ảnh HD, xem trước Mockup sản phẩm và tính năng tạo logo bằng AI — tất cả đều có kịch bản tự động kiểm tra nghiêm ngặt trước mỗi đợt phát hành.*
> 
> *Toàn bộ dữ liệu này đã được số hóa và xuất bản thành bộ tài liệu Excel ma trận kiểm thử chi tiết, giúp Product Owner, Dev Lead và QA luôn nắm rõ trạng thái sẵn sàng của sản phẩm."*

---

### SLIDE 7: BẢO ĐẢM TIẾN ĐỘ RELEASE & TỐI ƯU THỜI GIAN LÀM VIỆC
* **Tiêu đề Slide**: *Bảo Đảm Tiến Độ Phát Hành (Release Readiness) & Tối Ưu Thời Gian Làm Việc*
* **Nội dung hiển thị trên slide**:
  - **1. Đảm Bảo Tiến Độ Phát Hành (Kịp Release Đúng Hạn)**:
    - Loại bỏ hoàn toàn sự chậm trễ do chờ đợi kiểm thử thủ công kéo dài trước ngày phát hành.
    - Toàn bộ luồng chính và tính năng cốt lõi được xác thực tự động, giúp đội ngũ tự tin phát hành ứng dụng lên Store ngay khi hoàn thành phát triển tính năng.
  - **2. Khả Năng Đáp Ứng Hotfix Thần Tốc**:
    - Khi phát sinh lỗi cần sửa gấp trên Production, hệ thống tự động kiểm chứng nhanh chóng tính toàn vẹn của ứng dụng, đảm bảo bản vá an toàn và không làm vỡ các tính năng sẵn có.
  - **3. Tối Ưu Thời Gian Làm Việc (Work Smarter)**:
    - Loại bỏ các thao tác lặp lại, giảm áp lực chạy đua deadline và làm thêm giờ (OT) dồn dập trước ngày release.
    - Đội ngũ có thêm thời gian hoàn thiện tính năng và chăm chút trải nghiệm người dùng một cách chủ động.
  - **4. Hiệu Quả Đầu Tư Bền Vững (ROI)**:
    - Chi phí hạ tầng 0 USD, hệ thống vận hành bền vững và ổn định qua từng chu kỳ phát hành.
    - Kiến trúc framework module hóa cao, sẵn sàng tái sử dụng phần lớn nền tảng cho các dự án ứng dụng tiếp theo của công ty.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Thưa Ban Giám đốc và các anh chị, giá trị lớn nhất mà hệ sinh thái tự động hóa này mang lại chính là **bảo đảm tiến độ phát hành (Release on Schedule)** và **tối ưu thời gian làm việc** cho toàn đội ngũ:*
> 
> *Thứ nhất: Trước đây, mỗi đợt release thường đối mặt với nỗi lo chậm trễ vì công tác kiểm thử thủ công kéo dài qua nhiều vòng. Giờ đây, ngay khi lập trình viên hoàn thành tính năng, hệ thống tự động xác thực toàn bộ các luồng chính trên thiết bị thật, đưa ra kết quả minh bạch giúp đội ngũ tự tin bấm nút phát hành ngay trong ngày mà không có độ trễ.*
> 
> *Thứ hai: Đối với các bản vá khẩn cấp (Hotfix), chúng ta có thể kiểm tra nhanh chóng và xuất bản bản vá an toàn mà không sợ phát sinh lỗi hồi quy ngoài ý muốn.*
> 
> *Thứ ba: Về tối ưu thời gian làm việc, hệ thống giúp đội ngũ loại bỏ áp lực phải chạy đua kiểm thử hay làm ngoài giờ (OT) dồn dập trước mỗi đợt release. Dev và QA có thêm nhiều thời gian để hoàn thiện tính năng mới và nâng cao trải nghiệm người dùng một cách chủ động, thoải mái.*
> 
> *Thứ tư: Chi phí hạ tầng hoàn toàn 0 USD, đồng thời nền tảng này sẵn sàng nhân bản sang các ứng dụng tiếp theo của studio với công sức thiết lập tối thiểu!"*

---

### SLIDE 8: TRÌNH DIỄN THỰC TẾ (LIVE DEMO KỊCH BẢN MOCKUP PREVIEW)
* **Tiêu đề Slide**: *Trình Diễn Thực Tế: Kiểm Thử Toàn Trình Kịch Bản TC_11 — Mockup Preview Screen*
* **Thao tác**: Chiếu video hoặc chạy trực tiếp lệnh trên máy thật Samsung S20 FE:
  `.\run_tests_windows.ps1 -File "TC_11_Test_Mockup_Preview_Screen.yaml" -Version "Premium"`
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Để minh chứng cho độ ổn định thực tế, xin mời mọi người cùng theo dõi kịch bản kiểm thử luồng phức tạp: **TC_11 — Mockup Preview Screen**.*
> 
> *[Chỉ vào màn hình thiết bị đang chạy] Các bạn có thể thấy:*
> *- Ứng dụng tự động khởi chạy an toàn, bảo toàn trạng thái Premium.*
> *- Hệ thống tự động chọn template, vượt qua popup lưu, chuyển sang màn hình Mockup.*
> *- Tự động duyệt qua 5 mẫu sản phẩm thời trang, biển hiệu thực tế.*
> *- Xử lý luồng lưu thích ứng và chuyển đổi trạng thái nút bấm mượt mà.*
> *- Thị giác máy tính OpenCV chụp màn hình và đo đạc độ khớp so với ảnh thiết kế chuẩn.*
> *- Toàn bộ chu trình kiểm thử diễn ra trơn tru, hoàn toàn tự động không cần bất kỳ thao tác tay nào của con người!"*

---

### SLIDE 9: TỔNG KẾT & LỜI CẢM ƠN
* **Tiêu đề Slide**: *Sẵn Sàng Cho Production Release & Lời Cảm Ơn*
* **Nội dung hiển thị**:
  - Hệ thống tự động hóa đã hoàn thiện và sẵn sàng phục vụ các đợt phát hành Production.
  - Chốt chặn chất lượng vững chắc giúp ứng dụng Logo Maker tự tin ra thị trường đúng hẹn.
  - Sẵn sàng chuyển giao tài liệu và nhân bản sang các ứng dụng tiếp theo của studio.
  - Q&A — Sẵn sàng lắng nghe câu hỏi và ý kiến chỉ đạo.
* **Lời thoại Presenter**:
> *"[Chuyển Slide] Tóm lại, hệ thống Mobile Automation của Logo Maker đã trở thành một **chốt chặn chất lượng tự động, ổn định và tin cậy**, giúp đội ngũ tự tin kiểm chứng toàn bộ tính năng và phát hành ứng dụng đúng tiến độ.*
> 
> *Cảm ơn mọi người đã lắng nghe. Hệ thống Mobile Automation đã sẵn sàng bảo đảm chất lượng và tiến độ phát hành. Sau đây, mời mọi người cùng trao đổi và đặt câu hỏi. Xin cảm ơn!"*

---

## 🎯 BỘ CÂU HỎI VẤN ĐÁP & PHẢN BIỆN (TOUGH Q&A DEFENSE)

#### ❓ Câu hỏi 1: "Tại sao nhóm chọn Maestro mà không dùng Appium — công cụ đang rất phổ biến trên thị trường?"
> **💡 Trả lời tự tin**:
> *"Appium là công cụ tốt nhưng có kiến trúc trung gian qua WebDriver server phức tạp và rất dễ bị gián đoạn kết nối khi tích hợp CI/CD.  
> Ngược lại, Maestro giao tiếp trực tiếp ở tầng OS/Accessibility của thiết bị:
> 1. Tốc độ phản hồi nhanh hơn, chạy ổn định và mượt mà hơn.
> 2. Cú pháp khai báo YAML giúp kịch bản dễ đọc, Tester hay Developer đều có thể bảo trì dễ dàng mà không cần lập trình code phức tạp.
> 3. Khả năng tích hợp CI/CD điều phối trực tiếp trên thiết bị thật rất mượt mà."*

---

#### ❓ Câu hỏi 2: "So sánh ảnh (Visual Regression) có dễ bị fail oan khi người dùng đổi cài đặt máy, ví dụ như đổi thanh vuốt cử chỉ hay độ phân giải màn hình?"
> **💡 Trả lời tự tin**:
> *"Đó chính là lý do chúng tôi xây dựng cơ chế **Safe Insets & Multi-Zone**:
> 1. Script so sánh tự động loại bỏ phần viền thanh trạng thái phía trên và thanh điều hướng cử chỉ phía dưới, đảm bảo dù máy dùng phím bấm ảo hay vuốt cử chỉ thì ảnh kiểm tra vẫn đồng nhất.
> 2. Kịch bản test sử dụng mã phím hệ điều hành `KEYCODE_BACK` ở tầng kernel chứ không bấm vào tọa độ phím ảo, đảm bảo thao tác back luôn hoạt động ổn định trên mọi dòng máy."*

---

#### ❓ Câu hỏi 3: "Việc lưu trữ artifact và chạy kiểm thử tự động trên GitHub Actions có làm phát sinh chi phí hoặc tràn dung lượng tài khoản không?"
> **💡 Trả lời tự tin**:
> *"Chúng tôi đã kiểm soát tuyệt đối bài toán chi phí:
> 1. Tài khoản GitHub được cài đặt hạn mức chi tiêu Spending Limit = $0.00, không thể phát sinh chi phí ngoài ý muốn.
> 2. Chúng tôi cấu hình chính sách dọn dẹp artifact tự động sau khi hoàn tất kiểm thử, giữ dung lượng lưu trữ luôn ở ngưỡng an toàn, hoàn toàn miễn phí."*

---

#### ❓ Câu hỏi 4: "Nếu các lập trình viên thay đổi giao diện hoặc đổi ID nút bấm, chi phí bảo trì bộ test case này có lớn không?"
> **💡 Trả lời tự tin**:
> *"Chi phí bảo trì cực kỳ thấp nhờ 3 yếu tố:
> 1. **Cơ chế Selector Đa hình**: Sử dụng Regex pattern như `.*mnItemSave.*`, nên dev có đổi prefix hay suffix ID thì test vẫn nhận diện chính xác.
> 2. **Cờ `-UpdateBaseline`**: Nếu giao diện thay đổi hợp lệ theo thiết kế mới, QA chỉ cần chạy lại runner kèm cờ cập nhật baseline, hệ thống sẽ tự chụp ảnh mới và ghi đè làm chuẩn, không cần cắt ảnh bằng tay.
> 3. **Công cụ Dump UI Hierarchy tự động**: Khi có lỗi, hệ thống hỗ trợ trích xuất nhanh cấu trúc XML giao diện thực tế để định vị và cập nhật selector mới chỉ trong vài phút."*

---

#### ❓ Câu hỏi 5: "Đầu tư làm automation tốn công sức ban đầu như vậy, hiệu quả thực tế mang lại cho dự án là gì?"
> **💡 Trả lời tự tin**:
> *"Hiệu quả thể hiện rõ trên 3 khía cạnh:
> 1. **Đảm bảo tiến độ phát hành**: Đội ngũ không còn bị phụ thuộc vào chu trình kiểm thử thủ công kéo dài, ứng dụng sẵn sàng phát hành lên Store ngay khi hoàn thành tính năng, loại bỏ hoàn toàn nguy cơ chậm trễ lịch release.
> 2. **Chất lượng sản phẩm đồng nhất**: Toàn bộ luồng người dùng sống còn được máy móc kiểm tra khách quan và kỹ lưỡng, phát hiện sớm mọi lỗi vỡ giao diện hay hồi quy tính năng trước khi đến tay người dùng.
> 3. **Tối ưu thời gian làm việc & Khả năng nhân bản**: Giảm tải áp lực làm ngoài giờ (OT) cho đội ngũ, tạo điều kiện để hoàn thiện chất lượng sản phẩm tốt hơn; đồng thời framework được module hóa giúp tái sử dụng cho các ứng dụng mobile tiếp theo của công ty."*

---

## 🛠 HƯỚNG DẪN CHUẨN BỊ TRƯỚC KHI LÊN SÂN KHẤU (CHECKLIST)
- [ ] Cắm thiết bị thật Samsung S20 FE, kiểm tra `adb devices` nhận thiết bị.
- [ ] Chạy trước lệnh mở app để máy sẵn sàng ở Home Screen: `maestro test .maestro/config/Launch_App.yaml`.
- [ ] Mở sẵn file Excel [`docs/LogoMaker_Automation_TestSuite.xlsx`](file:///d:/logo-maker/docs/LogoMaker_Automation_TestSuite.xlsx) ở chế độ toàn màn hình để chiếu khi nói về các luồng tính năng.
- [ ] Mở sẵn tab GitHub Actions để chứng minh pipeline chạy tự động trên thiết bị thật pass tất cả các luồng.
- [ ] Tinh thần tự tin, giọng nói dõng dạc, nhấn mạnh vào **chất lượng sản phẩm và sự chủ động đảm bảo tiến độ release**!
