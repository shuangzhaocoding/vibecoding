<template>
  <div class="page">
    <div class="page-panel">
      <h2 class="page-title">{{ t('profile.title') }}</h2>

      <section class="profile-section">
        <h3 class="section-heading">{{ t('profile.basicInfo') }}</h3>
        <div class="avatar-row">
          <div class="avatar-preview" :style="avatarStyle">
            <span v-if="!form.avatar_url">{{ avatarLetter }}</span>
          </div>
          <div class="avatar-actions">
            <tiny-button :loading="uploading" @click="fileInput?.click()">
              {{ t('profile.uploadAvatar') }}
            </tiny-button>
            <tiny-button v-if="form.avatar_url" plain @click="clearAvatar">
              {{ t('profile.removeAvatar') }}
            </tiny-button>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="onAvatarFile" />
            <p class="hint">{{ t('profile.avatarHint') }}</p>
          </div>
        </div>

        <tiny-form label-width="100px" class="profile-form">
          <tiny-form-item :label="t('auth.username')">
            <tiny-input :model-value="userStore.user?.username" disabled />
            <p class="field-hint">{{ t('profile.usernameHint') }}</p>
          </tiny-form-item>
          <tiny-form-item :label="t('auth.email')">
            <tiny-input :model-value="userStore.user?.email" disabled />
          </tiny-form-item>
          <tiny-form-item :label="t('auth.displayName')" required>
            <tiny-input v-model="form.display_name" maxlength="128" />
            <p class="field-hint">{{ t('profile.displayNameHint') }}</p>
          </tiny-form-item>
          <tiny-form-item>
            <tiny-button type="primary" :loading="savingProfile" @click="saveProfile">
              {{ t('profile.saveProfile') }}
            </tiny-button>
          </tiny-form-item>
        </tiny-form>
      </section>

      <section class="profile-section">
        <h3 class="section-heading">{{ t('profile.changePassword') }}</h3>
        <tiny-form label-width="100px" class="profile-form">
          <tiny-form-item :label="t('profile.oldPassword')" required>
            <tiny-input v-model="pwd.old_password" type="password" show-password />
          </tiny-form-item>
          <tiny-form-item :label="t('profile.newPassword')" required>
            <tiny-input v-model="pwd.new_password" type="password" show-password />
          </tiny-form-item>
          <tiny-form-item :label="t('profile.confirmPassword')" required>
            <tiny-input v-model="pwd.confirm" type="password" show-password />
          </tiny-form-item>
          <tiny-form-item>
            <tiny-button type="primary" :loading="savingPwd" @click="savePassword">
              {{ t('profile.savePassword') }}
            </tiny-button>
          </tiny-form-item>
        </tiny-form>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Modal } from '@opentiny/vue'
import { changePasswordApi, uploadAvatarApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()
const fileInput = ref(null)
const uploading = ref(false)
const savingProfile = ref(false)
const savingPwd = ref(false)

const form = reactive({
  display_name: userStore.user?.display_name || '',
  avatar_url: userStore.user?.avatar_url || '',
})

const pwd = reactive({
  old_password: '',
  new_password: '',
  confirm: '',
})

const avatarLetter = computed(() => (form.display_name || userStore.user?.username || '?').slice(0, 1).toUpperCase())
const avatarStyle = computed(() => {
  if (form.avatar_url) {
    return { backgroundImage: `url(${form.avatar_url})` }
  }
  return {}
})

async function onAvatarFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const res = await uploadAvatarApi(file)
    form.avatar_url = res.data.url
    Modal.message({ message: t('common.success'), status: 'success' })
  } catch (err) {
    Modal.message({ message: err.message, status: 'error' })
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

function clearAvatar() {
  form.avatar_url = ''
}

async function saveProfile() {
  const name = form.display_name.trim()
  if (!name) {
    Modal.message({ message: t('profile.displayNameRequired'), status: 'warning' })
    return
  }
  savingProfile.value = true
  try {
    await userStore.updateProfile({
      display_name: name,
      avatar_url: form.avatar_url || '',
    })
    form.display_name = userStore.user.display_name
    form.avatar_url = userStore.user.avatar_url || ''
    Modal.message({ message: t('common.success'), status: 'success' })
  } catch (err) {
    Modal.message({ message: err.message, status: 'error' })
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  if (!pwd.old_password || !pwd.new_password) {
    Modal.message({ message: t('profile.passwordRequired'), status: 'warning' })
    return
  }
  if (pwd.new_password.length < 6) {
    Modal.message({ message: t('profile.passwordTooShort'), status: 'warning' })
    return
  }
  if (pwd.new_password !== pwd.confirm) {
    Modal.message({ message: t('profile.passwordMismatch'), status: 'warning' })
    return
  }
  savingPwd.value = true
  try {
    await changePasswordApi({
      old_password: pwd.old_password,
      new_password: pwd.new_password,
    })
    pwd.old_password = ''
    pwd.new_password = ''
    pwd.confirm = ''
    Modal.message({ message: t('profile.passwordChanged'), status: 'success' })
  } catch (err) {
    Modal.message({ message: err.message, status: 'error' })
  } finally {
    savingPwd.value = false
  }
}
</script>

<style scoped>
.profile-section + .profile-section {
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid var(--border);
}

.section-heading {
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 600;
}

.avatar-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
}

.avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  border: 1px solid var(--border);
  background-size: cover;
  background-position: center;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: 700;
  flex-shrink: 0;
}

.avatar-actions .hint,
.field-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.profile-form {
  max-width: 480px;
}

@media (max-width: 768px) {
  .avatar-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-form {
    max-width: none;
  }
}
</style>
