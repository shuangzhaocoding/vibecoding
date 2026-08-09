<template>
  <div class="page page-wide">
    <div class="page-toolbar">
      <h2 class="page-title icon-text">
        <AppIcon name="ranking" :size="20" />
        {{ t('project.rankingTitle') }}
      </h2>
      <span class="ranking-hint">{{ t('project.rankingTop', { n: 100 }) }}</span>
    </div>
    <div v-if="loading" class="empty-state">{{ t('common.loading') }}</div>
    <div v-else-if="!items.length" class="empty-state">
      <AppIcon name="inbox" :size="36" />
      <span>{{ t('project.empty') }}</span>
    </div>
    <div v-else class="project-grid">
      <ProjectCard v-for="p in items" :key="p.id" :project="p" :rank="p.rank" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchRanking } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import ProjectCard from '@/components/ProjectCard.vue'

const { t } = useI18n()
const items = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await fetchRanking({ limit: 100 })
    items.value = res.data || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  margin: 0;
}

.ranking-hint {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
