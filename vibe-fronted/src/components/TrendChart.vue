<template>
  <div class="trend-chart">
    <svg :viewBox="`0 0 ${W} ${H}`" class="trend-svg" preserveAspectRatio="none">
      <defs>
        <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.28" />
          <stop offset="100%" stop-color="var(--primary)" stop-opacity="0" />
        </linearGradient>
      </defs>
      <line
        v-for="(g, i) in gridYs"
        :key="i"
        class="grid"
        :x1="PAD_L"
        :x2="W - PAD_R"
        :y1="g"
        :y2="g"
      />
      <path v-if="areaPath" class="area" :d="areaPath" :fill="`url(#${gradId})`" />
      <path v-if="linePath" class="line" :d="linePath" />
      <circle
        v-for="(p, i) in points"
        :key="i"
        class="dot"
        :cx="p.x"
        :cy="p.y"
        r="3.2"
      >
        <title>{{ p.label }}: {{ p.value }}</title>
      </circle>
    </svg>
    <div class="trend-x">
      <span>{{ startLabel }}</span>
      <span>{{ midLabel }}</span>
      <span>{{ endLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  series: { type: Array, default: () => [] }, // [{ date, total }]
})

const W = 640
const H = 200
const PAD_L = 8
const PAD_R = 8
const PAD_T = 16
const PAD_B = 12
const gradId = `trend-grad-${Math.random().toString(36).slice(2, 8)}`

const values = computed(() => props.series.map((d) => Number(d.total) || 0))
const maxVal = computed(() => Math.max(1, ...values.value))

const points = computed(() => {
  const n = props.series.length
  if (!n) return []
  const innerW = W - PAD_L - PAD_R
  const innerH = H - PAD_T - PAD_B
  return props.series.map((d, i) => {
    const x = PAD_L + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW)
    const y = PAD_T + innerH - (values.value[i] / maxVal.value) * innerH
    return { x, y, value: values.value[i], label: d.date }
  })
})

const linePath = computed(() => {
  if (!points.value.length) return ''
  return points.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
})

const areaPath = computed(() => {
  if (!points.value.length) return ''
  const baseY = H - PAD_B
  const head = points.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
  const last = points.value[points.value.length - 1]
  const first = points.value[0]
  return `${head} L${last.x.toFixed(1)} ${baseY} L${first.x.toFixed(1)} ${baseY} Z`
})

const gridYs = computed(() => {
  const innerH = H - PAD_T - PAD_B
  return [0, 0.5, 1].map((t) => PAD_T + innerH * t)
})

function shortDate(iso) {
  if (!iso) return ''
  const parts = String(iso).split('-')
  return parts.length >= 3 ? `${Number(parts[1])}/${Number(parts[2])}` : iso
}

const startLabel = computed(() => shortDate(props.series[0]?.date))
const endLabel = computed(() => shortDate(props.series[props.series.length - 1]?.date))
const midLabel = computed(() => {
  if (props.series.length < 3) return ''
  return shortDate(props.series[Math.floor(props.series.length / 2)]?.date)
})
</script>

<style scoped>
.trend-chart {
  width: 100%;
}

.trend-svg {
  width: 100%;
  height: 200px;
  display: block;
}

.grid {
  stroke: var(--border);
  stroke-width: 1;
  stroke-dasharray: 4 4;
}

.line {
  fill: none;
  stroke: var(--primary);
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.dot {
  fill: var(--bg-elevated);
  stroke: var(--primary);
  stroke-width: 2;
}

.trend-x {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
