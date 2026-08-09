import QRCode from 'qrcode'

const W = 720
const H = 1080
const PAD = 40
const FOOTER_H = 168

function roundRect(ctx, x, y, w, h, r) {
  const radius = Math.min(r, w / 2, h / 2)
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.arcTo(x + w, y, x + w, y + h, radius)
  ctx.arcTo(x + w, y + h, x, y + h, radius)
  ctx.arcTo(x, y + h, x, y, radius)
  ctx.arcTo(x, y, x + w, y, radius)
  ctx.closePath()
}

function wrapText(ctx, text, maxWidth, maxLines) {
  const chars = String(text || '')
  const lines = []
  let line = ''
  for (const ch of chars) {
    const next = line + ch
    if (ctx.measureText(next).width > maxWidth && line) {
      lines.push(line)
      line = ch
      if (lines.length >= maxLines) break
    } else {
      line = next
    }
  }
  if (lines.length < maxLines && line) lines.push(line)
  if (lines.length === maxLines) {
    const last = lines[maxLines - 1]
    if (ctx.measureText(last).width > maxWidth - 12 || chars.length > lines.join('').length) {
      let trimmed = last
      while (trimmed.length > 1 && ctx.measureText(`${trimmed}…`).width > maxWidth) {
        trimmed = trimmed.slice(0, -1)
      }
      lines[maxLines - 1] = `${trimmed}…`
    }
  }
  return lines
}

function loadImage(src) {
  return new Promise((resolve) => {
    if (!src) {
      resolve(null)
      return
    }
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = () => resolve(null)
    img.src = src
  })
}

function drawCoverPlaceholder(ctx, x, y, w, h, title) {
  const grad = ctx.createLinearGradient(x, y, x + w, y + h)
  grad.addColorStop(0, '#1d4ed8')
  grad.addColorStop(0.55, '#2563eb')
  grad.addColorStop(1, '#0f172a')
  ctx.fillStyle = grad
  ctx.fillRect(x, y, w, h)

  const letter = (title || 'V').trim().charAt(0).toUpperCase() || 'V'
  ctx.fillStyle = 'rgba(255,255,255,0.92)'
  ctx.font = '700 120px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(letter, x + w / 2, y + h / 2)
  ctx.textAlign = 'left'
  ctx.textBaseline = 'alphabetic'
}

function drawCover(ctx, img, x, y, w, h) {
  const iw = img.naturalWidth || img.width
  const ih = img.naturalHeight || img.height
  const scale = Math.max(w / iw, h / ih)
  const sw = w / scale
  const sh = h / scale
  const sx = (iw - sw) / 2
  const sy = (ih - sh) / 2
  ctx.drawImage(img, sx, sy, sw, sh, x, y, w, h)
}

/**
 * 生成作品分享海报（含底部二维码）。
 * @returns {Promise<{ dataUrl: string, blob: Blob }>}
 */
export async function createProjectShareCard(project, { url, labels = {} } = {}) {
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  // 背景
  ctx.fillStyle = '#f4f7fb'
  ctx.fillRect(0, 0, W, H)

  // 顶部品牌条
  const headerGrad = ctx.createLinearGradient(0, 0, W, 0)
  headerGrad.addColorStop(0, '#1d4ed8')
  headerGrad.addColorStop(1, '#2563eb')
  ctx.fillStyle = headerGrad
  ctx.fillRect(0, 0, W, 88)
  ctx.fillStyle = '#ffffff'
  ctx.font = '700 34px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.fillText('VibeCoding', PAD, 42)
  ctx.font = '500 16px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.82)'
  const slogan = labels.slogan || 'Discover AI projects'
  const sloganLines = wrapText(ctx, slogan, W - PAD * 2, 1)
  ctx.fillText(sloganLines[0] || slogan, PAD, 70)

  // 封面卡片
  const coverX = PAD
  const coverY = 118
  const coverW = W - PAD * 2
  const coverH = 360
  ctx.save()
  roundRect(ctx, coverX, coverY, coverW, coverH, 18)
  ctx.clip()
  const cover = await loadImage(project?.cover_url)
  if (cover) {
    drawCover(ctx, cover, coverX, coverY, coverW, coverH)
  } else {
    drawCoverPlaceholder(ctx, coverX, coverY, coverW, coverH, project?.title)
  }
  ctx.restore()

  // 轻微阴影底
  ctx.fillStyle = 'rgba(15, 23, 42, 0.06)'
  roundRect(ctx, coverX + 6, coverY + coverH - 2, coverW - 12, 14, 8)
  ctx.fill()

  // 标题 / 简介
  let ty = coverY + coverH + 36
  ctx.fillStyle = '#0f172a'
  ctx.font = '700 40px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  const titleLines = wrapText(ctx, project?.title || 'Untitled', coverW, 2)
  for (const line of titleLines) {
    ctx.fillText(line, PAD, ty)
    ty += 48
  }

  ty += 8
  ctx.fillStyle = '#475569'
  ctx.font = '400 24px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  const summary = (project?.summary || labels.defaultSummary || '').trim()
  const summaryLines = wrapText(ctx, summary, coverW, 3)
  for (const line of summaryLines) {
    ctx.fillText(line, PAD, ty)
    ty += 34
  }

  ty += 18
  const author = project?.author?.display_name || project?.author?.username || ''
  if (author) {
    ctx.fillStyle = '#2563eb'
    ctx.font = '600 22px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.fillText(`${labels.authorPrefix || 'By'} ${author}`, PAD, ty)
  }

  // 底部条
  const footerY = H - FOOTER_H
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, footerY, W, FOOTER_H)
  ctx.fillStyle = '#e2e8f0'
  ctx.fillRect(0, footerY, W, 1)

  const qrSize = 120
  const qrDataUrl = await QRCode.toDataURL(url, {
    margin: 1,
    width: qrSize * 2,
    color: { dark: '#0f172a', light: '#ffffff' },
    errorCorrectionLevel: 'M',
  })
  const qrImg = await loadImage(qrDataUrl)
  const qrX = W - PAD - qrSize
  const qrY = footerY + (FOOTER_H - qrSize) / 2
  if (qrImg) {
    ctx.drawImage(qrImg, qrX, qrY, qrSize, qrSize)
  }

  ctx.fillStyle = '#0f172a'
  ctx.font = '700 26px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.fillText(labels.scanTitle || 'Scan to view', PAD, footerY + 64)
  ctx.fillStyle = '#64748b'
  ctx.font = '400 20px "Source Sans 3", "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.fillText(labels.scanHint || 'Open in VibeCoding', PAD, footerY + 100)

  const dataUrl = canvas.toDataURL('image/png')
  const blob = await new Promise((resolve) => canvas.toBlob((b) => resolve(b), 'image/png'))
  return { dataUrl, blob: blob || dataUrlToBlob(dataUrl) }
}

function dataUrlToBlob(dataUrl) {
  const [meta, body] = dataUrl.split(',')
  const mime = /data:(.*?);/.exec(meta)?.[1] || 'image/png'
  const bin = atob(body)
  const arr = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i += 1) arr[i] = bin.charCodeAt(i)
  return new Blob([arr], { type: mime })
}
