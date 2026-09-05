import http from './http'

export type Intent = 'order_issue' | 'account_issue' | 'refund_request' | 'general_inquiry' | 'other'

export interface UserMessage {
    role: 'user',
    content: string
}

export interface ToolCall {
    name: string,
    args: Record<string, unknown>,
    result?: Record<string, unknown>
    status: 'calling' | 'done'
}

export interface AssistantMessage {
    role: 'assistant',
    intent: Intent,
    answer: string,
    confidence: number
    needHuman: boolean
    suggestedActions: string[]
    toolCalls: ToolCall[]
    pending?: boolean
}

export type ChatMessage = UserMessage | AssistantMessage

export interface ChatResponseDto {
    intent: Intent,
    answer: string,
    confidence: number
    need_human: boolean
    suggested_actions: string[]
    tool_calls: {
        name: string;
        args: Record<string, unknown>;
        result: Record<string, unknown>
    }[]
}

export interface IntentData {
    intent: string
    confidence: number
    reasoning: string
    need_human: boolean
    label: string
    color: string
}

// 发给后端的历史消息里，AI 消息只需要还原成一段文本，后端目前只有 content 字段拼接对话上下文。不关心当时判断出的 intent 和置信度这些衍生字段
function toApiMessage(message: ChatMessage): {
    role: 'user' | 'assistant'; content: string
} {
    if (message.role === 'user') {
        return { role: 'user', content: message.content }
    } else {
        return { role: 'assistant', content: message.answer }
    }
}

interface StreamHandlers {
    onToolCallStart: (
        name: string,
        args: Record<string, unknown>
    ) => void
    onToolCallEnd: (
        name: string,
        args: Record<string, unknown>,
        result: Record<string, unknown>
    ) => void
    onFinal: (
        message: AssistantMessage
    ) => void
    onSources?: (data: {
        conversation_id: string
        sources: Array<{
            index: number
            filename: string
            chunk_index: number
            content: string
            score: number
            page?: number | null
        }>
    }) => void
    onIntent?: (data: IntentData) => void
    onError: (
        message: string
    ) => void
}

// 原生 EventSource 只能发送 GET 请求，没法带上完整的对话历史作为请求体，这里改为 fetch 拿到 ReadableStream 自己解析 SSE 格式。本质上和 EventSource 做的事情一样，只是把发起请求和解析事件流两件事都自己接管。

export async function streamChatMessage(history: ChatMessage[], handlers: StreamHandlers): Promise<void> {
    const payload = {
        messages: history.map(toApiMessage)
    }
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    if (!response.ok || !response.body) {
        handlers.onError('请求发送失败，请稍后重试')
        return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    // SSE 事件块之间用连续两个换行符分割，但网络分片不保证一个 chunk 刚好落在事件边界上，所以要维护一个缓冲区，每次追加新内容后按分割符分割，切不完整的尾巴留到下一次 chunk 再拼。
    let buffer = ''

    function processBuffer(fullBuffer: string): string {
        const events = fullBuffer.split('\n\n')
        const remainder = events.pop() ?? ''

        for (const rawEvent of events) {
            const dataLine = rawEvent.split('\n').find((line) => line.startsWith('data: '))
            if (!dataLine) {
                continue
            }

            const event = JSON.parse(dataLine.slice('data: '.length))
            switch (event.type) {
                case 'tool_call_start':
                    handlers.onToolCallStart(event.name, event.args)
                    break
                case 'tool_call_end':
                    handlers.onToolCallEnd(event.name, event.args, event.result)
                    break
                case 'final': {
                    const data = event.data as ChatResponseDto
                    handlers.onFinal({
                        role: 'assistant',
                        intent: data.intent,
                        answer: data.answer,
                        confidence: data.confidence,
                        needHuman: data.need_human,
                        suggestedActions: data.suggested_actions,
                        toolCalls: data.tool_calls.map((call) => ({
                            ...call, status: 'done' as const
                        }))
                    })
                    break
                }
                case 'sources':
                    handlers.onSources?.(event.data)
                    break
                case 'intent':
                    handlers.onIntent?.(event.data)
                    break
                case 'error':
                    handlers.onError(event.message)
                    break
            }
        }

        return remainder
    }

    while (true) {
        const { done, value } = await reader.read()
        if (done) {
            // 流结束时处理缓冲区中可能残留的最后一个事件
            processBuffer(buffer)
            break
        }

        buffer += decoder.decode(value, { stream: true })
        buffer = processBuffer(buffer)
    }
}