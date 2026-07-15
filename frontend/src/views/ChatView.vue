<script setup lang="ts">
import { ref } from 'vue'
import { streamChatMessage, type AssistantMessage, type ChatMessage } from '../api/chat'
import { useTaskContext } from '../composables/useTaskContext'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import ContextPanel from '../components/context/ContextPanel.vue'
import SourceList from '../components/rag/SourceList.vue'
import SourceDrawer from '../components/rag/SourceDrawer.vue'

interface SourceInfo {
  index: number
  filename: string
  chunk_index: number
  content: string
  score: number
  page?: number | null
}

const { recordToolCall } = useTaskContext()

const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const errorMessage = ref('')

// 引用来源抽屉的状态
const drawerVisible = ref(false)
const selectedSource = ref<SourceInfo | null>(null)

function onSelectSource(source: SourceInfo) {
  selectedSource.value = source
  drawerVisible.value = true
}

function onCloseDrawer() {
  drawerVisible.value = false
  selectedSource.value = null
}

function createPendingMessage(): AssistantMessage {
  return {
    role: 'assistant',
    intent: 'other',
    answer: '',
    confidence: 0,
    needHuman: false,
    suggestedActions: [],
    toolCalls: [],
    pending: true,
  }
}

async function handleSend(text: string) {
  errorMessage.value = ''
  messages.value.push({ role: 'user', content: text })

  const pendingMessage = createPendingMessage()
  messages.value.push(pendingMessage)
  loading.value = true

  try {
    await streamChatMessage(messages.value.slice(0, -1), {
      onToolCallStart(name, args) {
        const label =
          name === 'search_knowledge_base'
            ? '正在检索知识库…'
            : `正在调用 ${name}…`
        pendingMessage.toolCalls.push({ name, args, status: 'calling', label } as any)
      },
      onToolCallEnd(name, args, result) {
        const target = pendingMessage.toolCalls.find(
          (call) => call.name === name && call.status === 'calling',
        )
        if (target) {
          target.status = 'done'
          target.result = result
        }
        // 上下文面板要跨越整个会话持续展示最新的用户、订单、工单信息
        recordToolCall(name, args, result)
      },
      onFinal(finalMessage) {
        const index = messages.value.indexOf(pendingMessage)
        if (index !== -1) {
          messages.value[index] = { ...finalMessage, pending: false }
        }
      },
      onSources(sourcesData) {
        // sources 事件在 final 之后到达，挂到对应的 assistant 消息上
        const lastAssistantMsg = [...messages.value].reverse().find(
          (m) => m.role === 'assistant',
        )
        if (lastAssistantMsg) {
          ; (lastAssistantMsg as any).sources = sourcesData.sources
        }
      },
      onError(message) {
        errorMessage.value = message
      },
    })
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '发送失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function handleSelectAction(action: string) {
  window.alert(`已记录建议操作：${action}，工具调用能力将在后续接入`)
}
</script>

<template>
  <div class="chat-view">
    <aside class="session-sidebar">
      <div class="session-item active">默认会话</div>
    </aside>
    <section class="chat-main">
      <MessageList :messages="messages" @select-action="handleSelectAction" @select-source="onSelectSource" />
      <p v-if="errorMessage" class="error-tip">{{ errorMessage }}</p>
      <ChatInput :loading="loading" @send="handleSend" />
    </section>
    <ContextPanel />
    <!-- 引用来源详情抽屉 -->
    <SourceDrawer :source="selectedSource" :visible="drawerVisible" @close="onCloseDrawer" />
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
}

.session-sidebar {
  width: 220px;
  border-right: 1px solid #e5e7eb;
  padding: 16px;
}

.session-item {
  padding: 8px 12px;
  border-radius: 6px;
}

.session-item.active {
  background-color: #eff6ff;
  color: #2563eb;
}

.chat-main {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.error-tip {
  margin: 0 16px 8px;
  color: #dc2626;
  font-size: 13px;
}
</style>