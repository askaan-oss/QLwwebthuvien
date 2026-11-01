$ErrorActionPreference='Stop'
$w=New-Object -ComObject Word.Application
$w.Visible=$false
$w.DisplayAlerts=0
$w.AutomationSecurity=3
try {
 Write-Output "Opening"
 $d=$w.Documents.Open('D:\QL dự án nhóm\output\Bao_cao_cuoi_ky_Nhom11_hoan_thien.docx')
 Write-Output "Updating"
 $d.Fields.Update() | Out-Null
 Write-Output "Paginating"
 $d.Repaginate()
 foreach($t in $d.TablesOfContents){$t.Update(); $t.Range.Font.Name="Times New Roman"; $t.Range.Font.Size=11; $t.Range.ParagraphFormat.SpaceBefore=0; $t.Range.ParagraphFormat.SpaceAfter=1; $t.Range.ParagraphFormat.LineSpacingRule=0}
 Write-Output "Paginating"
 $d.Repaginate()
 foreach($t in $d.TablesOfContents){$t.UpdatePageNumbers()}
 Write-Output "Saving"
 $d.Save()
 Write-Output "Exporting"
 $d.ExportAsFixedFormat('D:\QL dự án nhóm\work\report-final\report-qa.pdf',17)
 Write-Output ('Pages: '+$d.ComputeStatistics(2))
 $d.Close(0)
} finally {$w.Quit()}
