/** 解析 JWT payload（不校验签名，仅读本地 claims） */
export function parseJwtPayload(token) {
  if (!token || typeof token !== 'string') return null
  try {
    const part = token.split('.')[1]
    if (!part) return null
    const json = atob(part.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(json)
  } catch {
    return null
  }
}

/** token 是否已过期（提前 skewSeconds 秒视为过期） */
export function isTokenExpired(token, skewSeconds = 5) {
  const payload = parseJwtPayload(token)
  if (!payload || typeof payload.exp !== 'number') return true
  return payload.exp * 1000 <= Date.now() + skewSeconds * 1000
}

/** 距离过期的毫秒数，已过期返回 0 */
export function msUntilExpire(token) {
  const payload = parseJwtPayload(token)
  if (!payload || typeof payload.exp !== 'number') return 0
  return Math.max(0, payload.exp * 1000 - Date.now())
}

const AUTH_FORCE_LOGIN_CODES = new Set([
  'AUTH_MISSING_TOKEN',
  'AUTH_INVALID_TOKEN',
  'AUTH_USER_INACTIVE',
  'AUTH_ROLE_NOT_FOUND',
  'AUTH_ROLE_NOT_ASSIGNED',
  'AUTH_ERROR',
  'AUTH_NO_ROLES',
])

export function isAuthForceLoginCode(code) {
  return typeof code === 'string' && AUTH_FORCE_LOGIN_CODES.has(code)
}
