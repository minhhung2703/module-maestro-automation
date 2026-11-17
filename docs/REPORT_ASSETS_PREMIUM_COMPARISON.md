# Báo Cáo Đối Soát Toàn Diện Hình Ảnh: `assets/Premium/` vs `assets/` (Root)

> **Mục tiêu**: Báo cáo kiểm tra và đối soát toàn bộ 100% các file ảnh giữa thư mục **`assets/Premium/`** và thư mục gốc **`assets/`** (chỉ tập trung duy nhất vào 2 thư mục này).

---

## 1. Kết Quả Tổng Quan & Xác Nhận Độ Đầy Đủ

| Danh mục | Số lượng file | Tỷ lệ (%) | Trạng thái kiểm tra |
|:---|:---:|:---:|:---|
| **Tổng số ảnh trong `assets/Premium/`** | **66** | 100% | **Đầy đủ 100%** (Cả 66 file đều có file cùng tên ở `assets/` gốc) |
| **Tổng số ảnh ở `assets/` gốc** | **78** | - | **Đầy đủ 100%** (Gồm 66 file trùng tên + 12 file chỉ có ở `assets/` gốc) |
| **Ảnh KHỚP CHUẨN ($\ge 92\%$)** | **49** | **74.24%** | Gồm 20 ảnh khớp tuyệt đối 100% + 29 ảnh khớp cao |
| **Ảnh KHÔNG KHỚP (< 92%)** | **17** | **25.76%** | Có sự thay đổi giao diện, phải dùng baseline riêng của Premium |
| **Ảnh CHỈ CÓ ở `assets/` gốc** | **12** | - | Không có trong `assets/Premium/` |

> **Xác nhận toán học**:  
> - **Trong `assets/Premium/`**: $17 \text{ (Mismatch)} + 20 \text{ (Exact 100%)} + 29 \text{ (High Match)} = \mathbf{66 \text{ file}}$.  
> - **Trong `assets/` gốc**: $66 \text{ (File đối ứng Premium)} + 12 \text{ (Chỉ có ở gốc)} = \mathbf{78 \text{ file}}$.  
> $\rightarrow$ **100% tất cả các file ảnh của cả 2 thư mục đều đã được liệt kê đầy đủ, không bỏ sót bất kỳ file nào.**

---

## 2. Danh Sách Chi Tiết 17 Ảnh KHÔNG KHỚP (Mismatch < 92%)

Các ảnh này có nội dung giao diện khác biệt giữa `assets/Premium/` và `assets/` gốc:

| STT | Tên File Ảnh | Độ tương đồng (%) | MAE | Nguyên nhân khác biệt |
|:---:|:---|:---:|:---:|:---|
| 1 | `backgroundTool_on_Edit_Screen.png` | **23.69%** | 104.45 | Bố cục template trên canvas và các ô màu nền khác nhau |
| 2 | `Input_Text_Edit_Existing.png` | **29.79%** | 3.76 | Nội dung chuỗi text trong popup sửa text khác nhau |
| 3 | `Input_Text_Empty_Validation.png` | **31.04%** | 3.91 | Thông báo lỗi text rỗng hiển thị khác nhau |
| 4 | `Input_Text_Typing_Result.png` | **31.58%** | 3.64 | Nội dung chữ vừa gõ vào khung soạn thảo khác nhau |
| 5 | `Input_Text_Screen_Default.png` | **32.12%** | 3.73 | Trạng thái ban đầu của màn hình nhập text khác nhau |
| 6 | `Custom_Gradient.png` | **37.95%** | 12.09 | Dải màu gradient tùy chỉnh được chọn khác nhau |
| 7 | `Verify_Displayed_Last_Image_On_Mockup_Preview_Screen.png` | **42.07%** | 25.16 | Ảnh mockup preview logo khác nhau |
| 8 | `Color_Custom_Gradient_Screen.png` | **73.58%** | 9.97 | Bảng phối màu gradient tùy chỉnh khác nhau |
| 9 | `background_Select_Screen.png` | **80.10%** | 14.01 | Danh mục thumbnail trong màn hình chọn ảnh nền có cập nhật |
| 10 | `Text_SubTab_Color_Applied.png` | **82.72%** | 24.42 | Màu sắc chữ áp dụng trên template Premium khác template gốc |
| 11 | `Verify_Displayed_Save_Options_Popup.png` | **83.59%** | 21.44 | Hộp thoại tùy chọn Save có nút/biểu tượng khác nhau |
| 12 | `Color_Texture_Scale_Displayed.png` | **84.70%** | 21.73 | Thanh trượt scale họa tiết Texture và canvas hiển thị khác nhau |
| 13 | `Add_Image_Background_on_Edit_Screen.png` | **85.31%** | 15.01 | Ảnh nền được thêm vào canvas chỉnh sửa khác nhau |
| 14 | `texture_Select_Screen.png` | **88.36%** | 10.03 | Thứ tự và danh sách thumbnail Texture khác nhau |
| 15 | `3D_Tool_Baseline.png` | **88.59%** | 17.28 | Lệch nhẹ góc xoay 3D hoặc khung viền text |
| 16 | `3D_Z_Rotation_Applied.png` | **90.38%** | 15.67 | Lệch nhẹ góc xoay trục Z trên canvas |
| 17 | `Verify_Navigated_To_Mockup_Preview_Screen.png` | **91.51%** | 5.12 | Khác biệt nhỏ ở thanh tiêu đề preview (gần đạt 92%) |

---

## 3. Danh Sách 49 Ảnh ĐÃ KHỚP CHUẨN ($\ge 92\%$)

### 3.1. Khớp Tuyệt Đối 100% (20 ảnh)
Các file này trùng khớp hoàn toàn từng điểm ảnh giữa `assets/Premium/` và `assets/` gốc:
1. `Closing_Layer_Dialog.png`
2. `Color_Opacity_Changed.png`
3. `Color_Palette_Dialog.png`
4. `Color_Solid_Red_Applied.png`
5. `Color_SubTab_Default.png`
6. `Color_Tool_Baseline.png`
7. `Displayed_Art_Tool_On_Edit_Screen.png`
8. `Home_Screen.png`
9. `Rate_App_Popup_On_Preview.png`
10. `Verify_Display_Dialog_Layer_On_Edit_Screen.png`
11. `Verify_Move_Layer_By_Using_pointer.png`
12. `Verify_Move_Layer_To_Down_On_Dialog_Layer.png`
13. `Verify_Move_Layer_To_Down_On_Dialog_Layer_2.png`
14. `Verify_Move_Layer_To_Top_On_Dialog_Layer.png`
15. `Verify_Move_Layer_To_Top_On_Dialog_Layer_2.png`
16. `Verify_Navigated_to_Style_Magic_AI_Screen.png`
17. `Verify_Redo_On_The_Template_Detail_Successfully.png`
18. `Verify_Undo_On_The_Template_Detail_Successfully.png`
19. `Verify_duplicate_Layer_To_Top_On_Dialog_Layer.png`
20. `Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2.png`

### 3.2. Khớp Mức Cao (92.08% – 99.69% - 29 ảnh)
1. `Outline_Eyedropper_Screen.png`: **99.69%**
2. `Outline_Palette_Dialog.png`: **99.06%**
3. `Outline_Custom_Hex_View.png`: **98.96%**
4. `Outline_Tool_Baseline.png`: **98.34%**
5. `Text_Tool_Baseline.png`: **98.22%**
6. `Color_Tool_Result.png`: **98.20%**
7. `Control_Final_Result.png`: **98.14%**
8. `3D_SubTab_Default.png`: **97.24%**
9. `Text_SubTabs_All_Applied_Result.png`: **97.15%**
10. `Text_SubTab_3D_Applied.png`: **96.22%**
11. `Text_SubTab_Curve_Applied.png`: **95.69%**
12. `Text_Tool_Applied_Result.png`: **95.48%**
13. `Outline_Solid_Red_Applied.png`: **94.71%**
14. `Text_SubTab_Shadow_Applied.png`: **94.68%**
15. `3D_Y_Rotation_Applied.png`: **94.60%**
16. `Outline_SubTab_Default.png`: **94.55%**
17. `Control_Move_Result.png`: **95.46%**
18. `Control_Text_Flipped.png`: **95.43%**
19. `3D_X_Rotation_Applied.png`: **95.41%**
20. `Control_Duplicate_Result.png`: **95.40%**
21. `Control_Align_Result.png`: **95.37%**
22. `Control_Text_Rotated.png`: **95.36%**
23. `Control_SubTab_Opened_After_Text.png`: **95.35%**
24. `Text_SubTab_Outline_Applied.png`: **94.30%**
25. `Outline_Width_Changed.png`: **94.13%**
26. `Control_Text_Zoomed.png`: **95.29%**
27. `Control_Text_Frame_Moved.png`: **95.28%**
28. `Text_SubTab_Fonts_Applied.png`: **92.87%**
29. `Text_SubTab_Background_Applied.png`: **92.08%**

---

## 4. Danh Sách 12 Ảnh Chỉ Có Ở Thư Mục Gốc `assets/` (Không Có Trong `assets/Premium/`)

12 file ảnh này tồn tại ở thư mục `assets/` gốc nhưng **không có** file tương ứng trong `assets/Premium/`:
1. `IAP_Sccreen_Free_Trial.png`
2. `IAP_Screen.png`
3. `Onboarding_Step3.png`
4. `Splash_Screen.png`
5. `TC_10_Preview_Screen_Baseline.png`
6. `TemplateDraft_Displayed_correctly_For_Art_Feature.png`
7. `Verify_Image_On_Style_Magic_AI_Matches_Template.png`
8. `image_Default.png`
9. `onboarding_1.png`
10. `onboarding_2.png`
11. `onboarding_3.png`
12. `template_restaurant_target.png`
