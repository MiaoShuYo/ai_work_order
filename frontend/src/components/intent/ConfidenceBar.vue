<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
    defineProps<{
        confidence: number
        size?: 'small' | 'normal'
    }>(),
    { size: 'normal' },
)

const percent = computed(() => Math.round(props.confidence * 100))

// 颜色映射：低置信度红色，中等黄色，高置信度绿色，三档足够直观地区分不同把握程度
const barColor = computed(() => {
    if (props.confidence >= 0.8) return '#059669'
    if (props.confidence >= 0.6) return '#d97706'
    return '#dc2626'
})
</script>

<template>
    <div class="confidence-bar" :class="size">
        <div class="bar-track">
            <div class="bar-fill" :style="{ width: percent + '%', backgroundColor: barColor }" />
        </div>
        <span class="bar-label" :style="{ color: barColor }">{{ percent }}%</span>
    </div>
</template>

<style scoped>
.confidence-bar {
    display: flex;
    align-items: center;
    gap: 8px;
}

.bar-track {
    flex: 1;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
}

.confidence-bar.small .bar-track {
    height: 4px;
}

.bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

.bar-label {
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
    min-width: 36px;
    text-align: right;
}

.confidence-bar.small .bar-label {
    font-size: 11px;
    min-width: 28px;
}
</style>