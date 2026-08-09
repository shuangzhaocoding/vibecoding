<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('menu.moderation') }}</h2>
        <div class="toolbar-right">
          <tiny-select v-model="status" style="width:140px" @change="reload">
            <tiny-option :label="t('report.statusPending')" value="pending" />
            <tiny-option :label="t('report.statusIgnored')" value="ignored" />
            <tiny-option :label="t('report.statusResolved')" value="resolved" />
            <tiny-option :label="t('common.all')" value="all" />
          </tiny-select>
          <tiny-button @click="load">
            <span class="icon-text"><AppIcon name="refresh" :size="15" />{{ t('common.reset') }}</span>
          </tiny-button>
        </div>
      </div>

      <tiny-grid :data="items" border size="small" style="margin-top:16px">
        <tiny-grid-column :title="t('project.title')" min-width="160">
          <template #default="{ row }">
            <a
              v-if="row.project"
              class="link"
              href="javascript:;"
              @click="goProject(row.project.id)"
            >{{ row.project.title }}</a>
            <span v-else>-</span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('report.reason')" width="120">
          <template #default="{ row }">{{ t(`report.reasons.${row.reason}`) }}</template>
        </tiny-grid-column>
        <tiny-grid-column field="detail" :title="t('report.detail')" min-width="160" show-overflow />
        <tiny-grid-column :title="t('report.reporter')" width="120">
          <template #default="{ row }">{{ row.reporter?.display_name || '-' }}</template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('project.status')" width="90">
          <template #default="{ row }">
            {{ row.project ? t(`project.${row.project.status}`) : '-' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('report.status')" width="90">
          <template #default="{ row }">{{ statusLabel(row.status) }}</template>
        </tiny-grid-column>
        <tiny-grid-column field="created_at" :title="t('report.createdAt')" width="170" />
        <tiny-grid-column :title="t('common.actions')" width="240" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <tiny-button type="text" @click="resolve(row, 'ignore')">{{ t('report.ignore') }}</tiny-button>
              <tiny-button type="text" @click="resolve(row, 'hide')">{{ t('report.hide') }}</tiny-button>
              <tiny-button type="text" @click="resolve(row, 'delete')">{{ t('report.deleteProject') }}</tiny-button>
            </template>
            <span v-else class="muted">{{ row.resolve_note || '-' }}</span>
          </template>
        </tiny-grid-column>
      </tiny-grid>

      <div v-if="total > pageSize" class="pager">
        <tiny-pager
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="onPage"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { fetchReports, resolveReport } from '@/api/project'
import AppIcon from '@/components/AppIcon.vue'

const { t } = useI18n()
const router = useRouter()
const items = ref([])
const status = ref('pending')
const page = ref(1)
const pageSize = 20
const total = ref(0)

function statusLabel(s) {
  if (s === 'pending') return t('report.statusPending')
  if (s === 'ignored') return t('report.statusIgnored')
  if (s === 'resolved') return t('report.statusResolved')
  return s
}

function goProject(id) {
  router.push({ name: 'project-detail', params: { id } })
}

function reload() {
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

async function load() {
  try {
    const res = await fetchReports({
      status: status.value,
      page: page.value,
      page_size: pageSize,
    })
    items.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

function resolve(row, action) {
  const confirmKey =
    action === 'delete'
      ? 'report.confirmDelete'
      : action === 'hide'
        ? 'report.confirmHide'
        : 'report.confirmIgnore'
  Modal.confirm(t(confirmKey)).then(async () => {
    try {
      await resolveReport(row.id, { action })
      Modal.message({ message: t('common.success'), status: 'success' })
      load()
    } catch (e) {
      Modal.message({ message: e.message, status: 'error' })
    }
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar-right {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.link {
  color: var(--primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.muted {
  color: var(--text-muted);
  font-size: 12px;
}

.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
