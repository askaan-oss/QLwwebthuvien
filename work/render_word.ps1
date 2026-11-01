$ErrorActionPreference = 'Stop'
$taskWord = $null
$taskDoc = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskFile = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\output\QLDA_Nhom11_Lab.docx'))
    $taskFalse = $false
    $taskTrue = $true
    $taskDoc = $taskWord.Documents.Open([ref]$taskFile, [ref]$taskFalse, [ref]$taskTrue, [ref]$taskFalse)
    $taskDoc.Repaginate()
    $taskPdf = Join-Path $PSScriptRoot 'QLDA_Nhom11_Lab_QA.pdf'
    $taskFormat = 17
    $taskDoc.ExportAsFixedFormat($taskPdf, $taskFormat)
    Write-Output 'Rendered PDF for layout review'
} catch {
    Write-Output $_.Exception.Message
    throw
} finally {
    $taskSave = 0
    if ($null -ne $taskDoc) { $taskDoc.Close([ref]$taskSave) }
    if ($null -ne $taskWord) { $taskWord.Quit([ref]$taskSave) }
}
