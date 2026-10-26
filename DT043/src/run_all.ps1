# Chạy toàn bộ DT043 từ đầu: môi trường → dữ liệu → kiểm thử → thí nghiệm → benchmark → tổng hợp → gói triển khai → báo cáo
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
if (-not (Test-Path ".venv")) { py -3.11 -m venv .venv; .venv\Scripts\python -m pip install -r requirements.txt }
$py = ".venv\Scripts\python.exe"

& $py ai/scripts/00_env_info.py
if (-not (Test-Path "data/MANIFEST.sha256")) { & $py ai/scripts/01_download.py }
& $py ai/scripts/02_verify_manifest.py
if (-not (Test-Path "data/processed")) { & $py ai/scripts/03_prepare.py }
& $py ai/scripts/03b_eda.py
& $py -m pytest ai/tests backend/tests -q
& $py ai/scripts/04_run_matrix.py E1_baseline E4_light E3_iforest E2_global E2_shared_pdnorm `
    E4_tiny_L5 E4_tiny_L3 E4_tiny_L1 E4_tiny_L01 E4_tiny_L001 E6_leak E9_robust E9_poison_1 E9_poison_5 --workers 2
& $py ai/scripts/05_bench_edge.py
& $py ai/scripts/07_mtd_sim.py
& $py ai/scripts/09_posthoc_threshold.py
& $py ai/scripts/06_aggregate.py
& $py ai/scripts/08_export_deploy.py
# Báo cáo Word (+ cập nhật mục lục, xuất PDF bằng Microsoft Word nếu có)
& $py report/build_report.py
powershell -NoProfile -ExecutionPolicy Bypass -File report/finalize_word.ps1 -Docx ../tailieu/bao_cao/BaoCao_DT043_1150080120_HoangThanhTra.docx
# Slide PowerPoint (cần Node.js; lần đầu: cd report; npm install)
& $py report/export_deck_data.py
Push-Location report; if (-not (Test-Path node_modules)) { npm install }; node build_deck.js; Pop-Location
powershell -NoProfile -ExecutionPolicy Bypass -File report/export_pptx_pdf.ps1 -Pptx ../tailieu/thuyet_trinh/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx
Write-Host "Xong. Chạy demo: $py -m uvicorn backend.app.main:app --port 8000"
