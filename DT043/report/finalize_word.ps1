# Mở báo cáo bằng Microsoft Word: cập nhật mục lục + trường số trang, lưu lại .docx và xuất .pdf
param([Parameter(Mandatory = $true)][string]$Docx)
$path = (Resolve-Path $Docx).Path
$pdf = [System.IO.Path]::ChangeExtension($path, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($path)
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17)   # 17 = wdExportFormatPDF
    "PAGES=" + $doc.ComputeStatistics(2)  # 2 = wdStatisticPages
    $doc.Close()
} finally {
    try { $word.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
"PDF=" + $pdf
