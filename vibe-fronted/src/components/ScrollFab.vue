<template>
  <div v-show="visible" class="scroll-fab" role="group" :aria-label="t('app.scrollNav')">
    <button type="button" class="scroll-fab-btn" :title="t('app.scrollTop')" @click="toTop">
      ↑
    </button>
    <button type="button" class="scroll-fab-btn" :title="t('app.scrollBottom')" @click="toBottom">
      ↓
    </button>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const visible = ref(false)

function getScrollTop() {
  return window.scrollY || document.documentElement.scrollTop || 0
}

function getScrollHeight() {
  return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)
}

function updateVisible() {
  const top = getScrollTop()
  const canScroll = getScrollHeight() > window.innerHeight + 240
  visible.value = canScroll && top > 120
}

function toTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function toBottom() {
  window.scrollTo({ top: getScrollHeight(), behavior: 'smooth' })
}

onMounted(() => {
  updateVisible()
  window.addEventListener('scroll', updateVisible, { passive: true })
  window.addEventListener('resize', updateVisible)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateVisible)
  window.removeEventListener('resize', updateVisible)
})
</script>

<style scoped>
.scroll-fab {
  position: fixed;
  right: 18px;
  bottom: 24px;
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scroll-fab-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-elevated);
  color: var(--text);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}

.scroll-fab-btn:hover {
  background: var(--primary-soft);
  color: var(--primary);
}

.scroll-fab-btn:active {
  transform: scale(0.96);
}

@media (max-width: 768px) {
  .scroll-fab {
    right: 12px;
    bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  }

  .scroll-fab-btn {
    width: 38px;
    height: 38px;
  }
}
</style>
