# -*- coding: utf-8 -*-
"""
Generate comprehensive Excel Execution Time Benchmark for Logo Maker (Android Platform).
Outputs to:
1. docs/LogoMaker_Execution_Time_Benchmark.xlsx (Standalone Dedicated Benchmark Workbook)
2. Also integrates into docs/LogoMaker_Automation_TestSuite.xlsx as Sheet 4
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_time_benchmark_sheet(wb, title="⏱️ Execution Time Benchmark"):
    ws = wb.create_sheet(title=title)
    ws.views.sheetView[0].showGridLines = True
    
    # Fonts
    font_family = "Segoe UI"
    font_title = Font(name=font_family, size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name=font_family, size=10, italic=True, color="D9E1F2")
    font_section = Font(name=font_family, size=11, bold=True, color="1F4E79")
    font_header = Font(name=font_family, size=9.5, bold=True, color="FFFFFF")
    font_card_num = Font(name=font_family, size=18, bold=True, color="1F4E79")
    font_card_lbl = Font(name=font_family, size=8.5, bold=True, color="595959")
    
    font_cell = Font(name=font_family, size=9, color="1F1F1F")
    font_cell_bold = Font(name=font_family, size=9, bold=True, color="1F1F1F")
    font_code = Font(name="Consolas", size=8.5, color="24292F")
    font_passed = Font(name=font_family, size=9, bold=True, color="1E6B38")
    
    # Fills
    fill_navy = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    fill_steel = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    fill_ice = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    fill_zebra = PatternFill(start_color="F7F9FC", end_color="F7F9FC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_card = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")
    fill_passed = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    fill_amber = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    
    # Borders
    thin_border_side = Side(border_style="thin", color="D9D9D9")
    border_all_thin = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_card = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    # Alignments
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

    # 1. Title Banner (Rows 1-3)
    ws.merge_cells("A1:O2")
    ws["A1"] = "BẢNG THỐNG KÊ CHI TIẾT THỜI GIAN THỰC THI KIỂM THỬ TỰ ĐỘNG (EXECUTION TIME BENCHMARK)"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_navy
    ws["A1"].alignment = align_center

    ws.merge_cells("A3:O3")
    ws["A3"] = "Hệ Thống 16 Core Automation YAML Suites trên Thiết Bị Thật Samsung Galaxy S20 FE (Android 13) | Toàn Bộ Chu Trình ~120 Phút (~2 Giờ)"
    ws["A3"].font = font_subtitle
    ws["A3"].fill = fill_steel
    ws["A3"].alignment = align_center

    # 2. Metadata Cards (Rows 5 to 7)
    cards = [
        ("A5:B5", "A6:B7", "TỔNG SỐ SUITES", "16 Kịch Bản", font_card_num),
        ("C5:E5", "C6:E7", "TỔNG THỜI GIAN CHẠY (1 MÁY THẬT)", "~115 – 120 Phút (~2 Giờ)", font_card_num),
        ("F5:H5", "F6:H7", "CHẠY SONG SONG 2 MÁY THẬT", "~55 – 60 Phút (~1 Giờ)", font_card_num),
        ("I5:K5", "I6:K7", "TEST TAY THỦ CÔNG (MANUAL QA)", "16 – 24 Giờ (2 – 3 Ngày)", font_card_num),
        ("L5:O5", "L6:O7", "HIỆU QUẢ RÚT NGẮN THỜI GIAN", "Tiết Kiệm >90% Thời Gian", font_card_num)
    ]
    for top_range, val_range, lbl, val, val_font in cards:
        ws.merge_cells(top_range)
        top_cell = ws[top_range.split(":")[0]]
        top_cell.value = lbl
        top_cell.font = font_card_lbl
        top_cell.fill = fill_ice
        top_cell.alignment = align_center
        
        ws.merge_cells(val_range)
        val_cell = ws[val_range.split(":")[0]]
        val_cell.value = val
        val_cell.font = val_font
        val_cell.fill = fill_card
        val_cell.alignment = align_center
        
        for row in ws[top_range]:
            for cell in row:
                cell.border = border_card
        for row in ws[val_range]:
            for cell in row:
                cell.border = border_card

    # 3. Section 1: Detailed Table of 16 Suites (Row 9)
    ws.cell(row=9, column=1, value="1. CHI TIẾT THỜI GIAN VÀ THÔNG SỐ VẬN HÀNH CỦA 16 KỊCH BẢN (TEST SUITES)").font = font_section
    
    headers_table = [
        "STT",
        "Mã Suite",
        "Tên Kịch Bản YAML",
        "Phân Hệ / Chức Năng Kiểm Thử",
        "Nhóm Quy Mô (Tier)",
        "Số Dòng Code",
        "Số Lệnh Tap / Thao Tác",
        "Số Lệnh Assert",
        "Số Ảnh Screenshot",
        "Số Lần Chờ Động (Waits)",
        "Số Test Cases (Specs)",
        "Thời Gian Trung Bình (Máy Thật)",
        "Thời Gian Giây (s)",
        "Tỉ Trọng Thời Gian (%)",
        "Đặc Điểm Kỹ Thuật Chi Phối Thời Gian"
    ]
    
    ws.row_dimensions[10].height = 28
    for col_idx, h in enumerate(headers_table, start=1):
        cell = ws.cell(row=10, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center
        cell.border = border_all_thin

    suite_data = [
        ("TC_00", "TC_00_Get_Payment_Flow.yaml", "IAP & Subscription Paywall", "Nhẹ & Vừa", 263, 8, 63, 8, 1, 10, "3m 40s (3 - 4 phút)", 220, "3.3%", "Khởi chạy sạch, chờ paywall xuất hiện, duyệt gói tuần/năm và thoát an toàn."),
        ("TC_01", "TC_01_Verify_Navigated_to_Edit_Screen_By_Select_Category_On_Home_Screen.yaml", "Home -> Select Template -> Edit", "Nhẹ & Vừa", 133, 5, 14, 0, 2, 12, "2m 30s (2 - 3 phút)", 150, "2.3%", "Điều hướng danh mục, xác thực thanh Toolbar và 6 công cụ Bottom Bar."),
        ("TC_02", "TC_02_Test_Background_Tool_On_Edit_Screen.yaml", "Background Tool (Color, Texture, Crop)", "Trung Bình Nặng", 458, 33, 48, 18, 4, 22, "6m 30s (6 - 7 phút)", 390, "5.9%", "Mở Gallery chọn ảnh, Crop xoay 90°/lật, đổi hình học Shape và so sánh Dual Compare."),
        ("TC_03", "TC_03_Test_Art_Tool_On_Edit_Screen.yaml", "Art Tool (Controls, Layers, Xoay 3D)", "Trung Bình Nặng", 483, 30, 32, 19, 1, 25, "6m 15s (6 - 7 phút)", 375, "5.7%", "Bật daemon OpenCV quét template qua HTTP 8765, nâng hạ layer, xoay 3D (Recorded: 375.3s)."),
        ("TC_04", "TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen.yaml", "Đổi Màu Đồ Họa (Color Sub-Tab)", "Nhẹ & Vừa", 204, 15, 25, 7, 6, 36, "4m 00s (3.5 - 4.5 phút)", 240, "3.6%", "Chọn bảng màu, mở Color Picker, đo MAE nền phẳng loại trừ false-negative."),
        ("TC_05", "TC_05_Test_Sub_Outline_Art_Tool_On_Edit_Screen.yaml", "Viền Đồ Họa (Outline Sub-Tab)", "Nhẹ & Vừa", 197, 15, 23, 7, 6, 35, "3m 50s (3.5 - 4.5 phút)", 230, "3.5%", "Kéo seekbar Stroke Width, đổi màu viền và so sánh visual vùng Canvas."),
        ("TC_06", "TC_06_Test_Sub_3D_Art_Tool_On_Edit_Screen.yaml", "Xoay 3D Đồ Họa (3D Rotation Sub-Tab)", "Nhẹ & Vừa", 152, 9, 16, 5, 7, 35, "3m 30s (3 - 4 phút)", 210, "3.2%", "Kéo 3 thanh trượt trục X, Y, Z và verify phối cảnh đồ họa 3 chiều."),
        ("TC_07", "TC_07_Test_Text_Tool_On_Edit_Screen.yaml", "Text Tool (Nhập Chữ, Font, Size)", "Nhẹ & Vừa", 249, 16, 29, 6, 12, 28, "4m 30s (4 - 5 phút)", 270, "4.1%", "Nhập văn bản bàn phím ảo, duyệt Font catalog, đổi Size và hideKeyboard an toàn."),
        ("TC_08", "TC_08_Test_Home_Screen.yaml", "Màn Hình Chính (Home Screen UI)", "Nhẹ & Vừa", 229, 11, 21, 1, 9, 18, "3m 30s (3 - 4 phút)", 210, "3.2%", "Kiểm tra Toolbar Logos4U, Crown VIP, 6 Feature Cards và Banner IAP."),
        ("TC_08.1", "TC_08_Test_Sub_Control_Text_Tool_On_Edit_Screen.yaml", "Điều Khiển Chữ (Text Controls & Layers)", "Trung Bình Nặng", 315, 27, 25, 9, 21, 45, "5m 30s (5 - 6 phút)", 330, "5.0%", "Di chuyển 4 hướng, Layer Up/Down, Duplicate đoạn text và Lock cố định."),
        ("TC_09", "TC_09_Test_Sub_Tabs_Text_Tool_On_Edit_Screen.yaml", "14 Tính Năng Con Của Chữ (Text Sub-Tabs)", "Trung Bình Nặng", 601, 34, 26, 8, 48, 33, "8m 30s (8 - 9 phút)", 510, "7.7%", "Duyệt liên hoàn 14 sub-tabs: Spacing, Shadow, Gradient, 3D, Curve uốn cong, Opacity..."),
        ("TC_10", "TC_10_Test_Preview_Screen.yaml", "Lưu Bản Thiết Kế & Preview Screen", "Siêu Nặng", 1383, 127, 62, 20, 98, 31, "19m 00s (18 - 20 phút)", 1140, "17.2%", "Siêu kịch bản: Lưu nháp Draft, xuất file PNG HD, xử lý Rate dialog, verify Preview & Share."),
        ("TC_11", "TC_11_Test_Mockup_Preview_Screen.yaml", "Mockup Preview (Brand Identify)", "Trung Bình Nặng", 338, 14, 10, 2, 17, 13, "5m 30s (5 - 6 phút)", 330, "5.0%", "Cuộn duyệt 5 mockup sản phẩm, lưu mockup có/không watermark, chuyển trạng thái Save -> Share."),
        ("TC_12", "TC_12_Test_Generate_AI_On_Style_Magic_AI_Screen.yaml", "Tạo Logo AI (Style Magic AI Studio)", "Nhẹ & Vừa", 64, 3, 12, 0, 0, 8, "2m 30s (2 - 3 phút)", 150, "2.3%", "Nhập Prompt, chọn Style Preset, gọi AI và chờ phản hồi mạng (extendedWaitUntil 30s)."),
        ("TC_13", "TC_13_Test_Feature_Usage_And_Save_On_Edit_Screen.yaml", "Tích Hợp Liên Hoàn 6 Công Cụ & Multi-Save", "Siêu Nặng", 1047, 94, 45, 14, 67, 30, "16m 00s (15 - 17 phút)", 960, "14.5%", "Siêu kịch bản E2E: Chỉnh sửa lần lượt 6 công cụ, sau mỗi công cụ xuất 1 ảnh PNG HD."),
        ("TC_14", "TC_14_Test_Background_Sub_Features_And_Save_On_Edit_Screen.yaml", "Chuyên Sâu 6 Tính Năng Nền & Multi-Save", "Siêu Nặng", 1026, 95, 42, 14, 68, 13, "15m 00s (14 - 16 phút)", 900, "13.6%", "Siêu kịch bản E2E: Kiểm thử sâu 6 tính năng con của Background và liên tục xuất PNG HD sau từng bước.")
    ]

    total_lines = sum(s[4] for s in suite_data)
    total_taps = sum(s[5] for s in suite_data)
    total_asserts = sum(s[6] for s in suite_data)
    total_screens = sum(s[7] for s in suite_data)
    total_waits = sum(s[8] for s in suite_data)
    total_cases = 317 # spec cases
    total_seconds = sum(s[11] for s in suite_data)

    for idx, row in enumerate(suite_data, start=1):
        row_num = 10 + idx
        ws.row_dimensions[row_num].height = 22
        fill_row = fill_white if idx % 2 != 0 else fill_zebra
        
        tier = row[3]
        if tier == "Siêu Nặng":
            tier_fill = fill_amber
        elif tier == "Trung Bình Nặng":
            tier_fill = fill_ice
        else:
            tier_fill = fill_white

        cells = [
            (1, idx, align_center, font_cell, fill_row),
            (2, row[0], align_center, font_cell_bold, fill_row),
            (3, row[1], align_left, font_code, fill_row),
            (4, row[2], align_left, font_cell_bold, fill_row),
            (5, tier, align_center, font_cell_bold, tier_fill),
            (6, row[4], align_right, font_cell, fill_row),
            (7, row[5], align_right, font_cell, fill_row),
            (8, row[6], align_right, font_cell, fill_row),
            (9, row[7], align_right, font_cell, fill_row),
            (10, row[8], align_right, font_cell, fill_row),
            (11, row[9], align_center, font_cell_bold, fill_row),
            (12, row[10], align_center, font_cell_bold, fill_passed),
            (13, row[11], align_right, font_code, fill_row),
            (14, row[12], align_center, font_cell_bold, fill_row),
            (15, row[13], align_left, font_cell, fill_row)
        ]
        for col_idx, val, alignment, font_style, cell_fill in cells:
            c = ws.cell(row=row_num, column=col_idx, value=val)
            c.alignment = alignment
            c.font = font_style
            c.fill = cell_fill
            c.border = border_all_thin

    # Summary Row of Table 1
    tot_row = 11 + len(suite_data)
    ws.row_dimensions[tot_row].height = 26
    ws.cell(row=tot_row, column=1, value="TỔNG CỘNG 16 KỊCH BẢN (TEST SUITES)")
    ws.merge_cells(f"A{tot_row}:D{tot_row}")
    for c in range(1, 5):
        cell_c = ws.cell(row=tot_row, column=c)
        cell_c.border = border_all_thin
        cell_c.fill = fill_navy
        cell_c.font = font_header
        cell_c.alignment = align_center

    ws.cell(row=tot_row, column=5, value="16 Suites").font = font_header
    ws.cell(row=tot_row, column=5).fill = fill_navy
    ws.cell(row=tot_row, column=5).alignment = align_center
    ws.cell(row=tot_row, column=5).border = border_all_thin

    tot_numeric = [
        (6, total_lines, font_header),
        (7, total_taps, font_header),
        (8, total_asserts, font_header),
        (9, total_screens, font_header),
        (10, total_waits, font_header),
        (11, "317 Cases", font_header),
        (12, "~115 - 120 Phút (~2h)", font_header),
        (13, f"{total_seconds}s", font_header),
        (14, "100.0%", font_header),
        (15, "Hoàn thành 100% kiểm thử hồi quy trên thiết bị thật", font_header)
    ]
    for col_idx, val, font_style in tot_numeric:
        c = ws.cell(row=tot_row, column=col_idx, value=val)
        c.font = font_style
        c.fill = fill_navy
        c.alignment = align_center if col_idx in [11, 12, 14] else (align_left if col_idx == 15 else align_right)
        c.border = border_all_thin

    # 4. Section 2: Tier Breakdown Summary (Rows 29 to 36)
    sec2_row = tot_row + 2
    ws.cell(row=sec2_row, column=1, value="2. PHÂN TÍCH THEO 3 PHÂN NHÓM QUY MÔ KỊCH BẢN (TIER BREAKDOWN)").font = font_section

    h_row = sec2_row + 1
    ws.row_dimensions[h_row].height = 24
    for c in range(1, 16):
        cell = ws.cell(row=h_row, column=c)
        cell.fill = fill_steel
        cell.font = font_header
        cell.border = border_all_thin

    ws.cell(row=h_row, column=1, value="STT").alignment = align_center
    ws.cell(row=h_row, column=2, value="Phân Nhóm (Tier)").alignment = align_center
    ws.cell(row=h_row, column=3, value="Danh Sách Kịch Bản Bao Gồm").alignment = align_center
    ws.cell(row=h_row, column=5, value="Số Kịch Bản").alignment = align_center
    ws.cell(row=h_row, column=6, value="Tổng Thời Gian").alignment = align_center
    ws.cell(row=h_row, column=7, value="Tỉ Trọng (%)").alignment = align_center
    ws.cell(row=h_row, column=8, value="Đặc Thù Kỹ Thuật & Nguyên Nhân Chi Phối Thời Gian").alignment = align_center
    
    ws.merge_cells(f"C{h_row}:D{h_row}")
    ws.merge_cells(f"H{h_row}:O{h_row}")

    tiers_data = [
        ("Tier 1: Siêu Nặng (Heavy E2E & Multi-Save)", "TC_10, TC_13, TC_14", 3, "~50 – 53 phút", "45.3%", "Xuất liên hoàn 6 lần ảnh PNG HD, ghi đĩa bộ nhớ máy, mở Activity Preview, tắt popup Rate App và cập nhật My Design."),
        ("Tier 2: Trung Bình Nặng (Deep Sub-Features & OpenCV)", "TC_02, TC_03, TC_08.1, TC_09, TC_11", 5, "~31 – 35 phút", "31.3%", "Bật daemon OpenCV quét template cổng 8765, duyệt 14 tab của Text Tool, mở Gallery cắt ảnh xoay 90° và Dual Visual Compare."),
        ("Tier 3: Nhẹ & Vừa (UI & Single Functional)", "TC_00, TC_01, TC_04, TC_05, TC_06, TC_07, TC_08, TC_12", 8, "~26 – 29 phút", "23.4%", "Kiểm thử hiển thị UI Toolbar, các thao tác đơn lẻ (đổi màu, kéo 3D, thanh toán IAP, sinh ảnh AI qua mạng).")
    ]

    for t_idx, (t_name, t_files, t_cnt, t_time, t_pct, t_note) in enumerate(tiers_data, start=1):
        r = h_row + t_idx
        ws.row_dimensions[r].height = 24
        fill_t = fill_amber if t_idx == 1 else (fill_ice if t_idx == 2 else fill_white)
        
        for c in range(1, 16):
            ws.cell(row=r, column=c).border = border_all_thin
            ws.cell(row=r, column=c).fill = fill_white
            
        ws.cell(row=r, column=1, value=t_idx).alignment = align_center
        ws.cell(row=r, column=1).font = font_cell
        
        ws.cell(row=r, column=2, value=t_name).alignment = align_left
        ws.cell(row=r, column=2).font = font_cell_bold
        ws.cell(row=r, column=2).fill = fill_t
        
        ws.cell(row=r, column=3, value=t_files).alignment = align_left
        ws.cell(row=r, column=3).font = font_code
        ws.merge_cells(f"C{r}:D{r}")
        
        ws.cell(row=r, column=5, value=f"{t_cnt} Suites").alignment = align_center
        ws.cell(row=r, column=5).font = font_cell_bold
        
        ws.cell(row=r, column=6, value=t_time).alignment = align_center
        ws.cell(row=r, column=6).font = font_passed
        ws.cell(row=r, column=6).fill = fill_passed
        
        ws.cell(row=r, column=7, value=t_pct).alignment = align_center
        ws.cell(row=r, column=7).font = font_cell_bold
        
        ws.cell(row=r, column=8, value=t_note).alignment = align_left
        ws.cell(row=r, column=8).font = font_cell
        ws.merge_cells(f"H{r}:O{r}")

    # 5. Section 3: Execution Modes Comparison
    sec3_row = h_row + len(tiers_data) + 2
    ws.cell(row=sec3_row, column=1, value="3. ĐỐI SÁNH HIỆU NĂNG THEO CÁC PHƯƠNG THỨC THỰC THI (EXECUTION MODES BENCHMARK)").font = font_section

    h3_row = sec3_row + 1
    ws.row_dimensions[h3_row].height = 24
    for c in range(1, 16):
        cell = ws.cell(row=h3_row, column=c)
        cell.fill = fill_steel
        cell.font = font_header
        cell.border = border_all_thin

    ws.cell(row=h3_row, column=1, value="STT").alignment = align_center
    ws.cell(row=h3_row, column=2, value="Phương Thức Kiểm Thử").alignment = align_center
    ws.cell(row=h3_row, column=5, value="Thời Gian Thực Thi").alignment = align_center
    ws.cell(row=h3_row, column=7, value="Tốc Độ So Với Manual").alignment = align_center
    ws.cell(row=h3_row, column=9, value="Mục Đích Sử Dụng & Khuyến Nghị Áp Dụng").alignment = align_center
    
    ws.merge_cells(f"B{h3_row}:D{h3_row}")
    ws.merge_cells(f"E{h3_row}:F{h3_row}")
    ws.merge_cells(f"G{h3_row}:H{h3_row}")
    ws.merge_cells(f"I{h3_row}:O{h3_row}")

    modes_data = [
        ("Kiểm Thử Thủ Công (Manual QA)", "16 – 24 Giờ (2 – 3 Ngày Làm Việc)", "Mốc chuẩn (1x)", "Chỉ dùng để khám phá tính năng mới (Exploratory Testing). Không dùng cho kiểm thử hồi quy trước release."),
        ("Chạy Tự Động Tuần Tự Trên 1 Máy Thật (`run_tests_windows.ps1`)", "~115 – 120 Phút (~2 Giờ)", "Nhanh gấp 10 lần", "Chạy kiểm thử hồi quy toàn diện (Full Regression) trước các đợt phát hành Production hoặc chạy tự động ban đêm."),
        ("Chạy Tự Động Song Song Trên 2 Máy Thật (`run_parallel.ps1 -Workers 2`)", "~55 – 60 Phút (~1 Giờ)", "Nhanh gấp 20 lần", "Rút ngắn 50% thời gian kiểm thử khi đội ngũ có sẵn 2 thiết bị cắm ADB tại máy local."),
        ("Chạy Smoke / Sanity Test Từng Kịch Bản Đơn Lẻ (`-File <TC.yaml>`)", "2 – 5 Phút / Test Suite", "Phản hồi tức thì", "Lập trình viên hoặc QA chạy verify ngay sau khi sửa code một tính năng hoặc một màn hình cụ thể.")
    ]

    for m_idx, (m_name, m_time, m_speed, m_rec) in enumerate(modes_data, start=1):
        r = h3_row + m_idx
        ws.row_dimensions[r].height = 24
        fill_m = fill_amber if m_idx == 1 else (fill_passed if m_idx in [2, 3] else fill_white)
        
        for c in range(1, 16):
            ws.cell(row=r, column=c).border = border_all_thin
            ws.cell(row=r, column=c).fill = fill_white
            
        ws.cell(row=r, column=1, value=m_idx).alignment = align_center
        ws.cell(row=r, column=1).font = font_cell
        
        ws.cell(row=r, column=2, value=m_name).alignment = align_left
        ws.cell(row=r, column=2).font = font_cell_bold
        ws.merge_cells(f"B{r}:D{r}")
        
        ws.cell(row=r, column=5, value=m_time).alignment = align_center
        ws.cell(row=r, column=5).font = font_cell_bold
        ws.cell(row=r, column=5).fill = fill_m
        ws.merge_cells(f"E{r}:F{r}")
        
        ws.cell(row=r, column=7, value=m_speed).alignment = align_center
        ws.cell(row=r, column=7).font = font_passed if m_idx > 1 else font_cell
        ws.merge_cells(f"G{r}:H{r}")
        
        ws.cell(row=r, column=9, value=m_rec).alignment = align_left
        ws.cell(row=r, column=9).font = font_cell
        ws.merge_cells(f"I{r}:O{r}")

    # Set Column Widths
    col_widths = [6, 12, 38, 28, 16, 12, 13, 12, 12, 14, 14, 20, 14, 12, 42]
    for i, w in enumerate(col_widths, start=1):
        col_letter = get_column_letter(i)
        ws.column_dimensions[col_letter].width = w

    return ws

def main():
    # 1. Create Dedicated Standalone Excel Workbook
    wb_standalone = openpyxl.Workbook()
    default_sheet = wb_standalone.active
    create_time_benchmark_sheet(wb_standalone, title="⏱️ Thống Kê Thời Gian Chạy")
    wb_standalone.remove(default_sheet)
    
    standalone_path = r"d:\logo-maker\docs\LogoMaker_Execution_Time_Benchmark.xlsx"
    wb_standalone.save(standalone_path)
    print(f"Generated standalone Excel benchmark at: {standalone_path}")
    
    # 2. Standalone only: DO NOT integrate into Master Workbook LogoMaker_Automation_TestSuite.xlsx
    # The master workbook only maintains the core 3 sheets (Dashboard, Matrix, Detailed Cases).
    print(f"Master workbook kept clean without benchmark tab.")

if __name__ == "__main__":
    main()
