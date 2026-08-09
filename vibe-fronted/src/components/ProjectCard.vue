<template>
  <router-link :to="{ name: 'project-detail', params: { id: project.id } }" class="project-card">
    <div class="cover" :style="coverStyle">
      <span v-if="rank" class="rank-badge" :class="{ top: rank <= 3 }">{{ rank }}</span>
      <span v-if="showStatus && project.status && project.status !== 'published'" class="status-badge">
        {{ statusLabel }}
      </span>
    </div>
    <div class="body">
      <h3 class="title">{{ project.title }}</h3>
      <p class="summary">{{ project.summary || '—' }}</p>
      <div class="meta">
        <button
          type="button"
          class="meta-author"
          :title="project.author?.display_name"
          @click.prevent.stop="goAuthor"
        >
          <AppIcon name="user" :size="14" />
          <span>{{ project.author?.display_name }}</span>
        </button>
        <MetaStat icon="heart" :value="project.like_count" :label="t('project.likes')" />
        <MetaStat icon="flame" :value="project.popularity" :label="t('project.popularity')" />
      </div>
      <div v-if="project.tags?.length" class="tags">
        <button
          v-for="tag in project.tags.slice(0, 3)"
          :key="tag"
          type="button"
          class="tag"
          @click.prevent.stop="goTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import MetaStat from '@/components/MetaStat.vue'

const props = defineProps({
  project: { type: Object, required: true },
  rank: { type: [Number, String], default: null },
  showStatus: { type: Boolean, default: false },
})
const { t } = useI18n()
const router = useRouter()

const coverStyle = computed(() => {
  if (props.project.cover_url) {
    return { backgroundImage: `url(${props.project.cover_url})` }
  }
  return {}
})

const statusLabel = computed(() => {
  const s = props.project.status
  if (s === 'draft') return t('project.draft')
  if (s === 'hidden') return t('project.hidden')
  return t('project.published')
})

function goTag(tag) {
  router.push({ name: 'plaza', query: { tag } })
}

function goAuthor() {
  const id = props.project.author?.id
  if (id) router.push({ name: 'author', params: { id } })
}
</script>

<style scoped>
.cover {
  position: relative;
}

.rank-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  min-width: 28px;
  height: 28px;
  padding: 0 8px;
  border-radius: 8px;
  display: inline-grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--bg-elevated) 88%, transparent);
  border: 1px solid var(--border);
  backdrop-filter: blur(6px);
}

.rank-badge.top {
  color: #fff;
  background: var(--primary);
  border-color: transparent;
}

.status-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  background: color-mix(in srgb, var(--bg-elevated) 90%, transparent);
  border: 1px solid var(--border);
  backdrop-filter: blur(6px);
}

.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 46%;
  min-width: 0;
  border: 0;
  background: transparent;
  padding: 0;
  color: inherit;
  cursor: pointer;
  font: inherit;
}

.meta-author:hover {
  color: var(--primary);
}

.meta-author span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag {
  border: 0;
  cursor: pointer;
  font: inherit;
}
</style>
