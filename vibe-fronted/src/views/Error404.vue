<template>
  <div class="page">
    <div class="page-panel error-page-card">
      <div class="error-code">404</div>
      <h2 class="page-title">{{ t('errorPage.notFoundTitle') }}</h2>
      <p class="error-desc">{{ t('errorPage.notFoundDesc') }}</p>
      <div class="error-actions">
        <tiny-button type="primary" @click="goHome">
          <span class="icon-text"><AppIcon name="home" :size="15" />{{ t('errorPage.backHome') }}</span>
        </tiny-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import { useUserStore } from '@/stores/user'
import { resolveHomeRoute } from '@/utils/access'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

function goHome() {
  router.replace(resolveHomeRoute(userStore))
}
</script>
