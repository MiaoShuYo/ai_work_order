<script setup lang="ts">
import type { AssistantMessage } from "../../api/chat";
import IntentTag from "./IntentTag.vue";
import SuggestedActions from "./SuggestedActions.vue";
import ToolCallCard from "../tools/ToolCallCard.vue";

defineProps<{
    message: AssistantMessage
}>()

const emit = defineEmits<{
    selectAction: [action: string]
}>()
</script>

<template>
    <div class="answer-card">
        <div v-if="!message.pending" class="answer-header">
            <IntentTag :intent="message.intent" />
            <span v-if="message.needHuman" class="human-alert">建议转人工</span>
        </div>
        <div v-for="(toolCall, index) in message.toolCalls" :key="index">
            <ToolCallCard :tool-call="toolCall" />
        </div>
        <p v-if="message.pending && !message.answer" class="answer-pending">AI 正在思考…</p>
        <p v-else class="answer-text">{{ message.answer }}</p>
        <div v-if="!message.pending" class="confidence-row">
            <span class="confidence-label">置信度 {{ Math.round(message.confidence * 100) }}%</span>
            <div class="confidence-bar">
                <div class="confidence-fill" :class="{ low: message.confidence < 0.6 }"
                    :style="{ width: `${message.confidence * 100}%` }" />
            </div>
        </div>
        <SuggestedActions v-if="!message.pending" :actions="message.suggestedActions"
            @select="emit('selectAction', $event)" />
    </div>
</template>

<style scoped>
.answer-card {
  max-width: 70%;
  padding: 12px 14px;
  border-radius: 8px;
  background-color: #f1f5f9;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.human-alert {
  font-size: 12px;
  color: #dc2626;
  font-weight: 600;
}

.answer-pending {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}

.answer-text {
  margin: 0 0 8px;
  white-space: pre-wrap;
  word-break: break-word;
  color: #1f2937;
}

.confidence-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-label {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.confidence-bar {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background-color: #e5e7eb;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background-color: #2563eb;
  transition: width 0.2s ease;
}

.confidence-fill.low {
  background-color: #f59e0b;
}
</style>