<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { ChatMessage } from '../../api/chat'

const props = defineProps<{
    messages: ChatMessage[]
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
            <div class="message-bubble">
                {{ message.content }}
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
.message-item.user{
    justify-content: flex-end;
}
.message-item.assistant{
    justify-content: flex-start;
}
.message-bubble {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 8px;
    white-space: pre-wrap;
    word-break: break-word;
}
.message-item.user .message-bubble {
    background-color: #2563eb;
    color: #fff;
}
.message-item.assistant .message-bubble {
    background-color: #f1f5f9;
    color: #1f2937;
}
</style>