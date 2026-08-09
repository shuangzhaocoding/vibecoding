<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('system.permissionsManage') }}</h2>
        <tiny-button v-if="userStore.hasPerm('system:perm:manage')" type="primary" @click="openCreate">
          <span class="icon-text"><AppIcon name="plus" :size="15" />{{ t('common.create') }}</span>
        </tiny-button>
      </div>
      <div class="filter-row" style="margin-top:16px">
        <tiny-select v-model="filterGroup" clearable :placeholder="t('system.permGroup')" style="width:180px">
          <tiny-option v-for="g in groupOptions" :key="g" :label="groupLabel(g)" :value="g" />
        </tiny-select>
        <tiny-input v-model="keyword" :placeholder="t('system.permCode')" style="width:220px" clearable />
      </div>
      <tiny-grid :data="filteredItems" border size="small">
        <tiny-grid-column field="code" :title="t('system.permCode')" min-width="180" />
        <tiny-grid-column field="name" :title="t('system.permName')" min-width="140" />
        <tiny-grid-column :title="t('system.permGroup')" width="140">
          <template #default="{ row }">{{ groupLabel(row.group) }}</template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <tiny-button v-if="userStore.hasPerm('system:perm:manage')" type="text" @click.stop="openEdit(row)">
              <span class="icon-text"><AppIcon name="edit" :size="14" />{{ t('common.edit') }}</span>
            </tiny-button>
            <tiny-button v-if="userStore.hasPerm('system:perm:manage')" type="text" @click.stop="onDelete(row)">
              <span class="icon-text"><AppIcon name="trash" :size="14" />{{ t('common.delete') }}</span>
            </tiny-button>
          </template>
        </tiny-grid-column>
      </tiny-grid>
    </div>

    <tiny-dialog-box
      v-model:visible="showForm"
      :title="form.id ? t('common.edit') : t('system.createPerm')"
      width="520px"
      append-to-body
    >
      <tiny-form label-width="110px">
        <tiny-form-item :label="t('system.permCode')" required>
          <tiny-input v-model="form.code" :disabled="!!form.id" placeholder="project:export" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.permName')" required>
          <tiny-input v-model="form.name" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.permGroup')" required>
          <tiny-select v-model="form.group" allow-create filterable style="width:100%">
            <tiny-option v-for="g in presetGroups" :key="g" :label="groupLabel(g)" :value="g" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showForm = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" @click="save">{{ t('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Modal } from '@opentiny/vue'
import { createPermission, deletePermission, fetchPermissions, updatePermission } from '@/api/system'
import AppIcon from '@/components/AppIcon.vue'
import { useUserStore } from '@/stores/user'

const { t, te } = useI18n()
const userStore = useUserStore()
const items = ref([])
const filterGroup = ref('')
const keyword = ref('')
const showForm = ref(false)
const presetGroups = ['system', 'project']
const form = reactive({ id: null, code: '', name: '', group: 'system' })

const groupOptions = computed(() => {
  const set = new Set(presetGroups)
  items.value.forEach((p) => set.add(p.group))
  return [...set]
})

const filteredItems = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return items.value.filter((p) => {
    if (filterGroup.value && p.group !== filterGroup.value) return false
    if (!kw) return true
    return p.code.toLowerCase().includes(kw) || p.name.toLowerCase().includes(kw)
  })
})

function groupLabel(group) {
  const key = `enum.perm_group.${group}`
  return te(key) ? t(key) : group
}

async function load() {
  const res = await fetchPermissions()
  items.value = res.data.items || []
}

function openCreate() {
  Object.assign(form, { id: null, code: '', name: '', group: 'system' })
  showForm.value = true
}

function openEdit(row) {
  Object.assign(form, { id: row.id, code: row.code, name: row.name, group: row.group })
  showForm.value = true
}

async function save() {
  try {
    if (!form.code.trim() || !form.name.trim() || !form.group.trim()) {
      Modal.message({ message: t('system.permRequired'), status: 'warning' })
      return
    }
    if (form.id) {
      await updatePermission(form.id, { name: form.name.trim(), group: form.group.trim() })
    } else {
      await createPermission({
        code: form.code.trim(),
        name: form.name.trim(),
        group: form.group.trim(),
      })
    }
    showForm.value = false
    Modal.message({ message: t('common.success'), status: 'success' })
    load()
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

async function onDelete(row) {
  Modal.confirm(t('system.permDeleteConfirm')).then(async (r) => {
    if (r !== 'confirm') return
    try {
      await deletePermission(row.id)
      Modal.message({ message: t('common.success'), status: 'success' })
      load()
    } catch (e) {
      Modal.message({ message: e.message, status: 'error' })
    }
  })
}

onMounted(load)
</script>
