<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { ChatMessage } from '../../api/chat'
import AnswerCard from './AnswerCard.vue'
import SourceList from '../rag/SourceList.vue'

interface SourceInfo {
    index: number
    filename: string
    chunk_index: number
    content: string
    score: number
    page?: number | null
}

const props = defineProps<{
    messages: ChatMessage[]
}>()

const emit = defineEmits<{
    selectAction: [action: string]
    selectSource: [source: SourceInfo]
}>()

const listRef = ref<HTMLDivElement | null>(null)

// 消息数组变化后要等 DOM 更新完再滚动，直接在这里滚会滚到旧的高度上
watch(
    () => props.messages.length,
    async () => {
        await nextTick()
        if (listRef.value) {
            listRef.value.scrollTop = listRef.value.scrollHeight
        }
    },
)
</script>

<template>
    <div ref="listRef" class="message-list">
        <div v-for="(message, index) in props.messages" :key="index" class="message-item" :class="message.role">
            <div v-if="message.role === 'user'" class="message-bubble">{{ message.content }}</div>
            <div v-else class="assistant-block">
                <AnswerCard :message="message" @selectAction="emit('selectAction', $event)" />
                <SourceList
                    v-if="(message as any).sources"
                    :sources="(message as any).sources"
                    @select="emit('selectSource', $event)"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-item {
  display: flex;
  margin-bottom: 12px;
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  min-width: 0;
  overflow: hidden;
  padding: 10px 14px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  background-color: #2563eb;
  color: #fff;
}
</style>