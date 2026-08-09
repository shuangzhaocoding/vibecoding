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
      <h1>{{ t('auth.resetTitle') }}</h1>
      <p class="auth-desc">{{ t('auth.resetHint') }}</p>
      <tiny-form label-position="top" @submit.prevent>
        <tiny-form-item :label="t('auth.email')">
          <tiny-input v-model="form.email" :placeholder="t('auth.emailPlaceholder')" />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.code')">
          <div class="code-row">
            <tiny-input v-model="form.code" :placeholder="t('auth.code')" />
            <tiny-button :disabled="cooldown > 0 || sending" @click="onSendCode">
              {{ cooldown > 0 ? `${cooldown}s` : t('auth.sendCode') }}
            </tiny-button>
          </div>
        </tiny-form-item>
        <tiny-form-item :label="t('auth.newPassword')">
          <tiny-input v-model="form.new_password" type="password" show-password />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.confirmPassword')">
          <tiny-input v-model="form.confirm" type="password" show-password />
        </tiny-form-item>
        <tiny-button type="primary" style="width:100%" :loading="loading" @click="onSubmit">
          {{ t('auth.resetPassword') }}
        </tiny-button>
      </tiny-form>
      <p class="auth-link">
        <router-link :to="{ name: 'login' }">{{ t('auth.toLogin') }}</router-link>
      </p>
      <p v-if="error" class="auth-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { onUnmounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { resetPasswordApi, sendResetCodeApi } from '@/api/auth'
import { localeOptions, setLocale } from '@/locales'
import { getStoredTheme, toggleTheme } from '@/utils/theme'

const { t, locale } = useI18n()
const router = useRouter()
const theme = ref(getStoredTheme())

const form = reactive({
  email: '',
  code: '',
  new_password: '',
  confirm: '',
})
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const cooldown = ref(0)
let timer = null

function onLocaleChange(val) {
  setLocale(val)
}

function onToggleTheme() {
  theme.value = toggleTheme()
}

function startCooldown() {
  cooldown.value = 60
  timer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function onSendCode() {
  if (!form.email.trim()) {
    error.value = t('auth.emailRequired')
    return
  }
  sending.value = true
  error.value = ''
  try {
    await sendResetCodeApi({ email: form.email.trim() })
    Modal.message({ message: t('auth.codeSent'), status: 'success' })
    startCooldown()
  } catch (e) {
    error.value = e.message || String(e)
  } finally {
    sending.value = false
  }
}

async function onSubmit() {
  if (!form.email.trim() || !form.code.trim() || !form.new_password) {
    error.value = t('auth.resetRequired')
    return
  }
  if (form.new_password.length < 6) {
    error.value = t('profile.passwordTooShort')
    return
  }
  if (form.new_password !== form.confirm) {
    error.value = t('profile.passwordMismatch')
    return
  }
  loading.value = true
  error.value = ''
  try {
    await resetPasswordApi({
      email: form.email.trim(),
      code: form.code.trim(),
      new_password: form.new_password,
    })
    Modal.message({ message: t('auth.resetSuccess'), status: 'success' })
    router.replace({ name: 'login' })
  } catch (e) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.auth-desc {
  margin: -8px 0 18px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.code-row .tiny-input {
  flex: 1;
}
</style>
