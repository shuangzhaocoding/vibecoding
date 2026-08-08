const STORAGE_KEY = 'vibe_theme'

export function getStoredTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark' || saved === 'light') return saved
  if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) return 'dark'
  return 'light'
}

export function applyTheme(theme) {
  const next = theme === 'dark' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', next)
  localStorage.setItem(STORAGE_KEY, next)
  return next
}

export function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || getStoredTheme()
  return applyTheme(current === 'dark' ? 'light' : 'dark')
}

export function initTheme() {
  return applyTheme(getStoredTheme())
}
