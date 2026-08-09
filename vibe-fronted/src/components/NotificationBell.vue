<template>
  <div ref="rootRef" class="notif-bell">
    <button
      type="button"
      class="icon-btn notif-trigger"
      :title="t('notify.title')"
      :aria-expanded="open"
      @click="toggle"
    >
      <AppIcon name="bell" :size="18" />
      <span v-if="unread > 0" class="notif-badge">{{ unread > 99 ? '99+' : unread }}</span>
    </button>
    <div v-show="open" class="notif-panel" role="menu">
      <div class="notif-head">
        <strong>{{ t('notify.title') }}</strong>
        <button v-if="unread > 0" type="button" class="notif-link" @click="onReadAll">
          {{ t('notify.readAll') }}
        </button>
      </div>
      <AppLoading v-if="loading" size="sm" inline />
      <div v-else-if="!items.length" class="notif-empty">{{ t('notify.empty') }}</div>
      <ul v-else class="notif-list">
        <li v-for="item in items" :key="item.id">
          <button
            type="button"
            class="notif-item"
            :class="{ unread: !item.is_read }"
            @click="onOpen(item)"
          >
            <div class="notif-item-title">{{ item.title }}</div>
            <div v-if="item.body" class="notif-item-body">
              <span v-if="item.actor">{{ item.actor.display_name }} · </span>{{ item.body }}
            </div>
            <div class="notif-item-time">{{ formatTime(item.created_at) }}</div>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  fetchNotifications,
  fetchUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
} from '@/api/user'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

const rootRef = ref(null)
const open = ref(false)
const loading = ref(false)
const items = ref([])
const unread = ref(0)
let pollTimer = null

async function refreshUnread() {
  if (!userStore.isLogin) {
    unread.value = 0
    return
  }
  try {
    const res = await fetchUnreadCount()
    unread.value = res.data?.count || 0
  } catch {
    /* ignore */
  }
}

async function loadList() {
  if (!userStore.isLogin) return
  loading.value = true
  try {
    const res = await fetchNotifications({ page: 1, page_size: 20 })
    items.value = res.data?.items || []
  } finally {
    loading.value = false
  }
}

async function toggle() {
  open.value = !open.value
  if (open.value) await loadList()
}

async function onReadAll() {
  await markAllNotificationsRead()
  unread.value = 0
  items.value = items.value.map((n) => ({ ...n, is_read: true }))
}

async function onOpen(item) {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      item.is_read = true
      unread.value = Math.max(0, unread.value - 1)
    } catch {
      /* ignore */
    }
  }
  open.value = false
  if (item.link) router.push(item.link)
}

function formatTime(v) {
  if (!v) return ''
  return new Date(v).toLocaleString()
}

function onDocClick(e) {
  if (rootRef.value && !rootRef.value.contains(e.target)) open.value = false
}

function startPoll() {
  stopPoll()
  if (!userStore.isLogin) return
  pollTimer = setInterval(refreshUnread, 60000)
}

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

watch(
  () => userStore.isLogin,
  (ok) => {
    if (ok) {
      refreshUnread()
      startPoll()
    } else {
      unread.value = 0
      items.value = []
      open.value = false
      stopPoll()
    }
  },
  { immediate: true },
)

onMounted(() => {
  document.addEventListener('click', onDocClick)
})
onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  stopPoll()
})
</script>

<style scoped>
.notif-bell {
  position: relative;
}

.notif-trigger {
  position: relative;
}

.notif-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--danger);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  line-height: 16px;
  text-align: center;
}

.notif-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: min(340px, 86vw);
  max-height: 420px;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--bg-elevated);
  box-shadow: var(--shadow-md);
  z-index: 70;
}

.notif-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--bg-elevated);
}

.notif-link {
  border: 0;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  font-size: 12px;
}

.notif-empty {
  padding: 28px 16px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
}

.notif-list {
  list-style: none;
  margin: 0;
  padding: 6px;
}

.notif-item {
  width: 100%;
  text-align: left;
  border: 0;
  background: transparent;
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  color: var(--text);
}

.notif-item:hover {
  background: var(--bg-muted);
}

.notif-item.unread {
  background: var(--primary-soft);
}

.notif-item-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
}

.notif-item-body {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-item-time {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
