import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

const RICH_CONFIG = {
  USE_PROFILES: { html: true },
  ADD_ATTR: ['target', 'rel', 'class'],
}

const SIMPLE_CONFIG = {
  ALLOWED_TAGS: [
    'p', 'br', 'b', 'strong', 'i', 'em', 'u', 'a', 'ul', 'ol', 'li', 'span',
    'code', 'pre', 'blockquote', 'h1', 'h2', 'h3', 'h4',
  ],
  ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
}

export function sanitizeRichHtml(html) {
  return DOMPurify.sanitize(html || '', RICH_CONFIG)
}

export function sanitizeSimpleHtml(html) {
  return DOMPurify.sanitize(html || '', SIMPLE_CONFIG)
}

/** 兼容旧版 wangEditor 存的 HTML */
export function looksLikeHtml(content) {
  const s = String(content || '').trim()
  return /^<[a-z][\s\S]*>/i.test(s) && /<\/[a-z][a-z0-9]*>/i.test(s)
}

/** Markdown（或旧 HTML）→ 安全 HTML */
export function renderContent(content, mode = 'full') {
  const raw = String(content || '')
  if (!raw.trim()) return ''
  let html = raw
  if (!looksLikeHtml(raw)) {
    html = marked.parse(raw)
  }
  return mode === 'simple' ? sanitizeSimpleHtml(html) : sanitizeRichHtml(html)
}

export function isEmptyHtml(content) {
  if (!content) return true
  const text = String(content)
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]*\)/g, ' ')
    .replace(/\[[^\]]*]\([^)]*\)/g, ' ')
    .replace(/[#>*_\-~\[\]()]/g, ' ')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .trim()
  return !text
}

// 兼容旧命名
export const isEmptyContent = isEmptyHtml
