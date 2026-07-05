<script setup lang="ts">
import type { ToolCall } from '../../api/chat'
import OrderInfoCard from '../business/OrderInfoCard.vue'

defineProps<{
    toolCall: ToolCall
}>()

// 目前只有订单查询这一个工具，这里按工具名做一次映射，后面接入工单、用户、知识库等更多工具之后，这回映射会扩成一张“工具->参数展示文案”的表
const ARG_LABEL: Record<string, string> = {
    query_order: '订单号'
}

</script>

<template>
    <div class="tool-call-card">
        <div class="tool-call-header">
            <span class="tool-call-icon">🔧</span>
            <span v-if="toolCall.status === 'calling'">AI 正在调用工具：{{ toolCall.name }}</span>
            <span v-else>工具调用完成：{{ toolCall.name }}</span>
        </div>
        <div v-if="toolCall.status === 'calling'" class="tool-call-args">
            {{ ARG_LABEL[toolCall.name] ?? '参数' }}：{{ Object.values(toolCall.args)[0] }}
        </div>
        <OrderInfoCard v-else-if="toolCall.name === 'query_order' && toolCall.result" :order="toolCall.result" />
    </div>
</template>

<style scoped>
.tool-call-card {
  margin-bottom: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 13px;
}

.tool-call-icon {
  font-size: 14px;
}

.tool-call-header {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
}

.tool-call-args {
  margin-top: 4px;
  color: #64748b;
}
</style>