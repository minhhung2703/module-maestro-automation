#!/bin/bash
# ============================================
# Maestro Test Runner Script (macOS / Linux)
# Project: Logo Maker
# ============================================

set -uo pipefail

# ── Color helpers ──────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
WHITE='\033[1;37m'
DARKGRAY='\033[0;37m'
NC='\033[0m' # No Color

# ── Parse arguments ───────────────────────────
FOLDER=""
FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -Folder|--folder|-f)
            FOLDER="$2"; shift 2 ;;
        -File|--file|-t)
            FILE="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [-f|--folder <folder>] [-t|--file <filename>]"
            echo "  -f, --folder   Run tests in a specific folder (e.g. 'test-suite', 'free-version')"
            echo "  -t, --file     Run a specific test file name (partial match)"
            exit 0 ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAESTRO_DIR="$SCRIPT_DIR/.maestro"

PASSED=0
FAILED=0
WARNED=0
TOTAL=0

# Result arrays (parallel arrays for bash 3 compatibility on macOS)
RESULT_TESTS=()
RESULT_FOLDERS=()
RESULT_SCREENS=()
RESULT_STATUSES=()
RESULT_DURATIONS=()

# Folders to exclude from auto-discovery
EXCLUDE_FOLDERS=("config" "screenshots")

# ── Ensure Maestro is in PATH ─────────────────
if [[ -d "$HOME/.maestro/bin" ]]; then
    export PATH="$HOME/.maestro/bin:$PATH"
fi

# ── Resolve Python command ────────────────────
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python not found! Please install Python 3.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  MAESTRO TEST RUNNER - Logo Maker (macOS)${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# ── Check Maestro CLI ─────────────────────────
if ! command -v maestro &>/dev/null; then
    echo -e "${RED}[ERROR] Maestro CLI not found! Please ensure Maestro is installed and added to PATH.${NC}"
    echo -e "${GRAY}  Install: curl -Ls \"https://get.maestro.mobile.dev\" | bash${NC}"
    exit 1
fi

# ── Check device connection ───────────────────
HAS_DEVICE=false
while IFS= read -r line; do
    if [[ "$line" =~ [[:space:]]device$ ]]; then
        HAS_DEVICE=true
        break
    fi
done < <(adb devices 2>&1)

if [ "$HAS_DEVICE" = false ]; then
    echo -e "${RED}[ERROR] No Android device connected! Please connect a device first.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Device connected${NC}"
echo ""

# ── Discover folders to run ───────────────────
FOLDERS_TO_RUN=()
if [[ -n "$FOLDER" ]]; then
    TARGET_DIR="$MAESTRO_DIR/$FOLDER"
    if [[ ! -d "$TARGET_DIR" ]]; then
        echo -e "${RED}[ERROR] Folder not found: $TARGET_DIR${NC}"
        exit 1
    fi
    FOLDERS_TO_RUN+=("$TARGET_DIR")
else
    for dir in "$MAESTRO_DIR"/*/; do
        [[ ! -d "$dir" ]] && continue
        dirname="$(basename "$dir")"
        skip=false
        for ex in "${EXCLUDE_FOLDERS[@]}"; do
            if [[ "$dirname" == "$ex" ]]; then
                skip=true
                break
            fi
        done
        if [ "$skip" = false ]; then
            FOLDERS_TO_RUN+=("$dir")
        fi
    done
fi

# ── Helper: check if a test name matches a wildcard pattern ──
matches_pattern() {
    local name="$1"
    local pattern="$2"
    # Use bash extended globbing for wildcard matching
    [[ "$name" == $pattern ]]
}

# ── Helper: run Python compare (single) ──────
run_single_compare() {
    local template="$1"
    local crop_id="$2"
    local screenshot="$3"

    local crop_arg="${crop_id:-none}"
    local screenshot_arg="${screenshot:-none}"

    echo -e "        ${CYAN}[INFO] Running image comparison post-step...${NC}"
    if [[ "$crop_arg" != "none" ]]; then
        echo -e "        ${CYAN}[INFO] Cropping to element: $crop_arg${NC}"
    fi
    if [[ "$screenshot_arg" != "none" ]]; then
        echo -e "        ${CYAN}[INFO] Looking for screenshot: $screenshot_arg${NC}"
    fi

    local compare_output
    local compare_exit_code=0
    compare_output=$($PYTHON_CMD scripts/compare.py "$SCRIPT_DIR" "$template" "$crop_arg" "$screenshot_arg" 2>&1) || compare_exit_code=$?

    echo -e "        ${DARKGRAY}----------------------------------------${NC}"
    if [[ -n "$compare_output" ]]; then
        while IFS= read -r line; do
            line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"  # trim (BSD-compatible)
            [[ -z "$line" ]] && continue
            if [[ "$line" == *"PASSED"* ]]; then
                echo -e "        ${GREEN}$line${NC}"
            elif [[ "$line" == *"FAILED"* || "$line" == *"Error"* ]]; then
                echo -e "        ${RED}$line${NC}"
            elif [[ "$line" == *"MATCH PERCENTAGE"* ]]; then
                if [[ $compare_exit_code -eq 0 ]]; then
                    echo -e "        ${GREEN}$line${NC}"
                else
                    echo -e "        ${RED}$line${NC}"
                fi
            else
                echo -e "        ${GRAY}$line${NC}"
            fi
        done <<< "$compare_output"
    fi
    echo -e "        ${DARKGRAY}----------------------------------------${NC}"

    return $compare_exit_code
}

# ── Helper: run Python compare (dual) ────────
run_dual_compare() {
    local screenshot1="$1"
    local crop_id1="$2"
    local screenshot2="$3"
    local crop_id2="$4"

    local crop1_arg="${crop_id1:-none}"
    local crop2_arg="${crop_id2:-none}"

    echo -e "        ${CYAN}[INFO] Running dual screenshot comparison...${NC}"
    echo -e "        ${CYAN}[INFO] Screenshot 1: $screenshot1 (crop: $crop1_arg)${NC}"
    echo -e "        ${CYAN}[INFO] Screenshot 2: $screenshot2 (crop: $crop2_arg)${NC}"

    local compare_output
    local compare_exit_code=0
    compare_output=$($PYTHON_CMD scripts/compare.py "$SCRIPT_DIR" dual "$screenshot1" "$crop1_arg" "$screenshot2" "$crop2_arg" 2>&1) || compare_exit_code=$?

    echo -e "        ${DARKGRAY}----------------------------------------${NC}"
    if [[ -n "$compare_output" ]]; then
        while IFS= read -r line; do
            line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"  # trim (BSD-compatible)
            [[ -z "$line" ]] && continue
            if [[ "$line" == *"PASSED"* ]]; then
                echo -e "        ${GREEN}$line${NC}"
            elif [[ "$line" == *"FAILED"* || "$line" == *"Error"* ]]; then
                echo -e "        ${RED}$line${NC}"
            elif [[ "$line" == *"MATCH PERCENTAGE"* ]]; then
                if [[ $compare_exit_code -eq 0 ]]; then
                    echo -e "        ${GREEN}$line${NC}"
                else
                    echo -e "        ${RED}$line${NC}"
                fi
            else
                echo -e "        ${GRAY}$line${NC}"
            fi
        done <<< "$compare_output"
    fi
    echo -e "        ${DARKGRAY}----------------------------------------${NC}"

    return $compare_exit_code
}

# ════════════════════════════════════════════════
# Image Compare Map
# Format: "pattern|template|crop_id|screenshot"
#   - Use "null" for empty crop_id or screenshot
#   - For multi-entry tests, use multiple lines with the same pattern
# ════════════════════════════════════════════════
IMAGE_COMPARE_MAP=(
    # Onboarding Screen
    "*TC_05-Verify_Display_Image_Preview*|assets/onboarding_1.png|null|screenshots/onboarding_step1_preview"
    "*TC_16-Verify_Displayed_Onboarding3*|assets/Onboarding_Step3.png|img|screenshots/onboarding3_compare"
    "*TC_21-Verify_Click_On_Get_Started_Button*|assets/IAP_Screen.png|null|screenshots/IAP_compare"
    "*TC_24-Verify_IAP_Screen_Is_Displayed_After_Killing_App_On_Onboarding*|assets/IAP_Screen.png|null|screenshots/IAP_compare"

    # IAP Screen
    "*TC_02-Verify_Logo_Background_Template_Displayed*|assets/IAP_Screen.png|null|screenshots/IAP_compare"
    "*TC_02.2-Verify_Logo_Background_Template_Displayed*|assets/IAP_Screen.png|null|screenshots/IAP_compare"
    "*TC_04-Verify_Displayed_Comparing_Table*|assets/IAP_Screen.png|rvAllFeatures|screenshots/comparing_table"

    # test-suite: TC_00
    "*TC_00_Get_Payment_Flow*|assets/IAP_Screen.png|null|screenshots/IAP_compare"
    "*TC_00_Get_Payment_Flow*|assets/IAP_Screen.png|null|screenshots/IAP_compare_2"
    "*TC_00_Get_Payment_Flow*|assets/IAP_Screen.png|null|screenshots/IAP_compare_3"
    "*TC_00_Get_Payment_Flow*|assets/onboarding_1.png|null|screenshots/Onboarding_Screen_1"
    "*TC_00_Get_Payment_Flow*|assets/onboarding_2.png|null|screenshots/Onboarding_Screen_2"
    "*TC_00_Get_Payment_Flow*|assets/onboarding_3.png|null|screenshots/Onboarding_Screen_3"
    "*TC_00_Get_Payment_Flow*|assets/Home_Screen.png|null|screenshots/Home_Screen"

    # test-suite: TC_02
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|assets/Custom_Gradient.png|null|screenshots/Custom_Gradient"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|assets/background_Select_Screen.png|null|screenshots/background_Select_Screen"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|assets/texture_Select_Screen.png|null|screenshots/texture_Select_Screen"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|assets/Added_Image_Background_on_Edit_Screen.png|null|screenshots/Add_Image_Background_on_Edit_Screen"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|assets/Verify_Displayed_Save_Options_Popup.png|null|screenshots/Verify_Displayed_Save_Options_Popup"

    # test-suite: TC_03
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Displayed_Art_Tool_On_Edit_Screen.png|null|screenshots/Displayed_Art_Tool_On_Edit_Screen"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Display_Dialog_Layer_On_Edit_Screen.png|null|screenshots/Verify_Display_Dialog_Layer_On_Edit_Screen"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Move_Layer_To_Down_On_Dialog_Layer.png|null|screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Move_Layer_To_Top_On_Dialog_Layer.png|null|screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_duplicate_Layer_To_Top_On_Dialog_Layer.png|null|screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Closing_Layer_Dialog.png|null|screenshots/Closing_Layer_Dialog"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Move_Layer_To_Top_On_Dialog_Layer_2.png|null|screenshots/Verify_Move_Layer_To_Top_On_Dialog_Layer_2"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Move_Layer_To_Down_On_Dialog_Layer_2.png|null|screenshots/Verify_Move_Layer_To_Down_On_Dialog_Layer_2"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2.png|null|screenshots/Verify_duplicate_Layer_To_Top_On_Dialog_Layer_2"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Move_Layer_By_Using_pointer.png|null|screenshots/Verify_Move_Layer_By_Using_pointer"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Undo_On_The_Template_Detail_Successfully.png|null|screenshots/Verify_Undo_On_The_Template_Detail_Successfully"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Redo_On_The_Template_Detail_Successfully.png|null|screenshots/Verify_Redo_On_The_Template_Detail_Successfully"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Rate_App_Popup_On_Preview.png|null|screenshots/Rate_App_Popup_On_Preview"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|assets/Verify_Navigated_to_Style_Magic_AI_Screen.png|null|screenshots/Verify_Navigated_to_Style_Magic_AI_Screen"
    # test-suite: TC_04
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_SubTab_Default.png|null|screenshots/Color_SubTab_Default"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Opacity_Changed.png|null|screenshots/Color_Opacity_Changed"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Solid_Red_Applied.png|null|screenshots/Color_Solid_Red_Applied"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Palette_Dialog.png|null|screenshots/Color_Palette_Dialog"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Custom_Gradient_Screen.png|null|screenshots/Color_Custom_Gradient_Screen"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Texture_Scale_Displayed.png|null|screenshots/Color_Texture_Scale_Displayed"
    "*TC_04_Test_Sub_Tab_Color_Art_Tool_On_Edit_Screen*|assets/Color_Tool_Baseline.png|null|screenshots/Color_Tool_Result"
)

# ════════════════════════════════════════════════
# Dual Compare Map
# Format: "pattern|screenshot1|crop_id1|screenshot2|crop_id2"
# ════════════════════════════════════════════════
DUAL_COMPARE_MAP=(
    "*AI_TC_08.2-Verify_Spam_Button_AI_Magic_Style_On_Saved_Screen*|screenshots/Saved_Screen_Card|imgStory|screenshots/AI_Magic_Style_Card|img_preview"

    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/Add_Image_Background_on_Edit_Screen|layout_transparent|screenshots/preview_screen_logo|imageTransparentGrid"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/backgroundTool_on_Edit_Screen|bgDesignArea|screenshots/backgroundTool_on_Edit_Screen2|bgDesignArea"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/backgroundTool_on_Edit_Screen|bgDesignArea|screenshots/backgroundTool_on_Edit_Screen3|bgDesignArea"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/backgroundTool_on_Edit_Screen|bgDesignArea|screenshots/backgroundTool_on_Edit_Screen4|bgDesignArea"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/backgroundTool_on_Edit_Screen|bgDesignArea|screenshots/backgroundTool_on_Edit_Screen5|bgDesignArea"
    "*TC_02_Test_Background_Tool_On_Edit_Screen*|screenshots/Add_Image_Background_on_Edit_Screen|bgDesignArea|screenshots/TemplateDraft_Displayed_correctly|bgDesignArea"

    "*TC_03_Test_Art_Tool_On_Edit_Screen*|screenshots/Verify_Redo_On_The_Template_Detail_Successfully|bgDesignArea|screenshots/Preview_Screen|imageTransparentGrid"
    "*TC_03_Test_Art_Tool_On_Edit_Screen*|screenshots/Verify_Image_On_Style_Magic_AI_Matches_Template|image|screenshots/Preview_Screen|imageTransparentGrid"
)

# ── Function: Run a single test file ─────────
run_test_file() {
    local test_file="$1"
    local folder_name="$2"
    local screen_name="$3"

    TOTAL=$((TOTAL + 1))
    local test_name
    test_name="$(basename "$test_file" .yaml)"

    echo ""
    echo -e "    ${WHITE}[$TOTAL] Running: $test_name${NC}"
    echo -e "        ${GRAY}File: $test_file${NC}"

    # Clean up stale session lock file
    local session_file="$HOME/.maestro/sessions"
    if [[ -f "$session_file" ]]; then
        rm -f "$session_file" 2>/dev/null || true
    fi

    local start_time
    start_time=$(date +%s)

    local output=""
    local exit_code=0
    output=$(maestro test "$test_file" 2>&1) || exit_code=$?

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    local status=""
    local color=""

    if [[ $exit_code -eq 0 ]]; then
        local compare_failed=false

        # ── Run dual compare configs ──
        for entry in "${DUAL_COMPARE_MAP[@]}"; do
            IFS='|' read -r pattern screenshot1 crop_id1 screenshot2 crop_id2 <<< "$entry"
            if matches_pattern "$test_name" "$pattern"; then
                [[ "$crop_id1" == "null" ]] && crop_id1=""
                [[ "$crop_id2" == "null" ]] && crop_id2=""
                if ! run_dual_compare "$screenshot1" "$crop_id1" "$screenshot2" "$crop_id2"; then
                    compare_failed=true
                fi
            fi
        done

        # ── Run single image compare configs ──
        for entry in "${IMAGE_COMPARE_MAP[@]}"; do
            IFS='|' read -r pattern template crop_id screenshot <<< "$entry"
            if matches_pattern "$test_name" "$pattern"; then
                [[ "$crop_id" == "null" ]] && crop_id=""
                [[ "$screenshot" == "null" ]] && screenshot=""
                if ! run_single_compare "$template" "$crop_id" "$screenshot"; then
                    compare_failed=true
                fi
            fi
        done

        # Determine final status
        if [ "$compare_failed" = true ]; then
            FAILED=$((FAILED + 1))
            status="FAILED"
            color="$RED"
        elif [[ "$output" == *"WARNED"* ]]; then
            WARNED=$((WARNED + 1))
            status="WARNED"
            color="$YELLOW"
        else
            PASSED=$((PASSED + 1))
            status="PASSED"
            color="$GREEN"
        fi
    else
        FAILED=$((FAILED + 1))
        status="FAILED"
        color="$RED"
        echo -e "        ${YELLOW}[MAESTRO OUTPUT]${NC}"
        while IFS= read -r line; do
            line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"  # trim (BSD-compatible)
            [[ -z "$line" ]] && continue
            echo -e "        ${YELLOW}$line${NC}"
        done <<< "$output"
    fi

    echo -e "        Result: ${color}${status}${NC} (${duration}s)"

    # Store results
    RESULT_TESTS+=("$test_name")
    RESULT_FOLDERS+=("$folder_name")
    RESULT_SCREENS+=("$screen_name")
    RESULT_STATUSES+=("$status")
    RESULT_DURATIONS+=("${duration}s")
}

# ── Main execution loop ──────────────────────
for folder_path in "${FOLDERS_TO_RUN[@]}"; do
    folder_name="$(basename "$folder_path")"

    echo -e "${DARKGRAY}========================================${NC}"
    echo -e "  ${YELLOW}Folder: $folder_name${NC}"
    echo -e "${DARKGRAY}========================================${NC}"

    # 1. Run direct YAML files in this folder
    if compgen -G "$folder_path"/*.yaml >/dev/null 2>&1; then
        for test_file in "$folder_path"/*.yaml; do
            [[ ! -f "$test_file" ]] && continue
            file_basename="$(basename "$test_file")"
            if [[ -n "$FILE" && "$file_basename" != *"$FILE"* ]]; then
                continue
            fi
            run_test_file "$test_file" "$folder_name" "$folder_name"
        done
    fi

    # 2. Run YAML files in subdirectories (screens)
    for screen_dir in "$folder_path"/*/; do
        [[ ! -d "$screen_dir" ]] && continue
        screen_name="$(basename "$screen_dir")"

        echo ""
        echo -e "  ${MAGENTA}Screen: $screen_name${NC}"

        if compgen -G "$screen_dir"/*.yaml >/dev/null 2>&1; then
            for test_file in "$screen_dir"/*.yaml; do
                [[ ! -f "$test_file" ]] && continue
                file_basename="$(basename "$test_file")"
                if [[ -n "$FILE" && "$file_basename" != *"$FILE"* ]]; then
                    continue
                fi
                run_test_file "$test_file" "$folder_name" "$screen_name"
            done
        fi
    done
done

# ── Summary ───────────────────────────────────
echo ""
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  TEST RESULTS SUMMARY${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Print results table
if [[ ${#RESULT_TESTS[@]} -gt 0 ]]; then
    # Simple table output (bash 3.2 compatible, no dynamic printf widths)
    printf "  %-55s  %-15s  %-15s  %-8s  %-10s\n" "Test" "Folder" "Screen" "Status" "Duration"
    printf "  %-55s  %-15s  %-15s  %-8s  %-10s\n" \
        "-------------------------------------------------------" \
        "---------------" "---------------" "--------" "----------"

    for i in "${!RESULT_TESTS[@]}"; do
        local_color="$NC"
        case "${RESULT_STATUSES[$i]}" in
            PASSED) local_color="$GREEN" ;;
            FAILED) local_color="$RED" ;;
            WARNED) local_color="$YELLOW" ;;
        esac
        # Use echo -e for reliable ANSI color output on macOS
        printf "  %-55s  %-15s  %-15s  " \
            "${RESULT_TESTS[$i]}" "${RESULT_FOLDERS[$i]}" "${RESULT_SCREENS[$i]}"
        echo -e "${local_color}${RESULT_STATUSES[$i]}${NC}$(printf '%*s' $((8 - ${#RESULT_STATUSES[$i]})) '')  ${RESULT_DURATIONS[$i]}"
    done
fi

echo ""
echo -e "  ${WHITE}Total: $TOTAL | Passed: $PASSED | Warned: $WARNED | Failed: $FAILED${NC}"
echo ""

if [[ $FAILED -gt 0 ]]; then
    echo -e "  ${RED}SOME TESTS FAILED!${NC}"
    exit 1
else
    echo -e "  ${GREEN}ALL TESTS PASSED!${NC}"
    exit 0
fi
