<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { fetchTicketDetail, type TicketDetail } from '../api/tickets'
import UserInfoCard from '../components/business/UserInfoCard.vue'
import OrderInfoCard from '../components/business/OrderInfoCard.vue'
import PaymentInfoCard from '../components/business/PaymentInfoCard.vue'
import LogisticsInfoCard from '../components/business/LogisticsInfoCard.vue'
import TicketInfoCard from '../components/business/TicketInfoCard.vue'

const route = useRoute()
const detail = ref<TicketDetail | null>(null)
const loading = ref(false)
const error = ref('')

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

// business 目录的旧卡片 prop 声明成 Record<string, unknown>，后端返回的对象在运行时就是这个形态，跨类型边界时统一在这里收窄一次
function toRecord(value: unknown): Record<string, unknown> {
    return (value ?? {}) as Record<string, unknown>
}

async function fetchDetail() {
    const ticketNo = String(route.params.ticket_no ?? '')
    if (!ticketNo) {
        error.value = '缺少工单号'
        return
    }
    loading.value = true
    error.value = ''
    try {
        detail.value = await fetchTicketDetail(ticketNo)
    } catch (e) {
        // 404 时 http 拦截器会把 detail 里的"工单 xxx 不存在"抛出来，直接展示
        detail.value = null
        error.value = e instanceof Error ? e.message : '工单详情加载失败'
    } finally {
        loading.value = false
    }
}

// 历史工单点击后仍在详情页内跳转，Vue Router 会复用当前组件实例，不 watch 路由参数的话页面内容不会刷新，会一直停留在上一张工单
watch(() => route.params.ticket_no, fetchDetail)

onMounted(fetchDetail)
</script>

<template>
    <div class="detail-page">
        <RouterLink to="/tickets" class="back-linl">← 返回工单列表</RouterLink>
        <div v-if="loading" class="state-tip">工单加载中......</div>
        <div v-else-if="error" class="state-tip error-tip">{{ error }}</div>
        <template v-else-if="detail">
            <header class="problem-block">
                <span class="problem-label">当前问题</span>
                <h2 class="problem-title">{{ detail.ticket.title }}</h2>
                <div class="problem-meta">
                    <span class="pill"
                        :style="{ color: STATUS_COLOR[detail.ticket.status] ?? '#374151', borderColor: STATUS_COLOR[detail.ticket.status] ?? '#d1d5db' }">{{
                            detail.ticket.status }}</span>
                    <span class="pill"
                        :style="{ color: PRIORITY_COLOR[detail.ticket.priority] ?? '#374151', borderColor: PRIORITY_COLOR[detail.ticket.priority] ?? '#d1d5db' }">{{
                            detail.ticket.priority }}</span>
                    <span class="meta-text">工单号 {{ detail.ticket.ticket_no }}</span>
                    <span class="meta-text">负责人 {{ detail.ticket.assignee }}</span>
                    <span class="meta-text">关联订单 {{ detail.ticket.order_no ?? '未关联' }}</span>
                </div>
            </header>
        </template>
        <div class="blocks-grid">
            <section class="block">
                <h3 class="blolk-title">用户信息</h3>
                <UserInfoCard v-if="detail?.user" :data="toRecord(detail.user)" />
                <p v-else class="block-empty">该工单暂未关联用户。</p>
            </section>

            <section class="block">
                <h3 class="block-title">订单信息</h3>
                <OrderInfoCard v-if="detail?.order" :data="toRecord(detail.order)" />
                <p v-else class="block-empty">该工单暂未关联订单。</p>
            </section>
            <!-- 支付与物流都是订单的下钻信息，订单不存在时这两个区块整体不渲染 -->
            <section v-if="detail?.order" class="block">
                <h3 class="block-title">支付流水</h3>
                <PaymentInfoCard :data="detail.payments" />
            </section>
            <section v-if="detail?.order" class="block">
                <h3 class="blocl-title">物流状态</h3>
                <LogisticsInfoCard v-if="detail.logistics" :data="detail.logistics" />
                <p v-else class="block-empty">该订单暂无物流轨迹。</p>
            </section>
            <section class="block block-history">
                <h3 class="block-title">历史工单</h3>
                <p v-if="detail?.history.length === 0" class="block-empty">该用户暂无其他工单。</p>
                <RouterLink v-for="item in detail?.history" v-else :key="item.ticket_no"
                    :to="`/tickets/${item.ticket_no}`" class="history-link">
                    <TicketInfoCard :data="toRecord(item)" />
                </RouterLink>
            </section>
        </div>
    </div>
</template>

<style scoped>
.detail-page {
    max-width: 1000px;
    margin: 0 auto;
    padding: 16px 24px 40px;
}

.back-link {
    display: inline-block;
    margin-bottom: 12px;
    color: #2563eb;
    text-decoration: none;
    font-size: 13px;
}

.back-link:hover {
    text-decoration: underline;
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

.problem-block {
    padding: 16px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    margin-bottom: 12px;
}

.problem-label {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 12px;
    line-height: 20px;
}

.problem-title {
    margin: 8px 0;
    font-size: 18px;
    color: #111827;
}

.problem-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    color: #6b7280;
}

.meta-text {
    color: #6b7280;
}

.blocks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 12px;
    align-items: start;
}

.block {
    padding: 12px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
}

.block-history {
    grid-column: 1 / -1;
}

.block-title {
    margin: 0 0 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f3f4f6;
    font-size: 14px;
    color: #374151;
}

.block-empty {
    margin: 0;
    padding: 8px 0;
    color: #9ca3af;
    font-size: 13px;
}

.history-link {
    display: block;
    text-decoration: none;
    color: inherit;
}

.history-link:hover .ticket-card {
    border-color: #2563eb;
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