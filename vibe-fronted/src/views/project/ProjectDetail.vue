<template>
  <AppLoading v-if="pageLoading && !project" />
  <div class="page" v-else-if="project">
    <div class="page-panel detail-panel">
      <div class="detail-hero" :style="coverStyle">
        <div class="detail-hero-mask">
          <h1>{{ project.title }}</h1>
          <p>{{ project.summary }}</p>
          <div class="detail-meta">
            <button
              type="button"
              class="meta-author"
              :title="project.author?.display_name"
              @click="goAuthor"
            >
              <AppIcon name="user" :size="15" />
              <span>{{ project.author?.display_name }}</span>
            </button>
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
              type="button"
              class="icon-action"
              :title="t('project.share')"
              :aria-label="t('project.share')"
              @click="onShare"
            >
              <AppIcon name="share" :size="18" />
            </button>
            <button
              v-if="canReport"
              type="button"
              class="icon-action"
              :title="t('project.report')"
              :aria-label="t('project.report')"
              @click="openReport"
            >
              <AppIcon name="flag" :size="18" />
            </button>
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
          <button
            v-for="tag in project.tags"
            :key="tag"
            type="button"
            class="tag tag-btn"
            @click="goTag(tag)"
          >
            {{ tag }}
          </button>
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
                <span class="icon-text"><AppIcon name="comment" :size="15" />{{ t('project.submitComment') }}</span>
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
            :can-delete-comment="canDeleteComment"
            @reply="onReply"
            @delete="onDeleteComment"
            @cancel-reply="cancelReply"
            @submit-reply="submitComment"
          />
        </section>
      </div>
    </div>

    <tiny-dialog-box v-model:visible="showReport" :title="t('project.report')" width="440px" append-to-body>
      <tiny-form label-width="80px">
        <tiny-form-item :label="t('report.reason')">
          <tiny-select v-model="reportForm.reason" style="width:100%">
            <tiny-option
              v-for="r in reportReasons"
              :key="r"
              :label="t(`report.reasons.${r}`)"
              :value="r"
            />
          </tiny-select>
        </tiny-form-item>
        <tiny-form-item :label="t('report.detail')">
          <tiny-input
            v-model="reportForm.detail"
            type="textarea"
            :rows="3"
            :maxlength="500"
            :placeholder="t('report.detailPlaceholder')"
          />
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showReport = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="reporting" @click="submitReport">{{ t('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <tiny-dialog-box
      v-model:visible="showShare"
      :title="t('project.share')"
      width="420px"
      append-to-body
      class="share-dialog"
    >
      <div class="share-body">
        <AppLoading v-if="sharing" size="sm" inline />
        <img v-else-if="shareImageUrl" class="share-preview" :src="shareImageUrl" :alt="t('project.shareCard')" />
        <p class="share-hint">{{ t('project.shareHint') }}</p>
      </div>
      <template #footer>
        <tiny-button @click="copyShareLink">{{ t('project.copyLink') }}</tiny-button>
        <tiny-button :disabled="!shareImageUrl" @click="downloadShareImage">{{ t('project.saveImage') }}</tiny-button>
        <tiny-button type="primary" :disabled="!shareImageUrl" @click="nativeShareImage">
          {{ t('project.shareImage') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import {
  createComment,
  deleteComment,
  deleteProject,
  favoriteProject,
  fetchComments,
  fetchProject,
  likeProject,
  reportProject,
  unfavoriteProject,
  unlikeProject,
} from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'
import AppLoading from '@/components/AppLoading.vue'
import CommentItem from '@/components/CommentItem.vue'
import MetaStat from '@/components/MetaStat.vue'
import RichEditor from '@/components/RichEditor.vue'
import RichHtml from '@/components/RichHtml.vue'
import { useUserStore } from '@/stores/user'
import { isEmptyHtml } from '@/utils/html'
import { createProjectShareCard } from '@/utils/shareCard'
import { setPageMeta } from '@/utils/title'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const project = ref(null)
const pageLoading = ref(true)
const comments = ref([])
const commentText = ref('')
const commenting = ref(false)
const replyTarget = ref(null)
const showReport = ref(false)
const reporting = ref(false)
const reportReasons = ['spam', 'abuse', 'copyright', 'inappropriate', 'other']
const reportForm = reactive({ reason: 'spam', detail: '' })
const showShare = ref(false)
const sharing = ref(false)
const shareImageUrl = ref('')
const shareBlob = ref(null)

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

const canReport = computed(() => {
  if (!project.value) return false
  if (!userStore.isLogin) return true
  return project.value.author?.id !== userStore.user?.id
})

function canDeleteComment(comment) {
  if (!userStore.isLogin || !project.value || !comment) return false
  return (
    comment.user?.id === userStore.user?.id ||
    project.value.author?.id === userStore.user?.id ||
    userStore.hasPerm('project:manage')
  )
}

function goTag(tag) {
  router.push({ name: 'plaza', query: { tag } })
}

function goAuthor() {
  const id = project.value?.author?.id
  if (id) router.push({ name: 'author', params: { id } })
}

function ensureLogin() {
  if (userStore.isLogin) return true
  router.push({ name: 'login', query: { redirect: route.fullPath } })
  return false
}

async function load() {
  const id = route.params.id
  pageLoading.value = true
  try {
    const res = await fetchProject(id)
    project.value = res.data
    setPageMeta({
      title: project.value?.title,
      description: project.value?.summary,
      image: project.value?.cover_url,
      url: window.location.href,
    })
    await loadComments()
  } finally {
    pageLoading.value = false
  }
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  const input = document.createElement('input')
  input.value = text
  document.body.appendChild(input)
  input.select()
  document.execCommand('copy')
  document.body.removeChild(input)
}

async function onShare() {
  if (!project.value) return
  const url = window.location.href
  showShare.value = true
  sharing.value = true
  shareImageUrl.value = ''
  shareBlob.value = null
  try {
    const { dataUrl, blob } = await createProjectShareCard(project.value, {
      url,
      labels: {
        slogan: t('app.slogan'),
        authorPrefix: t('project.author'),
        defaultSummary: t('app.slogan'),
        scanTitle: t('project.shareScanTitle'),
        scanHint: t('project.shareScanHint'),
      },
    })
    shareImageUrl.value = dataUrl
    shareBlob.value = blob
    await copyText(url)
  } catch (e) {
    Modal.message({ message: e.message || t('project.shareFailed'), status: 'error' })
  } finally {
    sharing.value = false
  }
}

async function copyShareLink() {
  try {
    await copyText(window.location.href)
    Modal.message({ message: t('project.shareCopied'), status: 'success' })
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

function downloadShareImage() {
  if (!shareImageUrl.value || !project.value) return
  const a = document.createElement('a')
  a.href = shareImageUrl.value
  a.download = `vibecoding-${project.value.id}.png`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

async function nativeShareImage() {
  if (!shareBlob.value || !project.value) return
  const file = new File([shareBlob.value], `vibecoding-${project.value.id}.png`, {
    type: 'image/png',
  })
  const url = window.location.href
  try {
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({
        files: [file],
        title: project.value.title,
        text: project.value.summary || t('app.slogan'),
        url,
      })
      return
    }
    if (navigator.share) {
      await navigator.share({
        title: project.value.title,
        text: project.value.summary || t('app.slogan'),
        url,
      })
      return
    }
    downloadShareImage()
    Modal.message({ message: t('project.shareSavedFallback'), status: 'info' })
  } catch (e) {
    if (e?.name === 'AbortError') return
    Modal.message({ message: e.message || t('project.shareFailed'), status: 'error' })
  }
}

function openReport() {
  if (!ensureLogin()) return
  reportForm.reason = 'spam'
  reportForm.detail = ''
  showReport.value = true
}

async function submitReport() {
  if (!project.value) return
  reporting.value = true
  try {
    await reportProject(project.value.id, {
      reason: reportForm.reason,
      detail: reportForm.detail.trim(),
    })
    showReport.value = false
    Modal.message({ message: t('report.submitted'), status: 'success' })
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  } finally {
    reporting.value = false
  }
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

function removeCommentFromTree(list, id) {
  const idx = list.findIndex((item) => item.id === id)
  if (idx >= 0) {
    list.splice(idx, 1)
    return true
  }
  for (const item of list) {
    if (item.children?.length && removeCommentFromTree(item.children, id)) {
      return true
    }
  }
  return false
}

async function onDeleteComment(comment) {
  if (!ensureLogin() || !canDeleteComment(comment)) return
  Modal.confirm(t('project.deleteCommentConfirm')).then(async () => {
    try {
      const res = await deleteComment(project.value.id, comment.id)
      removeCommentFromTree(comments.value, comment.id)
      project.value.comment_count = res.data.comment_count
      if (replyTarget.value?.id === comment.id) cancelReply()
    } catch (e) {
      Modal.message({ message: e.message, status: 'error' })
    }
  })
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

watch(
  () => route.params.id,
  () => {
    load()
  },
)

onMounted(load)
</script>

<style scoped>
.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 5px;
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

.share-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.share-body :deep(.app-loading) {
  min-height: 220px;
}

.share-preview {
  width: min(100%, 300px);
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg-muted);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.share-hint {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.5;
}
</style>
