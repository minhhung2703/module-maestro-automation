"""
Kiểm tra ảnh đã xoay đúng 90 độ sang phải (clockwise).

Cách dùng:
  # So sánh ảnh trước/sau xoay (Solution 2):
  python verify_rotation.py screenshots/crop_before_rotate.png screenshots/crop_after_rotate.png

  # Tùy chỉnh ngưỡng match (mặc định 80%):
  python verify_rotation.py before.png after.png --threshold 0.75

  # Kiểm chứng chu kỳ 360 độ (Solution 3):
  python verify_rotation.py screenshots/crop_before_rotate.png screenshots/crop_angle_360.png --mode cycle
"""
import cv2
import sys
import os
import subprocess
import re
import argparse
import numpy as np


def read_image_unicode(path):
    """Đọc ảnh hỗ trợ unicode path trên Windows & Linux"""
    try:
        path = os.path.normpath(path)
        if not os.path.exists(path):
            print(f"Error: File does not exist at '{path}'")
            return None
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            print(f"Error: File is empty (0 bytes) at '{path}'")
            return None
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error reading image {path}: {e}")
        return None


def get_element_bounds(element_id):
    """
    Lấy tọa độ (bounds) của element trên màn hình thông qua adb uiautomator.
    Trả về tuple (x1, y1, x2, y2) hoặc None nếu không tìm thấy.
    """
    try:
        subprocess.run(
            ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
            capture_output=True, text=True, timeout=10
        )
        result = subprocess.run(
            ["adb", "shell", "cat", "/sdcard/ui_dump.xml"],
            capture_output=True, text=True, timeout=10
        )
        xml_content = result.stdout
        if not xml_content:
            print("Error: Could not dump UI hierarchy")
            return None

        pattern = rf'resource-id="[^"]*{re.escape(element_id)}"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        match = re.search(pattern, xml_content)
        if match:
            x1, y1, x2, y2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
            print(f"Element '{element_id}' bounds: [{x1},{y1}][{x2},{y2}]")
            return (x1, y1, x2, y2)
        else:
            print(f"Warning: Element with id '{element_id}' not found")
            return None
    except Exception as e:
        print(f"Error getting element bounds: {e}")
        return None


def crop_image(img, bounds):
    """Crop ảnh theo tọa độ bounds (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = bounds
    h, w = img.shape[:2]
    x1, y1 = max(0, min(x1, w)), max(0, min(y1, h))
    x2, y2 = max(0, min(x2, w)), max(0, min(y2, h))
    return img[y1:y2, x1:x2]


def crop_center(img, crop_ratio=0.5):
    """
    Cắt lấy phần lõi trung tâm của ảnh (nơi chứa nội dung chính)
    để loại bỏ thanh toolbar, viền ngoài không bị xoay.
    """
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    new_w = int(w * crop_ratio)
    new_h = int(h * crop_ratio)
    half_w = new_w // 2
    half_h = new_h // 2
    return img[cy - half_h : cy + half_h, cx - half_w : cx + half_w]


def verify_90_rotation(before_path, after_path, crop_element_id=None, threshold=0.80):
    """
    Solution 2: Kiểm tra ảnh đã xoay đúng 90 độ theo chiều kim đồng hồ.
    
    Nguyên lý:
    - Lấy ảnh trước khi xoay, dùng OpenCV xoay 90 độ sang phải.
    - So sánh kết quả xoay với ảnh thực tế sau khi xoay.
    - Nếu khớp >= threshold -> PASS.
    """
    before_path = os.path.normpath(before_path)
    after_path = os.path.normpath(after_path)
    print("========================================")
    print("  VERIFY 90° CLOCKWISE ROTATION")
    print("  (Solution 2: Before/After Compare)")
    print("========================================")
    print(f"Before rotate: {before_path}")
    print(f"After rotate : {after_path}")
    print(f"Threshold    : {threshold * 100:.0f}%")

    img_before = read_image_unicode(before_path)
    img_after = read_image_unicode(after_path)

    if img_before is None or img_after is None:
        print("[ERROR] Không thể đọc một trong 2 file ảnh!")
        sys.exit(1)

    print(f"Before image size: {img_before.shape[1]}x{img_before.shape[0]}")
    print(f"After image size : {img_after.shape[1]}x{img_after.shape[0]}")

    # Crop theo element ID nếu có (ví dụ: chỉ lấy vùng ảnh crop, bỏ toolbar)
    if crop_element_id:
        print(f"Cropping to element: {crop_element_id}")
        bounds = get_element_bounds(crop_element_id)
        if bounds:
            img_before = crop_image(img_before, bounds)
            img_after = crop_image(img_after, bounds)
            print(f"Cropped Before size: {img_before.shape[1]}x{img_before.shape[0]}")
            print(f"Cropped After size : {img_after.shape[1]}x{img_after.shape[0]}")
        else:
            print("Warning: Could not find element bounds, using center crop fallback")
            img_before = crop_center(img_before, 0.6)
            img_after = crop_center(img_after, 0.6)
    else:
        # Mặc định crop vùng trung tâm 60% để bỏ toolbar/navigation bar
        img_before = crop_center(img_before, 0.6)
        img_after = crop_center(img_after, 0.6)
        print(f"Center cropped Before: {img_before.shape[1]}x{img_before.shape[0]}")
        print(f"Center cropped After : {img_after.shape[1]}x{img_after.shape[0]}")

    # 1. Xoay ảnh trước đó 90 độ theo chiều kim đồng hồ (sang phải)
    rotated_before = cv2.rotate(img_before, cv2.ROTATE_90_CLOCKWISE)
    print(f"Rotated expected size: {rotated_before.shape[1]}x{rotated_before.shape[0]}")

    # 2. Resize về cùng kích thước để so sánh
    if rotated_before.shape != img_after.shape:
        img_after = cv2.resize(img_after, (rotated_before.shape[1], rotated_before.shape[0]))

    # 3. So sánh độ khớp bằng Template Matching (giống compare_screens.py)
    res = cv2.matchTemplate(rotated_before, img_after, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    match_percentage = max_val * 100
    print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")

    if max_val >= threshold:
        print("PASSED: Ảnh đã xoay đúng 90 độ sang phải!")
        sys.exit(0)
    else:
        print("FAILED: Ảnh chưa xoay đúng 90 độ hoặc xoay sai hướng!")
        sys.exit(1)


def verify_360_cycle(original_path, after_360_path, crop_element_id=None, threshold=0.85):
    """
    Solution 3: Kiểm chứng chu kỳ 360 độ.
    
    Nguyên lý:
    - Xoay 4 lần x 90° = 360° -> ảnh phải trở về trạng thái ban đầu.
    - So sánh ảnh gốc với ảnh sau 4 lần xoay.
    - Nếu khớp >= threshold -> PASS (chu kỳ đúng).
    """
    original_path = os.path.normpath(original_path)
    after_360_path = os.path.normpath(after_360_path)
    print("========================================")
    print("  VERIFY 360° ROTATION CYCLE")
    print("  (Solution 3: 4x90° = Original)")
    print("========================================")
    print(f"Original (0°) : {original_path}")
    print(f"After 360°     : {after_360_path}")
    print(f"Threshold      : {threshold * 100:.0f}%")

    img_original = read_image_unicode(original_path)
    img_after_360 = read_image_unicode(after_360_path)

    if img_original is None or img_after_360 is None:
        print("[ERROR] Không thể đọc một trong 2 file ảnh!")
        sys.exit(1)

    print(f"Original image size : {img_original.shape[1]}x{img_original.shape[0]}")
    print(f"After 360 image size: {img_after_360.shape[1]}x{img_after_360.shape[0]}")

    # Crop theo element ID nếu có
    if crop_element_id:
        print(f"Cropping to element: {crop_element_id}")
        bounds = get_element_bounds(crop_element_id)
        if bounds:
            img_original = crop_image(img_original, bounds)
            img_after_360 = crop_image(img_after_360, bounds)
            print(f"Cropped Original size : {img_original.shape[1]}x{img_original.shape[0]}")
            print(f"Cropped After 360 size: {img_after_360.shape[1]}x{img_after_360.shape[0]}")
        else:
            print("Warning: Could not find element bounds, comparing full screenshots")

    # Resize nếu kích thước khác nhau
    if img_original.shape != img_after_360.shape:
        img_after_360 = cv2.resize(img_after_360, (img_original.shape[1], img_original.shape[0]))

    # So sánh độ khớp
    res = cv2.matchTemplate(img_original, img_after_360, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    match_percentage = max_val * 100
    print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")

    if max_val >= threshold:
        print("PASSED: Chu kỳ 360° đúng - Ảnh trở về trạng thái ban đầu!")
        sys.exit(0)
    else:
        print("FAILED: Sau 4 lần xoay, ảnh không trở về trạng thái ban đầu!")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    parser = argparse.ArgumentParser(
        description="Kiểm tra ảnh xoay 90 độ sang phải (Solution 2) hoặc chu kỳ 360° (Solution 3)"
    )
    parser.add_argument("image1", help="Đường dẫn ảnh thứ 1 (trước khi xoay / ảnh gốc)")
    parser.add_argument("image2", help="Đường dẫn ảnh thứ 2 (sau khi xoay / sau 360°)")
    parser.add_argument(
        "--mode", choices=["rotate", "cycle"], default="rotate",
        help="Chế độ: 'rotate' = kiểm tra xoay 90° (Solution 2), 'cycle' = kiểm tra chu kỳ 360° (Solution 3). Mặc định: rotate"
    )
    parser.add_argument("--crop-id", help="Element ID để crop vùng ảnh (tùy chọn)", default=None)
    parser.add_argument("--threshold", type=float, default=None, help="Ngưỡng match (mặc định: 0.80 cho rotate, 0.85 cho cycle)")

    args = parser.parse_args()

    if args.mode == "rotate":
        threshold = args.threshold if args.threshold is not None else 0.80
        verify_90_rotation(args.image1, args.image2, args.crop_id, threshold)
    else:
        threshold = args.threshold if args.threshold is not None else 0.85
        verify_360_cycle(args.image1, args.image2, args.crop_id, threshold)
