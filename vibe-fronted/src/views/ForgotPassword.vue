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
      <h1>{{ t('auth.resetTitle') }}</h1>
      <p class="auth-desc">{{ t('auth.resetHint') }}</p>
      <tiny-form label-position="top" autocomplete="off" @submit.prevent>
        <tiny-form-item :label="t('auth.email')">
          <tiny-input
            v-model="form.email"
            name="reset-email"
            type="email"
            autocomplete="email"
            :placeholder="t('auth.emailPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.code')">
          <div class="code-row">
            <tiny-input
              v-model="form.code"
              name="reset-otp"
              autocomplete="one-time-code"
              inputmode="numeric"
              :placeholder="t('auth.codePlaceholder')"
            />
            <tiny-button :disabled="cooldown > 0 || sending" :reset-time="0" @click="onSendCode">
              <span v-if="cooldown > 0">{{ cooldown }}s</span>
              <span v-else class="icon-text"><AppIcon name="mail" :size="14" />{{ t('auth.sendCode') }}</span>
            </tiny-button>
          </div>
        </tiny-form-item>
        <tiny-form-item :label="t('auth.newPassword')">
          <tiny-input
            v-model="form.new_password"
            type="password"
            show-password
            name="reset-new-password"
            autocomplete="new-password"
            :placeholder="t('auth.newPasswordPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.confirmPassword')">
          <tiny-input
            v-model="form.confirm"
            type="password"
            show-password
            name="reset-confirm-password"
            autocomplete="new-password"
            :placeholder="t('auth.confirmPasswordPlaceholder')"
          />
        </tiny-form-item>
        <tiny-button type="primary" style="width:100%" :loading="loading" :reset-time="0" @click="onSubmit">
          <span class="icon-text"><AppIcon name="lock" :size="15" />{{ t('auth.resetPassword') }}</span>
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
import { nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { resetPasswordApi, sendResetCodeApi } from '@/api/auth'
import { localeOptions, setLocale } from '@/locales'
import AppIcon from '@/components/AppIcon.vue'
import AuthScene from '@/components/AuthScene.vue'
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
  if (sending.value || cooldown.value > 0) return
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
  if (loading.value) return
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

onMounted(async () => {
  const lastAccount = localStorage.getItem('vibe_last_account') || ''
  // 若上次登录用的是邮箱，预填到邮箱框；勿让浏览器填进验证码框
  if (lastAccount.includes('@')) {
    form.email = lastAccount
  }
  await nextTick()
  if (form.code && (form.code === lastAccount || form.code === form.email)) {
    form.code = ''
  }
  // 再清一次，覆盖部分浏览器延迟自动填充
  setTimeout(() => {
    if (form.code && (form.code === lastAccount || form.code === form.email || form.code.includes('@'))) {
      form.code = ''
    }
  }, 100)
})

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
