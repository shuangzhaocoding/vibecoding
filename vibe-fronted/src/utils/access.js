/** 登录后默认回首页；个人中心入口单独走 /center */
export function resolveHomeRoute() {
  return { name: 'plaza' }
}

export function isNotFoundErrorCode(code) {
  if (!code || typeof code !== 'string') return false
  return code === 'NOT_FOUND' || code.endsWith('_NOT_FOUND')
}
