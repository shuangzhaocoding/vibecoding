<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title icon-text">
          <AppIcon name="dashboard" :size="20" />
          {{ t('menu.dashboard') }}
        </h2>
        <div class="toolbar-right">
          <tiny-select v-model="days" style="width:120px" @change="load">
            <tiny-option :value="7" :label="t('dashboard.days7')" />
            <tiny-option :value="30" :label="t('dashboard.days30')" />
            <tiny-option :value="90" :label="t('dashboard.days90')" />
          </tiny-select>
        </div>
      </div>

      <AppLoading v-if="loading" />

      <template v-else>
        <div class="stat-grid">
          <div v-for="card in overviewCards" :key="card.key" class="stat-card">
            <div class="stat-icon" :class="card.key">
              <AppIcon :name="card.icon" :size="18" />
            </div>
            <div class="stat-meta">
              <div class="stat-value">{{ formatNum(card.value) }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </div>

        <div class="dash-row">
          <section class="dash-block trend-block">
            <div class="block-head">
              <h3>{{ t('dashboard.trendTitle') }}</h3>
              <span class="period-chip">
                {{ t('dashboard.periodTotal', { n: period.total || 0 }) }}
              </span>
            </div>
            <div class="period-stats">
              <span><AppIcon name="heart" :size="14" />{{ period.likes || 0 }}</span>
              <span><AppIcon name="star" :size="14" />{{ period.favorites || 0 }}</span>
              <span><AppIcon name="comment" :size="14" />{{ period.comments || 0 }}</span>
            </div>
            <TrendChart v-if="trend.length" :series="trend" />
            <div v-else class="empty-mini">{{ t('dashboard.noTrend') }}</div>
          </section>

          <section class="dash-block status-block">
            <div class="block-head">
              <h3>{{ t('dashboard.statusTitle') }}</h3>
            </div>
            <div class="status-bars">
              <div v-for="s in statusBars" :key="s.key" class="status-row">
                <div class="status-label">
                  <span>{{ s.label }}</span>
                  <strong>{{ s.value }}</strong>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" :class="s.key" :style="{ width: s.pct + '%' }" />
                </div>
              </div>
            </div>
          </section>
        </div>

        <div class="dash-row">
          <section class="dash-block">
            <div class="block-head">
              <h3>{{ t('dashboard.topTitle') }}</h3>
            </div>
            <div v-if="!topProjects.length" class="empty-mini">{{ t('dashboard.noProjects') }}</div>
            <ul v-else class="top-list">
              <li v-for="(p, idx) in topProjects" :key="p.id">
                <button type="button" class="top-item" @click="goProject(p.id)">
                  <span class="rank">{{ idx + 1 }}</span>
                  <span class="cover" :style="coverStyle(p)" />
                  <span class="top-info">
                    <span class="top-title">{{ p.title }}</span>
                    <span class="top-meta">
                      <span>{{ t(`project.${p.status}`) }}</span>
                      <span><AppIcon name="eye" :size="13" />{{ p.view_count }}</span>
                      <span><AppIcon name="heart" :size="13" />{{ p.like_count }}</span>
                      <span><AppIcon name="flame" :size="13" />{{ p.popularity }}</span>
                    </span>
                  </span>
                </button>
              </li>
            </ul>
          </section>

          <section class="dash-block">
            <div class="block-head">
              <h3>{{ t('dashboard.recentTitle') }}</h3>
            </div>
            <div v-if="!recent.length" class="empty-mini">{{ t('dashboard.noRecent') }}</div>
            <ul v-else class="recent-list">
              <li v-for="(item, idx) in recent" :key="idx">
                <button type="button" class="recent-item" @click="goProject(item.project?.id)">
                  <span class="recent-kind" :class="item.kind">
                    <AppIcon :name="kindIcon(item.kind)" :size="14" />
                  </span>
                  <span class="recent-body">
                    <span class="recent-text">
                      <strong>{{ item.user?.display_name || '-' }}</strong>
                      {{ kindText(item.kind) }}
                      <em>{{ item.project?.title || '' }}</em>
                    </span>
                    <span class="recent-time">{{ formatTime(item.created_at) }}</span>
                  </span>
                </button>
              </li>
            </ul>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { fetchCreatorDashboard } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import TrendChart from '@/components/TrendChart.vue'

const { t } = useI18n()
const router = useRouter()
const loading = ref(true)
const days = ref(30)
const overview = ref({})
const period = ref({})
const trend = ref([])
const topProjects = ref([])
const recent = ref([])

const overviewCards = computed(() => [
  { key: 'views', icon: 'eye', label: t('project.views'), value: overview.value.view_count || 0 },
  { key: 'likes', icon: 'heart', label: t('project.likes'), value: overview.value.like_count || 0 },
  { key: 'favorites', icon: 'star', label: t('project.favorites'), value: overview.value.favorite_count || 0 },
  { key: 'comments', icon: 'comment', label: t('project.comments'), value: overview.value.comment_count || 0 },
  { key: 'projects', icon: 'publish', label: t('dashboard.projects'), value: overview.value.project_count || 0 },
  { key: 'popularity', icon: 'flame', label: t('project.popularity'), value: overview.value.popularity || 0 },
])

const statusBars = computed(() => {
  const total = Math.max(1, overview.value.project_count || 0)
  const rows = [
    { key: 'published', label: t('project.published'), value: overview.value.published_count || 0 },
    { key: 'draft', label: t('project.draft'), value: overview.value.draft_count || 0 },
    { key: 'hidden', label: t('project.hidden'), value: overview.value.hidden_count || 0 },
  ]
  return rows.map((r) => ({ ...r, pct: Math.round((r.value / total) * 100) }))
})

function formatNum(n) {
  const v = Number(n) || 0
  if (v >= 10000) return `${(v / 10000).toFixed(1)}w`
  if (v >= 1000) return `${(v / 1000).toFixed(1)}k`
  return String(v)
}

function coverStyle(p) {
  if (p?.cover_url) return { backgroundImage: `url(${p.cover_url})` }
  return {}
}

function kindIcon(kind) {
  if (kind === 'favorite') return 'star'
  if (kind === 'comment') return 'comment'
  return 'heart'
}

function kindText(kind) {
  if (kind === 'favorite') return t('dashboard.actedFavorite')
  if (kind === 'comment') return t('dashboard.actedComment')
  return t('dashboard.actedLike')
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return String(iso).slice(0, 16)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function goProject(id) {
  if (id) router.push({ name: 'project-detail', params: { id } })
}

async function load() {
  loading.value = true
  try {
    const res = await fetchCreatorDashboard({ days: days.value })
    overview.value = res.data.overview || {}
    period.value = res.data.period || {}
    trend.value = res.data.trend || []
    topProjects.value = res.data.top_projects || []
    recent.value = res.data.recent || []
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-elevated) 92%, var(--primary-soft)), var(--bg-elevated));
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: var(--primary);
  background: var(--primary-soft);
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.1;
  color: var(--text);
}

.stat-label {
  margin-top: 2px;
  font-size: 12px;
  color: var(--text-muted);
}

.dash-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 14px;
  margin-top: 14px;
}

.dash-block {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  background: var(--bg-elevated);
  min-height: 220px;
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.block-head h3 {
  margin: 0;
  font-size: 16px;
}

.period-chip {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-soft);
  padding: 4px 8px;
  border-radius: 999px;
}

.period-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.period-stats span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 8px;
}

.status-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 6px;
  color: var(--text-secondary);
}

.bar-track {
  height: 8px;
  border-radius: 999px;
  background: var(--bg-muted);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
  transition: width 0.35s ease;
}

.bar-fill.draft {
  background: #94a3b8;
}

.bar-fill.hidden {
  background: #f59e0b;
}

.top-list,
.recent-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.top-item,
.recent-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 0;
  background: transparent;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  color: inherit;
  font: inherit;
}

.top-item:hover,
.recent-item:hover {
  background: var(--bg-muted);
}

.rank {
  width: 22px;
  text-align: center;
  font-weight: 700;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.cover {
  width: 44px;
  height: 32px;
  border-radius: 6px;
  background:
    linear-gradient(135deg, var(--primary-soft), var(--bg-muted)),
    center / cover no-repeat;
  flex-shrink: 0;
}

.top-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.top-title {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.top-meta span {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.recent-kind {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
  flex-shrink: 0;
}

.recent-kind.favorite {
  color: #d97706;
  background: color-mix(in srgb, #f59e0b 16%, transparent);
}

.recent-kind.comment {
  color: #0d9488;
  background: color-mix(in srgb, #14b8a6 16%, transparent);
}

.recent-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.recent-text {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-text em {
  font-style: normal;
  color: var(--text);
}

.recent-time {
  font-size: 12px;
  color: var(--text-muted);
}

.empty-mini {
  padding: 28px 8px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 960px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dash-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
