<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    order: Record<string, unknown>
}>()

const STATUS_COLOR: Record<string, string> = {
    待发货: '#f59e0b',
    已发货: '#2563eb',
    已完成: '#059669',
    已取消: '#6b7280',
}

// order 来自工具返回的原始 JSON，类型是 Record<string, unknown>，后端已经用 OrderInfo 这个 Pydantic 模型校验过字段是否合法，前端这里只需要按约定的 key 读取并转成字符串展示，不需要再重复做一遍业务校验。
const orderNo = computed(() => String(props.order.order_no ?? ''))
const status = computed(() => String(props.order.status ?? ''))
const payStatus = computed(() => String(props.order.pay_status ?? ''))
const logisticsStatus = computed(() => String(props.order.logistics_status ?? ''))
const hasError = computed(() => typeof props.order.error === 'string')

</script>

<template>
    <div v-if="hasError" class="order-card order-card-error">{{ order.error }}</div>
    <div v-else class="order-card">
        <div class="order-row">
            <span class="order-label">订单号</span>
            <span>{{ orderNo }}</span>
        </div>
        <div class="order-row">
            <span class="order-label">订单状态</span>
            <span class="order-status" :style="{ color: STATUS_COLOR[status] ?? '#374151' }">{{ status }}</span>
        </div>
        <div class="order-row">
            <span class="order-label">支付状态</span>
            <span>{{ payStatus }}</span>
    </div>
</template>

<style scoped></style>