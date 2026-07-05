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
        <div class="order-row">
            <span class="order-label">物流状态</span>
            <span>{{ logisticsStatus }}</span>
        </div>
    </div>
</template>

<style scoped>
.order-card {
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 6px;
    background-color: #fff;
    border: 1px solid #e5e7eb;
}

.order-card-error {
    color: #dc2626;
}

.order-row {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
    font-size: 13px;
}

.order-label {
    color: #6b7280;
}

.order-status {
    font-weight: 600;
}
</style>