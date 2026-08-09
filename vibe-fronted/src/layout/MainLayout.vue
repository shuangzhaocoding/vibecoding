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
            <AppIcon :name="item.icon" :size="16" />
            {{ t(item.label) }}
          </router-link>
        </nav>
      </div>
      <div class="layout-actions desktop-actions">
        <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
          <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" :size="18" />
        </button>
        <tiny-select
          class="action-select action-select-locale"
          :model-value="locale"
          :options="localeOptions"
          @change="onLocaleChange"
        />
        <tiny-select
          v-if="userStore.isLogin && userStore.roles.length > 1"
          class="action-select action-select-role"
          :model-value="userStore.currentRole?.id"
          :options="roleOptions"
          @change="onRoleChange"
        />
        <NotificationBell v-if="userStore.isLogin" />
        <template v-if="userStore.isLogin">
          <div ref="userMenuRef" class="user-menu">
            <button
              type="button"
              class="user-chip"
              :aria-expanded="userMenuOpen"
              aria-haspopup="menu"
              @click="userMenuOpen = !userMenuOpen"
            >
              <span class="user-avatar" :style="userAvatarStyle">{{ userAvatarLetter }}</span>
              <span class="user-name">{{ userStore.user?.display_name }}</span>
              <span class="user-caret" :class="{ open: userMenuOpen }" />
            </button>
            <div v-show="userMenuOpen" class="user-menu-dropdown" role="menu">
              <router-link
                class="user-menu-item"
                role="menuitem"
                to="/center/profile"
                @click="userMenuOpen = false"
              >
                <AppIcon name="user" :size="15" />
                {{ t('menu.profile') }}
              </router-link>
              <button type="button" class="user-menu-item danger" role="menuitem" @click="onLogout">
                <AppIcon name="logout" :size="15" />
                {{ t('app.logout') }}
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <tiny-button type="primary" plain @click="router.push({ name: 'login' })">
            <span class="icon-text"><AppIcon name="user" :size="15" />{{ t('app.login') }}</span>
          </tiny-button>
          <tiny-button type="primary" @click="router.push({ name: 'register' })">
            <span class="icon-text"><AppIcon name="plus" :size="15" />{{ t('app.register') }}</span>
          </tiny-button>
        </template>
      </div>
      <div class="layout-actions mobile-actions">
        <button type="button" class="icon-btn" :title="t('app.theme')" @click="onToggleTheme">
          <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" :size="18" />
        </button>
        <NotificationBell v-if="userStore.isLogin" />
        <div v-if="userStore.isLogin" ref="mobileUserMenuRef" class="user-menu">
          <button
            type="button"
            class="user-chip user-chip-compact"
            :aria-expanded="mobileUserMenuOpen"
            aria-haspopup="menu"
            @click="mobileUserMenuOpen = !mobileUserMenuOpen"
          >
            <span class="user-avatar" :style="userAvatarStyle">{{ userAvatarLetter }}</span>
            <span class="user-caret" :class="{ open: mobileUserMenuOpen }" />
          </button>
          <div v-show="mobileUserMenuOpen" class="user-menu-dropdown" role="menu">
            <router-link
              class="user-menu-item"
              role="menuitem"
              to="/center/profile"
              @click="mobileUserMenuOpen = false"
            >
              <AppIcon name="user" :size="15" />
              {{ t('menu.profile') }}
            </router-link>
            <button type="button" class="user-menu-item danger" role="menuitem" @click="onLogout">
              <AppIcon name="logout" :size="15" />
              {{ t('app.logout') }}
            </button>
          </div>
        </div>
        <template v-else>
          <tiny-button type="primary" plain size="mini" @click="router.push({ name: 'login' })">
            <span class="icon-text"><AppIcon name="user" :size="14" />{{ t('app.login') }}</span>
          </tiny-button>
        </template>
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
          <AppIcon :name="item.icon" :size="16" />
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
      <div v-if="!userStore.isLogin" class="mobile-drawer-actions">
        <tiny-button type="primary" plain style="width:100%" @click="goAuth('login')">{{ t('app.login') }}</tiny-button>
        <tiny-button type="primary" style="width:100%" @click="goAuth('register')">{{ t('app.register') }}</tiny-button>
      </div>
    </aside>

    <div class="layout-body">
      <main class="layout-main full">
        <router-view />
      </main>
    </div>
    <SiteFooter v-if="!isCenter" />
    <ScrollFab />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import NotificationBell from '@/components/NotificationBell.vue'
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
const userMenuOpen = ref(false)
const mobileUserMenuOpen = ref(false)
const userMenuRef = ref(null)
const mobileUserMenuRef = ref(null)

const roleOptions = computed(() =>
  userStore.roles.map((r) => ({ value: r.id, label: r.name })),
)

const userAvatarLetter = computed(() =>
  (userStore.user?.display_name || userStore.user?.username || '?').slice(0, 1).toUpperCase(),
)

const userAvatarStyle = computed(() => {
  const url = userStore.user?.avatar_url
  if (url) return { backgroundImage: `url(${url})`, color: 'transparent' }
  return {}
})

const topMenus = [
  { to: '/', name: 'plaza', label: 'menu.home', icon: 'home' },
  { to: '/ranking', name: 'ranking', label: 'menu.ranking', icon: 'ranking' },
]

const isCenter = computed(() => route.path.startsWith('/center'))

function isTopActive(item) {
  if (item.name === 'plaza') return route.name === 'plaza'
  if (item.name === 'ranking') return route.name === 'ranking'
  return false
}

function onToggleTheme() {
  theme.value = toggleTheme()
}

async function onRoleChange(roleId) {
  menuOpen.value = false
  userMenuOpen.value = false
  mobileUserMenuOpen.value = false
  await userStore.switchRole(roleId)
  router.replace(resolveHomeRoute(userStore))
  window.location.reload()
}

function onLocaleChange(val) {
  setLocale(val)
}

async function onLogout() {
  menuOpen.value = false
  userMenuOpen.value = false
  mobileUserMenuOpen.value = false
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

function onDocClick(e) {
  const target = e.target
  if (userMenuRef.value && !userMenuRef.value.contains(target)) {
    userMenuOpen.value = false
  }
  if (mobileUserMenuRef.value && !mobileUserMenuRef.value.contains(target)) {
    mobileUserMenuOpen.value = false
  }
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    userMenuOpen.value = false
    mobileUserMenuOpen.value = false
  }
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
    userMenuOpen.value = false
    mobileUserMenuOpen.value = false
  },
)

onMounted(() => {
  window.addEventListener('resize', onResize)
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.user-menu {
  position: relative;
  margin-left: 2px;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 180px;
  padding: 4px 10px 4px 4px;
  border: 1px solid transparent;
  border-radius: 999px;
  color: var(--text-secondary);
  background: transparent;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.user-chip:hover,
.user-chip[aria-expanded='true'] {
  background: var(--bg-muted);
  color: var(--text);
  border-color: var(--border);
}

.user-chip-compact {
  max-width: none;
  padding: 3px 8px 3px 3px;
  gap: 6px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--primary);
  background: var(--primary-soft);
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  max-width: 110px;
}

.user-caret {
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid currentColor;
  opacity: 0.55;
  transition: transform 0.15s ease;
  flex-shrink: 0;
}

.user-caret.open {
  transform: rotate(180deg);
}

.user-menu-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 168px;
  padding: 6px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  box-shadow: var(--shadow-md);
  z-index: 60;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  text-align: left;
  padding: 9px 12px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--text);
  font-size: 13px;
  line-height: 1.3;
  cursor: pointer;
  transition: background 0.12s ease;
}

.user-menu-item:hover {
  background: var(--bg-muted);
}

.user-menu-item.danger {
  color: var(--danger);
  margin-top: 2px;
}
</style>
