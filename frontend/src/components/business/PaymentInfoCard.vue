<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    // 兼容两种数据结构：工具返回的 { order_no, payments: [...] } 整包，或详情接口的纯 payments 数组
    data: unknown
}>()

// 先把两种来源归一化成同一份列表，模板只需要关心 payments 数组。
// 工具包结构里取 payments 字段，纯数组就直接用，都不是就当成空列表。
const payments = computed<Array<Record<string, unknown>>>(() => {
    if (Array.isArray(props.data)) {
        return props.data as Array<Record<string, unknown>>
    }
    const raw = props.data as Record<string, unknown> | null
    const list = raw?.payments
    return Array.isArray(list) ? (list as Array<Record<string, unknown>>) : []
})

const orderNo = computed(() => {
    if (Array.isArray(props.data)) {
        return props.data.length ? String(props.data[0].order_no ?? '') : ''
    }
    return String((props.data as Record<string, unknown> | null)?.order_no ?? '')
})

// 金额在后端已经是两位小数的字符串，这里直接拼进合计，不再做浮点运算
const totalAmount = computed(() => {
    const total = payments.value.reduce((sum, payment) => sum + Number(payment.amount ?? 0), 0)
    return total.toFixed(2)
})

const hasError = computed(() => {
    const raw = props.data as Record<string, unknown> | null
    return typeof raw?.error === 'string'
})

const errorMessage = computed(() => String((props.data as Record<string, unknown>)?.error ?? ''))
</script>

<template>
    <div v-if="hasError" class="payment-card payment-card-error">{{ errorMessage }}</div>
    <div v-else-if="payments.length === 0" class="payment-card payment-card-empty">该订单暂无支付流水</div>
    <div v-else class="payment-card">
        <div class="payment-header">
            <span>订单 {{ orderNo }} · 共 {{ payments.length }} 笔</span>
            <span class="payment-total">合计 ￥{{ totalAmount }}</span>
        </div>
        <div v-for="payment in payments" :key="String(payment.pay_no)" class="payment-row">
            <div>
                <div class="payment-type">{{ payment.pay_type }}</div>
                <div class="payment-no">{{ payment.pay_no }}</div>
            </div>
            <div class="payment-right">
                <div class="payment-amount">{{ payment.amount }}</div>
                <div class="payment-time">{{ payment.pay_time }}</div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.payment-card {
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 6px;
    background-color: #fff;
    border: 1px solid #e5e7eb;
}

.payment-card-error,
.payment-card-empty {
    color: #6b7280;
}

.payment-card-error {
    color: #dc2626;
}

.payment-header {
    display: flex;
    justify-content: space-between;
    padding-bottom: 6px;
    border-bottom: 1px dashed #e5e7eb;
    font-size: 13px;
    font-weight: 600;
}

.payment-total {
    color: #dc2626;
    font-weight: 700;
}

.payment-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    font-size: 13px;
}

.payment-type {
    font-weight: 600;
    color: #374151;
}

.payment-no {
    color: #9ca3af;
    font-size: 12px;
}

.payment-right {
    text-align: right;
}

.payment-amount {
    color: #374151;
    font-weight: 600;
}

.payment-time {
    color: #9ca3af;
    font-size: 12px;
}
</style>