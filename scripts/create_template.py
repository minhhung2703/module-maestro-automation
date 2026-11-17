"""
Script tạm: Crop ảnh screenshot theo element ID và lưu làm ảnh template.
Chạy 1 lần duy nhất để tạo ảnh mẫu.
"""
import cv2
import sys
import os
import subprocess
import re
import numpy as np

def read_image_unicode(path):
    try:
        return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def get_element_bounds(element_id):
    subprocess.run(
        ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
        capture_output=True, text=True, timeout=10
    )
    result = subprocess.run(
        ["adb", "shell", "cat", "/sdcard/ui_dump.xml"],
        capture_output=True, text=True, timeout=10
    )
    xml_content = result.stdout
    pattern = rf'resource-id="[^"]*{re.escape(element_id)}"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
    match = re.search(pattern, xml_content)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
    return None

if __name__ == "__main__":
    screenshot_path = "d:\\logo-maker\\onboarding3_compare.png"
    output_path = "d:\\logo-maker\\assets\\Onboarding_Step3.png"
    element_id = "img"

    img = read_image_unicode(screenshot_path)
    if img is None:
        print("Cannot read screenshot!")
        sys.exit(1)

    bounds = get_element_bounds(element_id)
    if bounds is None:
        print(f"Cannot find element '{element_id}'!")
        sys.exit(1)

    x1, y1, x2, y2 = bounds
    print(f"Element bounds: [{x1},{y1}][{x2},{y2}]")
    
    cropped = img[y1:y2, x1:x2]
    print(f"Cropped size: {cropped.shape[1]}x{cropped.shape[0]}")
    
    # Lưu ảnh template
    cv2.imencode('.png', cropped)[1].tofile(output_path)
    print(f"Saved template to: {output_path}")
