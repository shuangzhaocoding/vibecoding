import axios from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import i18n from '@/locales'
import { isNotFoundErrorCode } from '@/utils/access'
import { isAuthForceLoginCode, isTokenExpired } from '@/utils/token'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

let forcingLogin = false

async function forceLoginFromRequest() {
  if (forcingLogin) return
  forcingLogin = true
  try {
    const user = useUserStore()
    const redirect = router.currentRoute.value.name === 'login'
      ? undefined
      : router.currentRoute.value.fullPath
    await user.forceLogin(redirect)
  } finally {
    forcingLogin = false
  }
}

request.interceptors.request.use((config) => {
  const user = useUserStore()
  if (user.token) {
    if (isTokenExpired(user.token)) {
      forceLoginFromRequest()
      return Promise.reject(new Error(i18n.global.t('error.AUTH_INVALID_TOKEN')))
    }
    config.headers.Authorization = `Bearer ${user.token}`
  }
  return config
})

function navigateIfNeeded(errCode, method) {
  const m = (method || 'get').toLowerCase()
  if (m !== 'get') return
  if (router.currentRoute.value.name === 'not-found' || router.currentRoute.value.name === 'forbidden') {
    return
  }
  if (isNotFoundErrorCode(errCode)) {
    router.replace({ name: 'not-found' })
    return
  }
  if (errCode === 'PERMISSION_DENIED') {
    router.replace({ name: 'forbidden' })
  }
}

request.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body.code !== 'undefined' && body.code !== 1200) {
      const errCode = body.detail?.error_code || body.message || 'BUSINESS_ERROR'
      if (isAuthForceLoginCode(errCode)) {
        forceLoginFromRequest()
      } else {
        navigateIfNeeded(errCode, res.config?.method)
      }
      const msg =
        i18n.global.t(`error.${errCode}`, i18n.global.t('error.BUSINESS_ERROR'))
      return Promise.reject(new Error(msg))
    }
    return body
  },
  (error) => {
    if (error.response?.status === 401) {
      forceLoginFromRequest()
    } else if (error.response?.status === 403) {
      navigateIfNeeded('PERMISSION_DENIED', error.config?.method)
    } else if (error.response?.status === 404) {
      navigateIfNeeded('NOT_FOUND', error.config?.method)
    }
    return Promise.reject(error)
  },
)

export default request
