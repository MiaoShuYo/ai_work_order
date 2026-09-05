<script setup lang="ts">
import ConfidenceBar from './ConfidenceBar.vue'

// 前端同时维护一份标签映射，虽然和后端 INTENT_LABELS 内容一致，但前端不应该依赖后端字典的完整性，在 SSE 事件里附带 label 和 color 已经解决了实时展示的问题，这里的映射是兜底，防止事件字段缺失。
const LABEL_MAP: Record<string, { label: string; color: string }> = {
    knowledge_qa: { label: '知识问答', color: '#2563eb' },
    order_query: { label: '订单查询', color: '#059669' },
    complaint_handle: { label: '投诉处理', color: '#dc2626' },
    ticket_create: { label: '工单创建', color: '#d97706' },
    refund_advice: { label: '退款建议', color: '#7c3aed' },
    transfer_human: { label: '转人工', color: '#6b7280' },
}

const props = defineProps<{
    intent: string
    confidence: number
    reasoning: string
    needHuman: boolean
    // SSE 事件里已经包含了 label 和 color，优先用事件里的值
    label?: string
    color?: string
}>()

const emit = defineEmits<{
    transferToHuman: []
    dismissWarning: []
}>()

const displayLabel =
    props.label || LABEL_MAP[props.intent]?.label || props.intent
const displayColor =
    props.color || LABEL_MAP[props.intent]?.color || '#6b7280'
</script>

<template>
    <div class="intent-card" :class="{ 'low-confidence': needHuman }">
        <div class="intent-header">
            <span class="intent-tag"
                :style="{ backgroundColor: displayColor + '18', color: displayColor, borderColor: displayColor + '40' }">{{
                    displayLabel }}</span>
            <span class="intent-confidence-label">置信度</span>
        </div>
        <ConfidenceBar :confidence="confidence" size="small" />
        <p v-if="reasoning" class="intent-reasoning">{{ reasoning }}</p>
        <div v-if="needHuman" class="intent-warning">
            <span class="warning-text">AI 对此判断把握较低，建议转接人工客服</span>
            <div class="warning-actions">
                <button class="warning-btn primary" @click="emit('transferToHuman')">转人工</button>
                <button class="warning-btn" @click="emit('dismissWarning')">忽略</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.intent-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13px;
}

.intent-card.low-confidence {
    border-color: #f59e0b;
    background: #fffbeb;
}

.intent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.intent-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid;
    line-height: 1.6;
}

.intent-confidence-label {
    font-size: 11px;
    color: #9ca3af;
}

.intent-reasoning {
    margin: 6px 0 0;
    color: #6b7280;
    font-size: 12px;
    line-height: 1.5;
}

.intent-warning {
    margin-top: 10px;
    padding: 8px 10px;
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

.warning-text {
    font-size: 12px;
    color: #92400e;
    font-weight: 500;
    flex: 1;
}

.warning-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
}

.warning-btn {
    padding: 4px 10px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    background: #fff;
    font-size: 12px;
    cursor: pointer;
    color: #374151;
    white-space: nowrap;
}

.warning-btn:hover {
    background: #f3f4f6;
}

.warning-btn.primary {
    background: #dc2626;
    color: #fff;
    border-color: #dc2626;
}

.warning-btn.primary:hover {
    background: #b91c1c;
}
</style>