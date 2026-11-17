# -*- coding: utf-8 -*-
"""
Generate professional 9-slide PowerPoint Presentation (.pptx) for Logo Maker Mobile Automation Testing.
Focus: Testing critical user flows and core features to ensure on-schedule release (Release Readiness).
STRICT CONSTRAINT: No specific hour/minute numbers.
Outputs to: docs/LogoMaker_Automation_Presentation.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# -------------------------------------------------------------
# PALETTE DEFINITIONS (Executive Tech Navy Theme)
# -------------------------------------------------------------
C_NAVY_DARK   = RGBColor(15, 30, 54)     # #0F1E36 (Dark Background / Primary)
C_NAVY        = RGBColor(27, 54, 93)     # #1B365D (Navy Blue)
C_STEEL       = RGBColor(47, 85, 151)    # #2F5597 (Steel Blue Accent)
C_BLUE_LIGHT  = RGBColor(217, 225, 242)  # #D9E1F2 (Light Ice Blue)
C_WHITE       = RGBColor(255, 255, 255)  # #FFFFFF
C_BG_LIGHT    = RGBColor(248, 250, 252)  # #F8FAFC (Slide Content BG)
C_CARD_BG     = RGBColor(255, 255, 255)  # #FFFFFF
C_CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
C_TEXT_DARK   = RGBColor(30, 41, 59)     # #1E293B
C_TEXT_MUTED  = RGBColor(100, 116, 139)  # #64748B
C_GREEN       = RGBColor(22, 163, 74)    # #16A34A (Success Accent)
C_GREEN_BG    = RGBColor(226, 239, 218)  # #E2EFDA
C_AMBER       = RGBColor(217, 119, 6)    # #D97706
C_AMBER_BG    = RGBColor(255, 242, 204)  # #FFF2CC

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"
FONT_CODE    = "Consolas"

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category="LOGO MAKER MOBILE AUTOMATION TESTING"):
    tx_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
    tf_cat = tx_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.name = FONT_HEADING
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_STEEL

    tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.65))
    tf_title = tx_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = C_NAVY

    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.02)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = C_CARD_BORDER
    line.line.color.rgb = C_CARD_BORDER

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def add_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, C_NAVY_DARK)

    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_STEEL
    bar.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11), Inches(0.5))
    p = t_box.text_frame.paragraphs[0]
    p.text = "ENTERPRISE QUALITY GATE | RELEASE ON SCHEDULE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_LIGHT

    t_box2 = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11), Inches(1.6))
    t_box2.text_frame.word_wrap = True
    p2 = t_box2.text_frame.paragraphs[0]
    p2.text = "Tự Động Hóa Kiểm Thử Các Luồng & Tính Năng Trọng Yếu\nChốt Chặn Chất Lượng Đảm Bảo Kịp Tiến Độ Release"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE

    t_box3 = s1.shapes.add_textbox(Inches(1.2), Inches(3.8), Inches(11), Inches(0.6))
    p3 = t_box3.text_frame.paragraphs[0]
    p3.text = "Case Study: Ứng Dụng Logo Maker (Android) | Kiểm Chứng Toàn Diện Luồng Cốt Lõi Trên Thiết Bị Thật"
    p3.font.name = FONT_HEADING
    p3.font.size = Pt(14.5)
    p3.font.color.rgb = C_BLUE_LIGHT

    badges = [
        ("TARGET HARDWARE", "Samsung Galaxy S20 FE (Android 13)"),
        ("FLOW COVERAGE", "16 Core Suites | 317 Specs"),
        ("RELEASE GATE", "100% PASSED (Không Lỗi Hồi Quy)"),
        ("CORE TECH", "Maestro + OpenCV + CI/CD")
    ]
    for i, (b_lbl, b_val) in enumerate(badges):
        b_x = Inches(1.2 + i * 2.8)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, b_x, Inches(4.8), Inches(2.6), Inches(1.1))
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(27, 45, 75)
        card.line.color.rgb = RGBColor(47, 85, 151)
        
        tf = card.text_frame
        tf.word_wrap = True
        p_lbl = tf.paragraphs[0]
        p_lbl.text = b_lbl
        p_lbl.font.size = Pt(8.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_BLUE_LIGHT
        
        p_val = tf.add_paragraph()
        p_val.text = b_val
        p_val.font.size = Pt(10.5)
        p_val.font.bold = True
        p_val.font.color.rgb = C_WHITE

    tx_pres = s1.shapes.add_textbox(Inches(1.2), Inches(6.3), Inches(11), Inches(0.5))
    p_pres = tx_pres.text_frame.paragraphs[0]
    p_pres.text = "Báo cáo: Đội ngũ Automation QA / Technical Lead  |  Mục tiêu: Sẵn sàng phát hành Production"
    p_pres.font.size = Pt(11)
    p_pres.font.color.rgb = RGBColor(160, 175, 200)

    add_speaker_notes(s1, """Kính chào các anh chị Ban Lãnh đạo và các bạn đồng nghiệp,

Trong chu kỳ phát triển ứng dụng di động, thách thức lớn nhất của đội ngũ là làm sao vừa đưa sản phẩm ra thị trường đúng thời hạn (Time-to-Market), vừa đảm bảo tuyệt đối chất lượng, không để phát sinh lỗi hồi quy hay crash làm ảnh hưởng đến trải nghiệm người dùng và điểm xếp hạng trên Store.

Đối với một ứng dụng thiết kế đồ họa phức tạp như Logo Maker, việc kiểm thử thủ công lặp đi lặp lại hàng trăm kịch bản trước mỗi đợt phát hành luôn là một nút thắt cổ chai lớn. Hôm nay, tôi xin đại diện đội ngũ QA trình bày về Hệ thống Tự động hóa Kiểm thử Toàn diện — giải pháp giúp chúng ta kiểm chứng tự động toàn bộ các luồng người dùng và tính năng cốt lõi trên thiết bị thật, tạo ra một chốt chặn chất lượng vững chắc để ứng dụng tự tin phát hành kịp tiến độ cam kết.""")

    # =========================================================
    # SLIDE 2: THÁCH THỨC ĐẶC THÙ
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, C_BG_LIGHT)
    add_header(s2, "Tại Sao Mobile Automation Truyền Thống Thất Bại Trên Logo Maker?")

    challenges = [
        ("1. Canvas 'Mù' (Pure Graphics)", 
         "OpenGL / Custom Canvas", 
         "Toàn bộ đối tượng vẽ, icon logo, font nghệ thuật nằm trong Canvas không hề có Resource-ID hay Text trong XML Hierarchy. Công cụ truyền thống như Appium hoàn toàn bị 'mù'.", 
         C_AMBER),
        ("2. Nguy Cơ Báo Pass Ảo", 
         "False Pass & False Negative", 
         "So sánh ảnh thông thường bị đánh lừa bởi vùng viền ngoài quá lớn. Khi kiểm tra đổi màu nền phẳng (Flat Color), độ lệch chuẩn = 0 dẫn đến lỗi chia cho 0 gây fail oan.", 
         RGBColor(220, 38, 38)),
        ("3. Độ Flaky Cực Kỳ Cao", 
         "Popups, Ads & Tooltips", 
         "Hệ thống quảng cáo xen kẽ, màn hình mời mua VIP (IAP Paywall) ngẫu nhiên, cùng 8 tooltips onboarding che phủ kín màn hình Edit sau khi cài mới nếu không được dọn dẹp sạch.", 
         C_STEEL),
        ("4. Phân Hóa Phiên Bản", 
         "Free vs Premium Architecture", 
         "Cùng tính năng Lưu: Bản Free có ID nút 'mnItemSave' và hiện popup Watermark; bản Premium đổi thành 'mnItemSavePremium' và chuyển thẳng sang nút Share. Viết test riêng lẻ gây tốn công bảo trì.", 
         C_NAVY)
    ]

    for i, (c_title, c_sub, c_desc, c_bar) in enumerate(challenges):
        x = Inches(0.8 + i * 2.98)
        y = Inches(1.65)
        w = Inches(2.8)
        h = Inches(5.1)
        
        card = add_card(s2, x, y, w, h)
        bar_card = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.1))
        bar_card.fill.solid()
        bar_card.fill.fore_color.rgb = c_bar
        bar_card.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.15), y + Inches(0.2), w - Inches(0.3), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        
        p_sub = tf.add_paragraph()
        p_sub.text = c_sub.upper()
        p_sub.font.size = Pt(8.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = c_bar
        p_sub.space_after = Pt(14)
        
        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_TEXT_DARK
        p_d.line_spacing = 1.3

    add_speaker_notes(s2, """[Chuyển Slide] Khi tiếp cận bài toán kiểm thử cho Logo Maker, nếu sử dụng các công cụ truyền thống như Appium, chúng ta sẽ lập tức gặp phải các rào cản kỹ thuật nghiêm trọng:

1. Logo Maker là ứng dụng đồ họa. Trên vùng Canvas, toàn bộ chi tiết logo là các layer đồ họa render trực tiếp — chúng hoàn toàn không có ID, không có Text để các công cụ thông thường định vị.
2. Khi kiểm thử đổi màu nền hoặc xoay 3D, nếu chỉ so sánh ảnh toàn màn hình một cách thô sơ, việc chữ trên logo bị biến dạng có thể bị bỏ lọt và hệ thống vẫn báo PASS ảo.
3. Thêm vào đó là sự phân hóa giữa bản Free và Premium: Nút Lưu tự đổi ID từ mnItemSave sang mnItemSavePremium, luồng lưu bản Free bật popup bắt xem quảng cáo, bản Premium lại chuyển thẳng sang nút Share.

Nếu chỉ dựa vào kiểm thử thủ công, đội ngũ sẽ mất rất nhiều công sức rà soát lặp đi lặp lại, dễ mệt mỏi và bỏ sót lỗi, dẫn đến nguy cơ chậm trễ lịch phát hành. Để giải quyết triệt để, chúng tôi đã xây dựng một kiến trúc Hybrid Automation 3 tầng.""")

    # =========================================================
    # SLIDE 3: KIẾN TRÚC HYBRID AUTOMATION 3 TẦNG
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, C_BG_LIGHT)
    add_header(s3, "Kiến Trúc Framework 3 Tầng: Ổn Định — Thông Minh — Tự Động Hóa Hoàn Toàn")

    tiers = [
        ("TẦNG 1: THI HÀNH KIỂM THỬ (EXECUTION LAYER)",
         "Maestro Declarative YAML Framework",
         "Giao tiếp trực tiếp ở tầng OS & Accessibility Service của Android.\n"
         "• Cú pháp YAML khai báo (Declarative): Rõ ràng, dễ đọc, dễ mở rộng.\n"
         "• Tốc độ chạy native: Chạy ổn định tuyệt đối và mượt mà hơn nhiều so với Appium WebDriver.\n"
         "• Triệt tiêu lỗi rớt kết nối, tự động xử lý bàn phím và animation kết thúc an toàn.",
         C_NAVY),
        ("TẦNG 2: THỊ GIÁC MÁY TÍNH & TRÍ TUỆ (INTELLIGENCE LAYER)",
         "Python 3 + OpenCV Engine + HTTP Daemon (Port 8765)",
         "Đóng vai trò là 'đôi mắt' phân tích và tương tác hình ảnh thông minh.\n"
         "• Dynamic Multi-Zone: Cắt bỏ an toàn StatusBar và Gesture Bar, chia vùng Canvas & Tool.\n"
         "• Thích ứng MAE (Mean Absolute Error): So sánh chuẩn xác màu sắc nền phẳng đơn sắc.\n"
         "• OpenCV Daemon: Quét template nhận diện và điều khiển tap chính xác vào element không có ID.",
         C_STEEL),
        ("TẦNG 3: ĐIỀU PHỐI & HẠ TẦNG (ORCHESTRATION LAYER)",
         "PowerShell Runner & CI/CD Pipeline Thiết Bị Thật",
         "Điều phối toàn diện môi trường kiểm thử tự động.\n"
         "• Windows Test Runner (run_tests_windows.ps1): Điều phối kịch bản, kiểm tra thiết bị, dọn session, cập nhật baseline.\n"
         "• Chốt Chặn Quality Gate: Tự động xác thực toàn bộ các luồng trọng yếu trước khi đưa bản build lên Google Play Store.\n"
         "• CI/CD Tối Ưu Chi Phí $0: Cơ chế tự động dọn dẹp artifact, duy trì lưu trữ luôn ở ngưỡng an toàn.",
         C_GREEN)
    ]

    for i, (t_title, t_sub, t_desc, t_color) in enumerate(tiers):
        y = Inches(1.65 + i * 1.75)
        card = add_card(s3, Inches(0.8), y, Inches(11.7), Inches(1.55))
        
        bar_card = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.15), Inches(1.55))
        bar_card.fill.solid()
        bar_card.fill.fore_color.rgb = t_color
        bar_card.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(1.15), y + Inches(0.12), Inches(11.2), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = t_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = t_color
        
        p_sub = tf.add_paragraph()
        p_sub.text = t_sub
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = C_NAVY
        p_sub.space_after = Pt(4)
        
        p_d = tf.add_paragraph()
        p_d.text = t_desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_DARK
        p_d.line_spacing = 1.25

    add_speaker_notes(s3, """[Chuyển Slide] Bức tranh tổng thể về kiến trúc giải pháp gồm 3 tầng bổ trợ chặt chẽ cho nhau:

Ở Tầng 1 - Test Execution, chúng tôi ứng dụng Maestro Framework. Khác với các công cụ cồng kềnh qua trung gian WebDriver, Maestro giao tiếp trực tiếp ở tầng OS/Accessibility của Android bằng cú pháp YAML khai báo. Nhờ vậy, kịch bản cực kỳ ổn định, tốc độ thực thi native và triệt tiêu các lỗi mất kết nối giữa chừng.

Ở Tầng 2 - Thị giác máy tính (Intelligence Layer), bộ script Python chuyên sâu đóng vai trò là 'đôi mắt' của hệ thống: tự động phân tích ảnh đa vùng, thích ứng màu sắc và chạy dịch vụ ngầm để nhận diện đồ họa.

Ở Tầng 3 - Điều phối & Hạ tầng (Orchestration), bộ Runner thông minh điều phối kịch bản chạy trực tiếp trên thiết bị thật, tự động dọn dẹp môi trường sau mỗi lượt và xuất báo cáo trực quan lên hệ thống CI/CD.""")

    # =========================================================
    # SLIDE 4: BỘ 3 THUẬT TOÁN ĐỘT PHÁ
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, C_BG_LIGHT)
    add_header(s4, "Bộ 3 Thuật Toán Cốt Lõi: Đột Phá Xử Lý Hình Ảnh & Kháng Lỗi Giao Diện")

    algos = [
        ("THUẬT TOÁN 1: DYNAMIC MULTI-ZONE & MAE",
         "Visual Regression & Nền Phẳng",
         "• Safe Insets: Cắt bỏ vùng viền trên (Status Bar) & dưới (Gesture Bar), loại bỏ sai khác vạch điều hướng.\n"
         "• Đa vùng độc lập: Canvas Zone (ngưỡng khắt khe) và Tool Zone đánh giá riêng biệt.\n"
         "• Thích ứng MAE: Khi kiểm tra nền phẳng đơn sắc (Flat Color), tự động chuyển sang đo khoảng cách sai số màu (MAE) trong không gian RGB, triệt tiêu lỗi chia cho 0 gây fail oan.",
         C_STEEL),
        ("THUẬT TOÁN 2: OPENCV TEMPLATE DAEMON",
         "Computer Vision Bắt Mẫu Đồ Họa 'Mù'",
         "• Daemon Service: Khởi chạy ngầm Python HTTP Daemon trên cổng 8765 kết nối qua JS Bridge.\n"
         "• TM_CCOEFF_NORMED: Áp dụng thuật toán chuẩn hóa tương quan quét ma trận ảnh màn hình thời gian thực.\n"
         "• Xác định vị trí khớp nhất, tự động tính tâm tọa độ và gửi lệnh tap chuẩn xác vào các element không có UI ID hay Text.",
         C_NAVY),
        ("THUẬT TOÁN 3: SELECTOR ĐA HÌNH & ADAPTIVE",
         "Kháng Lỗi Phân Hóa Free vs Premium",
         "• Regex Selector Đa Hình: id: '.*mnItemSave.*' tương thích cả mnItemSave (bản Free) và mnItemSavePremium (bản Premium).\n"
         "• Cây Quyết Định Thích Ứng: Rẽ nhánh tự động: thấy dialog watermark thì xử lý; không có dialog thì kiểm tra nút Share.\n"
         "• 1 kịch bản duy nhất chạy thông suốt cả Free và Premium.",
         C_GREEN)
    ]

    for i, (a_title, a_sub, a_desc, a_col) in enumerate(algos):
        x = Inches(0.8 + i * 3.98)
        y = Inches(1.65)
        w = Inches(3.75)
        h = Inches(5.1)

        card = add_card(s4, x, y, w, h)
        bar_card = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.1))
        bar_card.fill.solid()
        bar_card.fill.fore_color.rgb = a_col
        bar_card.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.18), y + Inches(0.2), w - Inches(0.36), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = a_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = a_col

        p_sub = tf.add_paragraph()
        p_sub.text = a_sub.upper()
        p_sub.font.size = Pt(8.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = C_NAVY
        p_sub.space_after = Pt(12)

        p_d = tf.add_paragraph()
        p_d.text = a_desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_DARK
        p_d.line_spacing = 1.3

    add_speaker_notes(s4, """[Chuyển Slide] Trọng tâm công nghệ giúp hệ thống kiểm thử chính xác mà không gặp lỗi 'báo động giả' nằm ở Bộ 3 Thuật Toán Cốt Lõi:

1. Thuật toán Dynamic Multi-Zone & Thích ứng MAE: Hệ thống tự động cắt bỏ thanh trạng thái và vạch cử chỉ, chia màn hình thành vùng Canvas và vùng công cụ để đánh giá với ngưỡng riêng biệt. Với các màn hình đổi màu nền phẳng — nơi các thuật toán tương quan thông thường dễ bị lỗi chia cho 0 và báo trượt oan — hệ thống tự động chuyển sang đo khoảng cách màu MAE, đảm bảo kiểm tra chuẩn xác từng thay đổi màu sắc.

2. Thuật toán Thị giác máy tính OpenCV Template Matching: Để chọn đúng các mẫu logo dạng ảnh không có ID hay text, một dịch vụ ngầm sẽ quét màn hình, xác định tọa độ khớp nhất và điều khiển bấm chính xác vào tâm đối tượng.

3. Thuật toán Selector Đa hình & Cây Quyết định Thích ứng: Kịch bản áp dụng biểu thức Regex .*mnItemSave.* kết hợp cơ chế tự động rẽ nhánh. Nhờ vậy, cùng một kịch bản có thể kiểm thử mượt mà trên cả bản Free lẫn bản Premium mà không bị gãy luồng khi lập trình viên thay đổi tiền tố ID nút bấm.

Ba thuật toán này tạo nên bộ khung vững chắc giúp việc kiểm thử tự động diễn ra ổn định và hoàn toàn tin cậy.""")

    # =========================================================
    # SLIDE 5: HẠ TẦNG CI/CD — CHỐT CHẶN CHẤT LƯỢNG TRƯỚC GIỜ RELEASE
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_BG_LIGHT)
    add_header(s5, "Quality Gate Tự Động Trên Thiết Bị Thật: Bảo Đảm Chất Lượng Kịp Tiến Độ Release")

    ci_cards = [
        ("THIẾT BỊ PHẦN CỨNG THẬT", "Samsung Galaxy S20 FE (Android 13)", "100% độ tin cậy phần cứng: Màn hình thật, GPU render thật, bộ nhớ RAM thật. Loại trừ hoàn toàn tình trạng sai màu do giả lập Emulator.", C_NAVY),
        ("CHỐT CHẶN CHẤT LƯỢNG (QUALITY GATE)", "Kiểm Chứng Tự Động Toàn Trình", "Tự động kiểm tra toàn bộ các luồng sống còn trước giờ phát hành. Độc lập, khách quan, loại bỏ sự phụ thuộc vào test tay kéo dài.", C_GREEN),
        ("TỐI ƯU CHI PHÍ HẠ TẦNG", "Chi Phí Cloud = $0.00", "Chính sách dọn dẹp artifact tự động, duy trì lưu trữ ở ngưỡng an toàn, hoàn toàn không phát sinh chi phí ngoài ý muốn.", C_STEEL)
    ]
    for i, (c_h, c_val, c_sub, c_col) in enumerate(ci_cards):
        x = Inches(0.8 + i * 3.98)
        card = add_card(s5, x, Inches(1.65), Inches(3.75), Inches(1.5))
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = c_h
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MUTED
        
        p2 = tf.add_paragraph()
        p2.text = c_val
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = c_col
        p2.space_after = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = c_sub
        p3.font.size = Pt(9)
        p3.font.color.rgb = C_TEXT_DARK

    y_tbl = Inches(3.4)
    tbl_card = add_card(s5, Inches(0.8), y_tbl, Inches(11.7), Inches(3.3))
    
    tb = s5.shapes.add_textbox(Inches(1.1), y_tbl + Inches(0.15), Inches(11.1), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "SO SÁNH MÔ THỨC KIỂM THỬ: THỦ CÔNG VS TỰ ĐỘNG HÓA CHỐT CHẶN RELEASE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(10)

    rows = [
        ("Mô Thức Kiểm Thử", "Đặc Điểm Vận Hành", "Tốc Độ & Hiệu Quả"),
        ("Kiểm thử thủ công (Manual QA)", "Hàng trăm bước test lặp lại, dễ mệt mỏi và sót lỗi", "Rất chậm · Dễ trễ lịch Release"),
        ("Quality Gate tự động (Máy thật)", "Tự động kiểm tra toàn bộ 6 luồng sống còn", "Nhanh chóng · Sẵn sàng Release ngay"),
        ("Kiểm tra 1 màn hình khi sửa code", "Chạy riêng từng kịch bản khi lập trình viên fix bug", "Tức thì · Phản hồi ngay cho Dev")
    ]
    for r_idx, (c1, c2, c3) in enumerate(rows):
        p_row = tf.add_paragraph()
        p_row.text = f"• {c1:42} | {c2:38} | {c3}"
        p_row.font.name = FONT_CODE if r_idx > 0 else FONT_HEADING
        p_row.font.size = Pt(9.5)
        p_row.font.bold = (r_idx == 0 or r_idx == 2)
        p_row.font.color.rgb = C_NAVY if r_idx == 0 else (C_GREEN if r_idx == 2 else C_TEXT_DARK)
        p_row.space_after = Pt(6)

    add_speaker_notes(s5, """[Chuyển Slide] Một bộ kiểm thử tự động sẽ chỉ thực sự mang lại giá trị khi nó được kiểm chứng trên chính môi trường phần cứng thực tế của người dùng.

Thay vì chạy trên các máy ảo giả lập vốn thường gặp sai lệch về màu sắc hiển thị hoặc khả năng render GPU, toàn bộ hệ thống của chúng tôi được thực thi trực tiếp trên thiết bị phần cứng thật (Samsung Galaxy S20 FE, Android 13).

Điều này tạo ra 3 giá trị sống còn cho tiến độ phát hành:
1. Độ tin cậy tuyệt đối: Mọi thao tác vẽ Canvas, chọn màu, lưu Mockup đều chạy trên màn hình thực, chip xử lý thực và bộ nhớ RAM thực tế.
2. Chốt chặn chất lượng (Quality Gate) tự động: Trước mỗi đợt Release, thay vì phải chờ đợi QA rà soát thủ công qua nhiều vòng căng thẳng, hệ thống sẽ tự động thực thi toàn bộ kịch bản kiểm thử, đưa ra kết quả xanh mướt và xác thực mọi tính năng hoạt động hoàn hảo.
3. Tối ưu chi phí $0: Toàn bộ quy trình được tích hợp vào pipeline với cơ chế tự động dọn dẹp dữ liệu lưu trữ, hoàn toàn không phát sinh chi phí hạ tầng cloud hay thuê dịch vụ ngoài.

Nhờ đó, đội ngũ hoàn toàn chủ động về mặt tiến độ, sẵn sàng đưa sản phẩm lên Store mà không gặp bất kỳ trở ngại nào!""")

    # =========================================================
    # SLIDE 6: KẾT QUẢ ĐẠT ĐƯỢC — PHỦ KÍN CÁC LUỒNG SỐNG CÒN
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_BG_LIGHT)
    add_header(s6, "Báo Cáo Thành Quả: Bao Phủ 100% Các Luồng & Tính Năng Trọng Yếu Của Ứng Dụng")

    kpis = [
        ("16 / 16", "CORE YAML SUITES", "100% PASSED (Zero Flaky)"),
        ("317", "CA KIỂM THỬ SPEC", "Tự Động Hóa Toàn Diện"),
        ("6 LUỒNG", "TRẢI NGHIỆM SỐNG CÒN", "Bảo Vệ Chất Lượng Release"),
        ("EXCEL", "TEST SUITE MATRIX", "Số Hóa Ma Trận Quản Trị")
    ]
    for i, (k_val, k_lbl, k_sub) in enumerate(kpis):
        x = Inches(0.8 + i * 2.98)
        card = add_card(s6, x, Inches(1.65), Inches(2.8), Inches(1.4))
        tf = card.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = k_val
        p.font.name = FONT_HEADING
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        
        p2 = tf.add_paragraph()
        p2.text = k_lbl
        p2.font.size = Pt(8.5)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_MUTED
        
        p3 = tf.add_paragraph()
        p3.text = k_sub
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = C_GREEN
        p3.font.bold = True

    card_det = add_card(s6, Inches(0.8), Inches(3.3), Inches(11.7), Inches(3.5))
    tb_det = s6.shapes.add_textbox(Inches(1.1), Inches(3.45), Inches(11.1), Inches(3.2))
    tf_det = tb_det.text_frame
    tf_det.word_wrap = True
    
    p = tf_det.paragraphs[0]
    p.text = "CHI TIẾT 6 LUỒNG TRẢI NGHIỆM NGƯỜI DÙNG CỐT LÕI ĐÃ ĐƯỢC BẢO VỆ TỰ ĐỘNG"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(8)

    modules_txt = [
        ("1. Luồng Khởi Động & Mua Hàng (IAP Paywall)", "Kiểm thử màn hình bảng giá VIP, thanh toán tuần/năm, dùng thử 3 ngày và đóng paywall an toàn."),
        ("2. Luồng Khám Phá & Chọn Mẫu (Template Discovery)", "Kiểm tra 6 thẻ tính năng Home, duyệt danh mục mẫu logo, tải tài nguyên vào Edit Canvas không lỗi."),
        ("3. Luồng Chỉnh Sửa Đồ Họa Cốt Lõi (Core Edit Flow)", "Background đổi màu/texture/cắt ảnh, Art controls/layers/3D, Text nhập chữ/font nghệ thuật/size/14 tính năng con."),
        ("4. Luồng Lưu & Xuất Bản Đồ Họa (Save & HD Export)", "Lưu bản nháp Draft, xuất PNG HD chất lượng cao, hộp thoại đánh giá Rate dialog, chia sẻ Preview Screen."),
        ("5. Luồng Nhận Diện Thương Hiệu (Mockup Preview)", "Xem logo trên 5 sản phẩm thời trang/biển hiệu thực tế, lưu mockup có/không watermark, chuyển trạng thái Save -> Share."),
        ("6. Luồng Sáng Tạo Logo Bằng AI (AI Studio Flow)", "Nhập Prompt ý tưởng, chọn Style Preset, gọi AI sinh logo và tự động đưa kết quả vào Canvas chỉnh sửa.")
    ]
    for m_title, m_desc in modules_txt:
        p_m = tf_det.add_paragraph()
        p_m.text = f"✔ {m_title:45}: {m_desc}"
        p_m.font.size = Pt(9.5)
        p_m.font.color.rgb = C_TEXT_DARK
        p_m.space_after = Pt(3)

    add_speaker_notes(s6, """[Chuyển Slide] Nhìn vào bức tranh thành quả, hệ thống đã bảo vệ toàn diện 6 luồng trải nghiệm người dùng sống còn của Logo Maker:

Toàn bộ 16 kịch bản tự động hóa tương ứng với 317 ca kiểm thử chi tiết đều đã đạt trạng thái PASSED 100% trên thiết bị thật.
Từ luồng thanh toán mua gói VIP, điều hướng chọn template, chỉnh sửa đa lớp trên Canvas, cho đến lưu xuất file ảnh HD, xem trước Mockup sản phẩm và tính năng tạo logo bằng AI — tất cả đều có kịch bản tự động kiểm tra nghiêm ngặt trước mỗi đợt phát hành.

Toàn bộ dữ liệu này đã được số hóa và xuất bản thành bộ tài liệu Excel ma trận kiểm thử chi tiết, giúp Product Owner, Dev Lead và QA luôn nắm rõ trạng thái sẵn sàng của sản phẩm.""")

    # =========================================================
    # SLIDE 7: BẢO ĐẢM TIẾN ĐỘ RELEASE & GIÁ TRỊ DOANH NGHIỆP
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_BG_LIGHT)
    add_header(s7, "Bảo Đảm Tiến Độ Phát Hành (Release Readiness) & Tối Ưu Thời Gian Làm Việc")

    roi_cards = [
        ("1. BẢO ĐẢM TIẾN ĐỘ RELEASE",
         "Sẵn Sàng Phát Hành Ngay",
         "Loại bỏ hoàn toàn sự chậm trễ do chờ đợi kiểm thử thủ công kéo dài trước ngày phát hành. Toàn bộ luồng chính được xác thực tự động, giúp app sẵn sàng đẩy lên Store ngay khi dev hoàn thành code.",
         C_NAVY),
        ("2. ĐÁP ỨNG HOTFIX THẦN TỐC",
         "Kiểm Chứng Bản Vá An Toàn",
         "Khi phát sinh lỗi cần sửa gấp trên Production, hệ thống tự động kiểm chứng nhanh chóng tính toàn vẹn của ứng dụng, đảm bảo bản vá an toàn và không làm vỡ các tính năng sẵn có.",
         C_GREEN),
        ("3. TỐI ƯU THỜI GIAN LÀM VIỆC",
         "Làm Việc Thông Minh Hơn",
         "Loại bỏ các thao tác lặp lại, giảm áp lực chạy đua deadline và làm thêm giờ (OT) trước ngày release. Đội ngũ có thêm thời gian hoàn thiện tính năng và chăm chút trải nghiệm người dùng.",
         C_STEEL),
        ("4. HIỆU QUẢ ĐẦU TƯ BỀN VỮNG",
         "Hạ Tầng $0 & Tái Sử Dụng",
         "Chi phí hạ tầng 0 USD, hệ thống vận hành bền vững trong chu kỳ release. Kiến trúc framework module hóa cao, sẵn sàng tái sử dụng phần lớn nền tảng cho các app tiếp theo.",
         C_AMBER)
    ]
    for i, (r_title, r_val, r_desc, r_col) in enumerate(roi_cards):
        x = Inches(0.8 + i * 2.98)
        card = add_card(s7, x, Inches(1.65), Inches(2.8), Inches(5.1))
        
        bar_card = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.65), Inches(2.8), Inches(0.1))
        bar_card.fill.solid()
        bar_card.fill.fore_color.rgb = r_col
        bar_card.line.fill.background()

        tb = s7.shapes.add_textbox(x + Inches(0.15), Inches(1.85), Inches(2.5), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = r_title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = r_col

        p2 = tf.add_paragraph()
        p2.text = r_val
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = C_NAVY
        p2.space_after = Pt(14)

        p3 = tf.add_paragraph()
        p3.text = r_desc
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_TEXT_DARK
        p3.line_spacing = 1.35

    add_speaker_notes(s7, """[Chuyển Slide] Thưa Ban Giám đốc và các anh chị, giá trị lớn nhất mà hệ sinh thái tự động hóa này mang lại chính là bảo đảm tiến độ phát hành (Release on Schedule) và tối ưu thời gian làm việc:

Thứ nhất: Trước đây, mỗi đợt release thường đối mặt với nỗi lo chậm trễ vì công tác kiểm thử thủ công kéo dài qua nhiều vòng. Giờ đây, ngay khi lập trình viên hoàn thành tính năng, hệ thống tự động xác thực toàn bộ các luồng chính trên thiết bị thật, đưa ra kết quả minh bạch giúp đội ngũ tự tin bấm nút phát hành ngay trong ngày mà không có độ trễ.

Thứ hai: Đối với các bản vá khẩn cấp (Hotfix), chúng ta có thể kiểm tra nhanh chóng và xuất bản bản vá an toàn mà không sợ phát sinh lỗi hồi quy ngoài ý muốn.

Thứ ba: Về tối ưu thời gian làm việc, hệ thống giúp đội ngũ loại bỏ áp lực phải chạy đua kiểm thử hay làm ngoài giờ (OT) dồn dập trước mỗi đợt release. Dev và QA có thêm nhiều thời gian để hoàn thiện tính năng mới và nâng cao trải nghiệm người dùng một cách chủ động, thoải mái!""")

    # =========================================================
    # SLIDE 8: LIVE DEMO MINH HỌA
    # =========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_BG_LIGHT)
    add_header(s8, "Trình Diễn Thực Tế: Kiểm Thử Toàn Trình Kịch Bản TC_11 — Mockup Preview Screen")

    demo_steps = [
        ("BƯỚC 1: KHỞI TẠO AN TOÀN", "Clear State = False", "Khởi động ứng dụng an toàn không mất dữ liệu Premium. Vượt qua Onboarding và màn hình chính tự động."),
        ("BƯỚC 2: CHỈNH SỬA & XUẤT PNG", "Tạo Logo Từ Template", "Chọn template nhà hàng qua OpenCV, chuyển sang Edit Canvas, bấm Lưu HD PNG và điều hướng sang Mockup Preview."),
        ("BƯỚC 3: DUYỆT 5 MẪU MOCKUP", "Brand Identify Simulation", "Tự động cuộn qua 5 mẫu sản phẩm (Áo thun, Mũ, Biển hiệu, Cốc cafe), kiểm tra render logo sắc nét trên mockup."),
        ("BƯỚC 4: LƯU MOCKUP THÍCH ỨNG", "Adaptive Save Flow", "Bản Free xử lý dialog watermark; bản Premium lưu trực tiếp, tự động chuyển trạng thái nút Lưu -> Share."),
        ("BƯỚC 5: THỊ GIÁC OPENCV MATCH", "So Khớp Ảnh Chuẩn", "Python OpenCV chụp màn hình và đo đạc độ khớp so với ảnh thiết kế chuẩn baseline, thông qua hoàn toàn.")
    ]

    for i, (d_step, d_h, d_desc) in enumerate(demo_steps):
        x = Inches(0.8 + i * 2.38)
        card = add_card(s8, x, Inches(1.65), Inches(2.25), Inches(3.8))
        
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = d_step
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_STEEL
        
        p2 = tf.add_paragraph()
        p2.text = d_h
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = C_NAVY
        p2.space_after = Pt(10)
        
        p3 = tf.add_paragraph()
        p3.text = d_desc
        p3.font.size = Pt(9)
        p3.font.color.rgb = C_TEXT_DARK
        p3.line_spacing = 1.25

    t_box = add_card(s8, Inches(0.8), Inches(5.7), Inches(11.7), Inches(1.1), bg_color=C_NAVY_DARK)
    tb_cmd = s8.shapes.add_textbox(Inches(1.0), Inches(5.75), Inches(11.3), Inches(1.0))
    tf_cmd = tb_cmd.text_frame
    tf_cmd.word_wrap = True
    
    p = tf_cmd.paragraphs[0]
    p.text = "LỆNH THỰC THI TRỰC TIẾP TRÊN MÁY THẬT SAMSUNG S20 FE (POWERSHELL):"
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_LIGHT
    
    p2 = tf_cmd.add_paragraph()
    p2.text = ".\\run_tests_windows.ps1 -File \"TC_11_Test_Mockup_Preview_Screen.yaml\" -Version \"Premium\""
    p2.font.name = FONT_CODE
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE

    add_speaker_notes(s8, """[Chuyển Slide] Để minh chứng cho độ ổn định thực tế, xin mời mọi người cùng theo dõi kịch bản kiểm thử luồng phức tạp: TC_11 — Mockup Preview Screen.

[Chỉ vào màn hình thiết bị đang chạy] Các bạn có thể thấy:
- Ứng dụng tự động khởi chạy an toàn, bảo toàn trạng thái Premium.
- Hệ thống tự động chọn template, vượt qua popup lưu, chuyển sang màn hình Mockup.
- Tự động duyệt qua 5 mẫu sản phẩm thời trang, biển hiệu thực tế.
- Xử lý luồng lưu thích ứng và chuyển đổi trạng thái nút bấm mượt mà.
- Thị giác máy tính OpenCV chụp màn hình và đo đạc độ khớp so với ảnh thiết kế chuẩn.
- Toàn bộ chu trình kiểm thử diễn ra trơn tru, hoàn toàn tự động không cần bất kỳ thao tác tay nào của con người!""")

    # =========================================================
    # SLIDE 9: TỔNG KẾT & Q&A PHẢN BIỆN
    # =========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_NAVY_DARK)

    bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_GREEN
    bar.line.fill.background()

    t_box = s9.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    p = t_box.text_frame.paragraphs[0]
    p.text = "Hệ Thống Đã Sẵn Sàng Cho Production Release & Lắng Nghe Q&A"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    takeaways = [
        ("SẴN SÀNG CHO PRODUCTION", "16 Suites bao phủ 317 test cases, 100% Pass trên thiết bị thật, là Quality Gate tự động vững chắc bảo đảm ứng dụng ra thị trường đúng hẹn."),
        ("BỘ TÀI LIỆU CHUẨN MỰC", "Đầy đủ file Excel Test Suite, kịch bản thuyết trình và tài liệu chuyển giao kỹ thuật chi tiết từ A–Z giúp các bên dễ dàng theo dõi trạng thái chất lượng."),
        ("KHẢ NĂNG NHÂN BẢN CAO", "Framework được thiết kế module hóa, có thể tái sử dụng phần lớn kiến trúc lõi cho các dự án ứng dụng di động tiếp theo của công ty.")
    ]
    for i, (t_h, t_d) in enumerate(takeaways):
        x = Inches(0.8 + i * 3.98)
        card = add_card(s9, x, Inches(1.65), Inches(3.75), Inches(2.2), bg_color=RGBColor(27, 45, 75), border_color=RGBColor(47, 85, 151))
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t_h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_BLUE_LIGHT
        p.space_after = Pt(8)
        
        p2 = tf.add_paragraph()
        p2.text = t_d
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_WHITE
        p2.line_spacing = 1.3

    q_card = add_card(s9, Inches(0.8), Inches(4.2), Inches(11.7), Inches(2.5), bg_color=RGBColor(20, 35, 60), border_color=RGBColor(40, 70, 120))
    tb_q = s9.shapes.add_textbox(Inches(1.1), Inches(4.35), Inches(11.1), Inches(2.2))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    
    p = tf_q.paragraphs[0]
    p.text = "HỎI ĐÁP & PHẢN BIỆN (Q&A DEFENSE - CHỦ ĐỀ CHUẨN BỊ SẴN):"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(6)

    q_items = [
        "1. Tại sao chọn Maestro mà không dùng Appium? (Native OS, Declarative YAML, chạy mượt và không bị timeout/flaky).",
        "2. Visual Regression có bị fail oan khi đổi cài đặt máy? (Safe Insets loại bỏ viền trên/dưới, MAE đo màu phẳng).",
        "3. Chạy CI/CD có bị tốn phí hay tràn dung lượng? (Spending limit $0, tự động dọn dẹp artifact giữ lưu trữ an toàn).",
        "4. Chi phí bảo trì khi dev đổi ID nút bấm? (Selector Regex .*mnItemSave.*, cờ cập nhật baseline tự động).",
        "5. Giá trị thực tế mang lại cho việc Release? (Chốt chặn chất lượng tự động, kịp tiến độ phát hành, tối ưu thời gian làm việc cho đội ngũ)."
    ]
    for q_t in q_items:
        p_q = tf_q.add_paragraph()
        p_q.text = f"• {q_t}"
        p_q.font.size = Pt(9)
        p_q.font.color.rgb = C_BLUE_LIGHT
        p_q.space_after = Pt(2)

    add_speaker_notes(s9, """[Chuyển Slide] Tóm lại, hệ thống Mobile Automation của Logo Maker đã trở thành một chốt chặn chất lượng tự động, ổn định và tin cậy, giúp đội ngũ tự tin kiểm chứng toàn bộ tính năng và phát hành ứng dụng đúng tiến độ.

Cảm ơn mọi người đã lắng nghe. Hệ thống Mobile Automation đã sẵn sàng bảo đảm chất lượng và tiến độ phát hành. Sau đây, mời mọi người cùng trao đổi và đặt câu hỏi. Xin cảm ơn!""")

    output_path = r"d:\logo-maker\docs\LogoMaker_Automation_Presentation.pptx"
    alt_path = r"d:\logo-maker\docs\LogoMaker_Automation_Presentation_Release.pptx"
    try:
        prs.save(output_path)
        print(f"Presentation saved successfully to: {output_path}")
    except PermissionError:
        prs.save(alt_path)
        print(f"LƯU Ý: File '{output_path}' đang được mở bởi PowerPoint. Đã lưu bản cập nhật mới vào '{alt_path}'.")

if __name__ == "__main__":
    build_deck()
