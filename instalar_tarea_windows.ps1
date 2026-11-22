# Script para registrar la tarea silenciosa en el Programador de Tareas de Windows
# Frecuencia: 1 imagen cada 4 horas (empezando dentro de 4 horas)
# Se ejecuta de forma oculta y actualiza automáticamente la web en GitHub.

$TaskName = "SOMBRA_Generador_Banners_21_9"
$WorkingDir = $PSScriptRoot
$ScriptPy = Join-Path $WorkingDir "generar_siguiente_banner.py"

Write-Host "Configurando tarea programada silenciosa de Windows (cada 4 horas): $TaskName"

# Acción: lanzar python sin ventana visible usando powershell -WindowStyle Hidden
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -Command `"Set-Location '$WorkingDir'; python '$ScriptPy' >> 'cron_banners.log' 2>&1`"" `
    -WorkingDirectory $WorkingDir

# Disparador: primera ejecución dentro de 4 horas y repetición cada 4 horas
$StartTime = (Get-Date).AddHours(4)
$Trigger = New-ScheduledTaskTrigger -Once -At $StartTime -RepetitionInterval (New-TimeSpan -Hours 4)

# Configuración: si el PC estaba apagado a esa hora, ejecutar al encender (StartWhenAvailable)
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Regenera 1 banner 21:9 de SOMBRA cada 4 horas, actualiza la web y sincroniza GitHub (se autoelimina al terminar)" `
    -Force

Write-Host "`n[OK] Tarea programada registrada con éxito en Windows."
Write-Host "Primera ejecución programada: $StartTime (y luego cada 4 horas)."
