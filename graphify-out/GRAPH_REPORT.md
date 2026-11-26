# Graph Report - logo-maker  (2026-11-19)

## Corpus Check
- 119 files · ~121,174 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 223 file(s) not represented in the graph (top: .xml 219, (none) 2, .pptx 2)
- WARNING: 223 of 342 files seen (65%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 278 nodes · 404 edges · 18 communities (14 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Export, Save & Mockup Workflows
- Automation Architecture & QA Presentation
- Screen Comparison & Cropping Engine
- Computer Vision & Zone Analysis
- CI/CD Pipeline Steps & Actions
- GitHub Actions Matrix & Sharding
- Report Merging & Daemon Orchestration
- Visual Baselines & Feature Validation
- PowerPoint Automation Reporting
- Excel Benchmark & Suite Generators
- Color Art & Gradient Tools
- Text Tool & Input Validation
- macOS Shell Test Runner
- Windows PowerShell Test Runner
- Linux Shell Test Runner

## God Nodes (most connected - your core abstractions)
1. `with` - 20 edges
2. `Text Tool Sub-Tabs Container` - 11 edges
3. `Text Tool Controls Sub-Tab` - 10 edges
4. `_verify_cross_device_full()` - 9 edges
5. `compare_images()` - 9 edges
6. `compare_two_screenshots()` - 9 edges
7. `Hybrid Automation Architecture` - 9 edges
8. `Art Tool Color Sub-Tab` - 9 edges
9. `get_element_bounds()` - 8 edges
10. `select_restaurant_template()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `3-Tier Framework Architecture (Native, Vision, CI/CD)` --semantically_similar_to--> `Hybrid Automation Architecture`  [INFERRED] [semantically similar]
  docs/LogoMaker_Automation_Presentation.html → README.md
- `Three Core Automation Algorithms (Multi-Zone/MAE, OpenCV Daemon, Adaptive Selectors)` --semantically_similar_to--> `OpenCV Template Service Daemon`  [INFERRED] [semantically similar]
  docs/LogoMaker_Automation_Presentation.html → README.md
- `Three Core Automation Algorithms (Multi-Zone/MAE, OpenCV Daemon, Adaptive Selectors)` --semantically_similar_to--> `Dynamic Multi-Zone Visual Comparison`  [INFERRED] [semantically similar]
  docs/LogoMaker_Automation_Presentation.html → README.md
- `Three Core Automation Algorithms (Multi-Zone/MAE, OpenCV Daemon, Adaptive Selectors)` --semantically_similar_to--> `Polymorphic Selectors Mechanism`  [INFERRED] [semantically similar]
  docs/LogoMaker_Automation_Presentation.html → README.md
- `Mockup Preview Screen Test Specification` --cites--> `Logo Maker Mobile Automation Overview`  [EXTRACTED]
  docs/test-cases/Mockup_Preview_Screen_TestCases.txt → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three-Tier Hybrid Automation Architecture Trio** — readme_hybrid_architecture, docs_logomaker_automation_presentation_three_tier_architecture, readme_dynamic_multizone_visual_compare [INFERRED 0.95]
- **Edit Canvas Tooling, Save Pipeline & Output Preview Cycle** — docs_test_cases_edit_screen_background_tool_sub_features_and_save_testcases_save_workflow, docs_test_cases_edit_screen_feature_usage_and_save_testcases_export_and_project_saving, docs_test_cases_edit_screen_feature_usage_and_save_testcases_dual_screen_visual_compare [EXTRACTED 1.00]
- **End-to-End Mockup Preview Brand Verification Flow** — docs_test_cases_mockup_preview_screen_testcases_e2e_workflows, docs_test_cases_mockup_preview_screen_testcases_five_mockup_products, docs_test_cases_mockup_preview_screen_testcases_button_state_transition [EXTRACTED 1.00]
- **Art Tool Editing and Export Pipeline** — docs_test_cases_edit_screen_sub_tab_color_art_tool_testcases_art_tool_color_sub_tab, docs_test_cases_edit_screen_sub_tab_outline_art_tool_testcases_art_tool_outline_sub_tab, docs_test_cases_edit_screen_sub_tab_3d_art_tool_testcases_art_tool_3d_sub_tab, docs_test_cases_edit_screen_save_feature_and_preview_testcases_export_logo_png [INFERRED 0.85]
- **Text Tool End-to-End Creation and Formatting Flow** — docs_test_cases_edit_screen_sub_tabs_text_tool_testcases_text_creation_workflow, docs_test_cases_edit_screen_sub_tab_controls_text_tool_testcases_text_tool_controls_sub_tab, docs_test_cases_edit_screen_sub_tabs_text_tool_testcases_text_fonts_sub_tab, docs_test_cases_edit_screen_sub_tabs_text_tool_testcases_text_color_sub_tab, docs_test_cases_edit_screen_sub_tabs_text_tool_testcases_text_curve_spacing_sub_tab [EXTRACTED 1.00]
- **Multi-Resolution Export and Preview Delivery Workflow** — docs_test_cases_edit_screen_save_feature_and_preview_testcases_save_options_dialog, docs_test_cases_edit_screen_save_feature_and_preview_testcases_logo_size_dialog, docs_test_cases_edit_screen_save_feature_and_preview_testcases_export_logo_png, docs_test_cases_edit_screen_save_feature_and_preview_testcases_preview_screen [EXTRACTED 1.00]

## Communities (18 total, 4 thin omitted)

### Community 0 - "Export, Save & Mockup Workflows"
Cohesion: 0.05
Nodes (42): Brand Identify Mockup Feature, Edit Screen Save Feature and Preview Screen Test Cases Document, Export Logo PNG, Logo Size Configuration Dialog, Preview Output Screen (LogoPreviewActivity), Re-edit Workflow from Preview Screen, Reward Ad Post-Save Handling, Save Options Dialog (+34 more)

### Community 1 - "Automation Architecture & QA Presentation"
Cohesion: 0.06
Nodes (34): Logo Maker Automation Presentation Deck, Real-Device Quality Gate (Samsung S20 FE), Six Critical User Experience Flows, Three Core Automation Algorithms (Multi-Zone/MAE, OpenCV Daemon, Adaptive Selectors), 3-Tier Framework Architecture (Native, Vision, CI/CD), Graphics App Testing Challenges (Canvas Mù, False Pass, Flakiness), Presentation Script & Speaker Notes, Background Custom Gradient Sub-Feature (Linear/Radial, Direction) (+26 more)

### Community 2 - "Screen Comparison & Cropping Engine"
Cohesion: 0.11
Nodes (11): compare_two_images(), crop_image(), get_element_bounds(), read_image_unicode(), get_element_bounds(), crop_center(), crop_image(), get_element_bounds() (+3 more)

### Community 3 - "Computer Vision & Zone Analysis"
Cohesion: 0.16
Nodes (14): compare_images(), compare_two_screenshots(), _compute_clahe_bands(), _compute_zone_score(), crop_image_by_bounds(), find_card_bounds(), get_element_bounds(), get_screenshot() (+6 more)

### Community 4 - "CI/CD Pipeline Steps & Actions"
Cohesion: 0.08
Nodes (27): GH_TOKEN, steps, steps, env, if, name, run, uses (+19 more)

### Community 5 - "GitHub Actions Matrix & Sharding"
Cohesion: 0.09
Nodes (22): jobs, maestro-shard-test, merge-and-report, name, runs-on, strategy, timeout-minutes, shardIndex (+14 more)

### Community 6 - "Report Merging & Daemon Orchestration"
Cohesion: 0.17
Nodes (6): merge_reports(), adb(), find_target(), get_screen(), select_restaurant_template(), TemplateHandler

### Community 7 - "Visual Baselines & Feature Validation"
Cohesion: 0.17
Nodes (12): Visual Baseline Assets Reconciliation Report, Exact Match Baseline Assets (49 Files), Premium vs Free Baseline Mismatch Analysis (17 Files), Root-Exclusive Baseline Assets (12 Files), Art Sticker Tool Operations (Move, Color, Outline, 3D, Duplicate), Dual Screenshot Visual Comparison (Edit Canvas vs Preview), Effect Overlay & Palette Theme Tools, PNG HD Export & Save Project Pipeline (+4 more)

### Community 8 - "PowerPoint Automation Reporting"
Cohesion: 0.23
Nodes (5): add_card(), add_header(), add_speaker_notes(), build_deck(), set_slide_background()

### Community 9 - "Excel Benchmark & Suite Generators"
Cohesion: 0.25
Nodes (3): create_time_benchmark_sheet(), main(), build_excel()

### Community 10 - "Color Art & Gradient Tools"
Cohesion: 0.20
Nodes (10): Advanced Palette and Custom HEX Dialog, Art Tool Color Sub-Tab, Canvas Eyedropper Color Picker, Custom Gradient Designer Tool, Edit Screen Sub-Tab Color Art Tool Test Cases Document, Art Opacity/Transparency Slider, Art Solid Color Palette, Texture Pattern Overlay and Scale (+2 more)

### Community 11 - "Text Tool & Input Validation"
Cohesion: 0.29
Nodes (7): Canvas Text Bounding Box & Curved/3D Effects, Character Counter & 40-Char Limit Enforcement, Empty Text Validation & Toast Error Handling, Input Text Screen & UI Components, Vietnamese Diacritics, Symbols & Emoji Handling, Edit Screen Text Tool Test Specification, Text Modification Undo/Redo Action Stack

### Community 12 - "macOS Shell Test Runner"
Cohesion: 0.60
Nodes (5): matches_pattern(), run_dual_compare(), run_single_compare(), run_test_file(), run_tests_macos.sh script

### Community 13 - "Windows PowerShell Test Runner"
Cohesion: 0.60
Nodes (3): Extract-MaestroError(), Parse-CompareResult(), Run-TestFile()

## Knowledge Gaps
- **71 isolated node(s):** `Bootstrap Setup Flow (Solution 3)`, `Auto-Queue Parallel Runner (run_parallel.ps1)`, `10-Shard Parallel GitHub Actions CI/CD`, `Rich JSON Reporting System`, `Real-Device Quality Gate (Samsung S20 FE)` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 152 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Export Logo PNG` connect `Export, Save & Mockup Workflows` to `Color Art & Gradient Tools`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `Bootstrap Setup Flow (Solution 3)`, `Auto-Queue Parallel Runner (run_parallel.ps1)`, `10-Shard Parallel GitHub Actions CI/CD` to the rest of the system?**
  _71 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Export, Save & Mockup Workflows` be split into smaller, more focused modules?**
  _Cohesion score 0.05110336817653891 - nodes in this community are weakly interconnected._
- **Why does `Text Tool Sub-Tabs Container` connect `Export, Save & Mockup Workflows` to `Color Art & Gradient Tools`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `Automation Architecture & QA Presentation` be split into smaller, more focused modules?**
  _Cohesion score 0.06190476190476191 - nodes in this community are weakly interconnected._
- **Should `Screen Comparison & Cropping Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.11088709677419355 - nodes in this community are weakly interconnected._
- **Should `CI/CD Pipeline Steps & Actions` be split into smaller, more focused modules?**
  _Cohesion score 0.08262108262108261 - nodes in this community are weakly interconnected._