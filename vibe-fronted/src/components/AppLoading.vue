<template>
  <div class="app-loading" :class="[`is-${size}`, { inline }]" role="status" :aria-label="label">
    <div class="app-loading-visual" aria-hidden="true">
      <span class="halo" />
      <span class="halo delay" />
      <svg class="orbit" viewBox="0 0 64 64" fill="none">
        <circle class="track" cx="32" cy="32" r="24" />
        <circle class="arc arc-a" cx="32" cy="32" r="24" />
        <circle class="arc arc-b" cx="32" cy="32" r="16" />
      </svg>
      <span class="core">
        <span class="core-shine" />
      </span>
      <span class="spark s1" />
      <span class="spark s2" />
      <span class="spark s3" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  text: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm | md
  inline: { type: Boolean, default: false },
})

const { t } = useI18n()
const label = computed(() => props.text || t('common.loading'))
</script>

<style scoped>
.app-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 52px 16px;
}

.app-loading.inline {
  padding: 28px 12px;
}

.app-loading.is-sm {
  padding: 18px 12px;
}

.app-loading-visual {
  position: relative;
  width: 64px;
  height: 64px;
}

.app-loading.is-sm .app-loading-visual {
  width: 40px;
  height: 40px;
}

.halo {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 28%, transparent) 0%,
    transparent 68%
  );
  animation: halo-breathe 2.2s ease-in-out infinite;
}

.halo.delay {
  inset: 0;
  animation-delay: -1.1s;
  opacity: 0.7;
}

.orbit {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  animation: orbit-spin 1.6s linear infinite;
}

.track {
  stroke: color-mix(in srgb, var(--primary) 14%, transparent);
  stroke-width: 3;
}

.arc {
  fill: none;
  stroke-linecap: round;
  transform-origin: 32px 32px;
}

.arc-a {
  stroke: var(--primary);
  stroke-width: 3.2;
  stroke-dasharray: 48 120;
  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--primary) 45%, transparent));
}

.arc-b {
  stroke: color-mix(in srgb, var(--primary) 70%, #93c5fd);
  stroke-width: 2.4;
  stroke-dasharray: 28 90;
  animation: counter-spin 1.1s linear infinite;
}

.core {
  position: absolute;
  inset: 0;
  margin: auto;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(145deg, #60a5fa, var(--primary) 45%, #1d4ed8);
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--primary) 12%, transparent),
    0 4px 12px color-mix(in srgb, var(--primary) 35%, transparent);
  animation: core-pulse 1.6s ease-in-out infinite;
  overflow: hidden;
}

.app-loading.is-sm .core {
  width: 9px;
  height: 9px;
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--primary) 12%, transparent),
    0 2px 8px color-mix(in srgb, var(--primary) 30%, transparent);
}

.core-shine {
  position: absolute;
  top: -30%;
  left: -20%;
  width: 70%;
  height: 70%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.55);
  animation: shine-drift 2s ease-in-out infinite;
}

.spark {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 55%, transparent);
  animation: spark-orbit 2.4s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
}

.app-loading.is-sm .spark {
  width: 4px;
  height: 4px;
}

.s1 {
  top: 2px;
  left: calc(50% - 3px);
  animation-delay: 0s;
}

.s2 {
  top: calc(50% - 3px);
  right: 2px;
  animation-delay: -0.8s;
  opacity: 0.75;
}

.s3 {
  bottom: 4px;
  left: 10px;
  animation-delay: -1.6s;
  opacity: 0.55;
  width: 4px;
  height: 4px;
}

@keyframes orbit-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes counter-spin {
  to {
    transform: rotate(-360deg);
  }
}

@keyframes halo-breathe {
  0%,
  100% {
    transform: scale(0.86);
    opacity: 0.35;
  }
  50% {
    transform: scale(1.08);
    opacity: 0.85;
  }
}

@keyframes core-pulse {
  0%,
  100% {
    transform: scale(0.92);
  }
  50% {
    transform: scale(1.08);
  }
}

@keyframes shine-drift {
  0%,
  100% {
    transform: translate(0, 0);
    opacity: 0.45;
  }
  50% {
    transform: translate(20%, 25%);
    opacity: 0.75;
  }
}

@keyframes spark-orbit {
  0% {
    transform: scale(0.6);
    opacity: 0.2;
  }
  40% {
    transform: scale(1.15);
    opacity: 1;
  }
  100% {
    transform: scale(0.6);
    opacity: 0.2;
  }
}

@media (prefers-reduced-motion: reduce) {
  .halo,
  .orbit,
  .arc-b,
  .core,
  .core-shine,
  .spark {
    animation: none;
  }

  .arc-a {
    stroke-dasharray: 70 100;
  }

  .halo {
    opacity: 0.45;
  }
}
</style>
