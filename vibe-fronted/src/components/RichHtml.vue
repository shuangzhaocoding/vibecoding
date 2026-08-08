<template>
  <div class="rich-html" :class="`mode-${mode}`" v-html="safeHtml" />
</template>

<script setup>
import { computed } from 'vue'
import { renderContent } from '@/utils/html'

const props = defineProps({
  /** Markdown 或旧版 HTML */
  html: { type: String, default: '' },
  content: { type: String, default: '' },
  mode: { type: String, default: 'full' }, // full | simple
})

const safeHtml = computed(() => renderContent(props.content || props.html, props.mode))
</script>

<style scoped>
.rich-html {
  color: var(--text);
  line-height: 1.7;
  word-break: break-word;
}

.rich-html :deep(p) {
  margin: 0 0 0.75em;
}

.rich-html :deep(p:last-child) {
  margin-bottom: 0;
}

.rich-html :deep(ul),
.rich-html :deep(ol) {
  margin: 0.5em 0 0.75em;
  padding-left: 1.4em;
}

.rich-html :deep(a) {
  color: var(--primary);
}

.rich-html :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}

.rich-html :deep(h1),
.rich-html :deep(h2),
.rich-html :deep(h3),
.rich-html :deep(h4) {
  margin: 1em 0 0.5em;
  line-height: 1.35;
}

.rich-html :deep(pre) {
  overflow: auto;
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--bg-muted);
  border: 1px solid var(--border);
}

.rich-html :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}

.rich-html :deep(:not(pre) > code) {
  padding: 0.1em 0.35em;
  border-radius: 4px;
  background: var(--bg-muted);
}

.rich-html :deep(blockquote) {
  margin: 0.75em 0;
  padding: 0.25em 0 0.25em 12px;
  border-left: 3px solid var(--primary);
  color: var(--text-secondary);
}

.mode-simple {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
