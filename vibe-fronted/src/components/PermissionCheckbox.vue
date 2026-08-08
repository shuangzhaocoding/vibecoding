<template>
  <div class="perm-panel">
    <div v-if="lockedIds.length" class="perm-hint">
      {{ t('system.roleOwnedHint') }}
    </div>
    <div style="margin-bottom:8px">
      <tiny-checkbox
        :indeterminate="indeterminate"
        :model-value="allChecked"
        @change="toggleAll"
      >
        {{ t('system.selectAll') }}
      </tiny-checkbox>
    </div>
    <div v-for="(list, group) in groups" :key="group" class="perm-group">
      <h4>{{ t(`enum.perm_group.${group}`, group) }}</h4>
      <div class="perm-grid">
        <tiny-checkbox
          v-for="p in list"
          :key="p.id"
          :model-value="isChecked(p.id)"
          :disabled="isLocked(p.id)"
          @change="(v) => toggleOne(p.id, v)"
        >
          {{ p.name }}
          <span class="perm-code">({{ p.code }})</span>
          <span v-if="isLocked(p.id)" class="perm-from-role">{{ t('system.fromRole') }}</span>
        </tiny-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  lockedIds: { type: Array, default: () => [] },
  groups: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()

const lockedSet = computed(() => new Set(props.lockedIds))
const allIds = computed(() => Object.values(props.groups).flat().map((p) => p.id))
const editableIds = computed(() => allIds.value.filter((id) => !lockedSet.value.has(id)))

function isLocked(id) {
  return lockedSet.value.has(id)
}

function isChecked(id) {
  return isLocked(id) || props.modelValue.includes(id)
}

const allChecked = computed(
  () =>
    editableIds.value.length > 0 &&
    editableIds.value.every((id) => props.modelValue.includes(id)),
)
const indeterminate = computed(() => {
  const n = editableIds.value.filter((id) => props.modelValue.includes(id)).length
  return n > 0 && n < editableIds.value.length
})

function toggleAll(checked) {
  if (checked) {
    emit('update:modelValue', [...editableIds.value])
  } else {
    emit('update:modelValue', [])
  }
}

function toggleOne(id, checked) {
  if (isLocked(id)) return
  const set = new Set(props.modelValue)
  if (checked) set.add(id)
  else set.delete(id)
  emit('update:modelValue', [...set])
}
</script>

<style scoped>
.perm-hint {
  margin-bottom: 10px;
  padding: 8px 10px;
  background: var(--primary-soft);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
}
.perm-code {
  color: var(--text-muted);
  font-size: 12px;
}
.perm-from-role {
  margin-left: 4px;
  color: var(--primary);
  font-size: 12px;
}
</style>
