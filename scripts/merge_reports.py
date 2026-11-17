#!/usr/bin/env python3
"""
Merge and aggregate test results from multiple parallel shards (GitHub Actions or Local).
Generates a unified markdown table and sets GitHub Step Summary if available.
"""
import os
import sys
import glob
import json

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def merge_reports(reports_dir="reports"):
    report_files = glob.glob(os.path.join(reports_dir, "**", "*.json"), recursive=True)
    if not report_files:
        report_files = glob.glob("*.json")
        report_files = [f for f in report_files if "report_shard" in f or "shard" in f]

    if not report_files:
        print(f"[WARNING] No shard report JSON files found in {reports_dir}")
        return 0

    total_tests = 0
    total_passed = 0
    total_warned = 0
    total_failed = 0
    all_results = []

    print(f"[INFO] Found {len(report_files)} shard reports to merge:")
    for fpath in sorted(report_files):
        if "test_status.json" in fpath or "consolidated_report.json" in fpath:
            continue
        print(f"  - {fpath}")
        try:
            with open(fpath, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            if "Results" not in data:
                continue
            total_tests += data.get("Total", 0)
            total_passed += data.get("Passed", 0)
            total_warned += data.get("Warned", 0)
            total_failed += data.get("Failed", 0)
            shard_idx = data.get("ShardIndex", 0)
            shard_tot = data.get("ShardTotal", 0)
            device = data.get("Device", "unknown")

            for res in data.get("Results", []):
                res["Shard"] = f"{shard_idx}/{shard_tot}" if shard_tot > 0 else "-"
                res["Device"] = device
                all_results.append(res)
        except Exception as e:
            print(f"[ERROR] Failed to read {fpath}: {e}")

    # Build Markdown table
    md_lines = []
    md_lines.append("# 📊 Consolidated Test Results (10 Shards Parallel)")
    md_lines.append("")
    status_icon = "✅ PASSED" if total_failed == 0 else "❌ FAILED"
    md_lines.append(f"**Overall Status**: {status_icon} | **Total**: {total_tests} | **Passed**: {total_passed} | **Failed**: {total_failed} | **Warned**: {total_warned}")
    md_lines.append("")
    md_lines.append("| Test Case | Shard | Device | Status | Duration | Failed Step |")
    md_lines.append("|:---|:---:|:---:|:---:|:---:|:---|")

    failed_details = []
    all_image_comparisons = []

    for r in all_results:
        st = r.get("Status", "UNKNOWN")
        icon = "✅ PASSED" if st == "PASSED" else ("⚠️ WARNED" if st == "WARNED" else "❌ FAILED")
        failed_step = r.get("FailedStep") or "-"
        md_lines.append(f"| `{r.get('Test', '')}` | {r.get('Shard', '-')} | `{r.get('Device', '')}` | {icon} | {r.get('Duration', '')} | {failed_step} |")
        
        if st == "FAILED" and (r.get("FailedStep") or r.get("ErrorMessage")):
            failed_details.append(r)

        for comp in (r.get("ImageComparisons") or []):
            target = f"{comp.get('Screenshot1', '')} vs {comp.get('Screenshot2', '')}" if comp.get("Type") == "Dual" else comp.get("Template", "")
            crop_id = comp.get("CropId") or comp.get("CropId1") or comp.get("CropId2") or "-"
            all_image_comparisons.append({
                "Test": r.get("Test", ""),
                "Device": r.get("Device", ""),
                "Type": comp.get("Type", "Template"),
                "Target": target,
                "CropId": crop_id,
                "MatchPercentage": comp.get("MatchPercentage"),
                "Status": comp.get("Status", "UNKNOWN"),
                "Summary": comp.get("Summary", "")
            })

    if failed_details:
        md_lines.append("")
        md_lines.append("## ❌ Failed Steps & Error Details")
        md_lines.append("")
        md_lines.append("| Test Case | Failed Step | Error Message |")
        md_lines.append("|:---|:---|:---|")
        for fd in failed_details:
            err_msg = (fd.get("ErrorMessage") or "-").replace("\n", " ").replace("|", "/")
            step_str = (fd.get("FailedStep") or "-").replace("|", "/")
            md_lines.append(f"| `{fd.get('Test', '')}` | **{step_str}** | `{err_msg}` |")

    if all_image_comparisons:
        md_lines.append("")
        md_lines.append(f"## 🖼️ Image Comparison Results ({len(all_image_comparisons)} Total)")
        md_lines.append("")
        md_lines.append("| Test Case | Type | Target / Template | Crop | Match % | Status | Details |")
        md_lines.append("|:---|:---:|:---|:---:|:---:|:---:|:---|")
        for ic in all_image_comparisons:
            st_icon = "✅ PASSED" if ic["Status"] == "PASSED" else "❌ FAILED"
            match_str = f"{ic['MatchPercentage']:.2f}%" if ic['MatchPercentage'] is not None else "N/A"
            summary_clean = ic["Summary"].replace("|", "/")
            md_lines.append(f"| `{ic['Test']}` | {ic['Type']} | `{ic['Target']}` | `{ic['CropId']}` | **{match_str}** | {st_icon} | {summary_clean} |")

    md_output = "\n".join(md_lines)
    print("\n" + "="*80)
    print(md_output)
    print("="*80 + "\n")

    # Write to GitHub Step Summary if running in GitHub Actions
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        try:
            with open(gh_summary, "a", encoding="utf-8") as gf:
                gf.write(md_output + "\n")
            print(f"[INFO] Appended consolidated summary to $GITHUB_STEP_SUMMARY ({gh_summary})")
        except Exception as e:
            print(f"[WARNING] Could not write to GITHUB_STEP_SUMMARY: {e}")

    # Save consolidated JSON report
    consolidated_json = os.path.join(reports_dir, "consolidated_report.json")
    try:
        with open(consolidated_json, "w", encoding="utf-8") as f:
            json.dump({
                "Total": total_tests,
                "Passed": total_passed,
                "Warned": total_warned,
                "Failed": total_failed,
                "Results": all_results
            }, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved consolidated JSON report to {consolidated_json}")
    except Exception as e:
        print(f"[WARNING] Could not write consolidated JSON: {e}")

    return 1 if total_failed > 0 else 0

if __name__ == "__main__":
    rep_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    exit_code = merge_reports(rep_dir)
    sys.exit(exit_code)

