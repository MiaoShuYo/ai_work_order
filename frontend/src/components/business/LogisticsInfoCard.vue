<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps < {
    // 与 PaymentInfoCard 同理：接 { order_no, steps: [...] } 整包或纯 steps 数组
    data: unknown
} > ()

const steps = computed < Array < Record < string, unknown>>> (() => {
    if (Array.isArray(props.data)) return props.data as Array<Record<string, unknown>>
    const raw = props.data as Record<string, unknown> | null
    const list = raw?.steps
    return Array.isArray(list) ? (list as Array<Record<string, unknown>>) : []
})

const orderNo = computed(() => {
    if (Array.isArray(props.data)) {
        return props.data.length ? String(props.data[0].order_no ?? '') : ''
    }
    return String((props.data as Record<string, unknown> | null)?.order_no ?? '')
})

const hasError = computed(() => {
    const raw = props.data as Record<string, unknown> | null
    return typeof raw?.error === 'string'
})

const errorMessage = computed(() => String((props.data as Record<string, unknown>)?.error ?? ''))
</script>

<template>
    <div v-if="hasError" class="logistics-card logistics-card-error">{{ errorMessage }}</div>
    <div v-else-if="steps.length === 0" class="logistics-card logistics-card-empty">该订单暂无物流轨迹</div>
    <div v-else class="logistics-card">
        <div class="logistics-title">订单 {{ orderNo }} · 物流轨迹</div>
        <div class="logistics-list">
            <div v-for="(step, index) in steps" :key="index" class="logistics-step">
                <div class="logistics-rail">
                    <span class="logistics-dot"></span>
                    <span v-if="index !== steps.length - 1" class="logistics-line"></span>
                </div>
                <div class="logistics-body">
                    <div class="logistics-head">
                        <span class="logistics-location">{{ step.location }}</span>
                        <span class="logistics-time">{{ step.time }}</span>
                    </div>
                    <div class="logistics-desc">{{ step.description }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.logistics-card {
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 6px;
    background-color: #fff;
    border: 1px solid #e5e7eb;
}

.logistics-card-error {
    color: #dc2626;
}

.logistics-card-empty {
    color: #6b7280;
}

.logistics-title {
    padding-bottom: 6px;
    border-bottom: 1px dashed #e5e7eb;
    font-size: 13px;
    font-weight: 600;
}

.logistics-step {
    display: flex;
    padding-top: 8px;
}

.logistics-rail {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 16px;
    flex-shrink: 0;
}

.logistics-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #2563eb;
    flex-shrink: 0;
}

.logistics-line {
    width: 1px;
    flex: 1;
    margin: 2px 0;
    background-color: #e5e7eb;
}

.logistics-body {
    flex: 1;
    min-width: 0;
}

.logistics-head {
    display: flex;
    justify-content: space-between;
    gap: 8px;
}

.logistics-location {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
}

.logistics-time {
    font-size: 12px;
    color: #9ca3af;
    flex-shrink: 0;
}

.logistics-desc {
    margin-top: 2px;
    font-size: 13px;
    color: #6b7280;
    line-height: 1.4;
}
</style>