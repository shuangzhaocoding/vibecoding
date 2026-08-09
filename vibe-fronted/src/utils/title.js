const APP_NAME = 'VibeCoding'
const DEFAULT_DESC = '发现并分享有趣的 AI 作品'

function upsertMeta(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

export function setPageTitle(title) {
  if (!title) {
    document.title = APP_NAME
    return
  }
  document.title = `${title} · ${APP_NAME}`
}

/** 更新详情页 SEO / Open Graph meta（客户端；爬虫走 nginx→/api/og）。 */
export function setPageMeta({ title, description, image, url } = {}) {
  const pageTitle = title ? `${title} · ${APP_NAME}` : APP_NAME
  document.title = pageTitle
  const desc = (description || DEFAULT_DESC).trim().slice(0, 200)
  const pageUrl = url || (typeof window !== 'undefined' ? window.location.href : '')

  upsertMeta('name', 'description', desc)
  upsertMeta('property', 'og:type', 'website')
  upsertMeta('property', 'og:site_name', APP_NAME)
  upsertMeta('property', 'og:title', title || APP_NAME)
  upsertMeta('property', 'og:description', desc)
  if (pageUrl) upsertMeta('property', 'og:url', pageUrl)
  if (image) upsertMeta('property', 'og:image', image)
  upsertMeta('name', 'twitter:card', image ? 'summary_large_image' : 'summary')
  upsertMeta('name', 'twitter:title', title || APP_NAME)
  upsertMeta('name', 'twitter:description', desc)
  if (image) upsertMeta('name', 'twitter:image', image)
}
