<template>
  <div class="page" v-if="project">
    <div class="page-panel detail-panel">
      <div class="detail-hero" :style="coverStyle">
        <div class="detail-hero-mask">
          <h1>{{ project.title }}</h1>
          <p>{{ project.summary }}</p>
          <div class="detail-meta">
            <span class="meta-author" :title="project.author?.display_name">
              <AppIcon name="user" :size="15" />
              <span>{{ project.author?.display_name }}</span>
            </span>
            <MetaStat icon="eye" :value="project.view_count" :label="t('project.views')" />
            <MetaStat icon="heart" :value="project.like_count" :label="t('project.likes')" :filled="!!project.liked" />
            <MetaStat icon="star" :value="project.favorite_count" :label="t('project.favorites')" :filled="!!project.favorited" />
            <MetaStat icon="flame" :value="project.popularity" :label="t('project.popularity')" />
            <MetaStat icon="comment" :value="project.comment_count" :label="t('project.comments')" />
          </div>
          <div class="detail-actions">
            <button
              type="button"
              class="icon-action"
              :class="{ active: project.liked, primary: true }"
              :title="project.liked ? t('project.unlike') : t('project.like')"
              :aria-label="project.liked ? t('project.unlike') : t('project.like')"
              @click="toggleLike"
            >
              <AppIcon name="heart" :size="18" :filled="!!project.liked" />
            </button>
            <button
              type="button"
              class="icon-action"
              :class="{ active: project.favorited }"
              :title="project.favorited ? t('project.unfavorite') : t('project.favorite')"
              :aria-label="project.favorited ? t('project.unfavorite') : t('project.favorite')"
              @click="toggleFavorite"
            >
              <AppIcon name="star" :size="18" :filled="!!project.favorited" />
            </button>
            <a
              v-if="project.site_url"
              class="icon-action"
              :href="project.site_url"
              target="_blank"
              rel="noopener"
              :title="t('project.openSite')"
              :aria-label="t('project.openSite')"
            >
              <AppIcon name="link" :size="18" />
            </a>
            <button
              v-if="canEdit"
              type="button"
              class="icon-action"
              :title="t('common.edit')"
              :aria-label="t('common.edit')"
              @click="$router.push({ name: 'project-edit', params: { id: project.id } })"
            >
              <AppIcon name="edit" :size="18" />
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="icon-action danger"
              :title="t('common.delete')"
              :aria-label="t('common.delete')"
              @click="onDelete"
            >
              <AppIcon name="trash" :size="18" />
            </button>
          </div>
        </div>
      </div>
      <div class="detail-body">
        <div class="tags" v-if="project.tags?.length">
          <span v-for="tag in project.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
        <RichHtml class="description" :html="project.description || ''" mode="full" />

        <section class="comments">
          <h3>{{ t('project.comments') }} ({{ project.comment_count }})</h3>

          <!-- 顶层发表评论（非回复时） -->
          <div v-if="userStore.isLogin && !replyTarget" class="comment-form">
            <RichEditor
              v-model="commentText"
              mode="simple"
              height="140px"
              :placeholder="t('project.writeComment')"
            />
            <div class="comment-form-actions">
              <tiny-button type="primary" :loading="commenting" @click="submitComment">
                {{ t('project.submitComment') }}
              </tiny-button>
            </div>
          </div>

          <div v-if="!comments.length" class="empty-state" style="padding:24px 0">{{ t('project.noComments') }}</div>
          <CommentItem
            v-for="c in comments"
            :key="c.id"
            :comment="c"
            :reply-target-id="replyTarget?.id"
            v-model:reply-text="commentText"
            :commenting="commenting"
            @reply="onReply"
            @cancel-reply="cancelReply"
            @submit-reply="submitComment"
          />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import {
  createComment,
  deleteProject,
  favoriteProject,
  fetchComments,
  fetchProject,
  likeProject,
  unfavoriteProject,
  unlikeProject,
} from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import CommentItem from '@/components/CommentItem.vue'
import MetaStat from '@/components/MetaStat.vue'
import RichEditor from '@/components/RichEditor.vue'
import RichHtml from '@/components/RichHtml.vue'
import { useUserStore } from '@/stores/user'
import { isEmptyHtml } from '@/utils/html'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const project = ref(null)
const comments = ref([])
const commentText = ref('')
const commenting = ref(false)
const replyTarget = ref(null)

const coverStyle = computed(() => {
  if (project.value?.cover_url) {
    return { backgroundImage: `url(${project.value.cover_url})` }
  }
  return {}
})

const canEdit = computed(() => {
  if (!userStore.isLogin || !project.value) return false
  return (
    userStore.hasPerm('project:manage') ||
    (userStore.hasPerm('project:update') && project.value.author?.id === userStore.user?.id)
  )
})

function ensureLogin() {
  if (userStore.isLogin) return true
  router.push({ name: 'login', query: { redirect: route.fullPath } })
  return false
}

async function load() {
  const id = route.params.id
  const res = await fetchProject(id)
  project.value = res.data
  await loadComments()
}

async function loadComments() {
  const c = await fetchComments(route.params.id)
  comments.value = c.data.items || []
}

async function toggleLike() {
  if (!ensureLogin()) return
  try {
    if (project.value.liked) {
      const res = await unlikeProject(project.value.id)
      project.value.liked = false
      project.value.like_count = res.data.like_count
    } else {
      const res = await likeProject(project.value.id)
      project.value.liked = true
      project.value.like_count = res.data.like_count
    }
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

async function toggleFavorite() {
  if (!ensureLogin()) return
  try {
    if (project.value.favorited) {
      const res = await unfavoriteProject(project.value.id)
      project.value.favorited = false
      project.value.favorite_count = res.data.favorite_count
    } else {
      const res = await favoriteProject(project.value.id)
      project.value.favorited = true
      project.value.favorite_count = res.data.favorite_count
    }
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

async function onReply(comment) {
  if (!ensureLogin()) return
  replyTarget.value = comment
  commentText.value = ''
  await nextTick()
  document.querySelector('.inline-reply')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

function cancelReply() {
  replyTarget.value = null
  commentText.value = ''
}

function insertCommentIntoTree(list, parentId, node) {
  for (const item of list) {
    if (item.id === parentId) {
      item.children = item.children || []
      item.children.push(node)
      return true
    }
    if (item.children?.length && insertCommentIntoTree(item.children, parentId, node)) {
      return true
    }
  }
  return false
}

async function submitComment() {
  if (!ensureLogin() || isEmptyHtml(commentText.value)) return
  commenting.value = true
  try {
    const res = await createComment(project.value.id, {
      content: commentText.value.trim(),
      parent_id: replyTarget.value?.id || null,
    })
    const node = { ...res.data, children: [] }
    if (replyTarget.value?.id) {
      if (!insertCommentIntoTree(comments.value, replyTarget.value.id, node)) {
        await loadComments()
      }
    } else {
      comments.value.unshift(node)
    }
    project.value.comment_count += 1
    commentText.value = ''
    replyTarget.value = null
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  } finally {
    commenting.value = false
  }
}

async function onDelete() {
  Modal.confirm(t('project.deleteConfirm')).then(async () => {
    await deleteProject(project.value.id)
    Modal.message({ message: t('common.success'), status: 'success' })
    router.replace({ name: 'plaza' })
  })
}

onMounted(load)
</script>

<style scoped>
.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.comment-form {
  margin-bottom: 8px;
}

.comment-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.description {
  margin-top: 14px;
  min-height: 24px;
  overflow-x: auto;
}

.icon-action {
  width: 40px;
  height: 40px;
  display: inline-grid;
  place-items: center;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: color-mix(in srgb, var(--bg-elevated) 88%, transparent);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  text-decoration: none;
}

.icon-action:hover {
  color: var(--text);
  background: var(--bg-muted);
  border-color: color-mix(in srgb, var(--primary) 30%, var(--border));
}

.icon-action.active,
.icon-action.primary.active {
  color: var(--primary);
  background: var(--primary-soft);
  border-color: color-mix(in srgb, var(--primary) 40%, var(--border));
}

.icon-action.danger:hover {
  color: var(--danger);
  border-color: color-mix(in srgb, var(--danger) 40%, var(--border));
  background: color-mix(in srgb, var(--danger) 10%, var(--bg-elevated));
}
</style>
