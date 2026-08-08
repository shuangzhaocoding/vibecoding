<template>
  <div class="center-layout" :class="{ 'menu-open': menuOpen }">
    <div class="layout-mask" @click="menuOpen = false" />
    <button
      type="button"
      class="menu-toggle center-menu-toggle"
      :aria-label="t('app.menuToggle')"
      @click="menuOpen = !menuOpen"
    >
      <span class="menu-toggle-bar" />
      <span class="menu-toggle-bar" />
      <span class="menu-toggle-bar" />
    </button>
    <aside class="center-aside">
      <router-link
        v-for="item in menus"
        :key="item.to"
        :to="item.to"
        class="menu-item"
        :class="{ active: isMenuActive(item) }"
        @click="menuOpen = false"
      >
        {{ t(item.label) }}
      </router-link>
    </aside>
    <div class="center-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const route = useRoute()
const userStore = useUserStore()
const menuOpen = ref(false)

const menus = computed(() => {
  const list = [
    { to: '/center/mine', label: 'menu.mine' },
    { to: '/center/likes', label: 'menu.likes' },
    { to: '/center/favorites', label: 'menu.favorites' },
  ]
  if (userStore.hasPerm('project:create')) {
    list.push({ to: '/center/publish', label: 'menu.publish' })
  }
  if (userStore.hasPerm('system:user:view')) list.push({ to: '/center/users', label: 'menu.users' })
  if (userStore.hasPerm('system:role:view')) list.push({ to: '/center/roles', label: 'menu.roles' })
  if (userStore.hasPerm('system:perm:view')) list.push({ to: '/center/permissions', label: 'menu.permissions' })
  return list
})

function isMenuActive(item) {
  const path = route.path
  const matched = menus.value
    .filter((m) => path === m.to || path.startsWith(`${m.to}/`))
    .sort((a, b) => b.to.length - a.to.length)[0]
  return matched?.to === item.to
}

function onResize() {
  if (window.innerWidth > 768) menuOpen.value = false
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  },
)

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.center-menu-toggle {
  display: none;
  position: fixed;
  top: calc(var(--header-h) + 12px);
  right: 12px;
  left: auto;
  z-index: 45;
}

@media (max-width: 768px) {
  .center-menu-toggle {
    display: flex;
  }

  .center-content {
    padding-top: 8px;
  }
}
</style>
