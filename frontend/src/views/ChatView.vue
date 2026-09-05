<script setup lang="ts">
import { ref } from 'vue'
import { streamChatMessage, type AssistantMessage, type ChatMessage } from '../api/chat'
import { useTaskContext } from '../composables/useTaskContext'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import ContextPanel from '../components/context/ContextPanel.vue'
import SourceList from '../components/rag/SourceList.vue'
import SourceDrawer from '../components/rag/SourceDrawer.vue'
import IntentResultCard from '../components/intent/IntentResultCard.vue'

// intent 事件的类型定义和 api/chat.ts 里的 IntentData 保持一致
interface IntentInfo {
  intent: string
  confidence: number
  reasoning: string
  need_human: boolean
  label: string
  color: string
}

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

// 意图识别相关状态
const currentIntent = ref<IntentInfo | null>(null)
const bannerDismissed = ref(false)  // 顶部转人工横幅的关闭状态

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

// 关闭意图卡片（不影响顶部横幅）
function onDismissIntent() {
  currentIntent.value = null
}

// 关闭顶部横幅
function onDismissBanner() {
  bannerDismissed.value = true
}

// 转人工操作：目前为占位实现，记录到控制台，Day 15 对接审批流程后替换为正式接口调用
function onTransferToHuman() {
  console.log('[Intent] 用户确认转人工，当前意图：', currentIntent.value)
  // TODO Day 15：调用转人工接口，创建审批记录
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
  currentIntent.value = null  // 新消息发出后重置意图状态
  bannerDismissed.value = false
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
      onIntent(IntentData) {
        // 意图识别结果到达，更新响应式状态驱动 UI 渲染
        currentIntent.value = IntentData
        // 如果是转人工意图且置信度较高，自动触发转人工流程
        if (IntentData.intent === 'transfer_human' && IntentData.confidence >= 0.7) {
          onTransferToHuman()
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
      <!-- 低置信度持续提示横幅：need_human 为 true 且未被关闭时显示 -->
      <div v-if="currentIntent?.need_human && !bannerDismissed" class="intent-banner">
        <span class="banner-icon">⚠️</span>
        <span class="banner-text">
          AI 对本次对话的意图判断把握较低（置信度 {{ (currentIntent.confidence * 100).toFixed(0) }}%），建议转接人工客服以确保处理准确。
        </span>
        <button class="banner-btn primary" @click="onTransferToHuman">转人工</button>
        <button class="banner-close" @click="onDismissBanner">✕</button>
      </div>
      <!-- 意图识别结果卡片：每次对话开始时展示，可手动关闭 -->
      <IntentResultCard v-if="currentIntent" :intent="currentIntent.intent" :confidence="currentIntent.confidence"
        :reasoning="currentIntent.reasoning" :need-human="currentIntent.need_human" :label="currentIntent.label"
        :color="currentIntent.color" @transfer-to-human="onTransferToHuman" @dismiss-warning="onDismissIntent" />
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

/* 低置信度转人工横幅 */
.intent-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #fef3c7;
  border-bottom: 2px solid #f59e0b;
  font-size: 13px;
  flex-shrink: 0;
}

.banner-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.banner-text {
  flex: 1;
  color: #92400e;
  line-height: 1.4;
}

.banner-btn {
  padding: 5px 14px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #fff;
  font-size: 12px;
  cursor: pointer;
  color: #374151;
  white-space: nowrap;
  flex-shrink: 0;
}

.banner-btn:hover {
  background: #f3f4f6;
}

.banner-btn.primary {
  background: #dc2626;
  color: #fff;
  border-color: #dc2626;
}

.banner-btn.primary:hover {
  background: #b91c1c;
}

.banner-close {
  background: none;
  border: none;
  font-size: 16px;
  color: #92400e;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.banner-close:hover {
  background: #fde68a;
}

.error-tip {
  margin: 0 16px 8px;
  color: #dc2626;
  font-size: 13px;
}
</style>