<template>
  <div class="md-editor-wrap" :class="`mode-${mode}`">
    <MdEditor
      v-model="inner"
      :theme="theme"
      :language="mdLang"
      :placeholder="placeholder"
      :preview="preview"
      :toolbars="toolbars"
      :footers="footers"
      :style="{ height }"
      @onChange="onChange"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getStoredTheme } from '@/utils/theme'

const props = defineProps({
  modelValue: { type: String, default: '' },
  mode: { type: String, default: 'full' }, // full | simple
  height: { type: String, default: '320px' },
  placeholder: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const { locale } = useI18n()
const inner = ref(props.modelValue || '')
const theme = ref(getStoredTheme() === 'dark' ? 'dark' : 'light')

const mdLang = computed(() => {
  if (locale.value === 'zh-CN') return 'zh-CN'
  return 'en-US'
})

const preview = computed(() => props.mode === 'full')

const toolbars = computed(() => {
  if (props.mode === 'simple') {
    return ['bold', 'italic', 'strikeThrough', 'link', 'unorderedList', 'orderedList', 'code', 'revoke', 'next']
  }
  return [
    'bold', 'underline', 'italic', 'strikeThrough', '-',
    'title', 'quote', 'unorderedList', 'orderedList', 'task', '-',
    'codeRow', 'code', 'link', 'image', 'table', '-',
    'revoke', 'next', '=', 'preview', 'catalog', 'pageFullscreen', 'fullscreen',
  ]
})

const footers = computed(() => (props.mode === 'simple' ? [] : ['markdownTotal', '=', 'scrollSwitch']))

watch(
  () => props.modelValue,
  (v) => {
    if (v !== inner.value) inner.value = v || ''
  },
)

function onChange(v) {
  emit('update:modelValue', v)
}

function syncTheme() {
  theme.value = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
}

const observer = new MutationObserver(syncTheme)
observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
onBeforeUnmount(() => observer.disconnect())
</script>

<style scoped>
.md-editor-wrap {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.md-editor-wrap.mode-full {
  min-height: 420px;
}

.md-editor-wrap :deep(.md-editor) {
  --md-bk-color: var(--bg-elevated);
  --md-color: var(--text);
  border: none;
}

.md-editor-wrap.mode-full :deep(.md-editor) {
  height: 100% !important;
  min-height: 420px;
}

/* 全屏时抬高层级，避免被布局/顶栏遮挡 */
.md-editor-wrap :deep(.md-editor-fullscreen),
.md-editor-wrap :deep(.md-editor-pageFullscreen) {
  z-index: 2000 !important;
}

.mode-simple :deep(.md-editor-toolbar-wrapper) {
  border-bottom: 1px solid var(--border);
}
</style>

