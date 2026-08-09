<template>
  <div class="auth-page">
    <AuthScene />
    <div class="auth-locale">
      <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
        {{ theme === 'dark' ? '☀' : '☾' }}
      </button>
      <tiny-select :model-value="locale" :options="localeOptions" style="width:120px" @change="onLocaleChange" />
    </div>
    <div class="auth-card">
      <div class="auth-brand">{{ t('app.title') }}</div>
      <h1>{{ t('auth.registerTitle') }}</h1>
      <tiny-form label-position="top" autocomplete="off" @submit.prevent>
        <tiny-form-item :label="t('auth.username')">
          <tiny-input
            v-model="form.username"
            name="register-username"
            autocomplete="username"
            :placeholder="t('auth.usernamePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.email')">
          <tiny-input
            v-model="form.email"
            name="register-email"
            type="email"
            autocomplete="email"
            :placeholder="t('auth.registerEmailPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.code')">
          <div class="code-row">
            <tiny-input
              v-model="form.code"
              name="register-otp"
              autocomplete="one-time-code"
              inputmode="numeric"
              :placeholder="t('auth.codePlaceholder')"
            />
            <tiny-button :disabled="cooldown > 0 || sending" :reset-time="0" @click="onSendCode">
              {{ cooldown > 0 ? `${cooldown}s` : t('auth.sendCode') }}
            </tiny-button>
          </div>
        </tiny-form-item>
        <tiny-form-item :label="t('auth.password')">
          <tiny-input
            v-model="form.password"
            type="password"
            show-password
            name="register-password"
            autocomplete="new-password"
            :placeholder="t('auth.passwordPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('auth.displayName')">
          <tiny-input
            v-model="form.display_name"
            name="register-display-name"
            autocomplete="nickname"
            :placeholder="t('auth.displayNamePlaceholder')"
          />
        </tiny-form-item>
        <tiny-button type="primary" style="width:100%" :loading="loading" :reset-time="0" @click="onSubmit">
          {{ t('auth.register') }}
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
import { sendCodeApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { localeOptions, setLocale } from '@/locales'
import { resolveHomeRoute } from '@/utils/access'
import AuthScene from '@/components/AuthScene.vue'
import { getStoredTheme, toggleTheme } from '@/utils/theme'

const { t, locale } = useI18n()
const router = useRouter()
const userStore = useUserStore()
const theme = ref(getStoredTheme())

const form = reactive({
  username: '',
  email: '',
  code: '',
  password: '',
  display_name: '',
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
  const email = form.email.trim()
  if (!email) {
    error.value = t('auth.emailRequired')
    return
  }
  sending.value = true
  error.value = ''
  try {
    await sendCodeApi({ email })
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
  if (!form.username.trim() || !form.email.trim() || !form.code.trim() || !form.password) {
    error.value = t('auth.registerRequired')
    return
  }
  loading.value = true
  error.value = ''
  try {
    await userStore.register({
      ...form,
      username: form.username.trim(),
      email: form.email.trim(),
      code: form.code.trim(),
      display_name: form.display_name.trim(),
    })
    localStorage.setItem('vibe_remember_account', '1')
    localStorage.setItem('vibe_last_account', form.username.trim())
    router.replace(resolveHomeRoute())
  } catch (e) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 避免从登录页跳转时，浏览器把账号误填进验证码框
  await nextTick()
  const lastAccount = localStorage.getItem('vibe_last_account') || ''
  if (form.code && (form.code === lastAccount || form.code === form.username)) {
    form.code = ''
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
