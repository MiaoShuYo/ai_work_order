<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import {
  streamChatMessage,
  type AssistantMessage,
  type ChatMessage,
  type Intent,
  type IntentData,
  type SourceInfo,
} from '../api/chat'
import { fetchMessages, type SessionMessageItem } from '../api/sessions'
import { useSessionStore } from '../stores/sessionStore'
import { useTaskContext } from '../composables/useTaskContext'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import SessionList from '../components/chat/SessionList.vue'
import ContextPanel from '../components/context/ContextPanel.vue'
import SourceDrawer from '../components/rag/SourceDrawer.vue'
import IntentResultCard from '../components/intent/IntentResultCard.vue'

interface IntentInfo {
  intent: string
  confidence: number
  reasoning: string
  need_human: boolean
  label: string
  color: string
}

const { recordToolCall } = useTaskContext()
const sessionStore = useSessionStore()

const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const errorMessage = ref('')

const currentIntent = ref<IntentInfo | null>(null)
const bannerDismissed = ref(false)

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

function onDismissIntent() {
  currentIntent.value = null
}

function onDismissBanner() {
  bannerDismissed.value = true
}

function onTransferToHuman() {
  console.log('[Intent] 用户确认转人工，当前意图：', currentIntent.value)
  // TODO Day 15：调用转人工接口，创建审批记录
}

// 历史消息还原，接口 schema 与界面 AssistantMessage 之间唯一的转换点
function restoreMessages(items: SessionMessageItem[]): ChatMessage[] {
  return items.map((item) => {
    if (item.role === 'user') {
      return { role: 'user', content: item.content }
    }
    return {
      role: 'assistant',
      intent: (item.intent as Intent | undefined) ?? 'general_inquiry',
      answer: item.content,
      confidence: item.confidence ?? 0,
      needHuman: item.need_human ?? false,
      suggestedActions: item.suggested_actions ?? [],
      toolCalls: (item.tool_calls ?? []).map((call) => ({
        name: call.name,
        args: call.args,
        result: call.result,
        status: 'done' as const,
      })),
      sources:
        item.sources && item.sources.length > 0
          ? (item.sources as unknown as SourceInfo[])
          : undefined,
      pending: false,
    }
  })
}

async function loadMessages(sessionId: string) {
  errorMessage.value = ''
  try {
    const items = await fetchMessages(sessionId)
    messages.value = restoreMessages(items)
  } catch (error) {
    messages.value = []
    errorMessage.value = error instanceof Error ? error.message : '历史消息加载失败'
  }
}

// 当前会话变化时重新加载历史，新建、切换、删除当前会话都会触发
watch(
  () => sessionStore.state.currentSessionId,
  (newId, oldId) => {
    if (!newId || newId === oldId) return
    currentIntent.value = null
    bannerDismissed.value = false
    selectedSource.value = null
    drawerVisible.value = false
    void loadMessages(newId)
  },
)

onMounted(async () => {
  await sessionStore.initSessions()
  if (sessionStore.state.currentSessionId) {
    await loadMessages(sessionStore.state.currentSessionId)
  }
})

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
  const sessionId = sessionStore.state.currentSessionId
  if (!sessionId) {
    errorMessage.value = '会话尚未准备好，请稍后重试'
    return
  }

  errorMessage.value = ''
  currentIntent.value = null
  bannerDismissed.value = false
  messages.value.push({ role: 'user', content: text })

  const pendingMessage = createPendingMessage()
  messages.value.push(pendingMessage)
  loading.value = true

  try {
    // 只传会话 ID 和当前一条，历史由后端从库里恢复，不再回传 messages 数组
    await streamChatMessage(sessionId, text, {
      onToolCallStart(name, args) {
        const label =
          name === 'search_knowledge_base' ? '正在检索知识库…' : `正在调用 ${name}…`
        pendingMessage.toolCalls.push({ name, args, status: 'calling', label } as any)
      },
      onToolCallEnd(name, _args, result) {
        const target = pendingMessage.toolCalls.find(
          (call) => call.name === name && call.status === 'calling',
        )
        if (target) {
          target.status = 'done'
          target.result = result
        }
        recordToolCall(name, _args, result)
      },
      onIntent(data: IntentData) {
        currentIntent.value = {
          intent: data.intent,
          confidence: data.confidence,
          reasoning: data.reasoning,
          need_human: data.need_human,
          label: data.label,
          color: data.color,
        }
        // Day 11 的规则保持不变，明确要转人工且置信度较高时直接触发占位流程
        if (data.intent === 'transfer_human' && data.confidence >= 0.7) {
          onTransferToHuman()
        }
      },
      onFinal(finalMessage) {
        const index = messages.value.indexOf(pendingMessage)
        if (index !== -1) {
          messages.value[index] = { ...finalMessage, pending: false }
        }
      },
      onSources(sourcesData) {
        const lastAssistant = [...messages.value]
          .reverse()
          .find((message) => message.role === 'assistant')
        if (lastAssistant) {
          ; (lastAssistant as AssistantMessage).sources = sourcesData.sources
        }
      },
      onSessionMeta(meta) {
        // 标题和工单关联回填到左侧列表，列表项会从"新会话"实时变成真实标题
        sessionStore.patchSessionMeta(meta.session_id, {
          title: meta.title,
          ticket_no: meta.ticket_no,
        })
      },
      onError(message) {
        // 错误处理沿用 Day 11 的行为，只展示错误文案不移除消息。
        // 区别是用户消息此刻已经落库，切换会话再切回来会以历史消息重现。
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
    <!-- Day 2 起写死的默认会话栏，今天替换为真正的会话列表组件 -->
    <SessionList :disabled="loading" />

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

    <SourceDrawer :source="selectedSource" :visible="drawerVisible" @close="onCloseDrawer" />
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
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