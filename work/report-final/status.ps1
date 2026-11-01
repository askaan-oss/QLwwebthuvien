$w=[Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
Write-Output $w.Documents.Count
Write-Output $w.StatusBar
