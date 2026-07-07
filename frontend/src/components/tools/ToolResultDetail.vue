<script setup lang="ts">
import type { Component } from 'vue'
import OrderInfoCard from '../business/OrderInfoCard.vue'
import TicketInfoCard from '../business/TicketInfoCard.vue'
import UserInfoCard from '../business/UserInfoCard.vue'
import KnowledgeCard from '../business/KnowledgeCard.vue'

defineProps<{
    name: string
    result: Record<string, unknown>
}>()

// 工具名到详情卡片组的映射表，新增工具时只需要在这里补一行，ToolCallCard.vue 和 ContextPanel.vue 两处调用都不用跟着改判断逻辑。
const DETAIL_COMPONENTS: Record<string, Component> = {
    query_order: OrderInfoCard,
    query_ticket: TicketInfoCard,
    query_user: UserInfoCard,
    search_knowledge_base: KnowledgeCard,
}
</script>

<template>
    <component :is="DETAIL_COMPONENTS[name]" v-if="DETAIL_COMPONENTS[name]" :data="result"></component>
</template>