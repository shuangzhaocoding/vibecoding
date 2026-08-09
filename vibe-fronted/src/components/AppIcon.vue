<template>
  <svg
    class="app-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <!-- search -->
    <template v-if="name === 'search'">
      <circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.8" />
      <path d="m16 16 4.2 4.2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- eye / views -->
    <template v-else-if="name === 'eye'">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8" />
    </template>

    <!-- heart / likes -->
    <template v-else-if="name === 'heart'">
      <path
        d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z"
        :fill="filled ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linejoin="round"
      />
    </template>

    <!-- star / favorites -->
    <template v-else-if="name === 'star'">
      <path
        d="m12 3.2 2.4 4.9 5.4.8-3.9 3.8.9 5.4L12 15.6 7.2 18.1l.9-5.4-3.9-3.8 5.4-.8L12 3.2Z"
        :fill="filled ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linejoin="round"
      />
    </template>

    <!-- flame / popularity -->
    <template v-else-if="name === 'flame'">
      <path
        d="M12 21c4 0 6.5-2.6 6.5-6.2 0-2.7-1.5-4.4-3.2-5.8.2 1.8-.4 3-1.5 3.7 0-3.4-1.7-5.8-4.8-7.7.3 2.4-.5 4.1-1.8 5.3C6 8.7 5.5 7 5.5 5.5 4 7.4 3.5 9.5 3.5 11.8 3.5 16.4 7.2 21 12 21Z"
        :fill="filled ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linejoin="round"
      />
    </template>

    <!-- message / comments -->
    <template v-else-if="name === 'comment'">
      <path
        d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9l-4 3v-3H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linejoin="round"
      />
    </template>

    <!-- user -->
    <template v-else-if="name === 'user'">
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" stroke-width="1.8" />
      <path d="M5 19.2c1.4-3 3.7-4.4 7-4.4s5.6 1.4 7 4.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- external link -->
    <template v-else-if="name === 'link'">
      <path d="M14 5h5v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M10 14 19 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M17 13.5V18a1.5 1.5 0 0 1-1.5 1.5H6A1.5 1.5 0 0 1 4.5 18V8.5A1.5 1.5 0 0 1 6 7h4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- edit -->
    <template v-else-if="name === 'edit'">
      <path d="M4 20h4l10.5-10.5-4-4L4 16v4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="m12.5 7.5 4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- delete -->
    <template v-else-if="name === 'trash'">
      <path d="M5 7h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M7.5 7 8.2 18a1.5 1.5 0 0 0 1.5 1.4h4.6a1.5 1.5 0 0 0 1.5-1.4L16.5 7" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>
  </svg>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 16 },
  filled: { type: Boolean, default: false },
})
</script>

<style scoped>
.app-icon {
  display: inline-block;
  flex-shrink: 0;
  vertical-align: -0.15em;
}
</style>
