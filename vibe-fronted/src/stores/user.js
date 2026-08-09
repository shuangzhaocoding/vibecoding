import { defineStore } from 'pinia'
import { loginApi, logoutApi, registerApi, switchRoleApi, updateProfileApi } from '@/api/auth'
import { isTokenExpired, msUntilExpire } from '@/utils/token'

const STORAGE_KEY = 'vibe_auth'

let expireTimer = null

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') || {}
  } catch {
    return {}
  }
}

function clearExpireTimer() {
  if (expireTimer != null) {
    clearTimeout(expireTimer)
    expireTimer = null
  }
}

export const useUserStore = defineStore('user', {
  state: () => {
    const saved = load()
    return {
      token: saved.token || '',
      user: saved.user || null,
      roles: saved.roles || [],
      currentRole: saved.currentRole || null,
      permissions: saved.permissions || [],
    }
  },
  getters: {
    isLogin: (s) => !!s.token && !isTokenExpired(s.token),
    hasPerm: (s) => (code) => s.permissions.includes(code),
  },
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          token: this.token,
          user: this.user,
          roles: this.roles,
          currentRole: this.currentRole,
          permissions: this.permissions,
        }),
      )
    },
    clearSession() {
      clearExpireTimer()
      this.token = ''
      this.user = null
      this.roles = []
      this.currentRole = null
      this.permissions = []
      localStorage.removeItem(STORAGE_KEY)
    },
    scheduleExpireRedirect() {
      clearExpireTimer()
      if (!this.token || isTokenExpired(this.token)) return
      const delay = msUntilExpire(this.token)
      const maxDelay = 2_147_483_647
      const wait = Math.min(delay, maxDelay)
      expireTimer = setTimeout(() => {
        if (!this.token) return
        if (isTokenExpired(this.token)) {
          this.forceLogin()
          return
        }
        this.scheduleExpireRedirect()
      }, wait)
    },
    async forceLogin(redirect) {
      this.clearSession()
      const { default: router } = await import('@/router')
      if (router.currentRoute.value.name === 'login') return
      const query = {}
      const path = redirect || router.currentRoute.value.fullPath
      if (path && path !== '/login') query.redirect = path
      router.replace({ name: 'login', query })
    },
    applyAuth(data) {
      this.token = data.access_token
      this.user = data.user
      this.roles = data.roles
      this.currentRole = data.current_role
      this.permissions = data.permissions || []
      this.persist()
      this.scheduleExpireRedirect()
    },
    async login(username, password) {
      const res = await loginApi({ username, password })
      this.applyAuth(res.data)
    },
    async register(payload) {
      const res = await registerApi(payload)
      this.applyAuth(res.data)
    },
    async switchRole(roleId) {
      const res = await switchRoleApi(roleId)
      this.applyAuth(res.data)
    },
    async updateProfile(payload) {
      const res = await updateProfileApi(payload)
      this.user = { ...(this.user || {}), ...res.data }
      this.persist()
      return res.data
    },
    async logout() {
      try {
        if (this.token && !isTokenExpired(this.token)) await logoutApi()
      } catch {
        /* ignore */
      }
      this.clearSession()
    },
  },
})
