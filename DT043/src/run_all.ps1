# Chạy lại toàn bộ phần tính toán của DT043: môi trường → dữ liệu → kiểm thử → thí nghiệm → benchmark → MTD → tái lập bài báo (E11, E12) → tổng hợp → gói triển khai.
# Script KHÔNG sinh lại báo cáo Word và slide: file Word đã được sửa tay và có mục 6.10 (E12) chèn bằng report/patch_report_e12.py,
# chạy report/build_report.py sẽ ghi đè và làm mất các phần đó. Muốn sinh lại tài liệu, xem README mục 2 (bước 10–11).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
if (-not (Test-Path ".venv")) { py -3.11 -m venv .venv; .venv\Scripts\python -m pip install -r requirements.txt }
$py = ".venv\Scripts\python.exe"

# Lệnh ngoài (python) không làm dừng script khi lỗi dù có $ErrorActionPreference, nên kiểm tra mã thoát từng bước.
function Step([string]$name, [scriptblock]$cmd) {
    Write-Host "== $name"
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "Bước '$name' lỗi (mã thoát $LASTEXITCODE)" }
}

Step "Ghi cấu hình máy" { & $py ai/scripts/00_env_info.py }
if (-not (Test-Path "data/MANIFEST.sha256")) { Step "Tải dữ liệu" { & $py ai/scripts/01_download.py } }
Step "Kiểm tra checksum" { & $py ai/scripts/02_verify_manifest.py }
if (-not (Test-Path "data/processed")) { Step "Chuẩn bị dữ liệu" { & $py ai/scripts/03_prepare.py } }
Step "EDA" { & $py ai/scripts/03b_eda.py }
Step "Kiểm thử" { & $py -m pytest ai/tests backend/tests -q }
# Bỏ qua các lần chạy đã có metrics.json; chỉ chạy đủ 4–5 giờ khi results/raw còn trống.
Step "Ma trận thí nghiệm" { & $py ai/scripts/04_run_matrix.py E1_baseline E4_light E3_iforest E2_global E2_shared_pdnorm `
    E4_tiny_L5 E4_tiny_L3 E4_tiny_L1 E4_tiny_L01 E4_tiny_L001 E6_leak E9_robust E9_poison_1 E9_poison_5 --workers 2 }
Step "Edge benchmark" { & $py ai/scripts/05_bench_edge.py }
Step "Mô phỏng MTD" { & $py ai/scripts/07_mtd_sim.py }
Step "Tái lập bài báo chính (E11)" { & $py ai/scripts/10_tharm_paper_replication.py }
Step "Vẽ lại hình của bài báo" { & $py ai/scripts/11_paper_figures.py }
Step "Tái hiện thêm kết quả bài báo (E12)" { & $py ai/scripts/12_masud_full_repro.py }
Step "Hậu kiểm ngưỡng" { & $py ai/scripts/09_posthoc_threshold.py }
Step "Tổng hợp bảng/hình" { & $py ai/scripts/06_aggregate.py }
Step "Xuất gói triển khai" { & $py ai/scripts/08_export_deploy.py }
Write-Host "Xong. Báo cáo Word và slide không bị thay đổi. Chạy demo: $py -m uvicorn backend.app.main:app --port 8000"
