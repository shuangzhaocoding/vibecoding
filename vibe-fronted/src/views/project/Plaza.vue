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
          {{ keyword.trim() ? t('project.searchResult') : t('project.allProjects') }}
        </h2>
        <router-link class="link-more" :to="{ name: 'ranking' }">
          <AppIcon name="ranking" :size="15" />
          {{ t('project.viewRanking') }}
        </router-link>
      </div>
      <div v-if="loading" class="empty-state">{{ t('common.loading') }}</div>
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
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchProjects } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import ProjectCard from '@/components/ProjectCard.vue'

const { t } = useI18n()
const keyword = ref('')
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

async function loadList() {
  loading.value = true
  try {
    const res = await fetchProjects({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value.trim() || undefined,
      sort: 'newest',
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadList()
}

function onPage(p) {
  page.value = p
  loadList()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadList)
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
