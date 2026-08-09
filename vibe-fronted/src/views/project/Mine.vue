<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('menu.mine') }}</h2>
        <tiny-button v-if="userStore.hasPerm('project:create')" type="primary" @click="$router.push({ name: 'project-create' })">
          <span class="icon-text"><AppIcon name="plus" :size="15" />{{ t('menu.publish') }}</span>
        </tiny-button>
      </div>
      <div v-if="!items.length" class="empty-state">
        <AppIcon name="inbox" :size="36" />
        <span>{{ t('project.empty') }}</span>
      </div>
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
import AppIcon from '@/components/AppIcon.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()
const items = ref([])

onMounted(async () => {
  const res = await fetchProjects({ mine: true, page_size: 50 })
  items.value = res.data.items
})
</script>
