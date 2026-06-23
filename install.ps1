# install.ps1 - Setup completo del proyecto

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  PDF/EPUB Translator - Setup" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no encontrado. Instalalo desde https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion`n" -ForegroundColor Green

# Verificar Ollama
Write-Host "Verificando Ollama..." -ForegroundColor Yellow
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ollama no encontrado." -ForegroundColor Red
    Write-Host "   Descargalo desde https://ollama.com/download" -ForegroundColor Yellow
    Write-Host "   Despues de instalarlo, ejecuta este script de nuevo.`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Ollama instalado`n" -ForegroundColor Green

# Crear entorno virtual
Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
python -m venv venv
venv\Scripts\activate
Write-Host "✅ Entorno virtual creado`n" -ForegroundColor Green

# Instalar dependencias
Write-Host "Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✅ Dependencias instaladas`n" -ForegroundColor Green

# Preguntar qué modelo bajar
Write-Host "¿Qué modelo querés usar?" -ForegroundColor Cyan
Write-Host "  [1] qwen2.5:7b  - Recomendado para 4-6GB VRAM" -ForegroundColor White
Write-Host "  [2] qwen2.5:14b - Recomendado para 8-12GB VRAM" -ForegroundColor White
Write-Host "  [3] qwen2.5:32b - Recomendado para 16GB+ VRAM" -ForegroundColor White
Write-Host "  [4] Saltar (ya tengo un modelo)" -ForegroundColor White

$choice = Read-Host "`nElegí una opción (1-4)"

switch ($choice) {
    "1" { ollama pull qwen2.5:7b }
    "2" { ollama pull qwen2.5:14b }
    "3" { ollama pull qwen2.5:32b }
    "4" { Write-Host "Saltando descarga de modelo." -ForegroundColor Yellow }
    default { Write-Host "Opción inválida, saltando." -ForegroundColor Yellow }
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  ✅ Setup completo!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nUso:" -ForegroundColor White
Write-Host "  venv\Scripts\activate" -ForegroundColor Yellow
Write-Host "  python translator.py archivo.pdf --lang es" -ForegroundColor Yellow
Write-Host "  python translator.py libro.epub --lang es`n" -ForegroundColor Yellow