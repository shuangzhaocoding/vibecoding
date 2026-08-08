<template>
  <div class="page">
    <div class="page-panel">
      <h2 class="page-title">{{ t('menu.favorites') }}</h2>
      <div v-if="!items.length" class="empty-state">{{ t('project.empty') }}</div>
      <div v-else class="project-grid">
        <ProjectCard v-for="p in items" :key="p.id" :project="p" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchProjects } from '@/api/project'
import ProjectCard from '@/components/ProjectCard.vue'

const { t } = useI18n()
const items = ref([])

onMounted(async () => {
  const res = await fetchProjects({ favorites: true, page_size: 50 })
  items.value = res.data.items
})
</script>
