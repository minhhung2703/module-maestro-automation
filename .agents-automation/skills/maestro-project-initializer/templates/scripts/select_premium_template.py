import cv2
import numpy as np
import subprocess
import time
import sys
import os

def adb(cmd, serial=None):
    if not serial:
        serial = os.environ.get('ANDROID_SERIAL')
    serial_opt = f"-s {serial} " if serial else ""
    res = subprocess.run(f"adb {serial_opt}{cmd}", shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        tag = f"[{serial}] " if serial else ""
        err = (res.stderr or res.stdout or "").strip()
        print(f"{tag}[WARN] ADB command failed ({res.returncode}): adb {serial_opt}{cmd} -> {err}", flush=True)
    return res

def get_screen(serial=None):
    suffix = f"_{serial}" if serial else ""
    remote_path = f"/sdcard/screen_temp{suffix}.png"
    local_path = f"screenshots/debug/screen_temp{suffix}.png"
    os.makedirs("screenshots/debug", exist_ok=True)
    # Remove any cached/Git-tracked screenshot first so ADB failure never reads stale pixels
    if os.path.exists(local_path):
        try:
            os.remove(local_path)
        except OSError:
            pass
    cap_res = adb(f"shell screencap -p {remote_path}", serial=serial)
    if cap_res.returncode != 0:
        return None
    pull_res = adb(f"pull {remote_path} {local_path}", serial=serial)
    if pull_res.returncode != 0 or not os.path.exists(local_path):
        return None
    return cv2.imread(local_path)

def find_target(screen, target_crop):
    target_gray = cv2.cvtColor(target_crop, cv2.COLOR_BGR2GRAY)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen_h, screen_w = screen_gray.shape[:2]
    
    best_val = -1
    best_loc = None
    best_w, best_h = 0, 0
    
    # Calculate scale dynamically relative to screen width (2-column layout ~44.5% width per column)
    target_w = max(1, target_gray.shape[1])
    base_scale = (screen_w * 0.445) / target_w
    scales = [base_scale * factor for factor in [0.96, 0.98, 1.00, 1.02, 1.04]]
    
    for scale in scales:
        w = int(target_gray.shape[1] * scale)
        h = int(target_gray.shape[0] * scale)
        if w >= screen_w or h >= screen_h:
            continue
        resized = cv2.resize(target_gray, (w, h), interpolation=cv2.INTER_CUBIC)
        res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val = max_val
            best_loc = max_loc
            best_w, best_h = w, h
            
    return best_val, best_loc, best_w, best_h

def select_restaurant_template(serial=None, max_scrolls=25):
    target_path = "assets/template_restaurant_target.png"
    if not os.path.exists(target_path):
        print(f"[ERROR] Target image {target_path} not found!", flush=True)
        return False
        
    target = cv2.imread(target_path)
    tag = f"[{serial}] " if serial else ""
    print(f"{tag}[INFO] Scanning for restaurant template (target: {target.shape})...", flush=True)

    # Chờ để RecyclerView và thumbnail trong danh mục tải xong từ mạng trên máy ảo CI
    time.sleep(4.0)

    last_loc = None
    stuck_count = 0
    capture_fail_count = 0

    for scroll_idx in range(max_scrolls):
        screen = get_screen(serial=serial)
        if screen is None:
            capture_fail_count += 1
            print(f"{tag}[WARN] Failed to capture screen via ADB ({capture_fail_count}/3), retrying...", flush=True)
            if capture_fail_count >= 3:
                print(f"{tag}[ERROR] Aborting template search: ADB screen capture failed 3 times consecutively.", flush=True)
                return False
            time.sleep(0.5)
            continue
        capture_fail_count = 0
            
        screen_h, screen_w = screen.shape[:2]
        score, loc, w, h = find_target(screen, target)
        print(f"{tag}[SCAN] Drag {scroll_idx} (res: {screen_w}x{screen_h}): score={score:.4f}, loc={loc}", flush=True)
        
        # Nếu ở lần đầu tiên ảnh chưa kịp tải xong từ mạng (score < 0.70), kiên nhẫn chờ thêm trước khi vuốt cuộn
        if scroll_idx == 0 and score < 0.70:
            for retry in range(2):
                time.sleep(2.0)
                screen = get_screen(serial=serial)
                if screen is not None:
                    score, loc, w, h = find_target(screen, target)
                    print(f"{tag}[RETRY {retry+1}] Waiting for network image download (res: {screen_w}x{screen_h}): score={score:.4f}, loc={loc}", flush=True)
                    if score >= 0.70:
                        break

        if score >= 0.70:
            center_x = loc[0] + w // 2
            center_y = loc[1] + h // 2
            print(f"{tag}[FOUND] Template matched at ({center_x}, {center_y}) with score {score:.4f}!", flush=True)
            
            # Save visual proof
            vis = screen.copy()
            cv2.rectangle(vis, loc, (loc[0]+w, loc[1]+h), (0, 255, 0), 4)
            proof_path = f"screenshots/debug/template_selected_{serial or 'def'}.png"
            cv2.imwrite(proof_path, vis)
            
            # Tap template card
            print(f"{tag}[ACTION] Tapping template at ({center_x}, {center_y})...", flush=True)
            tap_res = adb(f"shell input tap {center_x} {center_y}", serial=serial)
            if tap_res.returncode != 0:
                print(f"{tag}[ERROR] ADB tap failed at ({center_x}, {center_y})!", flush=True)
                return False
            time.sleep(3.0)
            return True

        # Check if screen is stuck on an overlay (e.g. AdMob native ad validator)
        if loc == last_loc and loc is not None:
            stuck_count += 1
            if stuck_count >= 2:
                print(f"{tag}[WARN] Detected screen stuck (loc={loc}), dismissing potential overlay...", flush=True)
                dismiss_x = int(screen_w * 0.75)
                dismiss_y = int(screen_h * 0.70)
                adb(f"shell input tap {dismiss_x} {dismiss_y}", serial=serial)
                time.sleep(0.5)
                stuck_count = 0
        else:
            stuck_count = 0
        last_loc = loc
            
        # Drag strictly in upper-middle area (50% -> 20%) to avoid any bottom ad banners or validator popups
        drag_x = int(screen_w * 0.50)
        drag_start_y = int(screen_h * 0.50)
        drag_end_y = int(screen_h * 0.20)
        adb(f"shell input swipe {drag_x} {drag_start_y} {drag_x} {drag_end_y} 350", serial=serial)
        time.sleep(0.5)
        
    print(f"{tag}[ERROR] Target template not found after {max_scrolls} scrolls!", flush=True)
    return False

if __name__ == "__main__":
    dev_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = select_restaurant_template(serial=dev_arg)
    sys.exit(0 if success else 1)
