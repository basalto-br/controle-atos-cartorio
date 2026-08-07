# Servidor de desenvolvimento — PowerShell puro. Sem Node, sem bundler, sem instalar nada.
#
# Por que existe: a ferramenta precisa rodar em http://localhost para a File System
# Access API (a "pasta de dados conectada") funcionar. Em file:// o navegador bloqueia,
# e ai so sobra o fallback em memoria, que perde tudo ao fechar a aba.
#
# Uso:    powershell -ExecutionPolicy Bypass -File .claude/serve.ps1
# Abrir:  http://localhost:8123/controle-atos.html
# Parar:  Ctrl+C nesta janela, ou  Get-Process powershell | Stop-Process -Force

$ErrorActionPreference = 'Stop'

$porta = 8123
# A raiz servida e a pasta do projeto (uma acima de .claude/).
$raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$raizComBarra = $raiz.TrimEnd('\') + '\'

$mime = @{
  '.html'  = 'text/html; charset=utf-8'
  '.htm'   = 'text/html; charset=utf-8'
  '.js'    = 'text/javascript; charset=utf-8'
  '.css'   = 'text/css; charset=utf-8'
  '.json'  = 'application/json; charset=utf-8'
  '.md'    = 'text/plain; charset=utf-8'
  '.jpg'   = 'image/jpeg'
  '.jpeg'  = 'image/jpeg'
  '.png'   = 'image/png'
  '.svg'   = 'image/svg+xml'
  '.ico'   = 'image/x-icon'
  '.woff'  = 'font/woff'
  '.woff2' = 'font/woff2'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$porta/")

try {
  $listener.Start()
} catch {
  Write-Host ""
  Write-Host "  Nao consegui abrir a porta $porta." -ForegroundColor Red
  Write-Host "  Provavel causa: ja existe um servidor rodando nessa porta."
  Write-Host "  Para derrubar:  Get-Process powershell | Stop-Process -Force"
  Write-Host ""
  Write-Host "  Detalhe: $($_.Exception.Message)" -ForegroundColor DarkGray
  exit 1
}

Write-Host ""
Write-Host "  Servidor no ar." -ForegroundColor Green
Write-Host "  Abra:  http://localhost:$porta/controle-atos.html"
Write-Host "  Raiz:  $raiz"
Write-Host "  Ctrl+C para parar."
Write-Host ""

while ($listener.IsListening) {
  try { $ctx = $listener.GetContext() } catch { break }

  $req = $ctx.Request
  $res = $ctx.Response

  try {
    $rel = [System.Uri]::UnescapeDataString($req.Url.AbsolutePath).TrimStart('/')
    if ([string]::IsNullOrWhiteSpace($rel)) { $rel = 'index.html' }
    $rel = $rel -replace '/', '\'

    $alvo = [System.IO.Path]::GetFullPath((Join-Path $raiz $rel))

    # Trava de seguranca: nunca servir arquivo de fora da pasta do projeto.
    # Sem isto, uma URL com ..\..\ leria qualquer arquivo do computador.
    if (-not $alvo.StartsWith($raizComBarra, [StringComparison]::OrdinalIgnoreCase)) {
      $res.StatusCode = 403
      Write-Host ("403  " + $req.Url.AbsolutePath) -ForegroundColor Red
      $res.Close()
      continue
    }

    if (Test-Path -LiteralPath $alvo -PathType Leaf) {
      $bytes = [System.IO.File]::ReadAllBytes($alvo)
      $ext = [System.IO.Path]::GetExtension($alvo).ToLowerInvariant()
      $tipo = $mime[$ext]
      if (-not $tipo) { $tipo = 'application/octet-stream' }

      $res.ContentType = $tipo
      # Sem cache: em desenvolvimento, F5 tem que trazer a versao recem-salva.
      $res.Headers.Add('Cache-Control', 'no-store, must-revalidate')
      $res.ContentLength64 = $bytes.Length
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host ("200  " + $req.Url.AbsolutePath)
    } else {
      $res.StatusCode = 404
      $msg = [System.Text.Encoding]::UTF8.GetBytes("404 - nao encontrado: $rel")
      $res.ContentType = 'text/plain; charset=utf-8'
      $res.ContentLength64 = $msg.Length
      $res.OutputStream.Write($msg, 0, $msg.Length)
      Write-Host ("404  " + $req.Url.AbsolutePath) -ForegroundColor DarkYellow
    }
  } catch {
    try { $res.StatusCode = 500 } catch {}
    Write-Host ("500  " + $_.Exception.Message) -ForegroundColor Red
  } finally {
    try { $res.Close() } catch {}
  }
}
