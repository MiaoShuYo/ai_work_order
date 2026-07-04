<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
    loading: boolean
}>()

const emit = defineEmits<{
    send: [text: string]
}>()

const draft = ref('')

function handleSend() {
    const text = draft.value.trim()
    if (!text) return
    emit('send', text)
    draft.value = ''
}

function handleKeydown(event: KeyboardEvent) {
    // 回车发送，shift+回车换行，是聊天类输入框的通用交互习惯
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        handleSend()
    }
}
</script>

<template>
    <div class="chat-input">
        <textarea v-model="draft" class="chat-textarea" placeholder="输入你的问题，按 Enter 发送，Shift + Enter 换行" rows="2"
            @keydown="handleKeydown" />
        <button class="send-button" :disabled="loading || !draft.trim()" @click="handleSend">
            {{ loading ? '发送中...' : '发送' }}
        </button>
    </div>
</template>

<style scoped>
.chat-input {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid #e5e7eb;
}

.chat-textarea {
    flex: 1;
    resize: none;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
}

.send-button {
    padding: 0px 20px;
    border: none;
    border-radius: 6px;
    background-color: #2563eb;
    color: #fff;
    cursor: pointer;
}
.send-button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
}
</style>