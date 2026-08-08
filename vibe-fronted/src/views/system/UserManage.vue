<template>
  <div class="page">
    <div class="page-panel">
      <div class="page-toolbar">
        <h2 class="page-title">{{ t('system.users') }}</h2>
        <tiny-button v-if="userStore.hasPerm('system:user:manage')" type="primary" @click="openCreate">
          {{ t('common.create') }}
        </tiny-button>
      </div>
      <tiny-grid :data="items" border size="small" style="margin-top:16px">
        <tiny-grid-column field="username" :title="t('auth.username')" />
        <tiny-grid-column field="email" :title="t('system.email')" />
        <tiny-grid-column field="display_name" :title="t('system.displayName')" />
        <tiny-grid-column :title="t('system.assignRoles')">
          <template #default="{ row }">{{ (row.roles || []).map((r) => r.name).join(', ') }}</template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('system.active')" width="90">
          <template #default="{ row }">{{ row.is_active ? t('system.active') : t('system.inactive') }}</template>
        </tiny-grid-column>
        <tiny-grid-column :title="t('common.actions')" width="220">
          <template #default="{ row }">
            <tiny-button v-if="userStore.hasPerm('system:user:manage')" type="text" @click.stop="openEdit(row)">
              {{ t('common.edit') }}
            </tiny-button>
            <tiny-button v-if="userStore.hasPerm('system:perm:assign')" type="text" @click.stop="openPerm(row)">
              {{ t('system.extraPerms') }}
            </tiny-button>
          </template>
        </tiny-grid-column>
      </tiny-grid>
    </div>

    <tiny-dialog-box
      v-model:visible="showForm"
      :title="form.id ? t('common.edit') : t('common.create')"
      width="520px"
      append-to-body
    >
      <tiny-form label-width="100px">
        <tiny-form-item :label="t('auth.username')">
          <tiny-input v-model="form.username" :disabled="!!form.id" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.email')">
          <tiny-input v-model="form.email" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.displayName')">
          <tiny-input v-model="form.display_name" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.password')">
          <tiny-input v-model="form.password" type="password" />
        </tiny-form-item>
        <tiny-form-item :label="t('system.assignRoles')">
          <tiny-select v-model="form.role_ids" multiple style="width:100%">
            <tiny-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showForm = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" @click="saveUser">{{ t('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <tiny-dialog-box
      v-model:visible="showPerm"
      :title="permDialogTitle"
      width="640px"
      append-to-body
    >
      <div v-if="permUser" class="perm-user-meta">
        <div>{{ t('system.currentUser') }}：{{ permUser.display_name }}（{{ permUser.username }}）</div>
        <div>{{ t('system.assignRoles') }}：{{ permRoleNames || '-' }}</div>
      </div>
      <PermissionCheckbox v-model="permIds" :groups="permGroups" :locked-ids="rolePermIds" />
      <template #footer>
        <tiny-button @click="showPerm = false">{{ t('common.cancel') }}</tiny-button>
        <tiny-button type="primary" @click="savePerm">{{ t('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Modal } from '@opentiny/vue'
import {
  assignUserPermissions,
  createUser,
  fetchPermissions,
  fetchRoles,
  fetchUsers,
  updateUser,
} from '@/api/system'
import PermissionCheckbox from '@/components/PermissionCheckbox.vue'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const userStore = useUserStore()
const items = ref([])
const roles = ref([])
const permGroups = ref({})
const showForm = ref(false)
const showPerm = ref(false)
const permIds = ref([])
const rolePermIds = ref([])
const currentUserId = ref(null)
const permUser = ref(null)
const form = reactive({
  id: null,
  username: '',
  email: '',
  display_name: '',
  password: '',
  role_ids: [],
})

const permDialogTitle = computed(() => {
  if (!permUser.value) return t('system.extraPerms')
  return `${t('system.extraPerms')} - ${permUser.value.display_name}`
})

const permRoleNames = computed(() =>
  (permUser.value?.roles || []).map((r) => r.name).join('、'),
)

async function load() {
  const res = await fetchUsers({ page: 1, page_size: 100 })
  items.value = res.data.items
}

async function loadMeta() {
  if (
    userStore.hasPerm('system:role:view') ||
    userStore.hasPerm('system:perm:assign') ||
    userStore.hasPerm('system:user:manage')
  ) {
    const r = await fetchRoles()
    roles.value = r.data
  }
  if (userStore.hasPerm('system:perm:assign') || userStore.hasPerm('system:role:view')) {
    const p = await fetchPermissions()
    permGroups.value = p.data.groups
  }
}

function openCreate() {
  Object.assign(form, {
    id: null,
    username: '',
    email: '',
    display_name: '',
    password: 'Passw0rd!',
    role_ids: [],
  })
  showForm.value = true
}

function openEdit(row) {
  Object.assign(form, {
    id: row.id,
    username: row.username,
    email: row.email || '',
    display_name: row.display_name,
    password: '',
    role_ids: (row.roles || []).map((r) => r.id),
  })
  showForm.value = true
}

async function saveUser() {
  try {
    if (form.id) {
      const payload = {
        display_name: form.display_name,
        email: form.email,
        role_ids: form.role_ids,
      }
      if (form.password) payload.password = form.password
      await updateUser(form.id, payload)
    } else {
      await createUser({ ...form })
    }
    showForm.value = false
    Modal.message({ message: t('common.success'), status: 'success' })
    load()
  } catch (e) {
    Modal.message({ message: e.message, status: 'error' })
  }
}

function collectRolePermIds(userRow) {
  const roleIdSet = new Set((userRow.roles || []).map((r) => r.id))
  const ids = new Set()
  for (const role of roles.value) {
    if (!roleIdSet.has(role.id)) continue
    for (const pid of role.permission_ids || []) ids.add(pid)
  }
  return [...ids]
}

function openPerm(row) {
  currentUserId.value = row.id
  permUser.value = row
  rolePermIds.value = collectRolePermIds(row)
  const locked = new Set(rolePermIds.value)
  permIds.value = (row.permission_ids || []).filter((id) => !locked.has(id))
  showPerm.value = true
}

async function savePerm() {
  await assignUserPermissions(currentUserId.value, permIds.value)
  showPerm.value = false
  Modal.message({ message: t('common.success'), status: 'success' })
  load()
}

onMounted(async () => {
  await loadMeta()
  await load()
})
</script>
