<script setup lang="ts">
import { computed, type Component } from 'vue'
import OrderInfoCard from '../business/OrderInfoCard.vue'
import TicketInfoCard from '../business/TicketInfoCard.vue'
import UserInfoCard from '../business/UserInfoCard.vue'
import RetrievalResultCard from '../rag/RetrievalResultCard.vue'

const props = defineProps<{
    toolName: string
    result: Record<string, any>
}>()

// 按工具名选择对应的详情卡片，知识库检索的展示组件今天从 KnowledgeCard 换成 RetrievalResultCard，后者内置了分数展示和点击展开原文的能力，更适合向量检索的返回结构。
const component = computed(() => {
    const map: Record<string, any> = {
        query_order: OrderInfoCard,
        query_ticket: TicketInfoCard,
        query_user: UserInfoCard,
        search_knowledge_base: RetrievalResultCard,
    }
    return map[props.toolName] || null
})

const cardData = computed(() => {
    // 知识库检索的返回结构是 { snippets: [...] }，直接传给 RetrievalResultCard 的 snippets prop，其他三个工具的返回结构本身就是对应卡片需要的 data prop，直接透传即可。
    if (props.toolName === 'search_knowledge_base') {
        return { snippets: props.result?.snippets || [] }
    }
    return { data: props.result }
})

</script>

<template>
    <component v-if="component" :is="component" v-bind="cardData" />
    <pre v-else class="raw-result">{{ JSON.stringify(result, null, 2) }}</pre>
</template>