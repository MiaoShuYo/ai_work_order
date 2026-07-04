<script setup lang="ts">
import { ref } from 'vue'
import { sendChatMessage, type ChatMessage } from '../api/chat'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'

const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const errorMessage = ref('')

async function handleSend(text: string) {
    errorMessage.value = ''
    messages.value.push({ role: 'user', content: text })
    loading.value = true
    try {
        // 把目前为止的完整对话历史发给后端，多轮上下文靠这份历史撑起来
        // 后端今天不维护任何会话状态
        const assistantMessage = await sendChatMessage(messages.value)
        messages.value.push(assistantMessage)
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : '发送失败，请稍后重试'
    } finally {
        loading.value = false
    }
}

function handleSelectAction(action: string) {
    // 真正触发工具调用是第 4 天要接入的能力，今天先用弹窗占位，把交互路径提前搭好，后面只需要替换这个函数的实现。
  window.alert(`已记录建议操作：${action}，工具调用能力将在后续接入`)
}
</script>

<template>
    <div class="chat-view">
        <aside class="session-sidebar">
            <div class="session-item active">默认会话</div>
        </aside>
        <section class="chat-main">
            <MessageList :messages="messages" @selectAction="handleSelectAction" />
            <p v-if="errorMessage" class="error-tip">
                {{ errorMessage }}
            </p>
            <ChatInput :loading="loading" @send="handleSend" />
        </section>
    </div>
</template>
<style scoped>
.chat-view{
    display: flex;
    height: 100vh;
}
.session-sidebar{
    width: 220px;
    border-right: 1px solid #e5e7eb;
    padding: 16px;
}
.session-item{
    padding: 8px 12px;
    border-radius: 6px;
}
.session-item.active{
    background-color: #eff6ff;
    color: #2563eb;
}
.chat-main{
    display: flex;
    flex-direction: column;
    flex: 1;
}
.error-tip{
    margin: 0 16px 8px;
    color: #dc2626;
    font-size: 13px;
}
</style>