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

    <!-- home -->
    <template v-else-if="name === 'home'">
      <path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5.2v-6.2H10.2V21H5a1 1 0 0 1-1-1v-9.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>

    <!-- ranking / chart -->
    <template v-else-if="name === 'ranking'">
      <path d="M5 19V11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M12 19V5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M19 19v-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
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

    <!-- reply -->
    <template v-else-if="name === 'reply'">
      <path d="M9 14 4 9l5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M4 9h9a6 6 0 0 1 6 6v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- user -->
    <template v-else-if="name === 'user'">
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" stroke-width="1.8" />
      <path d="M5 19.2c1.4-3 3.7-4.4 7-4.4s5.6 1.4 7 4.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- users / group -->
    <template v-else-if="name === 'users'">
      <circle cx="9" cy="8" r="2.8" stroke="currentColor" stroke-width="1.8" />
      <path d="M3.5 18.5c1-2.4 2.8-3.6 5.5-3.6s4.5 1.2 5.5 3.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <circle cx="17" cy="8.5" r="2.3" stroke="currentColor" stroke-width="1.8" />
      <path d="M14.2 14.2c1.5-.4 2.9-.2 4.3.8 1.2.9 2 2.2 2.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
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

    <!-- plus -->
    <template v-else-if="name === 'plus'">
      <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- publish / pen -->
    <template v-else-if="name === 'publish'">
      <path d="M12 19V8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="m7.5 11.5 4.5-4.5 4.5 4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M5 19h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- upload -->
    <template v-else-if="name === 'upload'">
      <path d="M12 16V6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="m8 9.5 4-4 4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M5 18h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- save -->
    <template v-else-if="name === 'save'">
      <path d="M5 4h11l3 3v13H5V4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="M8 4v5h7V4" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="M8 20v-6h8v6" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>

    <!-- close -->
    <template v-else-if="name === 'close'">
      <path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- logout -->
    <template v-else-if="name === 'logout'">
      <path d="M10 12h9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="m16 8 4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M13 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- mail -->
    <template v-else-if="name === 'mail'">
      <rect x="3.5" y="5.5" width="17" height="13" rx="2" stroke="currentColor" stroke-width="1.8" />
      <path d="m4.5 7.5 7.5 6 7.5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- lock -->
    <template v-else-if="name === 'lock'">
      <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.8" />
      <path d="M8 10V7.5a4 4 0 0 1 8 0V10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- shield / roles -->
    <template v-else-if="name === 'shield'">
      <path d="M12 3.5 19 6.5v5.2c0 4.4-2.9 7.4-7 8.8-4.1-1.4-7-4.4-7-8.8V6.5L12 3.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>

    <!-- key / permissions -->
    <template v-else-if="name === 'key'">
      <circle cx="8" cy="14" r="3.2" stroke="currentColor" stroke-width="1.8" />
      <path d="M10.5 11.5 19 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M16 5.5 18.5 8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- sun -->
    <template v-else-if="name === 'sun'">
      <circle cx="12" cy="12" r="3.6" stroke="currentColor" stroke-width="1.8" />
      <path d="M12 3.5v2.2M12 18.3v2.2M3.5 12h2.2M18.3 12h2.2M6 6l1.6 1.6M16.4 16.4 18 18M18 6l-1.6 1.6M7.6 16.4 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- moon -->
    <template v-else-if="name === 'moon'">
      <path d="M16.5 14.2A6.5 6.5 0 0 1 9.8 7.5 6.6 6.6 0 1 0 16.5 14.2Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
    </template>

    <!-- arrow up -->
    <template v-else-if="name === 'arrow-up'">
      <path d="M12 19V6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="m7 11 5-5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- arrow down -->
    <template v-else-if="name === 'arrow-down'">
      <path d="M12 5v13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="m7 13 5 5 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- refresh / reset -->
    <template v-else-if="name === 'refresh'">
      <path d="M20 12a8 8 0 1 1-2.3-5.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M20 5v5h-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- inbox / empty -->
    <template v-else-if="name === 'inbox'">
      <path d="M4 8h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="M4 8 7.2 3.8h9.6L20 8" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
      <path d="M4 13h4.2l1.3 2h5l1.3-2H20" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
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
