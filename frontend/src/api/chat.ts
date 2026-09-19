export type Intent =
  | 'order_issue'
  | 'account_issue'
  | 'refund_request'
  | 'general_inquiry'
  | 'other'

export interface UserMessage {
  role: 'user'
  content: string
}

export interface ToolCall {
  name: string
  args: Record<string, unknown>
  result?: Record<string, unknown>
  status: 'calling' | 'done'
}

export interface SourceInfo {
  index: number
  filename: string
  chunk_index: number
  content: string
  score: number
  page?: number | null
}

export interface AssistantMessage {
  role: 'assistant'
  intent: Intent
  answer: string
  confidence: number
  needHuman: boolean
  suggestedActions: string[]
  toolCalls: ToolCall[]
  pending?: boolean
  sources?: SourceInfo[]
}

export type ChatMessage = UserMessage | AssistantMessage

// final 事件的载荷是后端 Pydantic 模型序列化的结果，字段仍是 Day 3 起约定的 snake_case，
// 这里保留一个 DTO 类型，在 switch 里做一次集中转换，组件层只接触 camelCase。
interface ChatResponseDto {
  intent: Intent
  answer: string
  confidence: number
  need_human: boolean
  suggested_actions: string[]
  tool_calls: { name: string; args: Record<string, unknown>; result: Record<string, unknown> }[]
}

export interface IntentData {
  intent: string
  confidence: number
  reasoning: string
  need_human: boolean
  label: string
  color: string
}

export interface SessionMetaData {
  session_id: string
  title: string
  ticket_no: string | null
}

interface StreamHandlers {
  onToolCallStart: (name: string, args: Record<string, unknown>) => void
  onToolCallEnd: (
    name: string,
    args: Record<string, unknown>,
    result: Record<string, unknown>,
  ) => void
  onFinal: (message: AssistantMessage) => void
  onSources?: (data: { conversation_id: string; sources: SourceInfo[] }) => void
  onIntent?: (data: IntentData) => void
  onSessionMeta?: (data: SessionMetaData) => void
  onError: (message: string) => void
}

interface SseEvent {
  event: string
  // 事件数据结构随事件类型变化，解析层不做强类型约束，由各 handler 自己收口
  data: any
}

function parseSseBuffer(buffer: string): { events: SseEvent[]; remainder: string } {
  const chunks = buffer.split('\n\n')
  const remainder = chunks.pop() ?? ''
  const events: SseEvent[] = []
  for (const chunk of chunks) {
    const lines = chunk.split('\n')
    const eventLine = lines.find((line) => line.startsWith('event: '))
    const dataLine = lines.find((line) => line.startsWith('data: '))
    if (!eventLine || !dataLine) continue
    events.push({
      event: eventLine.slice('event: '.length),
      data: JSON.parse(dataLine.slice('data: '.length)),
    })
  }
  return { events, remainder }
}

export async function streamChatMessage(
  sessionId: string,
  message: string,
  handlers: StreamHandlers,
): Promise<void> {
  let response: Response
  try {
    response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message }),
    })
  } catch {
    handlers.onError('网络异常，请稍后重试')
    return
  }

  if (!response.ok || !response.body) {
    // 开流之前的错误是标准 JSON 响应（例如会话不存在的 404），取出 detail 展示
    let detail = '请求发送失败，请稍后重试'
    try {
      const body = await response.text()
      detail = JSON.parse(body)?.detail ?? detail
    } catch {
      // 响应体不是 JSON，沿用通用提示
    }
    handlers.onError(detail)
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parsed = parseSseBuffer(buffer)
    buffer = parsed.remainder

    for (const event of parsed.events) {
      switch (event.event) {
        case 'tool_call_start':
          handlers.onToolCallStart(event.data.name, event.data.args)
          break
        case 'tool_call_end':
          handlers.onToolCallEnd(event.data.name, event.data.args, event.data.result)
          break
        case 'intent':
          handlers.onIntent?.(event.data.data)
          break
        case 'final': {
          // snake_case 到 camelCase 的映射收口在解析层，和 Day 4 引入流式接口时的处理保持一致
          const data = event.data.data as ChatResponseDto
          handlers.onFinal({
            role: 'assistant',
            intent: data.intent,
            answer: data.answer,
            confidence: data.confidence,
            needHuman: data.need_human,
            suggestedActions: data.suggested_actions,
            toolCalls: data.tool_calls.map((call) => ({ ...call, status: 'done' as const })),
          })
          break
        }
        case 'sources':
          handlers.onSources?.(event.data.data)
          break
        case 'session_meta':
          handlers.onSessionMeta?.(event.data.data)
          break
        case 'error':
          handlers.onError(event.data.message)
          break
      }
    }
  }
}