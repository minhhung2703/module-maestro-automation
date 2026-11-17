"""
So sánh 2 ảnh screenshot (có thể crop theo element ID).
Dùng để kiểm tra hình ảnh ở 2 màn hình khác nhau có GIỐNG hay KHÁC nhau.

Cách dùng:
  # So sánh 2 ảnh toàn màn hình:
  python compare_screens.py image1.png image2.png

  # So sánh 2 ảnh nhưng chỉ vùng element "img":
  python compare_screens.py image1.png image2.png --crop-id img

  # Kiểm tra 2 ảnh phải KHÁC nhau (expect-different):
  python compare_screens.py image1.png image2.png --expect-different

  # Kết hợp cả 2:
  python compare_screens.py image1.png image2.png --crop-id img --expect-different
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
        print(f"Error reading image from {path}: {e}")
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
            print(f"Error: Element with id '{element_id}' not found")
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

def compare_two_images(path1, path2, crop_element_id=None, expect_different=False):
    """
    So sánh 2 ảnh screenshot.
    - expect_different=False: PASS nếu 2 ảnh GIỐNG nhau (match >= 85%)
    - expect_different=True:  PASS nếu 2 ảnh KHÁC nhau (match < 85%)
    """
    path1 = os.path.normpath(path1)
    path2 = os.path.normpath(path2)
    print(f"Image 1: {path1}")
    print(f"Image 2: {path2}")
    print(f"Mode: {'Expect DIFFERENT' if expect_different else 'Expect SAME'}")

    # Đọc 2 ảnh
    img1 = read_image_unicode(path1)
    img2 = read_image_unicode(path2)

    if img1 is None or img2 is None:
        print("Error: Cannot read one or both images!")
        sys.exit(1)

    # Crop nếu có element ID
    if crop_element_id:
        print(f"Cropping to element: {crop_element_id}")
        bounds = get_element_bounds(crop_element_id)
        if bounds:
            img1 = crop_image(img1, bounds)
            img2 = crop_image(img2, bounds)
            print(f"Cropped Image 1 size: {img1.shape[1]}x{img1.shape[0]}")
            print(f"Cropped Image 2 size: {img2.shape[1]}x{img2.shape[0]}")
        else:
            print("Warning: Could not find element bounds, comparing full screenshots")

    # Resize nếu kích thước khác nhau
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # So sánh độ tương đồng
    res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    match_percentage = max_val * 100
    print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")

    # Đánh giá kết quả (ngưỡng 92%)
    threshold = 0.92
    if expect_different:
        # Mong đợi 2 ảnh KHÁC nhau -> PASS nếu match < 92%
        if max_val < threshold:
            print("PASSED: Images are DIFFERENT as expected")
            sys.exit(0)
        else:
            print("FAILED: Images are TOO SIMILAR (expected different)")
            sys.exit(1)
    else:
        # Mong đợi 2 ảnh GIỐNG nhau -> PASS nếu match >= 92%
        if max_val >= threshold:
            print("PASSED: Images MATCH")
            sys.exit(0)
        else:
            print("FAILED: Images do NOT match")
            sys.exit(1)

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    parser = argparse.ArgumentParser(description="So sánh 2 ảnh screenshot")
    parser.add_argument("image1", help="Đường dẫn ảnh thứ 1")
    parser.add_argument("image2", help="Đường dẫn ảnh thứ 2")
    parser.add_argument("--crop-id", help="Element ID để crop (tùy chọn)", default=None)
    parser.add_argument("--expect-different", help="PASS nếu 2 ảnh KHÁC nhau", action="store_true")

    args = parser.parse_args()
    compare_two_images(args.image1, args.image2, args.crop_id, args.expect_different)
