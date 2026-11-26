#!/bin/bash
# ==============================================================================
# CI/CD Test Runner Script for Logo Maker (Linux / macOS / GitHub Actions)
# Inspired by logox-maker setup, tailored for com.thmobile.logomaker & Android 13
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Tạo thư mục app nếu chưa có
mkdir -p app

# 2. Chờ máy ảo Android khởi động hoàn tất
echo "Waiting for device to come online..."
adb wait-for-device
echo "Device connected. Waiting for boot to complete..."
BOOT_TIMEOUT=300
ELAPSED=0
while [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; do
  if [ "$ELAPSED" -ge "$BOOT_TIMEOUT" ]; then
    echo "Error: Emulator did not boot within ${BOOT_TIMEOUT} seconds."
    exit 1
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  echo "  Still waiting... (${ELAPSED}s)"
done
echo "Emulator fully booted! (${ELAPSED}s)"

# 3. Chuẩn hóa độ phân giải & mật độ hiển thị theo máy thật Samsung S20 FE (1080x2400, 480dpi)
echo "=== Cấu hình màn hình khớp thiết bị thật (1080x2400 @ 480dpi) ==="
adb shell wm size 1080x2400 || true
adb shell wm density 480 || true
echo "Resolution: $(adb shell wm size 2>/dev/null)"
echo "Density   : $(adb shell wm density 2>/dev/null)"

# 4. Kiểm tra hoặc tải bản build (APK / AAB) từ GitHub Releases
aab_file=$(ls app/*.aab 2>/dev/null | head -n 1 || true)
apk_file=$(ls app/*.apk 2>/dev/null | head -n 1 || true)

if [ -z "$aab_file" ] && [ -z "$apk_file" ]; then
  echo "No local APK or AAB file found in app/ directory!"
  REPO="${GITHUB_REPOSITORY:-minhhung2703/module-maestro-automation}"
  echo "Checking latest GitHub Releases for $REPO..."
  AUTH_HEADER=""
  if [ -n "$GH_TOKEN" ]; then
    AUTH_HEADER="Authorization: token $GH_TOKEN"
    echo "Using authenticated GitHub API access."
  else
    echo "Warning: GH_TOKEN not set. API calls to private repos may fail."
  fi

  API_RESPONSE=$(curl -s -H "$AUTH_HEADER" "https://api.github.com/repos/$REPO/releases/latest" || echo "{}")

  # Tìm asset .aab hoặc .apk trong release mới nhất
  ASSET_INFO=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for asset in data.get('assets', []):
        name = asset.get('name', '')
        if name.endswith('.aab') or name.endswith('.apk'):
            print(f\"{asset['id']}|{name}\")
            break
except Exception:
    pass
" 2>/dev/null || true)

  if [ -n "$ASSET_INFO" ]; then
    ASSET_ID=$(echo "$ASSET_INFO" | cut -d'|' -f1)
    ASSET_NAME=$(echo "$ASSET_INFO" | cut -d'|' -f2)
    echo "Found release asset: $ASSET_NAME (ID: $ASSET_ID)"

    ASSET_API_URL="https://api.github.com/repos/$REPO/releases/assets/$ASSET_ID"
    TARGET_FILE="app/$ASSET_NAME"

    echo "Downloading to $TARGET_FILE..."
    curl -L \
      -H "$AUTH_HEADER" \
      -H "Accept: application/octet-stream" \
      -o "$TARGET_FILE" \
      "$ASSET_API_URL"

    # Kiểm tra kích thước file tải về
    FILE_SIZE=$(stat -c%s "$TARGET_FILE" 2>/dev/null || stat -f%z "$TARGET_FILE" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -lt 1024 ]; then
      echo "Warning: Downloaded file is too small (${FILE_SIZE} bytes). Might be invalid."
      rm -f "$TARGET_FILE"
    else
      echo "Downloaded successfully: $TARGET_FILE (${FILE_SIZE} bytes)"
    fi
  else
    echo "Notice: No APK/AAB found in GitHub Releases."
    if adb shell pm list packages | grep -q "com.thmobile.logomaker"; then
      echo "App 'com.thmobile.logomaker' is already installed on device. Proceeding with installed version."
    fi
  fi

  # Cập nhật lại biến file sau khi tải
  aab_file=$(ls app/*.aab 2>/dev/null | head -n 1 || true)
  apk_file=$(ls app/*.apk 2>/dev/null | head -n 1 || true)
fi

# 5. Chuyển đổi AAB sang APK bằng bundletool (nếu có file AAB)
if [ -n "$aab_file" ]; then
  echo "Found AAB file: $aab_file. Converting to APK using bundletool..."

  DEBUG_KEYSTORE="$HOME/.android/debug.keystore"
  mkdir -p "$HOME/.android"
  if [ ! -f "$DEBUG_KEYSTORE" ]; then
    echo "Creating debug keystore..."
    keytool -genkey -v \
      -keystore "$DEBUG_KEYSTORE" \
      -storepass android \
      -alias androiddebugkey \
      -keypass android \
      -keyalg RSA \
      -keysize 2048 \
      -validity 10000 \
      -dname "CN=Android Debug,O=Android,C=US"
  fi

  if [ ! -f "bundletool.jar" ]; then
    echo "Downloading bundletool.jar..."
    curl -L -o bundletool.jar https://github.com/google/bundletool/releases/download/1.15.6/bundletool-all-1.15.6.jar
  fi

  java -jar bundletool.jar build-apks \
    --bundle="$aab_file" \
    --output=app/app.apks \
    --mode=universal \
    --ks="$DEBUG_KEYSTORE" \
    --ks-pass=pass:android \
    --ks-key-alias=androiddebugkey \
    --key-pass=pass:android \
    --overwrite

  unzip -p app/app.apks universal.apk > app/Logo_Maker.apk
  echo "Converted AAB to app/Logo_Maker.apk successfully."
elif [ -n "$apk_file" ]; then
  echo "Found local APK file: $apk_file"
  cp "$apk_file" app/Logo_Maker.apk
fi

# 6. Cài đặt APK vào thiết bị / máy ảo
if [ -f "app/Logo_Maker.apk" ]; then
  echo "=== Installing app/Logo_Maker.apk onto device ==="
  adb install -r -g app/Logo_Maker.apk
fi

# 7. Chẩn đoán cài đặt ứng dụng
echo "=== Diagnostic: Verifying installed package ==="
if adb shell pm list packages | grep -q "com.thmobile.logomaker"; then
  echo "[OK] Package com.thmobile.logomaker is successfully installed on device."
else
  echo "[ERROR] Package com.thmobile.logomaker not found on device!"
  echo "Please provide an APK/AAB in app/ directory or publish it as an asset on GitHub Releases."
  exit 1
fi

# 8. Đồng bộ ảnh mẫu test vào thư viện Gallery thiết bị
echo "=== Syncing test media to device Gallery ==="
if [ -f "assets/image_Default.png" ]; then
  adb push assets/image_Default.png /sdcard/Pictures/image_Default.png 2>&1 || true
  adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Pictures/image_Default.png 2>&1 || true
  echo "[OK] Test image synced to /sdcard/Pictures/image_Default.png"
fi

# 8.5 Khởi tạo trạng thái lần đầu (Bootstrap First-Run: Language, Onboarding, Edit Intro)
echo "=== Running First-Run Bootstrap Setup Flow (.maestro/config/Init_First_Run_State.yaml) ==="
maestro test .maestro/config/Init_First_Run_State.yaml || true

# 9. Thực thi kịch bản kiểm thử Maestro đồng nhất qua PowerShell Runner (run_tests_windows.ps1)
echo ""
echo "=============================================================================="
echo "  STARTING MAESTRO TEST SUITE VIA POWERSHELL RUNNER"
echo "=============================================================================="

# Chuyển tiếp toàn bộ tham số truyền vào (hoặc mặc định chạy test-suite)
if [ "$#" -gt 0 ]; then
  pwsh -File ./run_tests_windows.ps1 "$@"
else
  pwsh -File ./run_tests_windows.ps1 -Folder "test-suite"
fi
