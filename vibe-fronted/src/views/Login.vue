<template>
  <div class="auth-page">
    <div class="auth-locale">
      <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
        {{ theme === 'dark' ? '☀' : '☾' }}
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
            :placeholder="t('auth.accountPlaceholder')"
            @keyup.enter="onSubmit"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.password')">
          <tiny-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="t('auth.password')"
            @keyup.enter="onSubmit"
          />
        </tiny-form-item>
        <div class="auth-extra">
          <router-link :to="{ name: 'forgot-password' }">{{ t('auth.forgotPassword') }}</router-link>
        </div>
        <tiny-button type="primary" style="width:100%" :loading="loading" @click="onSubmit">
          {{ t('auth.login') }}
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
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { localeOptions, setLocale } from '@/locales'
import { resolveHomeRoute } from '@/utils/access'
import { getStoredTheme, toggleTheme } from '@/utils/theme'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const theme = ref(getStoredTheme())

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

function onLocaleChange(val) {
  setLocale(val)
}

function onToggleTheme() {
  theme.value = toggleTheme()
}

async function onSubmit() {
  loading.value = true
  error.value = ''
  try {
    await userStore.login(form.username, form.password)
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
  justify-content: flex-end;
  margin: -4px 0 14px;
  font-size: 13px;
}

.auth-extra a {
  color: var(--primary);
}

.auth-extra a:hover {
  text-decoration: underline;
}
</style>
