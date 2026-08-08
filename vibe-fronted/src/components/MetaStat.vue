<template>
  <span class="meta-stat" :title="label">
    <AppIcon :name="icon" :size="size" :filled="filled" />
    <span class="meta-stat-value">{{ value }}</span>
  </span>
</template>

<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  icon: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  label: { type: String, default: '' },
  size: { type: [Number, String], default: 15 },
  filled: { type: Boolean, default: false },
})
</script>

<style scoped>
.meta-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: inherit;
  line-height: 1;
  white-space: nowrap;
}

.meta-stat-value {
  font-variant-numeric: tabular-nums;
}
</style>
