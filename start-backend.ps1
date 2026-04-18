# Backend API Başlatma Scripti
# Bu script Python bağımlılıklarını yükler ve backend sunucusunu başlatır

$ErrorActionPreference = "Stop"

# Script dizinini al
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Çalışma dizini: $ScriptPath" -ForegroundColor Cyan
Set-Location $ScriptPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend API Başlatma Scripti" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python sürümünü kontrol et
Write-Host "Python sürümü kontrol ediliyor..." -ForegroundColor Yellow
try {
    $pythonVersion = py -3.12 --version 2>&1
    Write-Host "Python sürümü: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "HATA: Python bulunamadı!" -ForegroundColor Red
    Write-Host "Lütfen Python 3.12'yi kurun." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Bağımlılıkları yükle
Write-Host "Python bağımlılıkları yükleniyor..." -ForegroundColor Yellow
try {
    py -3.12 -m pip install -r requirements.txt
    Write-Host "Bağımlılıklar başarıyla yüklendi!" -ForegroundColor Green
} catch {
    Write-Host "HATA: Bağımlılıklar yüklenirken hata oluştu!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Backend sunucusunu başlat
Write-Host "Backend sunucusu başlatılıyor..." -ForegroundColor Yellow
Write-Host "API adresi: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Durdurmak için CTRL+C tuşlarına basın" -ForegroundColor Yellow
Write-Host ""

try {
    py -3.12 app.py
} catch {
    Write-Host "HATA: Backend sunucusu başlatılamadı!" -ForegroundColor Red
    exit 1
}
