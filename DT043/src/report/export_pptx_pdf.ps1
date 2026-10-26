# Xuất slide .pptx sang .pdf bằng Microsoft PowerPoint (để kiểm tra hình ảnh / nộp kèm)
param([Parameter(Mandatory = $true)][string]$Pptx)
$path = (Resolve-Path $Pptx).Path
$pdf = [System.IO.Path]::ChangeExtension($path, ".pdf")
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($path, $true, $false, $false)   # ReadOnly, Untitled, WithWindow=false
    $pres.SaveAs($pdf, 32)                                          # 32 = ppSaveAsPDF
    "SLIDES=" + $pres.Slides.Count
    $pres.Close()
} finally {
    try { $app.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
}
"PDF=" + $pdf
