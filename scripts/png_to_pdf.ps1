param(
  [string]$InputDir = "docs\assets\sheets",
  [string]$OutputDir = "docs\assets\sheets\pdf"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

function Get-JpegBytes {
  param([string]$Path)

  $img = [System.Drawing.Image]::FromFile($Path)
  $ms = $null
  try {
    $ms = New-Object System.IO.MemoryStream
    $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
      Where-Object { $_.MimeType -eq "image/jpeg" } |
      Select-Object -First 1
    $params = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
      [System.Drawing.Imaging.Encoder]::Quality,
      [int64]95
    )
    $img.Save($ms, $codec, $params)

    return @{
      Bytes = $ms.ToArray()
      Width = $img.Width
      Height = $img.Height
    }
  }
  finally {
    $img.Dispose()
    if ($ms) {
      $ms.Dispose()
    }
  }
}

function Escape-PdfString {
  param([string]$Text)

  return $Text.Replace('\', '\\').Replace('(', '\(').Replace(')', '\)')
}

function New-ImagePdf {
  param(
    [string[]]$ImagePaths,
    [string]$OutputPath,
    [string]$Title
  )

  $enc = [System.Text.Encoding]::ASCII
  $out = New-Object System.IO.MemoryStream
  $writer = New-Object System.IO.StreamWriter($out, $enc)
  $writer.NewLine = "`n"
  $offsets = New-Object System.Collections.Generic.List[int64]
  $objects = New-Object System.Collections.Generic.List[object]

  function Add-Obj {
    param([object]$Content)

    $objects.Add($Content)
    return $objects.Count
  }

  $pageW = 595.28
  $pageH = 841.89
  $margin = 18
  $pageIds = @()

  $catalogId = Add-Obj ""
  $pagesId = Add-Obj ""

  foreach ($path in $ImagePaths) {
    $jpeg = Get-JpegBytes $path
    $iw = [double]$jpeg.Width
    $ih = [double]$jpeg.Height
    $maxW = $pageW - ($margin * 2)
    $maxH = $pageH - ($margin * 2)
    $scale = [Math]::Min($maxW / $iw, $maxH / $ih)
    $drawW = [Math]::Round($iw * $scale, 2)
    $drawH = [Math]::Round($ih * $scale, 2)
    $x = [Math]::Round(($pageW - $drawW) / 2, 2)
    $y = [Math]::Round(($pageH - $drawH) / 2, 2)

    $imgId = $objects.Count + 1
    $imgHeader = "<< /Type /XObject /Subtype /Image /Width $($jpeg.Width) /Height $($jpeg.Height) /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length $($jpeg.Bytes.Length) >>`nstream`n"
    $objects.Add(@{
      Header = $imgHeader
      Bytes = $jpeg.Bytes
      Footer = "`nendstream"
    })

    $content = "q`n$drawW 0 0 $drawH $x $y cm`n/Im0 Do`nQ`n"
    $contentBytes = $enc.GetBytes($content)
    $contentId = $objects.Count + 1
    $objects.Add(@{
      Header = "<< /Length $($contentBytes.Length) >>`nstream`n"
      Bytes = $contentBytes
      Footer = "endstream"
    })

    $pageId = Add-Obj "<< /Type /Page /Parent $pagesId 0 R /MediaBox [0 0 $pageW $pageH] /Resources << /XObject << /Im0 $imgId 0 R >> >> /Contents $contentId 0 R >>"
    $pageIds += $pageId
  }

  $objects[$catalogId - 1] = "<< /Type /Catalog /Pages $pagesId 0 R >>"
  $kids = ($pageIds | ForEach-Object { "$_ 0 R" }) -join " "
  $objects[$pagesId - 1] = "<< /Type /Pages /Kids [$kids] /Count $($pageIds.Count) >>"
  $infoId = Add-Obj ("<< /Title (" + (Escape-PdfString $Title) + ") /Creator (Codex PowerShell PDF generator) >>")

  $writer.Write("%PDF-1.4`n%PDF`n")
  $writer.Flush()

  for ($i = 0; $i -lt $objects.Count; $i++) {
    $offsets.Add($out.Position)
    $writer.Write("$($i + 1) 0 obj`n")
    $writer.Flush()

    $obj = $objects[$i]
    if ($obj -is [hashtable]) {
      $writer.Write($obj.Header)
      $writer.Flush()
      $out.Write($obj.Bytes, 0, $obj.Bytes.Length)
      $writer.Write("`n$($obj.Footer)`nendobj`n")
    }
    else {
      $writer.Write("$obj`nendobj`n")
    }
    $writer.Flush()
  }

  $xrefPos = $out.Position
  $writer.Write("xref`n0 $($objects.Count + 1)`n")
  $writer.Write("0000000000 65535 f `n")
  foreach ($off in $offsets) {
    $writer.Write(("{0:D10} 00000 n `n" -f $off))
  }
  $writer.Write("trailer`n<< /Size $($objects.Count + 1) /Root $catalogId 0 R /Info $infoId 0 R >>`nstartxref`n$xrefPos`n%%EOF`n")
  $writer.Flush()

  [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputPath)) | Out-Null
  [System.IO.File]::WriteAllBytes($OutputPath, $out.ToArray())
  $writer.Dispose()
  $out.Dispose()
}

$resolvedInput = Resolve-Path $InputDir
[System.IO.Directory]::CreateDirectory($OutputDir) | Out-Null

$images = Get-ChildItem $resolvedInput -Filter "*.png" | Sort-Object Name
if (-not $images) {
  throw "No PNG files found in $InputDir"
}

New-ImagePdf `
  -ImagePaths ($images.FullName) `
  -OutputPath (Join-Path $OutputDir "g-kentei-cheatsheets.pdf") `
  -Title "G検定 直前チートシート"

foreach ($img in $images) {
  New-ImagePdf `
    -ImagePaths @($img.FullName) `
    -OutputPath (Join-Path $OutputDir ($img.BaseName + ".pdf")) `
    -Title $img.BaseName
}

Get-ChildItem $OutputDir -Filter "*.pdf" | Sort-Object Name | Select-Object Name,Length
