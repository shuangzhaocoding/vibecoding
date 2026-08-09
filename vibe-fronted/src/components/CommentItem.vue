<template>
  <div class="comment-node">
    <div class="comment-card">
      <div class="comment-main">
        <div class="comment-avatar" :style="avatarStyle" :title="comment.user?.display_name">
          <span v-if="!comment.user?.avatar_url">{{ avatarLetter }}</span>
        </div>
        <div class="comment-body">
          <div class="comment-meta">
            <span class="author">{{ comment.user?.display_name }}</span>
            <span v-if="comment.reply_to" class="reply-to">
              {{ t('project.replyTo') }} @{{ comment.reply_to.display_name }}
            </span>
            <span class="time">{{ formatTime(comment.created_at) }}</span>
          </div>
          <RichHtml class="comment-content" :html="comment.content" mode="simple" />
          <div class="comment-actions">
            <button type="button" class="reply-btn" @click="$emit('reply', comment)">
              <AppIcon name="reply" :size="14" />
              {{ t('project.reply') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isReplying" class="inline-reply">
      <div class="reply-bar">
        <span>{{ t('project.replyingTo') }} @{{ comment.user?.display_name }}</span>
      </div>
      <RichEditor
        :model-value="replyText"
        mode="simple"
        height="140px"
        :placeholder="t('project.writeComment')"
        @update:model-value="$emit('update:replyText', $event)"
      />
      <div class="reply-actions">
        <tiny-button @click="$emit('cancel-reply')">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="commenting" @click="$emit('submit-reply')">
          {{ t('project.reply') }}
        </tiny-button>
      </div>
    </div>

    <div
      v-if="comment.children?.length"
      class="comment-children"
      :class="{ nested: depth === 0 }"
    >
      <CommentItem
        v-for="child in comment.children"
        :key="child.id"
        :comment="child"
        :depth="depth + 1"
        :reply-target-id="replyTargetId"
        :reply-text="replyText"
        :commenting="commenting"
        @reply="$emit('reply', $event)"
        @cancel-reply="$emit('cancel-reply')"
        @submit-reply="$emit('submit-reply')"
        @update:reply-text="$emit('update:replyText', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import RichEditor from '@/components/RichEditor.vue'
import RichHtml from '@/components/RichHtml.vue'

const props = defineProps({
  comment: { type: Object, required: true },
  depth: { type: Number, default: 0 },
  replyTargetId: { type: [Number, String], default: null },
  replyText: { type: String, default: '' },
  commenting: { type: Boolean, default: false },
})

defineEmits(['reply', 'cancel-reply', 'submit-reply', 'update:replyText'])

const { t } = useI18n()
const isReplying = computed(() => props.replyTargetId === props.comment.id)

const avatarLetter = computed(() =>
  (props.comment.user?.display_name || props.comment.user?.username || '?').slice(0, 1).toUpperCase(),
)

const avatarStyle = computed(() => {
  const url = props.comment.user?.avatar_url
  if (url) return { backgroundImage: `url(${url})` }
  return {}
})

function formatTime(v) {
  if (!v) return ''
  return new Date(v).toLocaleString()
}
</script>

<script>
export default {
  name: 'CommentItem',
}
</script>

<style scoped>
.comment-node {
  margin-top: 12px;
}

.comment-card {
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: var(--bg-muted);
  border: 1px solid var(--border);
}

.comment-main {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
  background: var(--primary-soft);
  background-size: cover;
  background-position: center;
  border: 1px solid var(--border);
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.author {
  color: var(--text);
  font-weight: 600;
  font-size: 13px;
}

.reply-to {
  color: var(--primary);
}

.comment-actions {
  margin-top: 8px;
}

.reply-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 0;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}

.reply-btn:hover {
  text-decoration: underline;
}

/* 仅一级下的二级缩进；二级及以下左对齐 */
.comment-children.nested {
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid var(--border);
}

.comment-children:not(.nested) {
  margin-left: 0;
  padding-left: 0;
}

.inline-reply {
  margin-top: 10px;
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-elevated);
}

.reply-bar {
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 13px;
}

.reply-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .comment-children.nested {
    margin-left: 12px;
    padding-left: 8px;
  }

  .comment-avatar {
    width: 32px;
    height: 32px;
    font-size: 13px;
  }
}
</style>
