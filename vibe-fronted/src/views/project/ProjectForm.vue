<template>
  <div class="page">
    <div class="page-panel">
      <h2 class="page-title">{{ isEdit ? t('project.edit') : t('project.publish') }}</h2>
      <tiny-form class="project-form" :label-width="formLabelWidth" :label-position="formLabelPosition">
        <tiny-form-item :label="t('project.title')" required>
          <tiny-input v-model="form.title" />
        </tiny-form-item>
        <tiny-form-item :label="t('project.cover')">
          <div class="cover-upload">
            <img v-if="form.cover_url" :src="form.cover_url" class="cover-preview" alt="cover" />
            <tiny-button :loading="uploading" @click="fileInput.click()">{{ t('project.uploadCover') }}</tiny-button>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="onFile" />
          </div>
        </tiny-form-item>
        <tiny-form-item :label="t('project.summary')">
          <tiny-input v-model="form.summary" />
        </tiny-form-item>
        <tiny-form-item :label="t('project.description')">
          <RichEditor
            v-model="form.description"
            mode="full"
            :height="editorHeight"
            :placeholder="t('project.description')"
          />
        </tiny-form-item>
        <tiny-form-item :label="t('project.siteUrl')">
          <tiny-input v-model="form.site_url" />
        </tiny-form-item>
        <tiny-form-item :label="t('project.tags')">
          <tiny-input v-model="tagsText" :placeholder="t('project.tagsHint')" />
        </tiny-form-item>
        <tiny-form-item :label="t('project.status')">
          <tiny-select v-model="form.status" style="width:200px">
            <tiny-option value="published" :label="t('enum.status.published')" />
            <tiny-option value="draft" :label="t('enum.status.draft')" />
            <tiny-option value="hidden" :label="t('enum.status.hidden')" />
          </tiny-select>
        </tiny-form-item>
        <tiny-form-item>
          <tiny-button @click="$router.back()">{{ t('common.cancel') }}</tiny-button>
          <tiny-button type="primary" :loading="saving" @click="onSave">{{ t('common.save') }}</tiny-button>
        </tiny-form-item>
      </tiny-form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { createProject, fetchProject, updateProject, uploadFile } from '@/api/project'
import RichEditor from '@/components/RichEditor.vue'
import { isEmptyHtml } from '@/utils/html'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id && route.name === 'project-edit')
const saving = ref(false)
const uploading = ref(false)
const tagsText = ref('')
const fileInput = ref(null)
const isMobile = ref(false)

const formLabelWidth = computed(() => (isMobile.value ? '' : '110px'))
const formLabelPosition = computed(() => (isMobile.value ? 'top' : 'right'))
const editorHeight = computed(() => (isMobile.value ? '360px' : '480px'))

function syncViewport() {
  isMobile.value = window.innerWidth <= 768
}

const form = reactive({
  title: '',
  cover_url: '',
  summary: '',
  description: '',
  site_url: '',
  status: 'published',
})

async function onFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const res = await uploadFile(file)
    form.cover_url = res.data.url
    Modal.message({ message: t('common.success'), status: 'success' })
  } catch (err) {
    Modal.message({ message: err.message, status: 'error' })
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function onSave() {
  if (!form.title.trim()) return
  saving.value = true
  try {
    const payload = {
      ...form,
      description: isEmptyHtml(form.description) ? '' : form.description,
      tags: tagsText.value
        .split(/[,，]/)
        .map((s) => s.trim())
        .filter(Boolean),
    }
    if (isEdit.value) {
      await updateProject(route.params.id, payload)
      router.replace({ name: 'project-detail', params: { id: route.params.id } })
    } else {
      const res = await createProject(payload)
      router.replace({ name: 'project-detail', params: { id: res.data.id } })
    }
    Modal.message({ message: t('common.success'), status: 'success' })
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  syncViewport()
  window.addEventListener('resize', syncViewport)
  if (!isEdit.value) return
  const res = await fetchProject(route.params.id)
  Object.assign(form, {
    title: res.data.title,
    cover_url: res.data.cover_url || '',
    summary: res.data.summary || '',
    description: res.data.description || '',
    site_url: res.data.site_url || '',
    status: res.data.status,
  })
  tagsText.value = (res.data.tags || []).join(', ')
})

onUnmounted(() => {
  window.removeEventListener('resize', syncViewport)
})
</script>
