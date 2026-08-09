<template>
  <div class="page">
    <div class="page-panel">
      <h2 class="page-title">{{ t('menu.likes') }}</h2>
      <AppLoading v-if="loading" />
      <div v-else-if="!items.length" class="empty-state">
        <AppIcon name="heart" :size="36" />
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
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchProjects } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import ProjectCard from '@/components/ProjectCard.vue'

const { t } = useI18n()
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await fetchProjects({
      liked: true,
      page: page.value,
      page_size: pageSize,
      sort: 'newest',
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onPage(p) {
  page.value = p
  load()
}

onMounted(load)
</script>
