<template>
  <div class="page page-wide">
    <AppLoading v-if="loading && !author" />
    <template v-else-if="author">
      <section class="author-hero page-panel">
        <div class="author-avatar" :style="avatarStyle">
          <span v-if="!author.avatar_url">{{ avatarLetter }}</span>
        </div>
        <div class="author-info">
          <h1>{{ author.display_name }}</h1>
          <p class="author-username">@{{ author.username }}</p>
          <div class="author-stats">
            <span><strong>{{ stats.project_count || 0 }}</strong>{{ t('author.projects') }}</span>
            <span><strong>{{ stats.like_count || 0 }}</strong>{{ t('project.likes') }}</span>
            <span><strong>{{ stats.favorite_count || 0 }}</strong>{{ t('project.favorites') }}</span>
            <span><strong>{{ stats.view_count || 0 }}</strong>{{ t('project.views') }}</span>
          </div>
        </div>
      </section>

      <section class="page-panel">
        <div class="page-toolbar">
          <h2 class="section-title">{{ t('author.works') }}</h2>
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
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { fetchAuthor } from '@/api/user'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import { setPageTitle } from '@/utils/title'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const author = ref(null)
const stats = ref({})
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)

const avatarLetter = computed(() =>
  (author.value?.display_name || author.value?.username || '?').slice(0, 1).toUpperCase(),
)

const avatarStyle = computed(() => {
  const url = author.value?.avatar_url
  if (url) return { backgroundImage: `url(${url})` }
  return {}
})

async function load() {
  loading.value = true
  try {
    const res = await fetchAuthor(route.params.id, {
      page: page.value,
      page_size: pageSize,
    })
    author.value = res.data.author
    stats.value = res.data.stats || {}
    items.value = res.data.items || []
    total.value = res.data.total || 0
    setPageTitle(author.value?.display_name)
  } catch (e) {
    if (String(e.message || '').includes('不存在') || e.message === 'USER_NOT_FOUND') {
      router.replace({ name: 'not-found' })
      return
    }
    author.value = null
  } finally {
    loading.value = false
  }
}

function onPage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(
  () => route.params.id,
  () => {
    page.value = 1
    load()
  },
)

onMounted(load)
</script>

<style scoped>
.author-hero {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 16px;
}

.author-avatar {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: 32px;
  font-weight: 700;
  color: var(--primary);
  background: var(--primary-soft);
  background-size: cover;
  background-position: center;
  border: 1px solid var(--border);
}

.author-info h1 {
  margin: 0 0 4px;
  font-size: 24px;
}

.author-username {
  margin: 0 0 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.author-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

.author-stats strong {
  color: var(--text);
  margin-right: 4px;
  font-weight: 700;
}

.section-title {
  margin: 0;
}

@media (max-width: 768px) {
  .author-hero {
    flex-direction: column;
    text-align: center;
  }

  .author-stats {
    justify-content: center;
  }
}
</style>
