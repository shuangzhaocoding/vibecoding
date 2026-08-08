<template>
  <router-link :to="{ name: 'project-detail', params: { id: project.id } }" class="project-card">
    <div class="cover" :style="coverStyle">
      <span v-if="rank" class="rank-badge" :class="{ top: rank <= 3 }">{{ rank }}</span>
    </div>
    <div class="body">
      <h3 class="title">{{ project.title }}</h3>
      <p class="summary">{{ project.summary || '—' }}</p>
      <div class="meta">
        <span class="meta-author" :title="project.author?.display_name">
          <AppIcon name="user" :size="14" />
          <span>{{ project.author?.display_name }}</span>
        </span>
        <MetaStat icon="heart" :value="project.like_count" :label="t('project.likes')" />
        <MetaStat icon="flame" :value="project.popularity" :label="t('project.popularity')" />
      </div>
      <div v-if="project.tags?.length" class="tags">
        <span v-for="tag in project.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import MetaStat from '@/components/MetaStat.vue'

const props = defineProps({
  project: { type: Object, required: true },
  rank: { type: [Number, String], default: null },
})
const { t } = useI18n()

const coverStyle = computed(() => {
  if (props.project.cover_url) {
    return { backgroundImage: `url(${props.project.cover_url})` }
  }
  return {}
})
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

.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 46%;
  min-width: 0;
}

.meta-author span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
