<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('menu.mine') }}</h2>
        <div class="toolbar-right">
          <tiny-select v-model="status" clearable :placeholder="t('project.statusAll')" style="width:130px" @change="onFilter">
            <tiny-option value="published" :label="t('project.published')" />
            <tiny-option value="draft" :label="t('project.draft')" />
            <tiny-option value="hidden" :label="t('project.hidden')" />
          </tiny-select>
          <tiny-button v-if="userStore.hasPerm('project:create')" type="primary" @click="$router.push({ name: 'project-create' })">
            <span class="icon-text"><AppIcon name="plus" :size="15" />{{ t('menu.publish') }}</span>
          </tiny-button>
        </div>
      </div>
      <AppLoading v-if="loading" />
      <div v-else-if="!items.length" class="empty-state">
        <AppIcon name="inbox" :size="36" />
        <span>{{ t('project.empty') }}</span>
      </div>
      <div v-else class="project-grid">
        <ProjectCard v-for="p in items" :key="p.id" :project="p" show-status />
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
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const status = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await fetchProjects({
      mine: true,
      page: page.value,
      page_size: pageSize,
      status: status.value || undefined,
      sort: 'newest',
    })
    items.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onFilter() {
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
