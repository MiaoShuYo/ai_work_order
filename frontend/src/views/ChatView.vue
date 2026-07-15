<script setup lang="ts">
import { ref } from 'vue'
import { streamChatMessage, type AssistantMessage, type ChatMessage } from '../api/chat'
import { useTaskContext } from '../composables/useTaskContext'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import ContextPanel from '../components/context/ContextPanel.vue'

const { recordToolCall } = useTaskContext()

const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const errorMessage = ref('')

function onToolCallStart(name: string, args: Record<string, any>) {
  // 对知识库检索使用更具体的提示文案，让客服明确知道系统正在翻公司资料而不是做别的操作 
  const label = name === 'search_knowledge_base' ? '正在检索知识库…' : `正在调用 ${name}…`

  messages.value.push({
    id: crypto.randomUUID(),
    role: 'assistant',
    content: '',
    toolCalls: [{ name, args, result: null, label }],
    timestamp: Date.now(),
  } as any)
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
    // 发给后端的历史消息要去掉刚推入的占位消息本身，它的 answer 还是空字符串，带上去只会在对话历史里插入一条没有意义的空白 AI 回复。
    await streamChatMessage(messages.value.slice(0, -1), {
      onToolCallStart(name, args) {
        onToolCallStart(name,args)
      },
      onToolCallEnd(name, args, result) {
        // 按工具名加状态反查刚才 push 进去的那条记录并原地更新，而不是重新 push 一条，避免同一次调用在卡片上重复出现两行。
        const target = pendingMessage.toolCalls.find(
          (call) => call.name === name && call.status === 'calling',
        )
        if (target) {
          target.status = 'done'
          target.result = result
        }
        // 上下文面板要跨越整个会话持续展示最新的用户、订单、工单信息，这份记录独立于当前这条消息的 toolCalls，写进 useTaskContext 维护的全局状态里。
        recordToolCall(name, args, result)
      },
      onFinal(finalMessage) {
        // 找到占位消息在数组中的索引，用新消息替换它以触发 Vue 响应式更新
        const index = messages.value.indexOf(pendingMessage)
        if (index !== -1) {
          messages.value[index] = { ...finalMessage, pending: false }
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
      <MessageList :messages="messages" @select-action="handleSelectAction" />
      <p v-if="errorMessage" class="error-tip">{{ errorMessage }}</p>
      <ChatInput :loading="loading" @send="handleSend" />
    </section>
    <ContextPanel />
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