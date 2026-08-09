<template>
  <div class="auth-page">
    <AuthScene />
    <div class="auth-locale">
      <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
        <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" :size="18" />
      </button>
      <tiny-select :model-value="locale" :options="localeOptions" style="width:120px" @change="onLocaleChange" />
    </div>
    <div class="auth-card">
      <div class="auth-brand">{{ t('app.title') }}</div>
      <h1>{{ t('auth.loginTitle') }}</h1>
      <tiny-form label-position="top" @submit.prevent>
        <tiny-form-item :label="t('auth.account')">
          <tiny-input
            v-model="form.username"
            name="username"
            autocomplete="username"
            :placeholder="t('auth.accountPlaceholder')"
            @keyup.enter="onSubmit"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.password')">
          <tiny-input
            v-model="form.password"
            type="password"
            show-password
            name="password"
            autocomplete="current-password"
            :placeholder="t('auth.password')"
            @keyup.enter="onSubmit"
          />
        </tiny-form-item>
        <div class="auth-extra">
          <label class="remember-account">
            <input v-model="rememberAccount" type="checkbox" />
            <span>{{ t('auth.rememberAccount') }}</span>
          </label>
          <router-link :to="{ name: 'forgot-password' }">{{ t('auth.forgotPassword') }}</router-link>
        </div>
        <tiny-button type="primary" style="width:100%" :loading="loading" :reset-time="0" @click="onSubmit">
          <span class="icon-text"><AppIcon name="user" :size="15" />{{ t('auth.login') }}</span>
        </tiny-button>
      </tiny-form>
      <p class="auth-link">
        <router-link :to="{ name: 'register' }">{{ t('auth.toRegister') }}</router-link>
      </p>
      <p v-if="error" class="auth-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { localeOptions, setLocale } from '@/locales'
import { resolveHomeRoute } from '@/utils/access'
import AppIcon from '@/components/AppIcon.vue'
import AuthScene from '@/components/AuthScene.vue'
import { getStoredTheme, toggleTheme } from '@/utils/theme'

const LAST_ACCOUNT_KEY = 'vibe_last_account'
const REMEMBER_ACCOUNT_KEY = 'vibe_remember_account'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const theme = ref(getStoredTheme())

const form = reactive({ username: '', password: '' })
const rememberAccount = ref(true)
const loading = ref(false)
const error = ref('')

onMounted(() => {
  const remember = localStorage.getItem(REMEMBER_ACCOUNT_KEY)
  rememberAccount.value = remember !== '0'
  if (rememberAccount.value) {
    form.username = localStorage.getItem(LAST_ACCOUNT_KEY) || ''
  }
})

function onLocaleChange(val) {
  setLocale(val)
}

function onToggleTheme() {
  theme.value = toggleTheme()
}

async function onSubmit() {
  if (loading.value) return
  const account = form.username.trim()
  if (!account || !form.password) {
    error.value = t('auth.loginRequired')
    return
  }
  loading.value = true
  error.value = ''
  try {
    await userStore.login(account, form.password)
    localStorage.setItem(REMEMBER_ACCOUNT_KEY, rememberAccount.value ? '1' : '0')
    if (rememberAccount.value) {
      localStorage.setItem(LAST_ACCOUNT_KEY, account)
    } else {
      localStorage.removeItem(LAST_ACCOUNT_KEY)
    }
    const redirect = route.query.redirect
    if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')) {
      router.replace(redirect)
    } else {
      router.replace(resolveHomeRoute())
    }
  } catch (e) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin: -4px 0 14px;
  font-size: 13px;
}

.auth-extra a {
  color: var(--primary);
  flex-shrink: 0;
}

.auth-extra a:hover {
  text-decoration: underline;
}

.remember-account {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.remember-account input {
  margin: 0;
  cursor: pointer;
}
</style>
