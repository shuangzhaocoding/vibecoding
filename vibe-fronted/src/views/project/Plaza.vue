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
        />
        <button type="button" class="search-box-btn" @click="onSearch">
          {{ t('project.searchAction') }}
        </button>
      </div>
    </section>

    <section v-if="searching" class="page-panel">
      <div class="page-toolbar">
        <h2 class="section-title">{{ t('project.searchResult') }}</h2>
        <tiny-button plain @click="clearSearch">{{ t('common.reset') }}</tiny-button>
      </div>
      <div v-if="loading" class="empty-state">{{ t('common.loading') }}</div>
      <div v-else-if="!items.length" class="empty-state">{{ t('project.empty') }}</div>
      <div v-else class="project-grid">
        <ProjectCard v-for="p in items" :key="p.id" :project="p" />
      </div>
      <div class="pager-wrap">
        <tiny-pager
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="onPage"
        />
      </div>
    </section>

    <section v-else>
      <div class="page-toolbar">
        <h2 class="section-title">{{ t('project.popularSection') }}</h2>
        <router-link class="link-more" :to="{ name: 'ranking' }">{{ t('project.viewRanking') }}</router-link>
      </div>
      <div v-if="loadingPopular" class="empty-state">{{ t('common.loading') }}</div>
      <div v-else-if="!popular.length" class="empty-state">{{ t('project.empty') }}</div>
      <div v-else class="project-grid">
        <ProjectCard v-for="p in popular" :key="p.id" :project="p" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchProjects, fetchRanking } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import ProjectCard from '@/components/ProjectCard.vue'

const { t } = useI18n()
const keyword = ref('')
const searching = ref(false)
const items = ref([])
const popular = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)
const loadingPopular = ref(false)

async function loadPopular() {
  loadingPopular.value = true
  try {
    const res = await fetchRanking({ limit: 8 })
    popular.value = res.data || []
  } finally {
    loadingPopular.value = false
  }
}

async function loadSearch() {
  loading.value = true
  try {
    const res = await fetchProjects({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      sort: 'popular',
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (!keyword.value.trim()) {
    clearSearch()
    return
  }
  searching.value = true
  page.value = 1
  loadSearch()
}

function clearSearch() {
  searching.value = false
  keyword.value = ''
  items.value = []
}

function onPage(p) {
  page.value = p
  loadSearch()
}

onMounted(loadPopular)
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
</style>
