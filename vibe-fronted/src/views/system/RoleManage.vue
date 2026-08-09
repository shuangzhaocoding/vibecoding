<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('system.roles') }}</h2>
        <tiny-button v-if="userStore.hasPerm('system:role:manage')" type="primary" @click="openCreate">
          <span class="icon-text"><AppIcon name="plus" :size="15" />{{ t('common.create') }}</span>
        </tiny-button>
      </div>
      <tiny-grid :data="items" border size="small" style="margin-top:16px">
        <tiny-grid-column field="code" :title="t('system.roleCode')" />
        <tiny-grid-column field="name" :title="t('system.roleName')" />
        <tiny-grid-column :title="t('system.dataScope')">
          <template #default="{ row }">{{ t(`enum.data_scope.${row.data_scope}`) }}</template>
        </tiny-grid-column>
        <tiny-grid-column field="is_system" title="System" width="90">
          <template #default="{ row }">{{ row.is_system ? 'Y' : 'N' }}</template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('common.actions')" width="240">
          <template #default="{ row }">
            <tiny-button v-if="userStore.hasPerm('system:role:manage')" type="text" @click.stop="openEdit(row)">
              <span class="icon-text"><AppIcon name="edit" :size="14" />{{ t('common.edit') }}</span>
            </tiny-button>
            <tiny-button v-if="userStore.hasPerm('system:perm:assign')" type="text" @click.stop="openPerm(row)">
              <span class="icon-text"><AppIcon name="key" :size="14" />{{ t('system.permissions') }}</span>
            </tiny-button>
            <tiny-button
              v-if="userStore.hasPerm('system:role:manage') && !row.is_system"
              type="text"
              @click.stop="onDelete(row)"
            >
              <span class="icon-text"><AppIcon name="trash" :size="14" />{{ t('common.delete') }}</span>
            </tiny-button>
          </template>
        </tiny-grid-column>
      </tiny-grid>
    </div>

    <tiny-dialog-box
      v-model:visible="showForm"
      :title="form.id ? t('common.edit') : t('common.create')"
      width="480px"
      append-to-body
    >
      <tiny-form label-width="100px">
        <tiny-form-item :label="t('system.roleCode')">
          <tiny-input v-model="form.code" :disabled="!!form.id" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.roleName')">
          <tiny-input v-model="form.name" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.dataScope')">
          <tiny-select v-model="form.data_scope" style="width:100%">
            <tiny-option v-for="s in scopes" :key="s" :label="t(`enum.data_scope.${s}`)" :value="s" />
          </tiny-select>
          <div class="field-hint">{{ t('system.dataScopeHint') }}</div>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showForm = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" @click="saveRole">{{ t('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <tiny-dialog-box v-model:visible="showPerm" :title="t('system.permissions')" width="640px" append-to-body>
      <PermissionCheckbox v-model="permIds" :groups="permGroups" />
      <template #footer>
        <tiny-button @click="showPerm = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" @click="savePerm">{{ t('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Modal } from '@opentiny/vue'
import {
  assignRolePermissions,
  createRole,
  deleteRole,
  fetchPermissions,
  fetchRoles,
  updateRole,
} from '@/api/system'
import AppIcon from '@/components/AppIcon.vue'
import PermissionCheckbox from '@/components/PermissionCheckbox.vue'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()
const items = ref([])
const permGroups = ref({})
const showForm = ref(false)
const showPerm = ref(false)
const permIds = ref([])
const currentRoleId = ref(null)
const scopes = ['all', 'assigned', 'reported']
const form = reactive({ id: null, code: '', name: '', data_scope: 'reported' })

async function load() {
  const res = await fetchRoles()
  items.value = res.data
}

async function loadPerms() {
  const p = await fetchPermissions()
  permGroups.value = p.data.groups
}

function openCreate() {
  Object.assign(form, { id: null, code: '', name: '', data_scope: 'reported' })
  showForm.value = true
}

function openEdit(row) {
  Object.assign(form, { id: row.id, code: row.code, name: row.name, data_scope: row.data_scope })
  showForm.value = true
}

async function saveRole() {
  try {
    if (form.id) {
      await updateRole(form.id, { name: form.name, data_scope: form.data_scope })
    } else {
      await createRole({ code: form.code, name: form.name, data_scope: form.data_scope })
    }
    showForm.value = false
    Modal.message({ message: t('common.success'), status: 'success' })
    load()
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

function openPerm(row) {
  currentRoleId.value = row.id
  permIds.value = [...(row.permission_ids || [])]
  showPerm.value = true
}

async function savePerm() {
  await assignRolePermissions(currentRoleId.value, permIds.value)
  showPerm.value = false
  Modal.message({ message: t('common.success'), status: 'success' })
  load()
}

async function onDelete(row) {
  Modal.confirm(t('common.confirm')).then(async (r) => {
    if (r === 'confirm') {
      await deleteRole(row.id)
      Modal.message({ message: t('common.success'), status: 'success' })
      load()
    }
  })
}

onMounted(async () => {
  await loadPerms()
  await load()
})
</script>

<style scoped>
.field-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}
</style>
