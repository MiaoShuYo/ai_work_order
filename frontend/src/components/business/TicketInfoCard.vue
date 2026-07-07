<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    data: Record<string, unknown>
}>()

const STATUS_COLOR: Record<string, string> = {
    待处理: '#f59e0b',
    处理中: '#2563eb',
    已解决: '#059669',
    已关闭: '#6b7280',
}

const PRIORITY_COLOR: Record<string, string> = {
    低: '#6b7280',
    中: '#2563eb',
    高: '#f59e0b',
    紧急: '#dc2626',
}

const ticketNo = computed(() => String(props.data.ticket_no ?? ''))
const title = computed(() => String(props.data.title ?? ''))
const status = computed(() => String(props.data.status ?? ''))
const priority = computed(() => String(props.data.priority ?? ''))
const assignee = computed(() => String(props.data.assignee ?? ''))
const hasError = computed(() => typeof props.data.error === 'string')
</script>

<template>
    <div v-if="hasError" class="ticket-card ticket-card-error">{{ data.error }}</div>
    <div v-else class="ticket-card">
        <div class="ticket-row">
            <span class="ticket-label">工单号</span>
            <span>{{ ticketNo }}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">标题</span>
            <span>{{ title }}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">状态</span>
            <span :style="{ color: STATUS_COLOR[status] ?? '#374151' }">{{ status }}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">优先级</span>
            <span :style="{ color: PRIORITY_COLOR[priority] ?? '#374151' }">{{ priority }}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">负责人</span>
            <span>{{ assignee }}</span>
        </div>
    </div>
</template>

<style scoped>
.ticket-card {
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 6px;
    background-color: #fff;
    border: 1px solid #e5e7eb;
}

.ticket-card-error {
    color: #dc2626;
}

.ticket-row {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
    font-size: 13px;
}

.ticket-label {
    color: #6b7280;
}
</style>