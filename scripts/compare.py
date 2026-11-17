import cv2
import sys
import os
import glob
import subprocess
import re
import numpy as np

def get_screenshot(directory, screenshot_name=None):
    """
    Tìm file screenshot trong thư mục.
    - Nếu có screenshot_name: tìm file khớp trực tiếp hoặc khớp tên file trong thư mục/thư mục con
    - Nếu không: lấy file .png mới nhất (fallback)
    """
    directory = os.path.normpath(directory)
    if screenshot_name:
        clean_name = os.path.normpath(screenshot_name.replace('\\', '/'))
        if clean_name.endswith('.png'):
            clean_name = clean_name[:-4]
        
        # 1. Thử kiểm tra đường dẫn trực tiếp
        direct_path = os.path.join(directory, clean_name + '.png')
        if os.path.exists(direct_path):
            return direct_path
            
        # 2. Tìm kiếm trong toàn bộ thư mục gốc và thư mục con
        all_pngs = glob.glob(os.path.join(directory, '**', '*.png'), recursive=True)
        base_name = os.path.basename(clean_name)
        # Ưu tiên exact match (tên file không có extension phải khớp chính xác)
        exact_matches = [f for f in all_pngs if os.path.splitext(os.path.basename(f))[0] == base_name]
        if exact_matches:
            latest = max(exact_matches, key=os.path.getctime)
            return latest
        # Fallback: substring match
        matching_files = [f for f in all_pngs if base_name in os.path.basename(f)]
        
        if matching_files:
            latest = max(matching_files, key=os.path.getctime)
            return latest
        else:
            print(f"Warning: No file matching '{screenshot_name}' found, falling back to latest")
    
    # Fallback: lấy file .png mới nhất trong directory và subdirectories
    list_of_files = glob.glob(os.path.join(directory, '**', '*.png'), recursive=True)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def read_image_unicode(path):
    # Đọc ảnh hỗ trợ unicode path trên Windows & Linux
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

import xml.etree.ElementTree as ET

def find_card_bounds(img, element_id="element"):
    """
    Tự động tìm và cắt khung phần tử/bảng nội dung chính từ hình ảnh dựa vào contours.
    """
    try:
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 40, 120)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Tìm contour hình chữ nhật dạng thẻ (card artwork)
        card_rects = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            aspect = ch / float(cw) if cw > 0 else 0
            if 0.3 * w < cw < 0.95 * w and 0.2 * h < ch < 0.85 * h:
                if 1.15 < aspect < 1.7:
                    center_x = x + cw / 2.0
                    if abs(center_x - w / 2.0) < w * 0.25:
                        card_rects.append((cw * ch, x, y, x + cw, y + ch))
                        
        if card_rects:
            # Chọn contour thẻ phù hợp nhất (kích thước vừa vặn nhất)
            card_rects.sort(key=lambda item: item[0])
            best = (card_rects[0][1], card_rects[0][2], card_rects[0][3], card_rects[0][4])
            print(f"Auto-detected element '{element_id}' bounds: [{best[0]},{best[1]}][{best[2]},{best[3]}]")
            return best

        # Fallback contour gộp
        boxes = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            if y > h * 0.12 and (y + ch) < h * 0.85 and cw > w * 0.1:
                boxes.append((x, y, x + cw, y + ch))
                
        if boxes:
            min_x = min(b[0] for b in boxes)
            min_y = min(b[1] for b in boxes)
            max_x = max(b[2] for b in boxes)
            max_y = max(b[3] for b in boxes)
            
            if (max_x - min_x) > w * 0.3 and (max_y - min_y) > h * 0.2:
                best = (min_x, min_y, max_x, max_y)
                print(f"Auto-detected element '{element_id}' bounds: [{best[0]},{best[1]}][{best[2]},{best[3]}]")
                return best
    except Exception as e:
        pass
    return None

def get_element_bounds(element_id, img=None):
    """
    Lấy tọa độ (bounds) của element trên màn hình thông qua adb uiautomator hoặc contour.
    Trả về tuple (x1, y1, x2, y2) hoặc None nếu không tìm thấy.
    """
    # 0. Hỗ trợ truyền tọa độ trực tiếp dạng [x1,y1][x2,y2]
    coord_match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', element_id)
    if coord_match:
        return (int(coord_match.group(1)), int(coord_match.group(2)), int(coord_match.group(3)), int(coord_match.group(4)))

    try:
        # Dump UI hierarchy từ thiết bị
        subprocess.run(
            ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
            capture_output=True, encoding='utf-8', errors='ignore', timeout=15
        )
        
        # Pull file XML về máy local
        result = subprocess.run(
            ["adb", "shell", "cat", "/sdcard/ui_dump.xml"],
            capture_output=True, encoding='utf-8', errors='ignore', timeout=15
        )
        
        xml_content = result.stdout
        
        if xml_content and "<hierarchy" in xml_content:
            root = ET.fromstring(xml_content)
            for elem in root.iter():
                res_id = elem.attrib.get('resource-id', '')
                text = elem.attrib.get('text', '')
                desc = elem.attrib.get('content-desc', '')
                bounds_str = elem.attrib.get('bounds', '')
                
                if (element_id in res_id or element_id == text or element_id == desc) and bounds_str:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
                    if match:
                        x1, y1, x2, y2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
                        print(f"Element '{element_id}' bounds from XML: [{x1},{y1}][{x2},{y2}]")
                        return (x1, y1, x2, y2)
    except Exception as e:
        pass

    # Nếu là các vùng canvas quen thuộc trên màn Edit nhưng thiết bị đã điều hướng sang màn khác
    if img is not None:
        h, w = img.shape[:2]
        if any(k in element_id for k in ["layout_transparent", "layout_designer", "stickerView", "bgDesignArea"]):
            top_y = int(304 * w / 1080)
            print(f"Known Edit Canvas '{element_id}' bounds: [0,{top_y}][{w},{top_y + w}]")
            return (0, top_y, w, top_y + w)

        if "imageTransparentGrid" in element_id:
            top_y = int(280 * w / 1080)
            print(f"Known Preview Canvas '{element_id}' bounds: [0,{top_y}][{w},{top_y + w}]")
            return (0, top_y, w, top_y + w)

        return find_card_bounds(img, element_id)

    print(f"Warning: Could not find element '{element_id}' bounds")
    return None

def crop_image_by_bounds(img, bounds):
    """
    Crop ảnh theo tọa độ bounds (x1, y1, x2, y2).
    """
    x1, y1, x2, y2 = bounds
    h, w = img.shape[:2]
    
    # Đảm bảo tọa độ nằm trong phạm vi ảnh
    x1 = max(0, min(x1, w))
    y1 = max(0, min(y1, h))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))
    
    cropped = img[y1:y2, x1:x2]
    print(f"Cropped image size: {cropped.shape[1]}x{cropped.shape[0]}")
    return cropped


def _match_best_patch(search_img, tpl_patch, scales=(1.0,), blur=0.0, early_stop=0.92):
    """Find best normalized correlation match of tpl_patch inside search_img across candidate DPI scales."""
    sh, sw = search_img.shape[:2]
    s_proc = cv2.GaussianBlur(search_img, (0, 0), blur) if blur > 0 else search_img
    if s_proc.std() < 2.5:
        return -1.0, (0, 0), 1.0

    best = -1.0
    best_loc = (0, 0)
    best_scale = 1.0
    for sc in scales:
        if sc == 1.0:
            tp = tpl_patch
        else:
            nw = max(8, int(round(tpl_patch.shape[1] * sc)))
            nh = max(8, int(round(tpl_patch.shape[0] * sc)))
            tp = cv2.resize(tpl_patch, (nw, nh))
        if tp.shape[0] > sh or tp.shape[1] > sw or tp.shape[0] < 10 or tp.shape[1] < 10:
            continue
        t_proc = cv2.GaussianBlur(tp, (0, 0), blur) if blur > 0 else tp
        if t_proc.std() < 2.5:
            continue
        res = cv2.matchTemplate(s_proc, t_proc, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(res)
        if mv > best:
            best = float(mv)
            best_loc = ml
            best_scale = sc
            if best >= early_stop:
                break
    return best, best_loc, best_scale


def _compute_zone_score(zone_act, zone_tpl):
    """Compute similarity score (%) for a single UI zone using MAE fallback on flat regions."""
    if zone_act.std() < 8.0 or zone_tpl.std() < 8.0:
        mae = float(np.mean(np.abs(zone_act.astype(float) - zone_tpl.astype(float))))
        return max(0.0, 100.0 - (mae / 255.0) * 100.0)
    return float(cv2.matchTemplate(zone_act, zone_tpl, cv2.TM_CCOEFF_NORMED)[0][0]) * 100.0


def _compute_clahe_bands(aligned_act, tpl_c):
    """Compare CLAHE-enhanced horizontal bands to catch low-contrast edits on dark canvases."""
    ga = cv2.cvtColor(aligned_act, cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(tpl_c, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    bh = ga.shape[0] // 3
    scores = []
    for bi in range(3):
        ca_b = clahe.apply(ga[bi * bh:(bi + 1) * bh])
        cb_b = clahe.apply(gb[bi * bh:(bi + 1) * bh])
        if cb_b.std() < 8.0 and ca_b.std() < 8.0:
            mae = float(np.mean(np.abs(ca_b.astype(float) - cb_b.astype(float))))
            scores.append(max(0.0, 1.0 - mae / 255.0))
        else:
            r = cv2.matchTemplate(
                cv2.GaussianBlur(ca_b, (0, 0), 1.0),
                cv2.GaussianBlur(cb_b, (0, 0), 1.0),
                cv2.TM_CCOEFF_NORMED,
            )[0][0]
            scores.append(float(r))
    return scores


def _score_tool_zone_cross_dpi(img_act, img_tpl, sb, t_top, t_bot):
    """Evaluate bottom Tool panel across multi-scale horizontal bands (tolerates dp scaling & RecyclerView reflow)."""
    h, w = img_act.shape[:2]
    scales_ui = (1.0, 0.875, 0.93, 0.85, 1.07, 1.14)
    t_h = t_bot - t_top
    t_bands = [
        (t_top, t_top + int(t_h * 0.30)),
        (t_top + int(t_h * 0.25), t_top + int(t_h * 0.72)),
        (t_top + int(t_h * 0.68), t_bot),
    ]
    t_search_y1 = max(sb, t_top - 75)
    t_search_y2 = min(h - int(h * 0.025), t_bot + 45)
    t_search = img_act[t_search_y1:t_search_y2, :]
    t_scores = []

    for ty1, ty2 in t_bands:
        full_p = img_tpl[ty1:ty2, 15:w - 15]
        if full_p.std() < 5.0 and t_search.std() < 5.0:
            mae_t = float(np.mean(np.abs(img_act[ty1:ty2].astype(float) - img_tpl[ty1:ty2].astype(float))))
            t_scores.append(max(0.0, 1.0 - mae_t / 255.0))
        elif full_p.std() < 5.0:
            ph = ty2 - ty1
            best_mae_sc = 0.0
            for oy in range(max(t_search_y1, ty1 - 50), min(t_search_y2 - ph, ty1 + 50) + 1, 10):
                mae_t = float(np.mean(np.abs(img_act[oy:oy + ph, 15:w - 15].astype(float) - full_p.astype(float))))
                best_mae_sc = max(best_mae_sc, 1.0 - mae_t / 255.0)
            t_scores.append(best_mae_sc)
        else:
            best_band = -1.0
            for x1, x2, sx1, sx2 in [
                (15, w - 15, 0, w),
                (15, int(w * 0.58), 0, int(w * 0.70)),
                (int(w * 0.42), w - 15, int(w * 0.30), w),
            ]:
                sub_p = img_tpl[ty1:ty2, x1:x2]
                if sub_p.std() < 4.0:
                    continue
                sc_b, _, _ = _match_best_patch(t_search[:, sx1:sx2], sub_p, scales=scales_ui, blur=1.5, early_stop=0.92)
                best_band = max(best_band, sc_b)
                if best_band >= 0.92:
                    break
            t_scores.append(max(0.0, best_band))

    return float(np.mean(t_scores)), float(min(t_scores))


def _score_sparse_ui_cross_dpi(img_act, img_tpl, sb, nb, t_avg, t_min):
    """Verify light-background stacked UI screens (e.g. Input Text, Custom Gradient) via active component matching."""
    h, w = img_act.shape[:2]
    body_act, body_tpl = img_act[sb:nb], img_tpl[sb:nb]
    bg_act = np.median(body_act, axis=(0, 1))
    bg_tpl = np.median(body_tpl, axis=(0, 1))
    scales_ui = (1.0, 0.875, 0.93, 0.85, 1.07, 1.14)

    row_diff = np.max(np.abs(body_tpl.astype(np.float32) - bg_tpl), axis=(1, 2))
    active = row_diff > 14
    segs = []
    in_seg, start = False, 0
    for idx, val in enumerate(active):
        if val and not in_seg:
            start = idx
            in_seg = True
        elif not val and in_seg:
            if idx - start >= 12:
                segs.append((start, idx))
            in_seg = False
    if in_seg and len(active) - start >= 12:
        segs.append((start, len(active)))

    seg_scores = []
    for s1, s2 in segs:
        y1, y2 = max(sb, sb + s1 - 12), min(nb, sb + s2 + 12)
        seg_diff = np.max(np.abs(img_tpl[y1:y2].astype(np.float32) - bg_tpl), axis=2)
        _, xs_s = np.where(seg_diff > 14)
        if len(xs_s) == 0:
            continue
        x1, x2 = max(0, int(xs_s.min()) - 25), min(w, int(xs_s.max()) + 25)
        if x2 - x1 < 40 or y2 - y1 < 18:
            continue
        patch = img_tpl[y1:y2, x1:x2]
        sy1, sy2 = max(sb, y1 - 85), min(nb, y2 + 85)
        if patch.std() < 12.0:
            ph = y2 - y1
            best_mae_s = 0.0
            for oy in range(sy1, max(sy1 + 1, sy2 - ph + 1), 8):
                mae_p = float(np.mean(np.abs(img_act[oy:oy + ph, x1:x2].astype(float) - patch.astype(float))))
                best_mae_s = max(best_mae_s, 1.0 - mae_p / 255.0)
            seg_scores.append(best_mae_s)
        else:
            best_seg = -1.0
            for px1, px2 in [(x1, x2), (x1, (x1 + x2) // 2), ((x1 + x2) // 2, x2)]:
                p = img_tpl[y1:y2, px1:px2]
                if p.std() < 3.0 or p.shape[1] < 20:
                    continue
                sc_s, _, _ = _match_best_patch(
                    img_act[sy1:sy2, max(0, px1 - 90):min(w, px2 + 90)],
                    p,
                    scales=scales_ui,
                    blur=2.0,
                    early_stop=0.92,
                )
                best_seg = max(best_seg, sc_s)
                if best_seg >= 0.92:
                    break
            if best_seg < 0.90:
                tp_ny = cv2.resize(patch, (patch.shape[1], max(10, int(round(patch.shape[0] * 0.875)))))
                sc_ny, _, _ = _match_best_patch(
                    img_act[sy1:sy2, max(0, x1 - 60):min(w, x2 + 60)],
                    tp_ny,
                    scales=(1.0,),
                    blur=2.0,
                    early_stop=0.92,
                )
                best_seg = max(best_seg, sc_ny)
            seg_scores.append(best_seg)

    if not seg_scores:
        return None

    fg_ratio_tpl = float(np.mean(np.max(np.abs(body_tpl.astype(np.float32) - bg_tpl), axis=2) > 18))
    fg_ratio_act = float(np.mean(np.max(np.abs(body_act.astype(np.float32) - bg_act), axis=2) > 18))
    fg_penalty = abs(fg_ratio_act - fg_ratio_tpl)
    sp_min = float(min(seg_scores))
    sp_avg = float(np.mean(seg_scores))
    bg_mae = float(np.mean(np.abs(bg_act - bg_tpl)))
    passed = (sp_min >= 0.77 and sp_avg >= 0.88 and fg_penalty < 0.15 and bg_mae < 25.0 and t_min >= 0.75)
    reason = "" if passed else f"Sparse UI mismatch (min={sp_min*100:.2f}%, avg={sp_avg*100:.2f}%, fgDelta={fg_penalty*100:.1f}%)"
    return passed, sp_avg * 100.0, sp_min * 100.0, t_avg * 100.0, reason, "sparse"


def _verify_cross_device_full(img_act, img_tpl, c_top, c_bot, t_top, t_bot):
    """
    Cross-device alignment fallback when exact 1:1 comparison fails due to status-bar offset or DPI scaling.
    Returns (passed, overall_pct, canvas_pct, tool_pct, reason, mode_tag).
    """
    h, w = img_act.shape[:2]
    sb, nb = int(h * 0.06), int(h * 0.96)
    t_avg, t_min = _score_tool_zone_cross_dpi(img_act, img_tpl, sb, t_top, t_bot)

    # 1. Standard Canvas alignment + sub-band & CLAHE verification
    c_margin = int(w * 0.02)
    cy1, cy2 = c_top + int(h * 0.015), c_bot - int(h * 0.015)
    tpl_c = img_tpl[cy1:cy2, c_margin:w - c_margin]
    search_c = img_act[max(sb, c_top - 65):min(nb, c_bot + 65), :]

    _, c_loc, _ = _match_best_patch(search_c, tpl_c, scales=(1.0,), blur=0.0, early_stop=0.99)
    aligned_c = search_c[c_loc[1]:c_loc[1] + tpl_c.shape[0], c_loc[0]:c_loc[0] + tpl_c.shape[1]]
    c_ncc = float(cv2.matchTemplate(
        cv2.GaussianBlur(aligned_c, (0, 0), 1.8),
        cv2.GaussianBlur(tpl_c, (0, 0), 1.8),
        cv2.TM_CCOEFF_NORMED,
    )[0][0])

    bh = tpl_c.shape[0] // 3
    band_scores = []
    for bi in range(3):
        bt = tpl_c[bi * bh:(bi + 1) * bh]
        ba = aligned_c[bi * bh:(bi + 1) * bh]
        if bt.std() < 6.0 and ba.std() < 6.0:
            band_scores.append(max(0.0, 1.0 - float(np.mean(np.abs(ba.astype(float) - bt.astype(float)))) / 255.0))
        else:
            pad = 55
            base_y = max(sb, c_top - 65) + c_loc[1] + bi * bh
            b_search = img_act[max(0, base_y - pad):min(h, base_y + bh + pad), :]
            sc_b, _, _ = _match_best_patch(b_search, bt, scales=(1.0, 0.93, 0.875, 1.07), blur=1.5, early_stop=0.92)
            band_scores.append(sc_b)

    c_min_band = float(min(band_scores))
    c_mean_band = float(np.mean(band_scores))
    c_mid_band = float(sorted(band_scores)[1])

    is_dark_canvas = float(np.median(tpl_c)) < 85.0
    clahe_scores = _compute_clahe_bands(aligned_c, tpl_c) if is_dark_canvas else [1.0, 1.0, 1.0]
    clahe_min = float(min(clahe_scores))

    band_ok = (
        (c_min_band >= 0.76 and (not is_dark_canvas or clahe_min >= 0.72))
        or (c_min_band >= 0.75 and c_mean_band >= 0.85 and c_mid_band >= 0.85 and (not is_dark_canvas or clahe_min >= 0.72))
        or (c_min_band >= 0.70 and c_mean_band >= 0.87 and c_mid_band >= 0.90 and (not is_dark_canvas or clahe_min >= 0.70))
        or (c_ncc >= 0.885 and c_min_band >= 0.72 and (not is_dark_canvas or clahe_min >= 0.75))
        or (c_ncc >= 0.94 and t_avg >= 0.92 and c_min_band >= 0.62 and (not is_dark_canvas or clahe_min >= 0.85))
    )
    if c_ncc >= 0.84 and band_ok and t_avg >= 0.84 and t_min >= 0.74:
        overall = min(c_ncc, t_avg) * 100.0
        return True, overall, c_ncc * 100.0, t_avg * 100.0, "", "aligned"

    # 2. Light stacked-card / sparse-text screens (Input Text, Custom Gradient; checked after aligned so Mockup cards never get misrouted)
    canvas_tpl = img_tpl[c_top:c_bot]
    canvas_white_ratio = float(np.mean(np.min(canvas_tpl, axis=2) > 225))
    bg_tpl = np.median(img_tpl[sb:nb], axis=(0, 1))
    if canvas_white_ratio >= 0.40 and float(np.min(bg_tpl)) > 215 and canvas_tpl.std() < 65.0:
        sparse_res = _score_sparse_ui_cross_dpi(img_act, img_tpl, sb, nb, t_avg, t_min)
        if sparse_res is not None:
            return sparse_res

    # 3. Side Layer Drawer overlay (left drawer scales ~0.875x & can wrap long item text; right dimmed canvas is 1.0x)
    if t_avg >= 0.84 and t_min >= 0.74 and c_ncc < 0.88:
        drawer_search = img_act[int(h * 0.08):int(h * 0.72), :int(w * 0.52)]
        right_tpl = img_tpl[c_top + 36:c_bot - 36, int(w * 0.58):w - 22]
        sc_right, _, _ = _match_best_patch(img_act[max(0, c_top - 40):min(h, c_bot + 65), int(w * 0.50):], right_tpl, scales=(1.0,), blur=0.8, early_stop=0.94)
        left_h = (c_bot - 20) - (c_top + 20)
        icon_scores = []
        icon_ys = []
        for f1, f2 in [(0.02, 0.14), (0.35, 0.55), (0.55, 0.75), (0.75, 0.95)]:
            t_icon = img_tpl[c_top + 20 + int(left_h * f1):c_top + 20 + int(left_h * f2), int(w * 0.24):int(w * 0.44)]
            sc_i, loc_i, _ = _match_best_patch(drawer_search[:, int(w * 0.15):], t_icon, scales=(0.82, 0.85, 0.875, 0.90), blur=2.0, early_stop=0.92)
            icon_scores.append(sc_i)
            icon_ys.append(loc_i[1])
        top3 = sorted(icon_scores, reverse=True)[:3]
        # Verify selected blue highlight row aligns in relative vertical position (catches wrong layer ordering)
        roi_a = img_act[int(h * 0.10):int(h * 0.65), :int(w * 0.44)]
        roi_t = img_tpl[int(h * 0.10):int(h * 0.65), :int(w * 0.44)]
        blue_a = np.where((roi_a[:, :, 0].astype(int) - roi_a[:, :, 2].astype(int)) > 80)[0]
        blue_t = np.where((roi_t[:, :, 0].astype(int) - roi_t[:, :, 2].astype(int)) > 80)[0]
        blue_ok = True
        if len(blue_t) > 50 and len(blue_a) > 50:
            blue_diff = abs(float(np.median(blue_a)) / roi_a.shape[0] - float(np.median(blue_t)) / roi_t.shape[0])
            blue_ok = blue_diff <= 0.12
        ordered = icon_scores[0] >= 0.90 and icon_ys[0] < min(icon_ys[1:]) and blue_ok
        if sc_right >= 0.86 and ordered and min(top3) >= 0.78 and float(np.mean(top3)) >= 0.86:
            drawer_score = float(np.mean(top3)) * 100.0
            overall = min(drawer_score, sc_right * 100.0, t_avg * 100.0)
            return True, overall, sc_right * 100.0, t_avg * 100.0, "", "drawer"

    # 4. Centered White Modal Reflow Dialog ("Select a Color" 4x5 vs 5x4 swatches across dp widths)
    if t_avg >= 0.82 and t_min >= 0.75 and c_ncc < 0.78:
        ca = img_act[int(h * 0.30):int(h * 0.62), int(w * 0.16):int(w * 0.84)]
        cb = img_tpl[int(h * 0.30):int(h * 0.62), int(w * 0.16):int(w * 0.84)]
        wa_center = float(np.mean(np.min(ca, axis=2) > 225))
        wb_center = float(np.mean(np.min(cb, axis=2) > 225))
        if wa_center >= 0.38 and wb_center >= 0.38 and abs(wa_center - wb_center) < 0.15:
            hdr_b = img_tpl[int(h * 0.22):int(h * 0.34), int(w * 0.12):int(w * 0.88)]
            ftr_b = img_tpl[int(h * 0.65):int(h * 0.80), int(w * 0.12):int(w * 0.88)]
            sc_hdr, _, _ = _match_best_patch(img_act[int(h * 0.16):int(h * 0.40), :], hdr_b, scales=(0.85, 0.875, 0.93, 1.0), blur=1.5)
            sc_ftr, _, _ = _match_best_patch(img_act[int(h * 0.58):int(h * 0.85), :], ftr_b, scales=(0.85, 0.875, 0.93, 1.0), blur=1.5)
            ma = img_act[int(h * 0.28):int(h * 0.72), int(w * 0.12):int(w * 0.88)]
            mb = img_tpl[int(h * 0.28):int(h * 0.72), int(w * 0.12):int(w * 0.88)]
            ha = cv2.calcHist([cv2.cvtColor(ma, cv2.COLOR_BGR2HSV)], [0, 1], None, [18, 8], [0, 180, 0, 256])
            hb = cv2.calcHist([cv2.cvtColor(mb, cv2.COLOR_BGR2HSV)], [0, 1], None, [18, 8], [0, 180, 0, 256])
            cv2.normalize(ha, ha)
            cv2.normalize(hb, hb)
            hcor = float(cv2.compareHist(ha, hb, cv2.HISTCMP_CORREL))
            if sc_hdr >= 0.78 and sc_ftr >= 0.82 and hcor >= 0.95:
                overall = min(hcor, sc_ftr, t_avg) * 100.0
                return True, overall, hcor * 100.0, t_avg * 100.0, "", "modal"

    if t_avg < 0.84 or t_min < 0.74:
        reason = f"Tool zone mismatch ({t_avg*100:.2f}%, minBand={t_min*100:.2f}%)"
    else:
        reason = f"Canvas zone mismatch ({c_ncc*100:.2f}%, minBand={c_min_band*100:.2f}%, claheMin={clahe_min*100:.2f}%)"
    return False, c_ncc * 100.0, c_ncc * 100.0, t_avg * 100.0, reason, "mismatch"


def compare_images(folder_actual, img_template_path, crop_element_id=None, screenshot_name=None, threshold=0.92):
    folder_actual = os.path.normpath(folder_actual)
    norm_tpl = os.path.normpath(img_template_path)
    if not os.path.isabs(norm_tpl) and not os.path.exists(norm_tpl):
        candidate = os.path.join(folder_actual, norm_tpl)
        if os.path.exists(candidate):
            img_template_path = candidate
        else:
            img_template_path = norm_tpl
    else:
        img_template_path = norm_tpl

    # 1. Tìm file screenshot (theo tên cụ thể hoặc file mới nhất)
    img_actual_path = get_screenshot(folder_actual, screenshot_name)
    
    if not img_actual_path:
        print(f"Error: Not Found Image on the folder's directory {folder_actual}")
        sys.exit(1)
        
    print(f"Screenshot: {img_actual_path}")
    print(f"Template Image: {img_template_path}")

    # 2. Đọc ảnh hỗ trợ đường dẫn Unicode
    img_actual = read_image_unicode(img_actual_path)
    img_template = read_image_unicode(img_template_path)

    if img_actual is None or img_template is None:
        print("Error: Not Found Image or Can't read the image!")
        sys.exit(1)

    # 3. Nếu có crop_element_id, crop ảnh screenshot và template theo vùng element
    if crop_element_id:
        print(f"Cropping screenshot to element: {crop_element_id}")
        bounds = get_element_bounds(crop_element_id, img_actual)
        if bounds:
            orig_h, orig_w = img_actual.shape[:2]
            img_actual = crop_image_by_bounds(img_actual, bounds)
            
            # Cắt ảnh template nếu template là ảnh toàn màn hình (full-screen)
            tpl_h, tpl_w = img_template.shape[:2]
            if tpl_h > orig_h * 0.8:
                scale_x = tpl_w / float(orig_w)
                scale_y = tpl_h / float(orig_h)
                x1, y1, x2, y2 = bounds
                tpl_bounds = (int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y))
                img_template = crop_image_by_bounds(img_template, tpl_bounds)
        else:
            print("Warning: Could not find element bounds, comparing full screenshot")

    # Kiểm tra lệch hướng màn hình (Portrait vs Landscape) trước khi resize
    if not crop_element_id and (img_actual.shape[0] >= img_actual.shape[1]) != (img_template.shape[0] >= img_template.shape[1]):
        print(f"MATCH PERCENTAGE (Overall): 0.00%")
        print(f"  [Zone Canvas] : 0.00% (Threshold: 88%)")
        print(f"  [Zone Tool]   : 0.00% (Threshold: 85%)")
        print(f"FAILED: Screen orientation mismatch ({img_actual.shape[1]}x{img_actual.shape[0]} vs {img_template.shape[1]}x{img_template.shape[0]})")
        sys.exit(1)

    # Resize ảnh mẫu về cùng kích thước ảnh vừa chụp để so sánh chính xác
    if img_actual.shape != img_template.shape:
        img_template = cv2.resize(img_template, (img_actual.shape[1], img_actual.shape[0]))

    # 4. So sánh độ tương đồng (Fast Path 1:1 cho cùng cấu hình DPI chuẩn)
    # Khi so sánh toàn màn hình, bỏ qua Status Bar (top 4.5%) và Navigation Bar (bottom 4%)
    # để loại trừ sai lệch do đồng hồ nhảy giờ, mức pin và thanh điều hướng hệ thống
    if not crop_element_id:
        h = img_actual.shape[0]
        sb_cut = int(h * 0.045)
        nb_cut = int(h * 0.96)
        eval_actual = img_actual[sb_cut:nb_cut, :]
        eval_template = img_template[sb_cut:nb_cut, :]
    else:
        eval_actual = img_actual
        eval_template = img_template

    res = cv2.matchTemplate(eval_actual, eval_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    match_percentage = max_val * 100

    if crop_element_id:
        print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")
        if max_val >= threshold:
            print("PASSED: Image Match Template")
            sys.exit(0)
        print(f"FAILED: Image Not Match Template (Overall match {match_percentage:.2f}% < {threshold*100:.0f}%)")
        sys.exit(1)

    h, w = img_actual.shape[:2]
    c_top = int(h * 0.11)
    c_bot = min(int(h * 0.62), c_top + w)
    t_top = int(h * 0.65)
    t_bot = int(h * 0.96)

    if c_bot > c_top and t_bot > t_top:
        c_score = _compute_zone_score(img_actual[c_top:c_bot, :], img_template[c_top:c_bot, :])
        t_score = _compute_zone_score(img_actual[t_top:t_bot, :], img_template[t_top:t_bot, :])

        # Fast-path PASS nếu ảnh khớp trực tiếp 1:1
        if max_val >= threshold and c_score >= 88.0 and t_score >= 85.0:
            print(f"MATCH PERCENTAGE (Overall): {match_percentage:.2f}%")
            print(f"  [Zone Canvas] : {c_score:.2f}% (Threshold: 88%)")
            print(f"  [Zone Tool]   : {t_score:.2f}% (Threshold: 85%)")
            print("PASSED: Image Match Template")
            sys.exit(0)

        # Fallback Cross-Device: bù lệch Status Bar & co giãn DPI giữa các dòng máy (vd: 420dpi vs 480dpi)
        cd_passed, cd_overall, cd_canvas, cd_tool, cd_reason, cd_mode = _verify_cross_device_full(
            img_actual, img_template, c_top, c_bot, t_top, t_bot
        )
        print(f"MATCH PERCENTAGE (Overall): {cd_overall:.2f}% [Cross-Device:{cd_mode}, 1:1={match_percentage:.2f}%]")
        print(f"  [Zone Canvas] : {cd_canvas:.2f}% (1:1 was {c_score:.2f}%)")
        print(f"  [Zone Tool]   : {cd_tool:.2f}% (1:1 was {t_score:.2f}%)")
        if cd_passed:
            print("PASSED: Image Match Template (Cross-Device Aligned)")
            sys.exit(0)
        print(f"FAILED: Image Not Match Template ({cd_reason})")
        sys.exit(1)

    print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")
    if max_val >= threshold:
        print("PASSED: Image Match Template")
        sys.exit(0)
    print(f"FAILED: Image Not Match Template (Overall match {match_percentage:.2f}% < {threshold*100:.0f}%)")
    sys.exit(1)

def compare_two_screenshots(folder, screenshot1_name, crop1_id, screenshot2_name, crop2_id):
    """
    So sánh 2 screenshot runtime với nhau (crop theo element ID).
    Dùng cho trường hợp so sánh cùng 1 element hiển thị trên 2 màn hình khác nhau.
    """
    folder = os.path.normpath(folder)
    # 1. Tìm và đọc 2 file screenshot
    img1_path = get_screenshot(folder, screenshot1_name)
    img2_path = get_screenshot(folder, screenshot2_name)

    if not img1_path:
        print(f"Error: Screenshot 1 not found: {screenshot1_name}")
        sys.exit(1)
    if not img2_path:
        print(f"Error: Screenshot 2 not found: {screenshot2_name}")
        sys.exit(1)

    print(f"Screenshot 1: {img1_path}")
    print(f"Screenshot 2: {img2_path}")

    img1 = read_image_unicode(img1_path)
    img2 = read_image_unicode(img2_path)

    if img1 is None or img2 is None:
        print("Error: Cannot read one or both screenshots!")
        sys.exit(1)

    # 2. Crop screenshot 1 theo element ID
    if crop1_id:
        print(f"Cropping Screenshot 1 by element: {crop1_id}")
        bounds1 = get_element_bounds(crop1_id, img1)
        if bounds1:
            img1 = crop_image_by_bounds(img1, bounds1)
        else:
            print(f"Warning: Could not find element '{crop1_id}' for Screenshot 1, using full image")

    # 3. Crop screenshot 2 theo element ID
    if crop2_id:
        print(f"Cropping Screenshot 2 by element: {crop2_id}")
        bounds2 = get_element_bounds(crop2_id, img2)
        if bounds2:
            img2 = crop_image_by_bounds(img2, bounds2)
        else:
            print(f"Warning: Could not find element '{crop2_id}' for Screenshot 2, using full image")

    # 4. So sánh 1:1 ban đầu
    img1_res = img1.copy()
    if img1_res.shape != img2.shape:
        img1_res = cv2.resize(img1_res, (img2.shape[1], img2.shape[0]))

    res = cv2.matchTemplate(img2, img1_res, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    best_val = max_val

    # 5. Nếu match 1:1 < 85%, dùng Multi-scale inner content matching
    if best_val < 0.85:
        h1, w1 = img1.shape[:2]
        # Crop inner 85% phần nội dung chính của img1 để bỏ qua viền outer container
        inner1 = img1[int(h1 * 0.08):int(h1 * 0.92), int(w1 * 0.08):int(w1 * 0.92)]
        for scale in np.linspace(0.7, 1.8, 30):
            tpl = cv2.resize(inner1, (0, 0), fx=scale, fy=scale)
            if tpl.shape[0] <= img2.shape[0] and tpl.shape[1] <= img2.shape[1] and tpl.shape[0] > 40 and tpl.shape[1] > 40:
                res_ms = cv2.matchTemplate(img2, tpl, cv2.TM_CCOEFF_NORMED)
                _, val_ms, _, _ = cv2.minMaxLoc(res_ms)
                if val_ms > best_val:
                    best_val = val_ms

    match_percentage = best_val * 100
    print(f"MATCH PERCENTAGE: {match_percentage:.2f}%")

    # 6. Ngưỡng Pass/Fail (80% hoặc mean pixel diff <= 10.0 cho đồ họa gradient/texture)
    diff = cv2.absdiff(img1_res, img2)
    mean_diff = float(np.mean(diff))

    if best_val >= 0.80 or mean_diff <= 10.0:
        print(f"PASSED: Two screenshots match (Score: {match_percentage:.2f}%, Mean Diff: {mean_diff:.2f})")
        sys.exit(0)
    else:
        print(f"FAILED: Two screenshots do not match (Score: {match_percentage:.2f}%, Mean Diff: {mean_diff:.2f})")
        sys.exit(1)

if __name__ == "__main__":
    # Cấu hình encoding utf-8 cho stdout trên Windows
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    # Kiểm tra số lượng tham số truyền vào
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Normal:  python compare.py <folder> <template> [crop_element_id] [screenshot_name]")
        print("  Dual:    python compare.py <folder> dual <screenshot1> <cropId1> <screenshot2> <cropId2>")
        sys.exit(1)

    folder_screenshots = os.path.normpath(sys.argv[1])
    mode = sys.argv[2]

    if mode.lower() == "dual":
        # Chế độ so sánh 2 screenshot runtime
        if len(sys.argv) < 7:
            print("Usage: python compare.py <folder> dual <screenshot1> <cropId1> <screenshot2> <cropId2>")
            sys.exit(1)

        screenshot1 = os.path.normpath(sys.argv[3])
        crop1 = sys.argv[4] if sys.argv[4].lower() != "none" else None
        screenshot2 = os.path.normpath(sys.argv[5])
        crop2 = sys.argv[6] if sys.argv[6].lower() != "none" else None

        compare_two_screenshots(folder_screenshots, screenshot1, crop1, screenshot2, crop2)
    else:
        # Chế độ so sánh screenshot với template (mặc định)
        template_path = os.path.normpath(mode)

        # Tham số thứ 3 (tùy chọn): element ID để crop ("none" = không crop)
        crop_id = sys.argv[3] if len(sys.argv) >= 4 else None
        if crop_id and crop_id.lower() == "none":
            crop_id = None

        # Tham số thứ 4 (tùy chọn): tên screenshot cụ thể ("none" = lấy mới nhất)
        screenshot_name = sys.argv[4] if len(sys.argv) >= 5 else None
        if screenshot_name and screenshot_name.lower() == "none":
            screenshot_name = None

        # Tham số thứ 5 (tùy chọn): threshold (mặc định 0.92)
        threshold = 0.92
        if len(sys.argv) >= 6:
            try:
                threshold = float(sys.argv[5])
            except ValueError:
                threshold = 0.92

        compare_images(folder_screenshots, template_path, crop_id, screenshot_name, threshold)
