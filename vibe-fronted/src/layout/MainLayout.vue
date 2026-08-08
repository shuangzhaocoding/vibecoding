<template>
  <div class="layout" :class="{ 'header-menu-open': menuOpen }">
    <header class="layout-header">
      <div class="layout-header-left">
        <button
          type="button"
          class="menu-toggle header-menu-toggle"
          :aria-label="t('app.menuToggle')"
          @click="menuOpen = !menuOpen"
        >
          <span class="menu-toggle-bar" />
          <span class="menu-toggle-bar" />
          <span class="menu-toggle-bar" />
        </button>
        <router-link to="/" class="layout-brand" @click="menuOpen = false">
          <span class="brand-mark">VC</span>
          <span class="brand-text">{{ t('app.title') }}</span>
        </router-link>
        <nav class="top-nav desktop-nav">
          <router-link
            v-for="item in topMenus"
            :key="item.to"
            :to="item.to"
            class="top-nav-link"
            :class="{ active: isTopActive(item) }"
          >
            {{ t(item.label) }}
          </router-link>
        </nav>
      </div>
      <div class="layout-actions desktop-actions">
        <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
          {{ theme === 'dark' ? '☀' : '☾' }}
        </button>
        <template v-if="userStore.isLogin">
          <span class="user-name">{{ userStore.user?.display_name }}</span>
          <tiny-select
            v-if="userStore.roles.length > 1"
            class="action-select action-select-role"
            :model-value="userStore.currentRole?.id"
            :options="roleOptions"
            @change="onRoleChange"
          />
        </template>
        <tiny-select
          class="action-select action-select-locale"
          :model-value="locale"
          :options="localeOptions"
          @change="onLocaleChange"
        />
        <template v-if="userStore.isLogin">
          <tiny-button type="primary" plain @click="onLogout">{{ t('app.logout') }}</tiny-button>
        </template>
        <template v-else>
          <tiny-button type="primary" plain @click="router.push({ name: 'login' })">{{ t('app.login') }}</tiny-button>
          <tiny-button type="primary" @click="router.push({ name: 'register' })">{{ t('app.register') }}</tiny-button>
        </template>
      </div>
      <div class="layout-actions mobile-actions">
        <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
          {{ theme === 'dark' ? '☀' : '☾' }}
        </button>
      </div>
    </header>

    <div class="layout-mask header-mask" @click="menuOpen = false" />
    <aside class="mobile-drawer" :aria-hidden="!menuOpen">
      <nav class="mobile-drawer-nav">
        <router-link
          v-for="item in topMenus"
          :key="item.to"
          :to="item.to"
          class="mobile-drawer-link"
          :class="{ active: isTopActive(item) }"
          @click="menuOpen = false"
        >
          {{ t(item.label) }}
        </router-link>
      </nav>
      <div class="mobile-drawer-section">
        <div class="mobile-drawer-label">{{ t('app.language') }}</div>
        <tiny-select
          class="mobile-drawer-select"
          :model-value="locale"
          :options="localeOptions"
          @change="onLocaleChange"
        />
      </div>
      <div v-if="userStore.isLogin && userStore.roles.length > 1" class="mobile-drawer-section">
        <div class="mobile-drawer-label">{{ t('app.role') }}</div>
        <tiny-select
          class="mobile-drawer-select"
          :model-value="userStore.currentRole?.id"
          :options="roleOptions"
          @change="onRoleChange"
        />
      </div>
      <div class="mobile-drawer-actions">
        <template v-if="userStore.isLogin">
          <div class="mobile-user">{{ userStore.user?.display_name }}</div>
          <tiny-button type="primary" plain style="width:100%" @click="onLogout">{{ t('app.logout') }}</tiny-button>
        </template>
        <template v-else>
          <tiny-button type="primary" plain style="width:100%" @click="goAuth('login')">{{ t('app.login') }}</tiny-button>
          <tiny-button type="primary" style="width:100%" @click="goAuth('register')">{{ t('app.register') }}</tiny-button>
        </template>
      </div>
    </aside>

    <div class="layout-body">
      <main class="layout-main full">
        <router-view />
      </main>
    </div>
    <SiteFooter />
    <ScrollFab />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import ScrollFab from '@/components/ScrollFab.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import { useUserStore } from '@/stores/user'
import { localeOptions, setLocale } from '@/locales'
import { resolveHomeRoute } from '@/utils/access'
import { getStoredTheme, toggleTheme } from '@/utils/theme'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const theme = ref(getStoredTheme())
const menuOpen = ref(false)

const roleOptions = computed(() =>
  userStore.roles.map((r) => ({ value: r.id, label: r.name })),
)

const topMenus = [
  { to: '/', name: 'plaza', label: 'menu.home' },
  { to: '/ranking', name: 'ranking', label: 'menu.ranking' },
  { to: '/center', name: 'center', label: 'menu.center' },
]

function isTopActive(item) {
  if (item.name === 'plaza') return route.name === 'plaza'
  if (item.name === 'ranking') return route.name === 'ranking'
  if (item.name === 'center') return route.path.startsWith('/center')
  return false
}

function onToggleTheme() {
  theme.value = toggleTheme()
}

async function onRoleChange(roleId) {
  menuOpen.value = false
  await userStore.switchRole(roleId)
  router.replace(resolveHomeRoute(userStore))
  window.location.reload()
}

function onLocaleChange(val) {
  setLocale(val)
}

async function onLogout() {
  menuOpen.value = false
  await userStore.logout()
  router.push({ name: 'plaza' })
}

function goAuth(name) {
  menuOpen.value = false
  router.push({ name })
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
