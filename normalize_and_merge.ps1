# Normaliza nombres de PDFs, los mueve a pdfs/ y actualiza metadata.json
param()

$ErrorActionPreference = 'Stop'

$Root = "c:\Users\Cynthia\OneDrive\Escritorio\T.S. EN CIENCIA DE DATOS\saia ia y educacion recursos"
$PdfDir = Join-Path $Root "pdfs"
$MetaPath = Join-Path $Root "metadata.json"

if (-not (Test-Path $PdfDir)) { New-Item -ItemType Directory -Path $PdfDir -Force | Out-Null }

function Normalize-Name([string]$name) {
  $nameNoExt = [System.IO.Path]::GetFileNameWithoutExtension($name)
  $ext = [System.IO.Path]::GetExtension($name)

  # Remover diacríticos
  $formD = $nameNoExt.Normalize([System.Text.NormalizationForm]::FormD)
  $chars = $formD.ToCharArray() | Where-Object { 
    [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($_) -ne [System.Globalization.UnicodeCategory]::NonSpacingMark
  }
  $ascii = -join $chars

  # Quitar símbolos raros, espacios -> '_', colapsar '_'
  $ascii = [regex]::Replace($ascii, '[^\w\.\- ]', '')
  $ascii = [regex]::Replace($ascii, '\s+', '_')
  $ascii = [regex]::Replace($ascii, '_+', '_')
  $ascii = $ascii.Trim('_')

  if ([string]::IsNullOrWhiteSpace($ascii)) { $ascii = 'documento' }
  return "$ascii$ext"
}

# Construir mapa de nombres y mover
$map = @{}
Get-ChildItem -Path $Root -Filter *.pdf -File | ForEach-Object {
  $oldFull = $_.FullName
  $newName = Normalize-Name $_.Name
  $newFull = Join-Path $PdfDir $newName

  # Resolver colisiones añadiendo sufijo incremental
  if (Test-Path $newFull) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($newName)
    $ext = [System.IO.Path]::GetExtension($newName)
    $i = 1
    do {
      $candidate = "$base-$i$ext"
      $newFull = Join-Path $PdfDir $candidate
      $i++
    } while (Test-Path $newFull)
    $newName = [System.IO.Path]::GetFileName($newFull)
  }

  Move-Item -LiteralPath $oldFull -Destination $newFull -Force
  $map[$_.Name] = $newName
}

# Leer y fusionar metadata.json
if (-not (Test-Path $MetaPath)) { throw "No se encontró metadata.json en $MetaPath" }
$jsonRaw = Get-Content -LiteralPath $MetaPath -Raw -ErrorAction Stop
if (-not $jsonRaw) { throw "metadata.json está vacío o no legible" }

$json = $jsonRaw | ConvertFrom-Json
if ($json -isnot [System.Collections.IEnumerable]) { $json = @($json) }

foreach ($entry in $json) {
  # Asegurar campos clave
  if (-not ($entry.PSObject.Properties.Name -contains 'original_url')) { $entry | Add-Member -NotePropertyName original_url -NotePropertyValue '' }

  # Actualizar file según mapa
  $oldFile = $entry.file
  if ($oldFile) {
    $base = [System.IO.Path]::GetFileName($oldFile)
    if ($map.ContainsKey($base)) {
      $entry.file = "pdfs/" + $map[$base]
    } else {
      # Si ya apunta a pdfs/, verificar existencia
      $maybe = Join-Path $Root $oldFile
      if (-not (Test-Path $maybe)) {
        # Intentar corregir por nombre normalizado del basename
        $norm = Normalize-Name $base
        $candidate = Join-Path $PdfDir $norm
        if (Test-Path $candidate) { $entry.file = "pdfs/" + [System.IO.Path]::GetFileName($candidate) }
      }
    }
  }
}

# Guardar
$json | ConvertTo-Json -Depth 12 | Out-File -FilePath $MetaPath -Encoding UTF8

Write-Host "Hecho. PDFs movidos a 'pdfs/' y metadata.json actualizado."
