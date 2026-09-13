<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listTickets, type TicketListItem } from '../api/tickets'
import router from '@/router'
import { RouterLink } from 'vue-router'

const tickets = ref<TicketListItem[]>([])
const loading = ref(false)
const error = ref('')
// 状态、优先级的取色沿用 business 卡片里的同一套色板，保证同一语义在列表和卡片里颜色一致
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

async function fetchTickets() {
    loading.value = true
    error.value = ''
    try {
        tickets.value = await listTickets()
    } catch (e) {
        // http 拦截器已经把 axios 错误转成后端 detail 文本，这里直接展示
        error.value = e instanceof Error ? e.message : '工单列表加载失败'
    } finally {
        loading.value = false
    }
}

onMounted(fetchTickets)
</script>

<template>
    <div class="tickets-page">
        <div class="page-header">
            <h2 class="page-title">工单列表</h2>
            <button class="refresh-btn" @click="fetchTickets">刷新</button>
        </div>
        <div v-if="loading" class="state-tip">工单加载中.....</div>
        <div v-else-if="error" class="state-tip error-tip">{{ error }}</div>
        <div v-else-if="tickets.length === 0" class="state-tip">暂无工单</div>
        <div v-else class="ticket-table">
            <thead>
                <tr>
                    <th>工单号</th>
                    <th>标题</th>
                    <th>状态</th>
                    <th>优先级</th>
                    <th>负责人</th>
                    <th>报障用户</th>
                    <th>关联订单</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="ticket in tickets" :key="ticket.ticket_no" class="ticket-row">
                    <td>
                        <RouterLink :to="`/tickets/${ticket.ticket_no}`" class="row-link">{{ ticket.ticket_no }}
                        </RouterLink>
                    </td>
                    <td class="cell-title">{{ ticket.title }}</td>
                    <td>
                        <span class="pill"
                            :style="{ color: STATUS_COLOR[ticket.status] ?? '#374151', borderColor: STATUS_COLOR[ticket.status] ?? '#d1d5db' }">{{
                                ticket.status }}</span>
                    </td>
                    <td>
                        <span class="pill"
                            :style="{ color: PRIORITY_COLOR[ticket.priority] ?? '#374151', borderColor: PRIORITY_COLOR[ticket.priority] ?? '#d1d5db' }">{{
                                ticket.priority }}</span>
                    </td>
                    <td>{{ ticket.assignee }}</td>
                    <td>{{ ticket.user_name ?? '—' }}</td>
                    <td>{{ ticket.order_no ?? '—' }}</td>
                </tr>
            </tbody>
        </div>
    </div>
</template>

<style scoped>
.tickets-page {
    max-width: 960px;
    margin: 0 auto;
    padding: 16px 24px 40px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.page-title {
    margin: 0;
    font-size: 18px;
    color: #111827;
}

.refresh-btn {
    padding: 5px 14px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    background: #fff;
    font-size: 13px;
    color: #374151;
    cursor: pointer;
}

.refresh-btn:hover {
    background: #f3f4f6;
}

.state-tip {
    padding: 24px 0;
    text-align: center;
    color: #6b7280;
    font-size: 14px;
}

.error-tip {
    color: #dc2626;
}

.ticket-table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 13px;
}

.ticket-table th {
    padding: 10px 12px;
    text-align: left;
    color: #6b7280;
    font-weight: 500;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
}

.ticket-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
}

.ticket-table tbody tr:last-child td {
    border-bottom: none;
}

.ticket-row:hover {
    background: #f9fafb;
}

.cell-title {
    color: #111827;
}

.row-link {
    color: #2563eb;
    text-decoration: none;
}

.row-link:hover {
    text-decoration: underline;
}

.pill {
    display: inline-block;
    padding: 1px 8px;
    border: 1px solid;
    border-radius: 999px;
    font-size: 12px;
    line-height: 18px;
    white-space: nowrap;
}
</style>