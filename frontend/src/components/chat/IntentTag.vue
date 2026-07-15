<script setup lang="ts">
import { computed } from 'vue'
import type { Intent } from '../../api/chat'

const props = defineProps<{
    intent: Intent
}>()

// 意图到展示文案、颜色的映射写在组件里，后面业务方扩充意图类型时只需要在这一份映射里加一条，不用改调用方的代码
const INTENT_META: Record<Intent, { label: string; color: string }> = {
    order_issue: { label: '订单问题', color: '#2563eb' },
    account_issue: { label: '账号问题', color: '#9333ea' },
    refund_request: { label: '退款请求', color: '#dc2626' },
    general_inquiry: { label: '一般咨询', color: '#059669' },
    other: { label: '其他', color: '#6b7280' },
}

const meta = computed(() => INTENT_META[props.intent])

</script>

<template>
    <span class="intent-tag" :style="{ backgroundColor: meta.color }">
        {{ meta.label }}
    </span>
</template>

<style scoped>
.intent-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    color: #fff;
    font-size: 12px;
}
</style>