<#
.SYNOPSIS
Запускает пайплайн обработки файла скользящим окном с сохранением каждого шага
#>

param(

# ------------------------------------------------------------------------------------------------------------
    # Заполнить перед запуском:
    [int]$WindowSize = 300, # количество строк в одном фрагменте крупного файла 
    [int]$StepSize = 250, # смещение начала фрагмента вправо (позволяет создать наложение фрагментов)
    [string]$InputFile = "../datasheets/AR9331.txt", # крупный файл, который нужно обработать по частям
    [string]$PromptTemplateFile = "../prompts/Конвертация схемы в текст.txt", # шаблон запроса к нейросети
# ------------------------------------------------------------------------------------------------------------

     # Промеуточные выходные файлы скрипта (создавать самостоятельно не нужно)
    [string]$AnswerFile = "../tmp/huge_file/answer_tmp.txt",
    [string]$InputPartTmpFile = "../tmp/huge_file/input_part_tmp.txt"
)

$global:ContinueHotkey = @{
    Ctrl = [System.Windows.Input.Key]::Q
}

# Создаём подпапку для выходных файлов
$OutputSubfolder = "../tmp/huge_file/prompt_outputs"
if (-not (Test-Path $OutputSubfolder)) {
    New-Item -ItemType Directory -Path $OutputSubfolder -Force | Out-Null
    Write-Host "Создана подпапка: $OutputSubfolder"
}

if (Test-Path "prompt_output.txt") {
    Remove-Item "prompt_output.txt" -Force
    Write-Host "Старый prompt_output.txt удалён"
}

if (-not (Test-Path $InputFile)) { Write-Error "Файл $InputFile не найден"; exit 1 }
if (-not (Test-Path $PromptTemplateFile)) { Write-Error "Файл $PromptTemplateFile не найден"; exit 1 }
if (-not (Test-Path $AnswerFile)) { Write-Error "Файл $AnswerFile не найден"; exit 1 }

$lines = Get-Content $InputFile
$totalLines = $lines.Count

Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName System.Windows.Forms

function Wait-ForHotkey {
    Write-Host "Нажмите Ctrl+Q для следующей итерации..."
    while ($true) {
        Start-Sleep -Milliseconds 100
        if ([System.Windows.Input.Keyboard]::IsKeyDown([System.Windows.Input.Key]::LeftCtrl) -or
            [System.Windows.Input.Keyboard]::IsKeyDown([System.Windows.Input.Key]::RightCtrl)) {
            if ([System.Windows.Input.Keyboard]::IsKeyDown($global:ContinueHotkey.Ctrl)) {
                Start-Sleep -Milliseconds 200
                break
            }
        }
    }
}

$stepNumber = 1
for ($start = 0; $start -lt $totalLines; $start += $StepSize) {
    $end = [Math]::Min($start + $WindowSize - 1, $totalLines - 1)
    
    Write-Host "Обработка строк $start - $end"
    
    $lines[$start..$end] | Set-Content $InputPartTmpFile
    
    $template = Get-Content $PromptTemplateFile -Raw
    $partContent = Get-Content $InputPartTmpFile -Raw
    $answerContent = Get-Content $AnswerFile -Raw
    
    $partText = if ($partContent) { $partContent.Trim() } else { "" }
    $answerText = if ($answerContent) { $answerContent.Trim() } else { "" }
    
    $startIndex = $start + 1
    $endIndex = $end + 1
    
    $result = $template `
        -replace '#1', $partText `
        -replace '#2', $answerText `
        -replace '#3', $startIndex `
        -replace '#4', $endIndex `
        -replace '#5', $totalLines
    
    $result | Set-Content "prompt_output.txt"
    
    # Сохраняем в подпапку с номером шага
    $outputFile = Join-Path $OutputSubfolder "prompt_step_$stepNumber.txt"
    $result | Set-Content $outputFile
    
    [System.Windows.Forms.Clipboard]::SetText($result)
    
    Write-Host "Создан prompt_output.txt и сохранён в $outputFile (строки $startIndex-$endIndex из $totalLines)"
    
    if ($end -lt $totalLines - 1) {
        Wait-ForHotkey
        $stepNumber++
    } else {
        Write-Host "Достигнут конец файла. Завершение."
    }
}

Write-Host "Готово. Все файлы сохранены в папке: $(Resolve-Path $OutputSubfolder)"