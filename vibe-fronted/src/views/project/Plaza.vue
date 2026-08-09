<template>
  <div class="page page-wide">
    <section class="home-search">
      <h1>{{ t('app.title') }}</h1>
      <p>{{ t('app.slogan') }}</p>
      <div class="search-box">
        <AppIcon class="search-box-icon" name="search" :size="20" />
        <tiny-input
          v-model="keyword"
          :placeholder="t('project.search')"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
        <button type="button" class="search-box-btn" @click="onSearch">
          <AppIcon name="search" :size="16" />
          {{ t('project.searchAction') }}
        </button>
      </div>
    </section>

    <section class="page-panel">
      <div class="page-toolbar">
        <h2 class="section-title">
          {{ activeTag || keyword.trim() ? t('project.searchResult') : t('project.allProjects') }}
        </h2>
        <div class="toolbar-right">
          <tiny-select v-model="sort" style="width:120px" @change="onSortChange">
            <tiny-option value="newest" :label="t('project.sortNewest')" />
            <tiny-option value="popular" :label="t('project.sortPopular')" />
            <tiny-option value="likes" :label="t('project.sortLikes')" />
          </tiny-select>
          <router-link class="link-more" :to="{ name: 'ranking' }">
            <AppIcon name="ranking" :size="15" />
            {{ t('project.viewRanking') }}
          </router-link>
        </div>
      </div>

      <div v-if="tags.length" class="tag-filter">
        <button
          type="button"
          class="tag-chip"
          :class="{ active: !activeTag }"
          @click="selectTag('')"
        >
          {{ t('project.allTags') }}
        </button>
        <button
          v-for="item in tags"
          :key="item.name"
          type="button"
          class="tag-chip"
          :class="{ active: activeTag === item.name }"
          @click="selectTag(item.name)"
        >
          {{ item.name }}
          <span class="tag-count">{{ item.count }}</span>
        </button>
      </div>

      <AppLoading v-if="loading" />
      <div v-else-if="!items.length" class="empty-state">
        <AppIcon name="inbox" :size="36" />
        <span>{{ t('project.empty') }}</span>
      </div>
      <div v-else class="project-grid">
        <ProjectCard v-for="p in items" :key="p.id" :project="p" />
      </div>
      <div v-if="total > 0" class="pager-wrap">
        <tiny-pager
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="onPage"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { fetchProjectTags, fetchProjects } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import { setPageTitle } from '@/utils/title'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const keyword = ref('')
const activeTag = ref('')
const sort = ref('newest')
const items = ref([])
const tags = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

async function loadTags() {
  try {
    const res = await fetchProjectTags({ limit: 30 })
    tags.value = res.data || []
  } catch {
    tags.value = []
  }
}

async function loadList() {
  loading.value = true
  try {
    const res = await fetchProjects({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value.trim() || undefined,
      tag: activeTag.value || undefined,
      sort: sort.value,
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function syncQuery() {
  const query = {}
  if (keyword.value.trim()) query.q = keyword.value.trim()
  if (activeTag.value) query.tag = activeTag.value
  if (sort.value && sort.value !== 'newest') query.sort = sort.value
  if (page.value > 1) query.page = String(page.value)
  router.replace({ query })
}

function applyRouteQuery() {
  keyword.value = typeof route.query.q === 'string' ? route.query.q : ''
  activeTag.value = typeof route.query.tag === 'string' ? route.query.tag : ''
  const s = typeof route.query.sort === 'string' ? route.query.sort : 'newest'
  sort.value = ['newest', 'popular', 'likes'].includes(s) ? s : 'newest'
  const p = Number(route.query.page || 1)
  page.value = Number.isFinite(p) && p > 0 ? p : 1
}

function onSearch() {
  page.value = 1
  syncQuery()
  loadList()
}

function selectTag(name) {
  activeTag.value = name
  page.value = 1
  syncQuery()
  loadList()
}

function onSortChange() {
  page.value = 1
  syncQuery()
  loadList()
}

function onPage(p) {
  page.value = p
  syncQuery()
  loadList()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

let ready = false

watch(
  () => route.query,
  () => {
    if (!ready) return
    applyRouteQuery()
    loadList()
  },
)

onMounted(async () => {
  setPageTitle('')
  applyRouteQuery()
  await Promise.all([loadTags(), loadList()])
  ready = true
})
</script>

<style scoped>
.link-more {
  color: var(--primary);
  font-size: 14px;
  font-weight: 500;
}

.section-title {
  margin: 0;
}

.search-box-icon {
  display: block;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tag-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 4px 0 18px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.tag-chip:hover {
  color: var(--text);
  border-color: color-mix(in srgb, var(--primary) 35%, var(--border));
}

.tag-chip.active {
  color: var(--primary);
  background: var(--primary-soft);
  border-color: color-mix(in srgb, var(--primary) 45%, var(--border));
  font-weight: 600;
}

.tag-count {
  font-size: 11px;
  opacity: 0.7;
}
</style>
